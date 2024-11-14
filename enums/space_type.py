from enum import Enum, auto

class SpaceType(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
    
    playing = auto() # 합주실
    party = auto() # 파티룸
    dance = auto() # 댄스연습실
    karaoke = auto() # 노래방
    studio = auto() # 스튜디오
    camping = auto() # 캠핑
    gym = auto() # 헬스장
    office = auto() # 사무실
    accommodation = auto() # 숙박시설
    kitchen = auto() # 공용주방
    studyroom = auto() # 스터디룸