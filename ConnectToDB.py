import psycopg2
from UsersTable import UsersTable


def get_db_connection():
    return psycopg2.connect(
        dbname="DataBase",
        user="postgres",
        password="MaXiMuS2505",
        host="127.0.0.1",
        port=5000
    )


def get_users_repository():
    conn = get_db_connection()
    return UsersTable(conn)
