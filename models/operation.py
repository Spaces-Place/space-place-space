from typing import Dict
from pydantic import BaseModel, Field
from enums.day_of_week import DayOfWeek


class OperatingHour(BaseModel):
    open: str
    close: str

class Operation(OperatingHour):
    day: DayOfWeek