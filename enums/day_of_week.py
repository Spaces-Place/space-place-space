from enum import Enum, auto

class DayOfWeek(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
    
    monday = auto() # 월
    tuesday = auto() # 화
    wednesday = auto() # 수
    thursday = auto() # 목
    friday = auto() # 금
    saturday = auto() # 토
    sunday = auto() # 일
