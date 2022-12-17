from pymysql import Connection


def new(user_id: str, game_id: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute("INSERT INTO participant VALUES (%s, %s)", (user_id, game_id))
        database.commit()


def get_ids(game_id: int, database: Connection) -> list[str]:
    ids = list()
    with database.cursor() as cursor:
        cursor.execute('SELECT user_id FROM participant WHERE game_id = %s', game_id)
        while line := cursor.fetchone():
            ids.append(line[0])
    return ids


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


def is_in(user_id: str, game_id: int, database: Connection):
    with database.cursor() as cursor:
        cursor.execute('SELECT game_id FROM participant WHERE user_id = %s AND game_id = %s', (user_id, game_id))
        return bool(cursor.fetchone())
