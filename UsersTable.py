from pydantic import EmailStr
from typing import Optional
from uuid import UUID
from User import UserCreate, UserUpdate, UserResponse


class UsersTable:
    def __init__(self, connection):
        self.connection = connection

    def add_user(self, user: UserCreate) -> UUID:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email, password, phone_number, qr_code)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING user_id
                """,
                (user.name, user.email, user.password, user.phone_number, user.qr_code))
            user_id = cursor.fetchone()[0]
            self.connection.commit()
            return user_id

    def get_user(self, user_id: UUID) -> Optional[UserResponse]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE user_id = %s",
                (user_id,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return UserResponse(zip(columns, result))
            return None

    def find_by_email(self, email: EmailStr) -> Optional[UserResponse]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,))
            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                return UserResponse(zip(columns, result))
            return None

    def get_user_password_by_email(self, email: EmailStr) -> Optional[str]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT password FROM users WHERE email = %s",
                (email,))
            result = cursor.fetchone()
            return result[0] if result else None

    def update_user(self, user: UserUpdate) -> bool:
        fields = user.dict()
        updates = []
        params = []

        for field, value in fields.items():
            if field != "user_id" and value is not None:
                updates.append(f"{field} = %s")
                params.append(value)

        if not updates:
            return False

        params.append(user.user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount > 0

    def delete_user(self, user_id: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM users WHERE user_id = %s",
                (user_id,))
            self.connection.commit()
            return cursor.rowcount > 0
