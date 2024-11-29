from pydantic import BaseModel, Field


class PaymentRequest(BaseModel):
    space_id: str = Field(description="공간 고유번호")
    use_date: str = Field(default='', description="이용일(YYYY-MM-DD)")
    start_time: str = Field(default='', description="이용 시작 시간")
    end_time: str = Field(default='', description="이용 종료 시간")