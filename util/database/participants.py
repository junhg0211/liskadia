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


def get_participant_count(game_id: int, database: Connection) -> int:
    with database.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM participant WHERE game_id = %s', game_id)
        return cursor.fetchone()[0]


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
            scored_user_counts[score - 1] += 1
        count = scored_user_counts[score - 1]
        user_information[user_id] = (score, -count)

    # noinspection PyTypeChecker
    return tuple(map(lambda x: x[0], sorted(user_information.items(), key=lambda x: x[1], reverse=True)))


def record_places(places: tuple[str], game_id: int, database: Connection):
    with database.cursor() as cursor:
        for i, user_id in enumerate(places):
            cursor.execute('UPDATE participant SET place = %s WHERE game_id = %s AND user_id = %s',
                           (i, game_id, user_id))
        database.commit()


def calculate_exp(user_id: str, database: Connection) -> int:
    """
    얼마나 게임을 많이 플레이했는지에 대한 수치.
    모든 플레이한 게임들에 대해 그 게임에 플레이한 사람들의 수를 곱해서 더해 출력한다.

    디버그 전용 함수이므로 웬만하면 사용하지 않을 것
    """
    with database.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM participant JOIN game g ON g.id = game_id '
                       'WHERE g.state = 2 '
                       'AND game_id IN ('
                       '    SELECT game_id FROM participant '
                       '    WHERE user_id = %s AND game_id >= 33)', user_id)
        return cursor.fetchone()[0]


def calculate_wins(user_id: str, database: Connection) -> int:
    """
    이긴 게임의 정도에 대한 수치
    모든 이긴 게임들에 대해 그 게임에 플레이한 사람들의 수를 곱해서 더해 출력한다.

    디버그 전용 함수이므로 웬만하면 사용하지 않을 것
    """
    with database.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM participant JOIN game g ON g.id = game_id '
                       'WHERE g.state = 2 '
                       'AND game_id IN ('
                       '    SELECT game_id FROM participant '
                       '    WHERE user_id = %s AND game_id >= 33 AND place = 0)',
                       user_id)
        return cursor.fetchone()[0]
