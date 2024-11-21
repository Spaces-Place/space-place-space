from typing import List
from pydantic import BaseModel, Field

class Location(BaseModel):
    sido: str = Field(description="시, 도 (서울특별시)")
    address: str = Field(description="상세 주소")
    type: str = Field(default="Point", description="GeoJSON 타입")  # GeoJSON 타입
    coordinates: List[float] = Field(description="경도, 위도 순서")
