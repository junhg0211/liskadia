from argparse import ArgumentParser
from datetime import datetime, timedelta
from hashlib import sha256
from random import randint
from typing import Optional
from urllib.parse import parse_qsl

from flask import Flask, jsonify, request, render_template, session, redirect, make_response
from pymysql import Connection

from lyskad import User, Nema, calculate_score_by
from lyskad.game import GameState, Game
from lyskad.nema import is_valid_position
from util import get_string, encrypt, get_language, DEFAULT_LANGUAGE, get_language_list_html
from util.database import users, games, participants, nemas, get_connection, scores, histories
from util.general import format_percentage

app = Flask(__name__)
app.secret_key = sha256('ydng0fug lrid2uf'.encode()).hexdigest()


def message(message_, code: int, **kwargs):
    kwargs.update({'message': message_, 'code': code})
    return jsonify(kwargs), code


def login(user_id: str, password: str, database: Connection, *, encrypted: bool = False) -> Optional[User]:
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
        histories.apply(id_, 0, database)

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
        return redirect('/login?error=wrong')

    with get_connection() as database:
        try:
            if login(user_id, password, database) is None:
                return redirect('/login?error=wrong')
        except ValueError:
            return redirect('/login?error=wrong')

        users.update_last_interaction(user_id, database)

    res = make_response(redirect('/'))
    if remember_me == 'on':
        until = datetime.utcnow() + timedelta(days=during_day)
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


@app.route('/users/edit', methods=['POST'])
def patch_users_id():
    if (login_id := session.get('id')) is None:
        return message(get_string('client_error.unauthorized'), 401)

    data = parse_data(request)

    with get_connection() as database:
        user = users.get(login_id, database)

        color = int(data.get('color')[1:], 16)
        if user.color != color:
            users.set_color(login_id, color, database)

        language = data.get('language')
        if user.language != language:
            users.set_language(login_id, language, database)

    return redirect('/')


@app.route('/ratings/<user_id>', methods=['GET'])
def get_ratings_id(user_id: str):
    with get_connection() as database:
        if not users.exists(user_id, database):
            return message(get_string('client_error.user_not_found'), 404)

        history = list(histories.get(user_id, database))

    return message('OK', 200, history=history)


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

    try:
        timeout = int(data.get('timeout'))
    except ValueError:
        return message(get_string('client_error.invalid_timeout'), 403)
    if not (10 <= timeout):
        return message(get_string('client_error.invalid_timeout'), 403)

    with get_connection() as database:
        user = users.get(login_id, database)
        game_id = games.new(user.id, direction, target_score, timeout, database)
        game = games.get(game_id, database)
        participants.new(user.id, game.id, database)

        users.update_last_interaction(user.id, database)
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

        users.update_last_interaction(user.id, database)
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

        users.update_last_interaction(user.id, database)
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

        users.update_last_interaction(user.id, database)
    return redirect(f'/game/{game.id}')


@app.route('/users/<user_id>/games', methods=['GET'])
def get_users_id_games(user_id: str):
    with get_connection() as database:
        if not users.exists(user_id, database):
            return message(get_string('client_error.user_not_found'), 404)

        ids = participants.get_game_ids(user_id, database)
    return message('OK', 200, games=ids)


def is_game_timeout(game: Game, database: Connection, last_nema: Optional[Nema] = None) -> bool:
    if game.state != GameState.PLAYING:
        return False

    if last_nema is None:
        last_nema = nemas.get_last_nema(game.id, database)

    now = datetime.now()
    return last_nema is not None and last_nema.created_at + timedelta(seconds=game.timeout) < now


def end_game(game: Game, database: Connection, loser_id: Optional[str] = None):
    """
    게임 종료를 진행합니다.

    `loser` 값이 설정되면 `loser`에 해당하는 사람의 순위를 가장 낮은 것으로 설정합니다.
    이 기능은 시간 제한으로 인한 게임 종료가 발생했을 때에 사용합니다.
    """
    games.set_state(game.id, GameState.END, database)

    places = participants.get_places(scores.get_scoring_nemas(game.id, database))
    if loser_id is not None and loser_id in places:
        places = list(places)
        places.remove(loser_id)
        places.append(loser_id)
    participants.record_places(places, game.id, database)

    users.add_exp_for_game(game.id, database)
    if places:
        users.add_wins(places[0], game.id, database)
    now = datetime.utcnow()
    users.apply_ratings(map(lambda id_: users.get(id_, database), places), database, now)


@app.route('/games/<int:game_id>/nemas/<int:nema_position>', methods=['POST'])
def post_games_id_put(game_id: int, nema_position: int):
    if (login_id := session.get('id')) is None:
        return message(get_string('client_error.unauthorized'), 401)

    with get_connection() as database:
        user = users.get(login_id, database)
        users.update_last_interaction(user.id, database)

        try:
            game = games.get(game_id, database)
        except ValueError:
            return message(get_string('client_error.game_not_found'), 404)

        ids = tuple(participants.get_ids(game.id, database))
        if user.id not in ids:
            return message(get_string('client_error.not_joined'), 403)

        if not is_valid_position(nema_position):
            return message(get_string('client_error.invalid_position'), 403)

        if game.state != GameState.PLAYING:
            return message(get_string('client_error.game_not_playing'), 403)

        if nemas.get(game.id, nema_position, database) is not None:
            return message(get_string('client_error.duplicated'), 403)

        if is_game_timeout(game, database):
            end_game(game, database, user.id)
            return message(get_string('client_error.timeout'), 403)

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
            end_game(game, database)

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

        game = games.get(game_id, database)

        last_nema = nemas.get_last_nema(game_id, database)
        if is_game_timeout(game, database, last_nema):
            end_game(game, database, last_nema.user_id)

        nema_count = nemas.get_nema_count(game_id, database)
        state = game.state
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

    if login_id is not None:
        return redirect('/')

    return render_template(
        'register.html', get_language=lambda x: get_language(x, language),
        language_list=get_language_list_html())


