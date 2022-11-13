from flask import Flask, jsonify, request

from lyskad import User, Game
from util import get_string

app = Flask(__name__)


def message(message_, code: int, **kwargs):
    kwargs.update({'message': message_, 'code': code})
    return jsonify(kwargs), code


users: dict[str, User] = dict()


@app.route('/users', methods=['GET'])
def get_users():
    return message('OK', 200, users=list(map(lambda x: x.jsonify(), users.values())))


@app.route('/users/new', methods=['POST'])
def post_users_new():
    data = request.get_json()
    id_ = data.get('id')
    password = data.get('password')

    if id_ is None or password is None:
        return message(get_string('client_error.register_malformed'), 400)
    if id_ in users:
        return message(get_string('client_error.duplicated_id'), 409)

    user = User(id_, password)
    users[id_] = user

    return message('OK', 200, user=user.jsonify())


@app.route('/users/<user_id>', methods=['GET'])
def get_users_id(user_id: str):
    if user_id not in users:
        return message(get_string('client_error.user_not_found'), 404)

    return message('OK', 200, user=users.get(user_id).jsonify())


@app.route('/users/<user_id>', methods=['PATCH'])
def patch_users_id(user_id: str):
    if user_id not in users:
        return message(get_string('client_error.user_not_found'), 404)

    data = request.get_json()
    if password := data.get('password'):
        users[user_id].change_password(password)

    return message('OK', 200)


@app.route('/users/<user_id>', methods=['DELETE'])
def delete_users_id(user_id: str):
    if user_id not in users:
        return message(get_string('client_error.user_not_found'), 404)

    del users[user_id]
    return message('OK', 200)


games: dict[int, Game] = dict()


@app.route('/games', methods=['GET'])
def get_games():
    return message('OK', 200, games=list(map(lambda x: x.jsonify(), games.values())))


@app.route('/games/new', methods=['POST'])
def post_games_new():
    game = Game.new()
    games[game.id] = game
    return message('OK', 200, game=game.jsonify())


@app.route('/games/<int:game_id>', methods=['GET'])
def get_games_id(game_id: int):
    if game_id not in games:
        return message(get_string('client_error.game_not_found'), 404)
    return message('OK', 200, game=games[game_id].jsonify())


if __name__ == '__main__':
    app.run(debug=True)
