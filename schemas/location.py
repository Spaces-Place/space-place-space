from typing import Dict
from pydantic import BaseModel, Field
from typing import Dict

class Coordinate(BaseModel):
    latitude: str = Field(description="위도")
    longitude: str = Field(description="경도")

class Location(BaseModel):
    sido: str = Field(description="시, 도 (서울특별시)")
    address: str = Field(description="상세 주소")
    type: str = Field(default="Point", description="GeoJSON 타입")  # GeoJSON 타입
    coordinates: Coordinate = Field(description="좌표") # GeoJSON
