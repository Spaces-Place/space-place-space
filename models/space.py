from datetime import datetime
from typing import List
from pydantic import BaseModel

from enums.space_type import SpaceType
from enums.usage_type import UsageType
from models.image import Image
from models.location import Location
from models.operation import Operation


class Space(BaseModel):
    vendor_id: str
    space_type: SpaceType
    name: str
    capacity: int
    space_size: int
    usage_unit: UsageType
    unit_price: int
    location: Location
    images: List[Image]
    amenities: List[str]
    description: str
    content: str
    operating_hour: List[Operation]
    created_at: datetime
    is_operate: bool
