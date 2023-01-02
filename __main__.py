from datetime import datetime, timedelta
from hashlib import sha256
from random import randint
from typing import Optional
from urllib.parse import parse_qsl

from flask import Flask, jsonify, request, render_template, session, redirect, make_response

from lyskad import User, Nema, calculate_score_by
from lyskad.game import GameState, Game
from lyskad.nema import is_valid_position
from util import get_string, encrypt, get_language, DEFAULT_LANGUAGE
from util.database import users, games, participants, nemas, get_connection, scores

app = Flask(__name__)
app.secret_key = sha256('ydng0fug lrid2uf'.encode()).hexdigest()


def message(message_, code: int, **kwargs):
    kwargs.update({'message': message_, 'code': code})
    return jsonify(kwargs), code


def login(user_id: str, password: str, *, encrypted: bool = False) -> Optional[User]:
    with get_connection() as database:
        if (user := users.login(user_id, password, database, encrypted)) is None:
            return
    if user.id != user_id:
        return
    return user


def parse_data(request_) -> dict:
    if request_.content_type == 'application/json':
        return request_.get_json()

    data = request_.get_data(as_text=True)
    if not data:
        return dict()

    return dict(parse_qsl(data, strict_parsing=True))


@app.route('/users', methods=['GET'])
def get_users():
    data = parse_data(request)
    limit = data.get('limit')

    with get_connection() as database:
        return message('OK', 200, users=list(map(lambda x: x.jsonify(), users.get_all(database, limit))))


@app.route('/users/new', methods=['POST'])
def post_users_new():
    data = parse_data(request)
    id_ = data.get('id')
    password = data.get('password')
    color = int(data.get('color')[1:], 16)
    language = data.get('language')

    if color is None:
        color = randint(0, 0xFFFFFF)

    if id_ is None or password is None:
        return message(get_string('client_error.register_malformed'), 400)
    with get_connection() as database:
        if users.exists(id_, database):
            return message(get_string('client_error.duplicated_id'), 409)

        users.new(id_, password, color, language, database)

    return redirect('/')


@app.route('/users/<user_id>', methods=['GET'])
def get_users_id(user_id: str):
    with get_connection() as database:
        if not users.exists(user_id, database):
            return message(get_string('client_error.user_not_found'), 404)

        return message('OK', 200, user=users.get(user_id, database).jsonify())


@app.route('/login', methods=['POST'])
def post_login():
    data = parse_data(request)
    user_id = data.get('id')
    password = data.get('password')
    remember_me = data.get('remember-me')
    during_day = int(data.get('during-day'))

    if user_id is None or password is None:
        return message(get_string('client_error.register_malformed'), 400)

    if login(user_id, password) is None:
        return message(get_string('client_error.unauthorized'), 401)

    res = make_response(redirect('/'))
    if remember_me == 'on':
        until = datetime.now() + timedelta(days=during_day)
        res.set_cookie('id', user_id, expires=until)
        res.set_cookie('password', encrypt(password, user_id), expires=until)

    session['id'] = user_id
    return res


@app.route('/logout', methods=['GET'])
def get_logout():
    session.pop('id', None)
    res = redirect('/')
    res.set_cookie('id', '', expires=0)
    res.set_cookie('password', '', expires=0)
    return res


@app.route('/users/<user_id>', methods=['PATCH'])
def patch_users_id(user_id: str):
    with get_connection() as database:
        try:
            user = users.get(user_id, database)
        except ValueError:
            return message(get_string('client_error.user_not_found'), 404)

        if (login_id := session.get('id')) is None:
            return message(get_string('client_error.unauthorized'), 401)

        if login_id != user.id:
            return message(get_string('client_error.forbidden'), 403)

        data = request.get_json()
        if password := data.get('password'):
            users.change_password(user, password, database)

    return message('OK', 200)


@app.route('/users/<user_id>', methods=['DELETE'])
def delete_users_id(user_id: str):
    with get_connection() as database:
        try:
            user = users.get(user_id, database)
        except ValueError:
            return message(get_string('client_error.user_not_found'), 404)

        if (login_id := session.get('id')) is None:
            return message(get_string('client_error.unauthorized'), 401)

        if user.id != login_id:
            return message(get_string('client_error.forbidden'), 403)

        users.delete_user(user_id, database)
    return message('OK', 200)


@app.route('/games', methods=['GET'])
def get_games():
    data = parse_data(request)
    limit = data.get('limit')

    with get_connection() as database:
        return message('OK', 200, games=list(map(lambda x: x.jsonify(), games.get_all(database, limit))))


