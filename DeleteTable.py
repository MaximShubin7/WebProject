from ConnectToDB import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM Users")
conn.commit()
