import json
from typing import Annotated, List, Set
from fastapi import Form, UploadFile
from pydantic import Field, BaseModel
from enums.space_type import SpaceType
from enums.usage_type import UsageType
from models.space import Space
from schemas.common import BaseResponse
from schemas.location import Location
from datetime import datetime

from schemas.operating_hour import OperatingHour


class SpaceRequest(BaseModel):
    user_id: str = Field(description="공급자 ID")
    space_type: SpaceType = Field(description="공간 타입(PlAYING | CAMP | ...)")
    name: str = Field(description="공간 이름 (업체명)")
    capacity: int = Field(description="수용 인원")
    space_size: int = Field(description="공간 크기")
    usage_unit: str = Field(description="이용 단위(년, 월, 주, 일, 시)")
    unit_price: int = Field(description="이용 단위별 가격")
    amenities: List[str] = Field(description="편의 시설")
    description: str = Field(description="한줄 소개")
    content: str = Field(description="내용")
    location: Location = Field(description="위치 정보")
    operating_hour: List[OperatingHour] = Field(description="운영 시간")

class SpaceCreate(SpaceRequest):
    images: List[UploadFile] = Field(description="공간 이미지")

class SpaceCreateResponse(BaseResponse):
    id: str = Field(description="공간 고유번호")

class SpaceListResponse(BaseModel):
    id: str = Field(description="공간 고유번호")
    name: str = Field(description="공간 이름 (업체명)")
    description: str = Field(description="한줄 소개")
    usage_unit: UsageType = Field(description="이용 단위(년, 월, 주, 일, 시)")
    unit_price: int = Field(description="이용 단위별 가격")
    location: Location
    operating_hour: List[OperatingHour] = Field(description="운영 시간")
    created_at: datetime = Field(description="공간 생성일")

class SpaceUpdateRequest(BaseModel):
    user_id: str = Field(description="공급자 ID")
    space_type: SpaceType = Field(description="공간 타입(rehearsal | camp | ...)")
    name: str = Field(description="공간 이름 (업체명)")
    capacity: int = Field(description="수용 인원")
    space_size: int = Field(description="공간 크기")
    usage_unit: UsageType = Field(description="이용 단위(년, 월, 주, 일, 시)")
    unit_price: int = Field(description="이용 단위별 가격")
    location: Location
    amenities: Set[str] = Field(description="편의 시설")
    description: str = Field(description="한줄 소개")
    content: str = Field(description="내용")
    operating_hour: List[OperatingHour] = Field(description="운영 시간")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="공간 등록일")
    is_operate: bool = Field(default=True, description="운영 여부")
    images: List[UploadFile] = Field(description="공간 이미지")

class SpaceUpdate(SpaceUpdateRequest):
    space_id: str = Field(description="공간 고유번호")
    images: List[UploadFile] = Field(description="공간 이미지")


class SpaceResponse(SpaceRequest):
    id: str = Field(description="공간 고유번호")
    created_at: datetime = Field(description="공간 생성일")


async def get_space_form(
    user_id: Annotated[str, Form(description="공급자 ID")],
    space_type: Annotated[str, Form(description="공간 타입(PLAYING | ...)")],
    name: Annotated[str, Form(description="공간 이름 (업체명)")],
    capacity: Annotated[int, Form(description="수용 인원")],
    space_size: Annotated[int, Form(description="공간 크기")],
    usage_unit: Annotated[str, Form(description="이용 단위(년, 월, 주, 일, 시)")],
    unit_price: Annotated[int, Form(description="이용 단위별 가격")],
    location: Annotated[str, Form(description="위치 정보 (JSON)")],
    amenities: Annotated[List[str], Form(description="편의 시설")],
    description: Annotated[str, Form(description="한줄 소개")],
    content: Annotated[str, Form(description="내용")],
    operating_hour: Annotated[str, Form(description="운영 시간")]
) -> SpaceRequest:
    
    return SpaceRequest(
        user_id=user_id,
        space_type=space_type,
        name=name,
        capacity=capacity,
        space_size=space_size,
        usage_unit=usage_unit,
        unit_price=unit_price,
        location=json.loads(location),
        amenities=set(amenities), 
        description=description,
        content=content,
        operating_hour=json.loads(operating_hour)
    )