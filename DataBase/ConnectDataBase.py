import os
from sqlalchemy import create_engine


def get_sqlalchemy_engine():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL не задан в переменных окружения")

    return create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        connect_args={
            "sslmode": "require"
        }
    )
