from datetime import datetime
from typing import Iterable, Optional

from pymysql import Connection
from pymysql.cursors import DictCursor

from lyskad import RatingHistory


def get(user_id: str, database: Connection) -> Iterable[RatingHistory]:
    with database.cursor(DictCursor) as cursor:
        cursor.execute('SELECT * FROM rating_history WHERE user_id = %s', user_id)
        for row in cursor.fetchall():
            yield RatingHistory.get(row)


def apply(user_id: str, rating: float, database: Connection, time: Optional[datetime] = None):
    if time is None:
        time = datetime.now()
    with database.cursor(DictCursor) as cursor:
        cursor.execute('INSERT INTO rating_history VALUES (%s, %s, %s)', (user_id, rating, time))
        database.commit()
