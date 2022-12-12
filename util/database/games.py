from datetime import datetime
from typing import Optional

from pymysql.cursors import DictCursor

from lyskad import Game
from lyskad.game import HjulienDirection
from util.database import database


def get(game_id: int) -> Game:
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM game WHERE id = %s', game_id)
        data = cursor.fetchone()
    if data is None:
        raise ValueError('존재하지 않는 게임 ID입니다.')
    return Game.get(data)


GET_ALL_DEFAULT_LIMIT = 50


def get_all(limit: Optional[int] = None) -> list[Game]:
    if limit is None:
        limit = GET_ALL_DEFAULT_LIMIT

    result = list()
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM game LIMIT %s', limit)
        while data := cursor.fetchone():
            result.append(Game.get(data))
    return result


def new(created_by: str, direction: Optional[bool]) -> int:
    if direction is None:
        direction = HjulienDirection.DEFAULT

    with database.cursor() as cursor:
        cursor.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_NAME = 'game'")
        game_id = cursor.fetchone()[0]
        cursor.execute(
            'INSERT INTO game (direction, created_at, created_by) VALUES (%s, %s, %s)',
            (direction, datetime.now(), created_by)
        )
        database.commit()
    return game_id


def exists(game_id: int) -> bool:
    try:
        get(game_id)
    except ValueError:
        return False
    else:
        return True


def set_state(game_id: int, state: int):
    with database.cursor() as cursor:
        cursor.execute('UPDATE game SET state = %s WHERE id = %s', (state, game_id))
        database.commit()