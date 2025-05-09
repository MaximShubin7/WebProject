from contextlib import contextmanager
from pydantic import EmailStr
from typing import Optional
from uuid import UUID
from sqlalchemy import Table, MetaData, select, insert, update, delete

from Classes.User import UserCreate, UserUpdate, UserResponse
from DataBase.ConnectDataBase import get_sqlalchemy_engine


class UsersTable:
    def __init__(self):
        self.engine = get_sqlalchemy_engine()
        self.metadata = MetaData()
        self.users = Table(
            'users',
            self.metadata,
            autoload_with=self.engine
        )

    @contextmanager
    def get_connection(self):
        conn = self.engine.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_user(self, user: UserCreate) -> UUID:
        stmt = (insert(self.users).
                values(
            name=user.name,
            email=user.email,
            password=user.password,
            phone_number=user.phone_number)
                .returning(self.users.c.user_id))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.scalar_one()

    def get_user(self, user_id: UUID) -> Optional[UserResponse]:
        stmt = (select(self.users)
                .where(self.users.c.user_id == user_id))

        with self.get_connection() as conn:
            result = conn.execute(stmt).fetchone()
            return UserResponse(**result._asdict()) if result else None

    def find_by_email(self, email: EmailStr) -> Optional[UserResponse]:
        stmt = (select(self.users)
                .where(self.users.c.email == email))

        with self.get_connection() as conn:
            result = conn.execute(stmt).fetchone()
            return UserResponse(**result._asdict()) if result else None

    def get_user_password_by_email(self, email: EmailStr) -> Optional[str]:
        stmt = (select(self.users.c.password)
                .where(self.users.c.email == email))

        with self.get_connection() as conn:
            result = conn.execute(stmt).scalar_one_or_none()
            return result

    def update_user(self, user: UserUpdate) -> bool:
        update_data = {
            k: v for k, v in user.dict().items()
            if k != "user_id" and v is not None
        }

        if not update_data:
            return False

        stmt = (update(self.users)
                .where(self.users.c.user_id == user.user_id)
                .values(**update_data))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0

    def delete_user(self, user_id: UUID) -> bool:
        stmt = (delete(self.users)
                .where(self.users.c.user_id == user_id))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0

    def change_bonus(self, user_id: UUID, bonus: float) -> bool:
        stmt = (update(self.users)
                .where(self.users.c.user_id == user_id)
                .values(bonus=self.users.c.bonus + bonus))

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0
