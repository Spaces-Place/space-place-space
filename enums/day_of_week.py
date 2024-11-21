from enum import Enum

class DayOfWeek(str, Enum):
    
    MONDAY = "MONDAY" # 월
    TUESDAY = "TUESDAY" # 화
    WEDNESDAY = "WEDNESDAY" # 수
    THURSDAY = "THURSDAY" # 목
    FRIDAY = "FRIDAY" # 금
    SATURDAY = "SATURDAY" # 토
    SUNDAY = "SUNDAY" # 일