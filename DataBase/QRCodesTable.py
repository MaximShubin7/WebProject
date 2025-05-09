from contextlib import contextmanager
from typing import Optional
from sqlalchemy import Table, MetaData, select, insert

from DataBase.ConnectDataBase import get_sqlalchemy_engine


class QRCodesTable:
    def __init__(self):
        self.engine = get_sqlalchemy_engine()
        self.metadata = MetaData()
        self.qr_codes = Table(
            'qr_codes',
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

    def add_qr_code(self, qr_code_data: str) -> None:
        stmt = (insert(self.qr_codes)
                .values(qr_code_data=qr_code_data))

        with self.get_connection() as conn:
            conn.execute(stmt)

    def get_qr_code(self, qr_code_data: str) -> Optional[str]:
        stmt = (select(self.qr_codes.c.qr_code_data)
                .where(self.qr_codes.c.qr_code_data == qr_code_data))

        with self.get_connection() as conn:
            result = conn.execute(stmt).scalar_one_or_none()
            return result
