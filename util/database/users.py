from typing import Optional, Iterable

from pymysql import Connection
from pymysql.cursors import DictCursor

from lyskad import User
from util import encrypt


def get(user_id: str, database: Connection) -> User:
    """
    :except ValueError: 사용자가 존재하지 않는 경우 발생
    :param user_id: 사용자의 아이디
    :param database: 사용자 정보를 가져올 데이터베이스
    :return: 사용자 User 객체
    """
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM user WHERE id = %s', (user_id,))
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


def get_by_ranking(database, limit: Optional[int] = None) -> Iterable[User]:
    if limit is None:
        limit = GET_ALL_DEFAULT_LIMIT

    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM user ORDER BY rating DESC LIMIT %s', limit)
        while data := cursor.fetchone():
            yield User.get(data)


def get_ranking_place(user_id: str, database: Connection) -> int:
    with database.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM user WHERE rating > (SELECT rating FROM user WHERE id = %s)', user_id)
        return cursor.fetchone()[0]


def new(user_id: str, token: str, color: int, language: str, database: Connection) -> User:
    user = User(user_id, encrypt(token, user_id))
    with database.cursor() as cursor:
        cursor.execute(
            'INSERT INTO user (id, password, joined_at, color, language) VALUES (%s, %s, %s, %s, %s)',
            (user_id, user.token, user.joined_at, color, language))
        database.commit()
    return user


def change_password(user: User, token: str, database: Connection) -> User:
    user.token = encrypt(token, user.id)
    with database.cursor() as cursor:
        cursor.execute('UPDATE user SET password = %s WHERE id = %s', (user.token, user.id))
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


def login(user_id: str, password: str, database: Connection, encrypted: bool = False) -> User:
    user = get(user_id, database)
    if encrypted:
        encrypted_token = password
    else:
        encrypted_token = encrypt(password, user_id)
    if user.token == encrypted_token:
        return user


def add_exp_for_game(game_id: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('UPDATE user '
                       'SET games = games + (SELECT COUNT(*) FROM participant WHERE game_id = %s) '
                       'WHERE id IN (SELECT user_id FROM participant WHERE game_id = %s)',
                       (game_id, game_id))
        database.commit()


def add_wins(user_id: str, game_id: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('UPDATE user '
                       'SET wins = wins + (SELECT COUNT(*) FROM participant WHERE game_id = %s) '
                       'WHERE id = %s', (game_id, user_id))
        database.commit()


def apply_ratings(users: Iterable[User], database: Connection):
    with database.cursor() as cursor:
        for user in users:
            cursor.execute('UPDATE user SET rating = %s WHERE id = %s', (user.calculate_rating(), user.id))
        database.commit()
