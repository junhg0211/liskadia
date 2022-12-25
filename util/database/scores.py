from pymysql import Connection
from pymysql.cursors import DictCursor

from lyskad import Score


def new(game_id: int, position: int, user_id: str, by_nema_position: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('INSERT INTO score VALUES (%s, %s, %s, %s)', (game_id, position, user_id, by_nema_position))
        database.commit()


def get_scores(game_id: int, database: Connection) -> dict[str, int]:
    result = dict()
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT score.user_id FROM score '
                       'JOIN nema n ON score.game_id = n.game_id AND score.position = n.position '
                       'WHERE n.game_id = %s '
                       'ORDER BY created_at', game_id)
        for score in cursor.fetchall():
            user_id = score.get('user_id')
            if user_id in result:
                result[user_id] += 1
            else:
                result[user_id] = 1
    return result


def get_scoring_nemas(game_id: int, database: Connection) -> list[Score]:
    result = list()
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM score '
                       'JOIN nema n ON score.game_id = n.game_id AND score.position = n.position '
                       'WHERE n.game_id = %s', game_id)
        for score in cursor.fetchall():
            result.append(Score.get(score))
    return result
