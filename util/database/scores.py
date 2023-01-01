from pymysql import Connection
from pymysql.cursors import DictCursor

from lyskad import Score


def new(game_id: int, position: int, user_id: str, by_nema_position: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('INSERT INTO score VALUES (%s, %s, %s, %s)', (game_id, position, user_id, by_nema_position))
        database.commit()


def get_scores(game_id: int, database: Connection) -> dict[str, int]:
    """
    어떤 플레이어가 몇점을 얻었는지 dict 형태로 만들어 출력한다.
    """
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
    """
    게임 중에 발생한 득점 네마 정보를 리스트에 담아 출력한다.
    """
    result = list()
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM score '
                       'JOIN nema n ON score.game_id = n.game_id AND score.by_nema_position = n.position '
                       'WHERE n.game_id = %s ORDER BY n.created_at', game_id)
        for score in cursor.fetchall():
            result.append(Score.get(score))
    return result
