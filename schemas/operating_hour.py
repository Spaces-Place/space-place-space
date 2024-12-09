from typing import Dict
from pydantic import BaseModel, Field
from enums.day_of_week import DayOfWeek


class OperatingHour(BaseModel):
    day: DayOfWeek = Field(description="운영 요일")
    open: str = Field(description="운영 시작 시간")
    close: str = Field(description="운영 종료 시간")