@app.route('/games/new', methods=['POST'])
def post_games_new():
    if (login_id := session.get('id')) is None:
        return message(get_string('client_error.unauthorized'), 401)

    data = parse_data(request)
    direction = data.get('direction') == 'on'
    try:
        target_score = int(data.get('score'))
    except ValueError:
        return message(get_string('client_error.invalid_max_score'), 403)

    if not (1 <= target_score <= 100):
        return message(get_string('client_error.invalid_max_score'), 403)

    with get_connection() as database:
        user = users.get(login_id, database)
        game_id = games.new(user.id, direction, target_score, database)
        game = games.get(game_id, database)
        participants.new(user.id, game.id, database)
    return redirect(f'/game/{game_id}')


@app.route('/games/<int:game_id>', methods=['GET'])
def get_games_id(game_id: int):
    with get_connection() as database:
        if not games.exists(game_id, database):
            return message(get_string('client_error.game_not_found'), 404)
        user_ids = participants.get_ids(game_id, database)
        return message(
            'OK', 200, game=games.get(game_id, database).jsonify(),
            participants=[users.get(user_id, database).jsonify() for user_id in user_ids])


@app.route('/games/<int:game_id>/join', methods=['POST'])
def post_games_id_join(game_id: int):
    if (login_id := session.get('id')) is None:
        return message(get_string('client_error.unauthorized'), 401)

    with get_connection() as database:
        try:
            game = games.get(game_id, database)
        except ValueError:
            return message(get_string('client_error.game_not_found'), 404)

        if game.state != GameState.IDLE:
            return message(get_string('client_error.game_not_idle'), 404)

        user = users.get(login_id, database)
        if user.id in participants.get_ids(game.id, database):
            return message(get_string('client_error.already_in'), 403)

        participants.new(user.id, game_id, database)
    return redirect(f'/game/{game.id}')


@app.route('/games/<int:game_id>/leave', methods=['POST'])
def post_games_id_leave(game_id: int):
    if (login_id := session.get('id')) is None:
        return message(get_string('client_error.unauthorized'), 401)

    with get_connection() as database:
        if not games.exists(game_id, database):
            return message(get_string('client_error.game_not_found'), 404)

        user = users.get(login_id, database)
        ids = participants.get_ids(game_id, database)
        if user.id not in ids:
            return message(get_string('client_error.not_joined'), 404)

        state = games.get_state(game_id, database)
        if state != GameState.IDLE:
            return message(get_string('client_error.not_in_idle_mode'), 403)

        participants.leave(user.id, game_id, database)
    return redirect(f'/game/{game_id}')


@app.route('/games/<int:game_id>/start', methods=['POST'])
def post_games_id_start(game_id: int):
    if (login_id := session.get('id')) is None:
        return message(get_string('client_error.unauthorized'), 401)

    with get_connection() as database:
        try:
            game = games.get(game_id, database)
        except ValueError:
            return message(get_string('client_error.game_not_found'), 404)

        user = users.get(login_id, database)
        if game.created_by != user.id:
            return message(get_string('client_error.not_owner'), 403)

        if game.state != GameState.IDLE:
            return message(get_string('client_error.game_not_idle'), 403)

        ids = tuple(participants.get_ids(game.id, database))
        if len(ids) < 2:
            return message(get_string('client_error.not_enough_player'), 403)

        games.set_state(game.id, GameState.PLAYING, database)
    return redirect(f'/game/{game.id}')


@app.route('/users/<user_id>/games', methods=['GET'])
def get_users_id_games(user_id: str):
    with get_connection() as database:
        if not users.exists(user_id, database):
            return message(get_string('client_error.user_not_found'), 404)

        ids = participants.get_game_ids(user_id, database)
    return message('OK', 200, games=ids)


@app.route('/games/<int:game_id>/nemas/<int:nema_position>', methods=['POST'])
def post_games_id_put(game_id: int, nema_position: int):
    if (login_id := session.get('id')) is None:
        return message(get_string('client_error.unauthorized'), 401)

    with get_connection() as database:
        try:
            game = games.get(game_id, database)
        except ValueError:
            return message(get_string('client_error.game_not_found'), 404)

        user = users.get(login_id, database)
        ids = tuple(participants.get_ids(game.id, database))
        if user.id not in ids:
            return message(get_string('client_error.not_joined'), 403)

        if not is_valid_position(nema_position):
            return message(get_string('client_error.invalid_position'), 403)

        if game.state != GameState.PLAYING:
            return message(get_string('client_error.game_not_playing'), 403)

        if nemas.get(game.id, nema_position, database) is not None:
            return message(get_string('client_error.duplicated'), 403)

        nema_count = nemas.get_nema_count(game.id, database)
        if ids[nema_count % len(ids)] != login_id:
            return message(get_string('client_error.not_turn'), 403)

        if nema_count == 0 and nema_position not in (44, 45, 54, 55):
            return message(get_string('client_error.invalid_position'), 403)

        nema = Nema(user.id, game.id, nema_position)
        nemas.new(nema, database)

        attack_positions, defence_data = \
            calculate_score_by(game, nemas.get_nemas(game.id, database), nema.get_position())
        for x, y in attack_positions:
            scores.new(game.id, 10 * y + x, user.id, nema_position, database)
        for (x, y), user_id in defence_data:
            scores.new(game.id, 10 * y + x, user_id, nema_position, database)

        player_ids = tuple(participants.get_ids(game.id, database))
        scores_ = tuple(scores.get_scores(game.id, database).values())
        if len(scores_) == len(player_ids) and min(scores_) >= game.max_score \
                or nemas.get_nema_count(game.id, database) == 100:
            games.set_state(game.id, GameState.END, database)

            places = participants.get_places(scores.get_scoring_nemas(game.id, database))
            participants.record_places(places, game.id, database)

            users.add_exp_for_game(game.id, database)
            users.add_wins(places[0], game.id, database)

    return message('OK', 200, nema=nema.jsonify())


