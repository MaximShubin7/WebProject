from datetime import time
from pydantic import BaseModel, validator, Field
from uuid import UUID


class StockValidator:
    @validator("time")
    def validate_time(cls, v: str) -> str:
        if v == "Весь день":
            return v
        if '-' not in v:
            raise ValueError("There must be a separator '-' between the time")
        try:
            start_str, end_str = v.split('-')
            start_time = str(time.fromisoformat(start_str))[:-3]
            end_time = str(time.fromisoformat(end_str))[:-3]
            return f"{str(start_time)}:{str(end_time)}"
        except Exception as e:
            raise ValueError("Incorrect time format")

    @validator("week_day")
    def validate_week_day(cls, v: str) -> str:
        week_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье",
                         "каждый день"]
        if v.lower() in week_days:
            return v.capitalize()
        if '-' not in v:
            raise ValueError("There must be a separator '-' between the week day or incorrect week day")

        start_day, end_day = v.split('-')
        if start_day.lower() not in week_days or end_day.lower() not in week_days:
            raise ValueError("Incorrect week day format")




class StockCreate(BaseModel, StockValidator):
    name: str = Field(..., min_length=3, max_length=30)
    time: str
    week_day: str
    text: str = Field(..., min_length=3, max_length=200)


class StockResponse(StockCreate):
    stock_id: UUID
