from typing import Optional

from pymysql.cursors import DictCursor

from lyskad import Nema
from util.database import database


def new(nema: Nema):
    with database.cursor() as cursor:
        cursor.execute(
            'INSERT INTO nema VALUES (%s, %s, %s, %s)',
            (nema.user_id, nema.game_id, nema.position, nema.created_at)
        )
        database.commit()


def get_nemas(game_id: int) -> list[Nema]:
    result = list()
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM nema WHERE game_id = %s', game_id)
        while line := cursor.fetchone():
            result.append(Nema.get(line))
    return result


def get(game_id: int, position: int) -> Optional[Nema]:
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM nema WHERE game_id = %s AND position = %s', (game_id, position))
        data = cursor.fetchone()

    if data is None:
        return
    return Nema.get(data)