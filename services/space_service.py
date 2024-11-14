
import os
from typing import Optional
from bson import ObjectId
from fastapi import Depends, HTTPException, Query, status

from database import get_database
from enums.space_type import SpaceType
from schemas.space import SpaceCreate, SpaceListResponse, SpaceUpdate
from utils.s3_config import s3_bucket

# 이미지 확장자 목록
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}

# 확장자 확인
def allowed_file(filename: str) -> bool:
    return '.' in filename and os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

# 공간 등록
async def create_space(space: SpaceCreate, db = Depends(get_database), s3 = Depends(s3_bucket)):

    # 1차적인 공간 저장
    space_dict = space.model_dump(exclude={"images"})
    space_id = db.spaces.insert_one(space_dict).inserted_id

    s3_client = s3["s3_client"]
    bucket_name = s3["bucket"]

    try:
        # s3 이미지 업로드
        image_urls = []
        for idx, image in enumerate(space.images):
            if not allowed_file(image.filename):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{image.filename}은 지원하지 않는 이미지 형식입니다.")
            
            file_extension = os.path.splitext(image.filename)[1]
            path = f"{space.vendor_id}/{space_id}/{idx}{file_extension}" # 예: user_id/space_id/0.png

            s3_client.upload_fileobj(image.file, bucket_name, path)
            image_urls.append({
                "filename": f"{idx}{file_extension}",
                "original_filename": image.filename
            })

        # 이후에 클라이언트에게 이렇게 내려주기 f"https://{bucket_name}.s3.amazonaws.com/{s3_path}"

        # 이미지 데이터 업데이트
        space_dict["images"] = image_urls
        space = await db.spaces.update_one({"_id": space_id}, {"$set": {"images": image_urls}})

    except Exception as e:
        await db.spaces.delete_one({"_id": space_id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="이미지 업로드 중 오류가 발생했습니다.")
    
    return space_id


# 공간 목록 조회
async def get_spaces(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    space_type: Optional[SpaceType] = None,
    sido: Optional[str] = None,
    db = Depends(get_database)
) -> SpaceListResponse:
    query = {"is_operate" : True}

    if space_type:
        query["space_type"] = space_type

    if sido:
        query["location.sido"] = sido

    result = db.spaces.find(query).skip(skip).limit(limit)
    spaces = await result.to_list(length=limit)

    return spaces


# 특정 공간 조회
async def get_space(space_id: str, db = Depends(get_database)):
    space = await db.spaces.find_one({"_id": space_id, "is_operate": True})
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="공간을 찾을 수 없습니다.")
    return space


# 공간 수정
async def update_spaces(user_id: str, space_id: str, space: SpaceUpdate, db = Depends(get_database), s3 = Depends(s3_bucket)):
    existing_space = await db.spaces.find_one({"_id": ObjectId(space_id)})
    if not existing_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="공간을 찾을 수 없습니다.")
    
    if user_id != existing_space["vendor_id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="본인 공간만 수정할 수 있습니다.")
    
    # 기존 이미지 삭제
    existing_image_paths = [f"{user_id}/{space_id}/{img['filename']}" for img in existing_space['images']]
    s3_client = s3["s3_client"]
    bucket_name = s3["bucket"]

    for image_path in existing_image_paths:
        s3_client.delete_object(Bucket=bucket_name, Key=image_path)

    try:
        # 받아온 이미지 업로드
        image_urls = []
        if not space.images:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미지를 등록해야 합니다.")
        
        # 1차적으로 지원하는 이미지 형식인지 확인하고 업로드
        for image in enumerate(space.images):
            if not allowed_file(image.filename):
                raise HTTPException(status_code=400, detail=f"{image.filename}은 지원하지 않는 이미지 형식입니다.")
            
        for idx, image in enumerate(space.images):
            file_extension = os.path.splitext(image.filename)[1]
            path = f"{user_id}/{space_id}/{idx}{file_extension}" # 예: user_id/space_id/0.png

            s3_client.upload_fileobj(image.file, bucket_name, path)
            image_urls.append({
                "filename": f"{idx}{file_extension}",
                "original_filename": image.filename
            })


        update_data = space.model_dump(exclude_unset=True)  
        if image_urls:
            update_data['images'] = image_urls
        await db.spaces.update_one({"_id": ObjectId(space_id)}, {"$set": update_data})

    except Exception as e:
        await db.spaces.delete_one({"_id": space_id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="이미지 업로드 중 오류가 발생했습니다.")
    

# 공간 삭제
async def delete_space(space_id: str, vendor_id: str, db = Depends(get_database), s3 = Depends(s3_bucket)):
    existing_space = await db.spaces.find_one({"_id": ObjectId(space_id)})

    if not existing_space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="공간을 찾을 수 없습니다.")
    
    if existing_space['vendor_id'] != vendor_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="본인 공간만 삭제할 수 있습니다.")
    
    # 이미지 삭제
    existing_image_paths = [f"{vendor_id}/{space_id}/{img['filename']}" for img in existing_space['images']]
    s3_client = s3["s3_client"]
    bucket_name = s3["bucket"]

    for image_path in existing_image_paths:
        s3_client.delete_object(Bucket=bucket_name, Key=image_path)
        
    await db.spaces.delete_one({"_id": ObjectId(space_id)})