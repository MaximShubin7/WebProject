import psycopg2


def get_db_connection():
    return psycopg2.connect(
        dbname="DataBase",
        user="postgres",
        password="qwerty123",
        host="localhost",
        port=3000
    )
