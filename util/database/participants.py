from datetime import datetime
from typing import Iterable, Iterator

from pymysql import Connection
from pymysql.cursors import DictCursor

from lyskad import Game, Score


def new(user_id: str, game_id: int, database: Connection):
    joined_at = datetime.now()
    with database.cursor() as cursor:
        cursor.execute("INSERT INTO participant VALUES (%s, %s, %s, NULL)", (user_id, game_id, joined_at))
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


def get_games(user_id: str, database: Connection, limit: int = 100) -> Iterator[Game]:
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM game '
                       'JOIN participant p ON game.id = p.game_id AND p.user_id = %s '
                       'ORDER BY id DESC '
                       'LIMIT %s', (user_id, limit))
        while line := cursor.fetchone():
            yield Game.get(line)


def is_in(user_id: str, game_id: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('SELECT game_id FROM participant WHERE user_id = %s AND game_id = %s', (user_id, game_id))
        return bool(cursor.fetchone())


def get_places(scores: list[Score]) -> tuple[str]:
    user_scores = dict()
    scored_user_counts = list()
    user_information: dict[str, tuple[int, int]] = dict()
    for score in scores:
        user_id = score.user_id

        if user_id in user_scores:
            user_scores[user_id] += 1
        else:
            user_scores[user_id] = 1
        score = user_scores[user_id]

        if len(scored_user_counts) < score:
            scored_user_counts.append(1)
        else:
            scored_user_counts[score-1] += 1
        count = scored_user_counts[score-1]
        user_information[user_id] = (score, -count)

    # noinspection PyTypeChecker
    return tuple(map(lambda x: x[0], sorted(user_information.items(), key=lambda x: x[1], reverse=True)))


def record_places(places: tuple[str], game_id: int, database: Connection):
    with database.cursor() as cursor:
        for i, user_id in enumerate(places):
            cursor.execute(
                'UPDATE participant SET place = %s WHERE game_id = %s AND user_id = %s',
                (i, game_id, user_id))
        database.commit()
