from enum import Enum, auto

class SpaceType(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
    
    PLAYING = auto() # 합주실
    PARTY = auto() # 파티룸
    DANCE = auto() # 댄스연습실
    KARAOKE = auto() # 노래방
    STUDIO = auto() # 스튜디오
    CAMPING = auto() # 캠핑
    GYM = auto() # 헬스장
    OFFICE = auto() # 사무실
    ACCOMMODATION = auto() # 숙박시설
    KITCHEN = auto() # 공용주방
    STUDYROOM = auto() # 스터디룸