@app.route('/games/<int:game_id>/nemas', methods=['GET'])
def get_games_id_nema(game_id: int):
    with get_connection() as database:
        if not games.exists(game_id, database):
            return message(get_string('client_error.game_not_found'), 404)

        ingame_nemas = nemas.get_nemas(game_id, database)
    nemas_ = list(map(lambda x: x.jsonify(), ingame_nemas))
    return message('OK', 200, nemas=nemas_, count=len(nemas_))


@app.route('/games/<int:game_id>/meta', methods=['GET'])
def get_games_id_nema_count(game_id: int):
    with get_connection() as database:
        if not games.exists(game_id, database):
            return message(get_string('client_error.game_not_found'), 404)

        nema_count = nemas.get_nema_count(game_id, database)
        state = games.get_state(game_id, database)
        user_count = len(tuple(participants.get_ids(game_id, database)))

        scores_ = list(map(lambda x: x.jsonify(), scores.get_scoring_nemas(game_id, database)))

        return message('OK', 200, nema_count=nema_count, state=state, user_count=user_count, scores=scores_)


@app.route('/', methods=['GET'])
def get_index():
    return redirect('/game')


@app.route('/register', methods=['GET'])
def get_register():
    language = DEFAULT_LANGUAGE
    if login_id := session.get('id'):
        with get_connection() as database:
            user = users.get(login_id, database)
        language = user.language

    return render_template('register.html', get_language=lambda x: get_language(x, language))


@app.route('/login', methods=['GET'])
def get_login():
    language = DEFAULT_LANGUAGE
    if login_id := session.get('id'):
        with get_connection() as database:
            user = users.get(login_id, database)
        language = user.language

    return render_template('login.html', get_language=lambda x: get_language(x, language))


@app.route('/game', methods=['GET'])
def get_game():
    joined_games = list()
    login_id = session.get('id')

    cookie_id = request.cookies.get('id')
    cookie_password = request.cookies.get('password')
    if login_id is None and cookie_id and cookie_password and login(cookie_id, cookie_password, encrypted=True):
        session['id'] = cookie_id
        login_id = cookie_id

    with get_connection() as database:
        games_list: list[list[Game]] = [list(), list(), list()]

        if login_id:
            joined_games = list(participants.get_games(login_id, database, 10))

        for game in games.get_all(database, 20):
            games_list[game.state].append(game)

        language = DEFAULT_LANGUAGE
        if login_id := session.get('id'):
            user = users.get(login_id, database)
            language = user.language

    return render_template(
        'games.html', login_id=login_id,
        idle_games=games_list[0], ongoing_games=games_list[1], ended_games=games_list[2], joined_games=joined_games,
        get_language=lambda x: get_language(x, language))


@app.route('/game/<int:game_id>', methods=['GET'])
def get_game_id(game_id: int):
    with get_connection() as database:
        try:
            game = games.get(game_id, database)
        except ValueError as e:
            return str(e), 404

        user_ids = sorted(participants.get_ids(game.id, database))

        language = DEFAULT_LANGUAGE
        if login_id := session.get('id'):
            user = users.get(login_id, database)
            language = user.language

    return render_template(
        'game.html', game=game, participants=user_ids, login_id=session.get('id'),
        get_language=lambda x: get_language(x, language))


@app.route('/new_game', methods=['GET'])
def get_new_game():
    language = DEFAULT_LANGUAGE
    if login_id := session.get('id'):
        with get_connection() as database:
            user = users.get(login_id, database)
        language = user.language

    return render_template(
        'new_game.html', login_id=session.get('id'),
        get_language=lambda x: get_language(x, language))


@app.route('/profile/<user_id>', methods=['GET'])
def get_profile_id(user_id: str):
    with get_connection() as database:
        try:
            user = users.get(user_id, database)
        except ValueError:
            return message(get_string('client_error.user_not_found'), 404)

        played_games = list(participants.get_games(user_id, database))

        language = DEFAULT_LANGUAGE
        if login_id := session.get('id'):
            login_user = users.get(login_id, database)
            language = login_user.language

    return render_template(
        'profile.html', user=user, played_games=played_games, login_id=session.get('id'),
        get_language=lambda x: get_language(x, language))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
