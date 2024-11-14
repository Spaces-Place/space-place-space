from pydantic import BaseModel

class Coordinate(BaseModel):
    latitude: str
    longitude: str

class Location(BaseModel):
    sido: str
    address: str
    type: str
    coordinates: Coordinate
