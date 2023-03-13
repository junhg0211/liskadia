from datetime import datetime
from typing import Optional

from pymysql import Connection
from pymysql.cursors import DictCursor

from lyskad import Game
from lyskad.game import HjulienDirection


def get(game_id: int, database: Connection) -> Game:
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM game WHERE id = %s', game_id)
        data = cursor.fetchone()
    if data is None:
        raise ValueError('존재하지 않는 게임 ID입니다.')
    return Game.get(data)


GET_ALL_DEFAULT_LIMIT = 50


def get_all(database: Connection, limit: Optional[int] = None, state: Optional[int] = None) -> list[Game]:
    if limit is None:
        limit = GET_ALL_DEFAULT_LIMIT

    result = list()
    with database.cursor(DictCursor) as cursor:
        if state is None:
            cursor.execute('SELECT * FROM game ORDER BY id DESC LIMIT %s', limit)
        else:
            cursor.execute('SELECT * FROM game WHERE state = %s ORDER BY id DESC LIMIT %s', (state, limit))
        while data := cursor.fetchone():
            result.append(Game.get(data))
    return result


def new(created_by: str, direction: Optional[bool], max_score: int, timeout: int, database: Connection) -> int:
    if direction is None:
        direction = HjulienDirection.DEFAULT

    with database.cursor() as cursor:
        cursor.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_NAME = 'game'")
        game_id = cursor.fetchone()[0]
        cursor.execute(
            'INSERT INTO game (direction, max_score, created_at, created_by, timeout) VALUES (%s, %s, %s, %s, %s)',
            (direction, max_score, datetime.utcnow(), created_by, timeout)
        )
        database.commit()
    return game_id


def exists(game_id: int, database: Connection) -> bool:
    try:
        get(game_id, database)
    except ValueError:
        return False
    else:
        return True


def set_state(game_id: int, state: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('UPDATE game SET state = %s WHERE id = %s', (state, game_id))
        database.commit()


def get_state(game_id, database):
    with database.cursor() as cursor:
        cursor.execute('SELECT state FROM game WHERE id = %s', game_id)
        try:
            return cursor.fetchone()[0]
        except IndexError:
            return
