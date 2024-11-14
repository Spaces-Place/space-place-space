from enum import Enum, auto

class UsageType(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
    
    time = auto() # 시
    day = auto() # 일