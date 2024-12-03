from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import Field
from enums.space_type import SpaceType
from schemas.common import BaseResponse
from schemas.payment import PaymentRequest
from schemas.space_request import SpaceRequest, SpaceUpdateRequest, get_space_form, get_space_update_form
from schemas.space_response import SpaceCreateResponse, SpaceListResponse, SpaceResponse
from services.space_service import SpaceService, get_space_service
from utils.authenticate import userAuthenticate


space_router = APIRouter(
    tags=["공간"]
)


# 위치 기준 데이터
@space_router.get("/nearby", response_model=List[SpaceListResponse], status_code=status.HTTP_200_OK, summary="위치 기반 공간 목록 조회")
async def get_nearby_spaces(
    longitude: float = Query(description="경도"),
    latitude: float = Query(description="위도"),
    radius: float = Query(1.0, description="반경"),
    space_service: SpaceService = Depends(get_space_service)
):
    nearby_spaces = await space_service.get_nearby_spaces(longitude, latitude, radius)
    return nearby_spaces


# 공간 등록
@space_router.post("", response_model=SpaceCreateResponse, status_code=status.HTTP_201_CREATED, summary="공간 등록")
async def create_space(
    space_data: SpaceRequest = Depends(get_space_form),
    token_info: Dict = Depends(userAuthenticate),
    space_service: SpaceService = Depends(get_space_service)
):
    """ Authorization: Bearer {token} """

    if token_info["user_id"] != space_data.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인을 다시 해주세요")
    
    if len(space_data.images) <= 0:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"이미지를 등록해주세요")
    
    space_id = await space_service.create_space(space_data)

    return SpaceCreateResponse(
        message="공간이 등록되었습니다.", 
        space_id= str(space_id)
    )


# 공간 목록 조회
@space_router.get("", response_model=List[SpaceListResponse], status_code=status.HTTP_200_OK, summary="공간 목록 조회")
async def get_spaces(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    space_type: Optional[SpaceType] = None,
    sido: Optional[str] = None,
    space_service: SpaceService = Depends(get_space_service)
):
    spaces = await space_service.get_spaces(skip, limit, space_type, sido)
    return [SpaceListResponse(**space) for space in spaces]


# 특정 공간 조회
@space_router.get("/{space_id}", response_model=SpaceResponse, status_code=status.HTTP_200_OK, summary="특정 공간 조회")
async def get_space(
    space_id: str, 
    space_service: SpaceService = Depends(get_space_service)
):
    space = await space_service.get_space(space_id)

    return SpaceResponse(
        message="공간이 조회되었습니다.", 
        **space
    )


# 공간 수정 
@space_router.put("/{space_id}", response_model=BaseResponse, status_code=status.HTTP_200_OK, summary="공간 수정")
async def update_spaces(
    space_id: str = Path(description="공간 고유번호"), 
    space_update_data: SpaceUpdateRequest = Depends(get_space_update_form), 
    token_info=Depends(userAuthenticate),
    space_service: SpaceService = Depends(get_space_service)
):
    """ Authorization: Bearer {token} """

    if len(space_update_data.images) <= 0:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="이미지를 등록해주세요")

    await space_service.update_spaces(token_info["user_id"], space_id, space_update_data)
    return BaseResponse(message = "공간이 정상적으로 수정되었습니다.")

# 공간 삭제
@space_router.delete("/{space_id}", response_model=BaseResponse, status_code=status.HTTP_200_OK, summary="공간 삭제")
async def delete_space(
    space_id: str, 
    token_info=Depends(userAuthenticate),
    space_service: SpaceService = Depends(get_space_service)
):
    await space_service.delete_space(space_id, token_info["user_id"])
    return BaseResponse(message="공간이 삭제되었습니다.")

# 예약 전 공간 이름과 총액을 받아오는 end-point
@space_router.post("/pre-order", response_model=Dict, status_code=status.HTTP_200_OK, summary="")
async def pre_order_data(
    payment_request: PaymentRequest,
    token_info=Depends(userAuthenticate),
    space_service: SpaceService = Depends(get_space_service)
):
    """구현이 필요하지 않습니다."""
    result_data = await space_service.get_space(payment_request.space_id)

    if result_data['usage_unit'] == "TIME":
        total_hours = calculate_time_difference(payment_request.start_time, payment_request.end_time)
        total_amount = result_data.get("unit_price") * total_hours
    else:
        total_hours = 1
        total_amount = result_data.get("unit_price")

    space_data = {
        "space_name": result_data.get("space_name"),
        "total_amount": total_amount,
        "quantity": total_hours
    }
    return space_data

def calculate_time_difference(start_time: str, end_time: str) -> dict:
    # 시간 차이 계산
    date_format = "%Y-%m-%d %H:%M:%S"
    start_time = datetime.strptime(start_time, date_format)
    end_time = datetime.strptime(end_time, date_format)
    time_difference = end_time - start_time
    return time_difference.total_seconds() / 3600
