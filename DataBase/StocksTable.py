from uuid import UUID
from contextlib import contextmanager
from sqlalchemy import Table, MetaData, insert, select, delete
from typing import List, Optional

from Classes.Stock import StockCreate, StockResponse
from DataBase.ConnectDataBase import get_sqlalchemy_engine


class StocksTable:
    def __init__(self):
        self.engine = get_sqlalchemy_engine()
        self.metadata = MetaData()
        self.stocks = Table(
            'stocks',
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

    def add_stock(self, stock: StockCreate) -> UUID:
        stmt = insert(self.stocks).values(
            name=stock.name,
            time=stock.time,
            week_day=stock.week_day,
            text=stock.text
        ).returning(self.stocks.c.stock_id)

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            stock_id = result.scalar_one()
            return stock_id

    def get_stock(self, stock_id: UUID) -> Optional[dict]:
        stmt = select(
            self.stocks.c.stock_id,
            self.stocks.c.name,
            self.stocks.c.time,
            self.stocks.c.week_day,
            self.stocks.c.text
        ).where(self.stocks.c.stock_id == stock_id)

        with self.get_connection() as conn:
            result = conn.execute(stmt).fetchone()
            if result:
                return StockResponse(
                    stock_id=result.stock_id,
                    name=result.name,
                    time=result.time,
                    week_day=result.week_day,
                    text=result.text
                )
            return None

    def get_all_stocks(self) -> List[dict]:
        stmt = select(
            self.stocks.c.stock_id,
            self.stocks.c.name,
            self.stocks.c.time,
            self.stocks.c.week_day,
            self.stocks.c.text
        )

        with self.get_connection() as conn:
            results = conn.execute(stmt).fetchall()
            return [StockResponse(
                    stock_id=result.stock_id,
                    name=result.name,
                    time=result.time,
                    week_day=result.week_day,
                    text=result.text
                ) for result in results]

    def delete_stock(self, stock_id: UUID) -> bool:
        stmt = delete(self.stocks).where(self.stocks.c.stock_id == stock_id)

        with self.get_connection() as conn:
            result = conn.execute(stmt)
            return result.rowcount > 0