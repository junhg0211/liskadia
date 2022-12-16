from typing import Optional

from pymysql import Connection
from pymysql.cursors import DictCursor

from lyskad import User
from util import encrypt


def get(user_id: str, database: Connection) -> User:
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM user WHERE id = %s', user_id)
        data = cursor.fetchone()
    if data is None:
        raise ValueError('존재하지 않는 사용자 ID입니다.')
    return User.get(data)


GET_ALL_DEFAULT_LIMIT = 50


def get_all(database: Connection, limit: Optional[int] = None) -> list[User]:
    if limit is None:
        limit = GET_ALL_DEFAULT_LIMIT

    result = list()
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM user LIMIT %s', limit)
        while data := cursor.fetchone():
            result.append(User.get(data))
    return result


def new(user_id: str, password: str, color: int, database: Connection) -> User:
    user = User(user_id, encrypt(password, user_id))
    with database.cursor() as cursor:
        cursor.execute(
            'INSERT INTO user (id, password, joined_at, color) VALUES (%s, %s, %s, %s)',
            (user_id, user.password_token, user.joined_at, color))
        database.commit()
    return user


def change_password(user: User, raw_password: str, database: Connection) -> User:
    user.password_token = encrypt(raw_password, user.id)
    with database.cursor() as cursor:
        cursor.execute('UPDATE user SET password = %s WHERE id = %s', (user.password_token, user.id))
        database.commit()
    return user


def delete_user(user_id: str, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('DELETE FROM user WHERE id = %s', user_id)
        database.commit()


def exists(user_id: str, database: Connection):
    try:
        get(user_id, database)
    except ValueError:
        return False
    else:
        return True


def login(user_id: str, password: str, database: Connection) -> User:
    user = get(user_id, database)
    if user.password_token == encrypt(password, user_id):
        return user
