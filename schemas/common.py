from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    message: str = Field(description="응답 내용")
