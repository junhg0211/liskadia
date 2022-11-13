from flask import Flask, jsonify, request

from lyskad import User
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

    return message('OK', 200, user=users[user_id].jsonify())


@app.route('/users/<user_id>', methods=['DELETE'])
def delete_users_id(user_id: str):
    if user_id not in users:
        return message(get_string('client_error.user_not_found'), 404)

    del users[user_id]
    return message('OK', 200)


if __name__ == '__main__':
    app.run(debug=True)
