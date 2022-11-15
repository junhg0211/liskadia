from pymysql import connect

from util import get_secret

database = connect(
    host=get_secret('database.host'),
    user=get_secret('database.user'),
    password=get_secret('database.password'),
    database=get_secret('database.database'),
)
