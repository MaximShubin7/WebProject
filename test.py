import psycopg2.extras
from ConnectToDB import get_db_connection, get_users_repository
from User import UserCreate, UserUpdate

psycopg2.extras.register_uuid()
conn = get_db_connection()
cursor = conn.cursor()
repository = get_users_repository()

user = UserCreate(email='example@gmail.com', password='ADGJLadgjl13579')
user_id = repository.add_user(user)

cursor.execute("SELECT * FROM Users")
rows = cursor.fetchall()
print(rows)

user = UserUpdate(user_id=user_id, name='Maxim', phone_number='89507776655')
repository.update_user(user)

cursor.execute("SELECT * FROM Users")
rows = cursor.fetchall()
print(rows)

repository.delete_user(user_id)

cursor.execute("SELECT * FROM Users")
rows = cursor.fetchall()
print(rows)
