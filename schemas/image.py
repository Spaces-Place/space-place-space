from pydantic import BaseModel, Field

class Image(BaseModel):
    url: str = Field(description="이미지 URL")
    order: int = Field(description="이미지 순서")