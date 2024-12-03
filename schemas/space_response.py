from datetime import datetime
from typing import List
from pydantic import Field, BaseModel
from enums.space_type import SpaceType
from enums.usage_type import UsageType
from schemas.common import BaseResponse
from schemas.location import Location

from schemas.operating_hour import OperatingHour
from schemas.space_request import SpaceRequest


class SpaceCreateResponse(BaseResponse):
    space_id: str = Field(description="공간 고유번호")

class SpaceListResponse(BaseModel):
    space_id: str = Field(description="공간 고유번호")
    space_name: str = Field(description="공간 이름 (업체명)")
    description: str = Field(description="한줄 소개")
    usage_unit: UsageType = Field(description="이용 단위(년, 월, 주, 일, 시)")
    unit_price: int = Field(description="이용 단위별 가격")
    amenities: List[str] = Field(description="편의 시설")
    location: Location
    thumbnail: str = Field(description="썸네일 이미지")

class SpaceResponse(BaseResponse):
    space_id: str = Field(description="공간 고유번호")
    user_id: str = Field(description="공급자 ID")
    space_type: SpaceType = Field(description="공간 타입(PlAYING | CAMP | ...)")
    space_name: str = Field(description="공간 이름 (업체명)")
    capacity: int = Field(description="수용 인원")
    space_size: int = Field(description="공간 크기")
    usage_unit: UsageType = Field(description="이용 단위(년, 월, 주, 일, 시)")
    unit_price: int = Field(description="이용 단위별 가격")
    amenities: List[str] = Field(description="편의 시설")
    description: str = Field(description="한줄 소개")
    content: str = Field(description="내용")
    location: Location = Field(description="위치 정보")
    operating_hour: List[OperatingHour] = Field(description="운영 시간")
    is_operate: bool = Field(default=True, description="운영 여부")
    created_at: datetime = Field(default_factory=datetime.now, description="생성일")
