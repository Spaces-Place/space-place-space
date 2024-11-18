from enum import Enum, auto

class UsageType(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
    
    TIME = auto() # 시
    DAY = auto() # 일