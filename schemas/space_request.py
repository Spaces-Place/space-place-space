import json
from typing import Annotated, List, Set
from fastapi import Form, UploadFile
from pydantic import Field, BaseModel
from enums.space_type import SpaceType
from enums.usage_type import UsageType
from schemas.location import Location
from datetime import datetime

from schemas.operating_hour import OperatingHour


class SpaceRequest(BaseModel):
    user_id: str = Field(description="공급자 ID")
    space_type: SpaceType = Field(description="공간 타입(PlAYING | CAMP | ...)")
    space_name: str = Field(description="공간 이름 (업체명)")
    capacity: int = Field(description="수용 인원")
    space_size: int = Field(description="공간 크기")
    usage_unit: UsageType = Field(description="이용 단위(DAY | TIME)")
    unit_price: int = Field(description="이용 단위별 가격")
    amenities: List[str] = Field(description="편의 시설")
    description: str = Field(description="한줄 소개")
    content: str = Field(description="내용")
    location: Location = Field(description="경도, 위도 순서")
    images: List[UploadFile] = Field(description="공간 이미지")
    operating_hour: List[OperatingHour] = Field(description="운영 시간")
    is_operate: bool = Field(default=True, description="운영 여부")
    created_at: datetime = Field(default_factory=datetime.now, description="생성일")

    class Config:
        json_encoders = {SpaceType: str, UsageType: str}


async def get_space_form(
    user_id: Annotated[str, Form(description="공급자 ID")],
    space_type: Annotated[str, Form(description="공간 타입(PLAYING | ...)")],
    space_name: Annotated[str, Form(description="공간 이름 (업체명)")],
    capacity: Annotated[int, Form(description="수용 인원")],
    space_size: Annotated[int, Form(description="공간 크기")],
    usage_unit: Annotated[str, Form(description="이용 단위(DAY | TIME)")],
    unit_price: Annotated[int, Form(description="이용 단위별 가격")],
    location: Annotated[str, Form(description="경도, 위도 순서 (JSON)")],
    amenities: Annotated[List[str], Form(description="편의 시설")],
    description: Annotated[str, Form(description="한줄 소개")],
    content: Annotated[str, Form(description="내용")],
    operating_hour: Annotated[str, Form(description="운영 시간 (JSON)")],
    images: Annotated[List[UploadFile], Form(description="공간 이미지")],
) -> SpaceRequest:

    return SpaceRequest(
        user_id=user_id,
        space_type=SpaceType(space_type),
        space_name=space_name,
        capacity=capacity,
        space_size=space_size,
        usage_unit=UsageType(usage_unit),
        unit_price=unit_price,
        location=json.loads(location),
        amenities=set(amenities),
        description=description,
        content=content,
        operating_hour=json.loads(operating_hour),
        images=images,
    )


class SpaceUpdateRequest(BaseModel):
    capacity: int = Field(description="수용 인원")
    usage_unit: UsageType = Field(description="이용 단위(DAY | TIME)")
    unit_price: int = Field(description="이용 단위별 가격")
    amenities: List[str] = Field(description="편의 시설")
    description: str = Field(description="한줄 소개")
    content: str = Field(description="내용")
    operating_hour: List[OperatingHour] = Field(description="운영 시간")
    is_operate: bool = Field(default=True, description="운영 여부")
    images: List[UploadFile] = Field(description="공간 이미지")

    class Config:
        json_encoders = {SpaceType: str, UsageType: str}


async def get_space_update_form(
    capacity: Annotated[int, Form(description="수용 인원")],
    usage_unit: Annotated[str, Form(description="이용 단위(DAY | TIME)")],
    unit_price: Annotated[int, Form(description="이용 단위별 가격")],
    amenities: Annotated[List[str], Form(description="편의 시설")],
    description: Annotated[str, Form(description="한줄 소개")],
    content: Annotated[str, Form(description="내용")],
    operating_hour: Annotated[str, Form(description="운영 시간 (JSON)")],
    images: Annotated[List[UploadFile], Form(description="공간 이미지")],
) -> SpaceUpdateRequest:

    return SpaceUpdateRequest(
        capacity=capacity,
        usage_unit=UsageType(usage_unit),
        unit_price=unit_price,
        amenities=amenities,
        description=description,
        content=content,
        operating_hour=json.loads(operating_hour),
        images=images,
    )
