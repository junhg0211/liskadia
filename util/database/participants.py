from datetime import datetime
from typing import Iterable, Iterator

from pymysql import Connection
from pymysql.cursors import DictCursor

from lyskad import Game


def new(user_id: str, game_id: int, database: Connection):
    joined_at = datetime.now()
    with database.cursor() as cursor:
        cursor.execute("INSERT INTO participant VALUES (%s, %s, %s)", (user_id, game_id, joined_at))
        database.commit()


def get_ids(game_id: int, database: Connection) -> Iterable[str]:
    with database.cursor() as cursor:
        cursor.execute('SELECT user_id FROM participant WHERE game_id = %s ORDER BY joined_at', game_id)
        return map(lambda x: x[0], cursor.fetchall())


def leave(user_id: str, game_id: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('DELETE FROM participant WHERE user_id = %s AND game_id = %s', (user_id, game_id))
        database.commit()


def get_game_ids(user_id: str, database: Connection) -> list[int]:
    ids = list()
    with database.cursor() as cursor:
        cursor.execute('SELECT game_id FROM participant WHERE user_id = %s', user_id)
        while line := cursor.fetchone():
            ids.append(line[0])
    return ids


def get_games(user_id: str, database: Connection) -> Iterator[Game]:
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM game '
                       'JOIN participant p ON game.id = p.game_id AND p.user_id = %s '
                       'ORDER BY id', user_id)
        while line := cursor.fetchone():
            yield Game.get(line)


def is_in(user_id: str, game_id: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('SELECT game_id FROM participant WHERE user_id = %s AND game_id = %s', (user_id, game_id))
        return bool(cursor.fetchone())