@app.route('/login', methods=['GET'])
def get_login():
    language = DEFAULT_LANGUAGE
    if login_id := session.get('id'):
        with get_connection() as database:
            user = users.get(login_id, database)
        language = user.language

    if login_id is not None:
        return redirect('/')

    error = request.args.get('error', '')
    if error:
        error = get_language(f'login.error.{error}', language)

    return render_template('login.html', get_language=lambda x: get_language(x, language), error=error)


@app.route('/game', methods=['GET'])
def get_game():
    joined_games = list()
    login_id = session.get('id')

    cookie_id = request.cookies.get('id')
    cookie_password = request.cookies.get('password')

    with get_connection() as database:
        if login_id is None \
                and cookie_id and cookie_password \
                and login(cookie_id, cookie_password, database, encrypted=True):
            session['id'] = cookie_id
            login_id = cookie_id
            users.update_last_interaction(cookie_id, database)

        games_list: list[list[Game]] = [list(), list(), list()]

        if login_id:
            joined_games = list(participants.get_games(login_id, database, 10))

        for game in games.get_all(database, 20):
            games_list[game.state].append(game)

        user = None
        language = DEFAULT_LANGUAGE
        if login_id := session.get('id'):
            user = users.get(login_id, database)
            language = user.language

    return render_template(
        'games.html', login_id=login_id, login_user=user,
        idle_games=games_list[0], ongoing_games=games_list[1], ended_games=games_list[2], joined_games=joined_games,
        get_language=lambda x: get_language(x, language))


@app.route('/game/<int:game_id>', methods=['GET'])
def get_game_id(game_id: int):
    with get_connection() as database:
        user = None
        language = DEFAULT_LANGUAGE
        if login_id := session.get('id'):
            user = users.get(login_id, database)
            language = user.language

        try:
            game = games.get(game_id, database)
        except ValueError:
            return render_template(
                'error.html', login_id=session.get('id'), login_user=user,
                get_language=lambda x: get_language(x, language), message='error.game_not_found'), 404

        last_nema = nemas.get_last_nema(game.id, database)
        if is_game_timeout(game, database, last_nema):
            end_game(game, database, last_nema.user_id)

        user_ids = sorted(participants.get_ids(game.id, database))

    return render_template(
        'game.html', game=game, participants=user_ids, login_id=session.get('id'), login_user=user,
        get_language=lambda x: get_language(x, language))


@app.route('/new_game', methods=['GET'])
def get_new_game():
    user = None
    language = DEFAULT_LANGUAGE
    if login_id := session.get('id'):
        with get_connection() as database:
            user = users.get(login_id, database)
        language = user.language

    return render_template(
        'new_game.html', login_id=session.get('id'), login_user=user,
        get_language=lambda x: get_language(x, language))


@app.route('/profile/<user_id>', methods=['GET'])
def get_profile_id(user_id: str):
    with get_connection() as database:
        login_user = None
        language = DEFAULT_LANGUAGE
        if login_id := session.get('id'):
            login_user = users.get(login_id, database)
            language = login_user.language

        try:
            user = users.get(user_id, database)
        except ValueError:
            return render_template(
                'error.html', login_id=session.get('id'), login_user=login_user,
                get_language=lambda x: get_language(x, language), message='error.user_not_found'), 404

        played_games = list(participants.get_games(user_id, database, limit=None))

        ranking_place = users.get_ranking_place(user.id, database) + 1

    return render_template(
        'profile.html', user=user, played_games=played_games, login_id=session.get('id'), ranking_place=ranking_place,
        get_language=lambda x: get_language(x, language), login_user=login_user)


@app.route('/ranking', methods=['GET'])
def get_ranking():
    return redirect('/ranking/1')


@app.route('/ranking/<int:page>', methods=['GET'])
def get_ranking_page(page: int):
    page -= 1
    with get_connection() as database:
        user_list = list(users.get_by_ranking(database, page))

        login_user = None
        language = DEFAULT_LANGUAGE
        if login_id := session.get('id'):
            login_user = users.get(login_id, database)
            language = login_user.language

        total_users = users.get_total(database)

    return render_template(
        'ranking.html', users=user_list, index=page, total_users=total_users,
        format_percentage=format_percentage, get_language=lambda x: get_language(x, language), login_id=login_id,
        count_per_page=users.GET_ALL_DEFAULT_LIMIT, login_user=login_user)


@app.route('/setting', methods=['GET'])
def get_setting():
    with get_connection() as database:
        language = DEFAULT_LANGUAGE
        if (login_id := session.get('id')) is None:
            return message(get_string('client_error.unauthorized'), 401)

        user = users.get(login_id, database)
        language = user.language

    return render_template(
        'setting.html', get_language=lambda x: get_language(x, language), login_id=login_id,
        user=user, language_list=get_language_list_html(user.language), login_user=user)


if __name__ == '__main__':
    parser = ArgumentParser(
        prog='Liskadia',
        description='리스카드 게임 서버 엔진'
    )
    parser.add_argument(
        '-t', '--http', action='store_true',
        help='설정된 경우 http 프로토콜로 서버를 실행합니다.')

    args = parser.parse_args()

    if args.http:
        app.run(host='0.0.0.0', port=80)
    else:
        app.run(
            host='0.0.0.0', port=443,
            ssl_context=(
                '/etc/letsencrypt/live/liskadia.shtelo.org/fullchain.pem',
                '/etc/letsencrypt/live/liskadia.shtelo.org/privkey.pem'))
