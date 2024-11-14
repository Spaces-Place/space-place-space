from typing import List, Dict
from bson import ObjectId
from fastapi import UploadFile
from pydantic import Field, BaseModel
from enums.space_type import SpaceType
from enums.day_of_week import DayOfWeek
from enums.usage_type import UsageType
from schemas.common import BaseResponse
from schemas.image import Image
from schemas.operation import Operation
from schemas.location import Location
from datetime import datetime


class SpaceCreate(BaseModel):
    vendor_id: str = Field(description="공급자 ID")
    space_type: SpaceType = Field(description="공간 타입(rehearsal | camp | ...)")
    name: str = Field(description="공간 이름 (업체명)")
    capacity: int = Field(description="수용 인원")
    space_size: int = Field(description="공간 크기")
    usage_unit: UsageType = Field(description="이용 단위(년, 월, 주, 일, 시)")
    unit_price: int = Field(description="이용 단위별 가격")
    location: Location
    images: List[UploadFile] = Field(description="공간 이미지")
    amenities: List[str] = Field(description="편의 시설")
    description: str = Field(description="한줄 소개")
    content: str = Field(description="내용")
    operating_hour: List[Operation] = Field(description="운영 시간")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="공간 등록일")
    is_operate: bool = Field(default=True, description="운영 여부")

class SpaceCreateResponse(BaseResponse):
    id: str = Field(description="공간 고유번호")

class SpaceListResponse(BaseModel):
    id: str = Field(description="공간 고유번호")
    name: str = Field(description="공간 이름 (업체명)")
    description: str = Field(description="한줄 소개")
    usage_unit: UsageType = Field(description="이용 단위(년, 월, 주, 일, 시)")
    unit_price: int = Field(description="이용 단위별 가격")
    location: Location
    operating_hour: List[Operation] = Field(description="운영 시간")
    created_at: datetime = Field(description="공간 생성일")

class SpaceUpdate(SpaceCreate):
    id: str = Field(description="공간 고유번호")

class SpaceResponse(SpaceCreate):
    id: str = Field(description="공간 고유번호")
    created_at: datetime = Field(description="공간 생성일")
    
    # class Config:
    #     json_encoders = {ObjectId: str}
    #     allow_population_by_field_name = True

# class SpaceDB(SpaceCreate):
#     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#     is_deleted: bool = False

#     class Config:
#         json_encoders = {ObjectId: str}
#         allow_population_by_field_name = True

