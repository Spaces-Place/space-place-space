from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile
from database import get_database
from enums.space_type import SpaceType
from schemas.common import BaseResponse
from schemas.space import SpaceCreate, SpaceCreateResponse, SpaceListResponse, SpaceResponse, SpaceUpdate
from services import space_service
from utils.authenticate import userAuthenticate
from utils.s3_config import s3_bucket


space_router = APIRouter(
    tags=["공간"]
)

# 공간 등록
@space_router.post("/", response_model=SpaceCreateResponse, status_code=status.HTTP_201_CREATED, summary="공간 등록")
async def create_space(space: SpaceCreate, token_info=Depends(userAuthenticate)):
    """ Authorization: Bearer {token} """
    
    space.vendor_id = token_info["user_id"]
    space_id = await space_service.create_space(space)
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
async def update_spaces(space_id: str, space: SpaceUpdate, token_info=Depends(userAuthenticate)):
    """ Authorization: Bearer {token} """

    await space_service.update_spaces(token_info["id"], space_id, space)
    return BaseResponse(message = "공간이 정상적으로 수정되었습니다.")

# 공간 삭제
@space_router.delete("/{space_id}", response_model=BaseResponse, status_code=status.HTTP_204_NO_CONTENT, summary="공간 삭제")
async def delete_space(space_id: str, token_info=Depends(userAuthenticate)):
    await space_service.delete_space(space_id, token_info["user_id"])
    return BaseResponse(message="공간이 삭제되었습니다.")