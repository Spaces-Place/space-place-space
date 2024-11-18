from enum import Enum, auto

class DayOfWeek(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
    
    MONDAY = auto() # 월
    TUESDAY = auto() # 화
    WEDNESDAY = auto() # 수
    THURSDAY = auto() # 목
    FRIDAY = auto() # 금
    SATURDAY = auto() # 토
    SUNDAY = auto() # 일
