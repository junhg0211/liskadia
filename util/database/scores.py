from pymysql import Connection


def new(game_id: int, position: int, user_id: str, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('INSERT INTO score VALUES (%s, %s, %s)', (game_id, position, user_id))
        database.commit()
