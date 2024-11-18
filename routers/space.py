from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from database import get_database
from enums.space_type import SpaceType
from schemas.common import BaseResponse
from schemas.location import Coordinate, Location
from schemas.operating_hour import OperatingHour
from schemas.space import SpaceCreate, SpaceRequest, SpaceCreateResponse, SpaceListResponse, SpaceResponse, SpaceUpdate, get_space_form
from services import space_service
from utils.authenticate import userAuthenticate
from utils.s3_config import s3_bucket


space_router = APIRouter(
    tags=["공간"]
)

# 공간 등록
@space_router.post("/", response_model=SpaceCreateResponse, status_code=status.HTTP_201_CREATED, summary="공간 등록")
async def create_space(
    space_data: SpaceRequest = Depends(get_space_form),
    images: List[UploadFile] = File(...), 
    token_info=Depends(userAuthenticate),
    db = Depends(get_database), 
    s3 = Depends(s3_bucket)
):
    """ Authorization: Bearer {token} """

    # TODO: 토큰 안 받는 형식 고려 (formData에 추가하는 방식)
    if token_info["user_id"] != space_data.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인을 다시 해주세요")
    
    space = SpaceCreate(
        **space_data.model_dump(),
        images=images
    )

    space_id = await space_service.create_space(space, db, s3)
    
    return SpaceCreateResponse(
        message="공간이 등록되었습니다.", 
        space_id= space_id
    )


# 공간 목록 조회
@space_router.get("/", response_model=List[SpaceListResponse], status_code=status.HTTP_200_OK, summary="공간 목록 조회")
async def get_spaces(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    space_type: Optional[SpaceType] = None,
    sido: Optional[str] = None
):
    spaces = await space_service.get_spaces(skip, limit, space_type, sido)
    return spaces


# 특정 공간 조회
@space_router.get("/{space_id}", response_model=SpaceResponse, status_code=status.HTTP_200_OK, summary="특정 공간 조회")
async def get_space(space_id: str, db = Depends(get_database)):
    space = await db.spaces.find_one({"_id": space_id, "is_operate": True})
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="공간을 찾을 수 없습니다.")
    return space


# 공간 수정 
@space_router.put("/{space_id}", response_model=BaseResponse, status_code=status.HTTP_200_OK, summary="공간 수정")
async def update_spaces(space_id: str, space_data: SpaceUpdate, images: List[UploadFile], token_info=Depends(userAuthenticate)):
    """ Authorization: Bearer {token} """

    space = SpaceUpdate(
        **space_data.model_dump(),
        user_id = token_info["user_id"],
        space_id = space_id,
        images = images
    )

    await space_service.update_spaces(token_info["user_id"], space)
    return BaseResponse(message = "공간이 정상적으로 수정되었습니다.")

# 공간 삭제
@space_router.delete("/{space_id}", response_model=BaseResponse, status_code=status.HTTP_200_OK, summary="공간 삭제")
async def delete_space(space_id: str, token_info=Depends(userAuthenticate)):
    await space_service.delete_space(space_id, token_info["user_id"])
    return BaseResponse(message="공간이 삭제되었습니다.")
