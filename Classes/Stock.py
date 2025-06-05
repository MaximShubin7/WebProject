from fastapi import FastAPI
from pydantic import BaseModel
from uuid import UUID

app = FastAPI()


class StockCreate(BaseModel):
    name: str
    time: str
    week_day: str
    text: str


class StockResponse(StockCreate):
    stock_id: UUID
