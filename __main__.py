from typing import Optional

from flask import Flask, jsonify, request

from lyskad import User, Game, Participant, Nema
from lyskad.game import GameState, HjulienDirection
from lyskad.nema import is_valid_position, get_nemas
from lyskad.participant import get_participant_ids, leave, get_user_games
from util import get_string
from util.database import users, games

app = Flask(__name__)


def message(message_, code: int, **kwargs):
    kwargs.update({'message': message_, 'code': code})
    return jsonify(kwargs), code


def login(request_) -> Optional[User]:
    data = request_.get_json()
    user_id = data.get('id')
    password = data.get('password')
    if user_id is None:
        return
    if password is None:
        return
    if (user := users.login(user_id, password)) is None:
        return
    if user.id != user_id:
        return
    return user


@app.route('/users', methods=['GET'])
def get_users():
    if request.content_type is None:
        data = dict()
    else:
        data = request.get_json()

    limit = data.get('limit')

    return message(
        'OK', 200,
        users=list(map(lambda x: x.jsonify(), users.get_all(limit)))
    )


@app.route('/users/new', methods=['POST'])
def post_users_new():
    data = request.get_json()
    id_ = data.get('id')
    password = data.get('password')

    if id_ is None or password is None:
        return message(get_string('client_error.register_malformed'), 400)
    if users.exists(id_):
        return message(get_string('client_error.duplicated_id'), 409)

    user = users.new(id_, password)
    return message('OK', 200, user=user.jsonify())


@app.route('/users/<user_id>', methods=['GET'])
def get_users_id(user_id: str):
    if not users.exists(user_id):
        return message(get_string('client_error.user_not_found'), 404)

    return message('OK', 200, user=users.get(user_id).jsonify())


@app.route('/users/<user_id>', methods=['PATCH'])
def patch_users_id(user_id: str):
    try:
        user = users.get(user_id)
    except ValueError:
        return message(get_string('client_error.user_not_found'), 404)

    if login(request) is None:
        return message(get_string('client_error.unauthorized'), 401)

    data = request.get_json()
    if password := data.get('password_to_be'):
        users.change_password(user, password)

    return message('OK', 200)


@app.route('/users/<user_id>', methods=['DELETE'])
def delete_users_id(user_id: str):
    try:
        user = users.get(user_id)
    except ValueError:
        return message(get_string('client_error.user_not_found'), 404)

    if (user_login := login(request)) is None:
        return message(get_string('client_error.unauthorized'), 401)

    if user.id != user_login.id:
        return message(get_string('client_error.forbidden'), 403)

    users.delete_user(user_id)
    return message('OK', 200)


@app.route('/games', methods=['GET'])
def get_games():
    if request.content_type is None:
        data = dict()
    else:
        data = request.get_json()

    limit = data.get('limit')

    return message(
        'OK', 200,
        games=list(map(lambda x: x.jsonify(), games.get_all(limit)))
    )


@app.route('/games/new', methods=['POST'])
def post_games_new():
    if (user := login(request)) is None:
        return message(get_string('client_error.unauthorized'), 401)

    direction = request.get_json().get('direction')

    game_id = games.new(user.id, direction)
    game = games.get(game_id)
    participants.append(Participant(user.id, game.id))
    return message('OK', 200, game=game.jsonify())


@app.route('/games/<int:game_id>', methods=['GET'])
def get_games_id(game_id: int):
    if not games.exists(game_id):
        return message(get_string('client_error.game_not_found'), 404)
    ids = get_participant_ids(game_id, participants)
    return message('OK', 200, game=games.get(game_id).jsonify(), participants=ids)


participants: list[Participant] = list()


@app.route('/games/<int:game_id>/join', methods=['POST'])
def post_games_id_join(game_id: int):
    if (user := login(request)) is None:
        return message(get_string('client_error.unauthorized'), 401)

    try:
        game = games.get(game_id)
    except ValueError:
        return message(get_string('client_error.game_not_found'), 404)

    if game.state != GameState.IDLE:
        return message(get_string('client_error.game_not_idle'), 404)

    participants.append(Participant(user.id, game_id))
    return message('OK', 200)


@app.route('/games/<int:game_id>/leave', methods=['POST'])
def post_games_id_leave(game_id: int):
    if (user := login(request)) is None:
        return message(get_string('client_error.unauthorized'), 401)

    if not games.exists(game_id):
        return message(get_string('client_error.game_not_found'), 404)

    ids = get_participant_ids(game_id, participants)
    if user.id not in ids:
        return message(get_string('client_error.not_joined'), 404)

    leave(user.id, game_id, participants)
    return message('OK', 200)


@app.route('/games/<int:game_id>/start', methods=['POST'])
def post_games_id_start(game_id: int):
    if (user := login(request)) is None:
        return message(get_string('client_error.unauthorized'), 401)

    try:
        game = games.get(game_id)
    except ValueError:
        return message(get_string('client_error.game_not_found'), 404)

    if game.created_by != user.id:
        return message(get_string('client_error.not_owner'), 403)

    if game.state != GameState.IDLE:
        return message(get_string('client_error.game_not_idle'), 403)

    ids = get_participant_ids(game.id, participants)
    if len(ids) < 2:
        return message(get_string('client_error.not_enough_player'), 403)

    game.state = GameState.PLAYING
    return message('OK', 200)


@app.route('/users/<user_id>/games', methods=['GET'])
def get_users_id_games(user_id: str):
    if not users.exists(user_id):
        return message(get_string('client_error.user_not_found'), 404)

    ids = get_user_games(user_id, participants)
    return message('OK', 200, games=ids)


nemas: list[Nema] = list()


@app.route('/games/<int:game_id>/nema/<int:nema_position>', methods=['POST'])
def post_games_id_put(game_id: int, nema_position: int):
    if (user := login(request)) is None:
        return message(get_string('client_error.unauthorized'), 401)

    try:
        game = games.get(game_id)
    except ValueError:
        return message(get_string('client_error.game_not_found'), 404)

    ids = get_participant_ids(game.id, participants)
    if user.id not in ids:
        return message(get_string('client_error.not_joined'), 403)

    if not is_valid_position(nema_position):
        return message(get_string('client_error.invalid_position'), 403)

    if game.state != GameState.PLAYING:
        return message(get_string('client_error.game_not_playing'), 403)

    nema = Nema(user.id, game.id, nema_position)
    nemas.append(nema)
    return message('OK', 200, nema=nema.jsonify())


@app.route('/games/<int:game_id>/nema', methods=['GET'])
def get_games_id_nema(game_id: int):
    if not games.exists(game_id):
        return message(get_string('client_error.game_not_found'), 404)

    ingame_nemas = get_nemas(game_id, nemas)
    return message('OK', 200, nemas=list(map(lambda x: x.jsonify(), ingame_nemas)))


if __name__ == '__main__':
    app.run(debug=True)
