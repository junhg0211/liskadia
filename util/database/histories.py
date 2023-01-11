from typing import Iterable

from pymysql import Connection
from pymysql.cursors import DictCursor

from lyskad import RatingHistory


def get(user_id: str, database: Connection) -> Iterable[RatingHistory]:
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM rating_history WHERE user_id = %s', user_id)
        for row in cursor.fetchall():
            yield RatingHistory.get(row)
