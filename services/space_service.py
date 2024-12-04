import logging
import os
from typing import Dict, List, Optional
from bson import ObjectId
from fastapi import Depends, HTTPException, Query, status

from enums.space_type import SpaceType
from schemas.space_request import SpaceRequest, SpaceUpdateRequest
from schemas.space_response import SpaceResponse
from services.aws_service import AWSService, get_aws_service
from motor.motor_asyncio import AsyncIOMotorDatabase

from utils.mongodb import get_mongodb


async def get_space_service(
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    aws_service: AWSService = Depends(get_aws_service),
):
    return SpaceService(db, aws_service)


class SpaceService:

    # 이미지 확장자 목록
    _ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}
    _logger = logging.getLogger()

    def __init__(self, db: AsyncIOMotorDatabase, aws_service: AWSService):
        self.db = db
        aws_service = get_aws_service()
        self.s3 = aws_service.get_s3_config()

    def _allowed_file(self, filename: str) -> bool:
        return (
            "." in filename
            and os.path.splitext(filename)[1].lower() in self._ALLOWED_EXTENSIONS
        )

    # 공간 등록
    async def create_space(self, space: SpaceRequest):
        # 1차적인 공간 저장
        space_dict = space.model_dump(exclude={"images"})
        space_dict["is_operate"] = True

        result = await self.db.spaces.insert_one(space_dict)
        space_id = result.inserted_id

        s3_client = self.s3["s3_client"]
        bucket_name = self.s3["bucket"]

        try:
            # s3 이미지 업로드
            image_urls = []
            for idx, image in enumerate(space.images):
                if not self._allowed_file(image.filename):
                    self._logger.error(
                        f"{image.filename}은 지원하지 않는 이미지 형식입니다."
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{image.filename}은 지원하지 않는 이미지 형식입니다.",
                    )

                file_extension = os.path.splitext(image.filename)[1]
                path = f"{space.user_id}/{space_id}/{idx}{file_extension}"  # 예: user_id/{space_id}/0.png

                s3_client.upload_fileobj(image.file, bucket_name, path)
                image_urls.append(
                    {
                        "filename": f"{idx}{file_extension}",
                        "original_filename": image.filename,
                    }
                )

                s3_client.put_object_acl(
                    Bucket=bucket_name, Key=path, ACL="public-read"
                )

            # 이미지 데이터 업데이트
            await self.db.spaces.update_one(
                {"_id": space_id}, {"$set": {"images": image_urls}}
            )
            self._logger.info(f"이미지 업로드 성공")

        except Exception as e:
            await self.db.spaces.delete_one({"_id": space_id})
            self._logger.error(f"이미지 업로드 중 오류가 발생했습니다.{space_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이미지 업로드 중 오류가 발생했습니다.{e}",
            )

        return space_id

    # 공간 목록 조회
    async def get_spaces(
        self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        space_type: Optional[SpaceType] = None,
        sido: Optional[str] = None,
    ) -> List[Dict]:
        query = {"is_operate": True}

        bucket_name = self.s3["bucket"]

        if space_type:
            query["space_type"] = space_type

        if sido:
            query["location.sido"] = sido

        result_cursor = self.db.spaces.find(query).skip(skip).limit(limit)
        spaces = await result_cursor.to_list()

        for space in spaces:
            space["space_id"] = str(space["_id"])
            space["thumbnail"] = (
                f"https://{bucket_name}.s3.{os.getenv('REGION_NAME')}.amazonaws.com/{space['user_id']}/{space['space_id']}/{space['images'][0]['filename']}"
            )
            del space["_id"]

        return spaces

    # 특정 공간 조회
    async def get_space(self, space_id: str) -> SpaceResponse:
        bucket_name = self.s3["bucket"]
        space = await self.db.spaces.find_one(
            {"_id": ObjectId(space_id), "is_operate": True}
        )
        if not space:
            self._logger.error(f"공간을 찾을 수 없습니다.{space_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="공간을 찾을 수 없습니다."
            )

        space["space_id"] = str(space["_id"])
        images = []
        for image in space["images"]:
            images.append(
                f"https://{bucket_name}.s3.{os.getenv('REGION_NAME')}.amazonaws.com/{space['user_id']}/{space['space_id']}/{image['filename']}"
            )
        del space["_id"]
        space["images"] = images

        return space

    # 공간 수정
    async def update_spaces(
        self, user_id: str, space_id: str, space: SpaceUpdateRequest
    ):
        existing_space = await self.db.spaces.find_one({"_id": ObjectId(space_id)})

        if not existing_space:
            self._logger.error(f"공간을 찾을 수 없습니다.{space_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="공간을 찾을 수 없습니다."
            )
        if user_id != existing_space["user_id"]:
            self._logger.error(f"본인 공간만 수정 가능합니다.{user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="본인 공간만 수정 가능합니다.",
            )

        # 기존 이미지 삭제
        existing_image_paths = [
            f"{user_id}/{space_id}/{img['filename']}"
            for img in existing_space["images"]
        ]
        s3_client = self.s3["s3_client"]
        bucket_name = self.s3["bucket"]

        for image_path in existing_image_paths:
            s3_client.delete_object(Bucket=bucket_name, Key=image_path)

        self._logger.error(f"기존 이미지 삭제 완료")

        try:
            # 받아온 이미지 업로드
            image_urls = []
            if not space.images:
                self._logger.error(f"이미지를 등록해야 합니다.{user_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미지를 등록해야 합니다.",
                )

            # 1차적으로 지원하는 이미지 형식인지 확인하고 업로드
            for image in space.images:
                if not self._allowed_file(image.filename):
                    self._logger.error(
                        f"{image.filename}은 지원하지 않는 이미지 형식입니다."
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"{image.filename}은 지원하지 않는 이미지 형식입니다.",
                    )

            for idx, image in enumerate(space.images):
                file_extension = os.path.splitext(image.filename)[1]
                path = f"{user_id}/{space_id}/{idx}{file_extension}"  # 예: user_id/space_id/0.png

                s3_client.upload_fileobj(image.file, bucket_name, path)
                image_urls.append(
                    {
                        "filename": f"{idx}{file_extension}",
                        "original_filename": image.filename,
                    }
                )

            self._logger.info(f"수정된 이미지 업로드 완료")

            update_data = space.model_dump(exclude_unset=True)
            if image_urls:
                update_data["images"] = image_urls
            await self.db.spaces.update_one(
                {"_id": ObjectId(space_id)}, {"$set": update_data}
            )

        except Exception as e:
            await self.db.spaces.delete_one({"_id": space_id})
            self._logger.error(f"이미지 업로드 중 오류가 발생했습니다.{space_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"이미지 업로드 중 오류가 발생했습니다.{e}",
            )

    # 공간 삭제
    async def delete_space(self, space_id: str, user_id: str):
        existing_space = await self.db.spaces.find_one({"_id": ObjectId(space_id)})

        if not existing_space:
            self._logger.error(f"유효하지 않은 공간입니다.{space_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="공간을 찾을 수 없습니다."
            )

        if existing_space["user_id"] != user_id:
            self._logger.error(f"본인 공간만 삭제할 수 있습니다.{user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="본인 공간만 삭제할 수 있습니다.",
            )

        # 이미지 삭제
        path = f"{user_id}/{space_id}"
        s3_client = self.s3["s3_client"]
        bucket_name = self.s3["bucket"]

        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=path)

        if "Contents" in response:
            for obj in response["Contents"]:
                s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])

        await self.db.spaces.delete_one({"_id": ObjectId(space_id)})
        self._logger.info(f"이미지 및 공간 삭제 완료: {space_id}")

    # 위치 기준 데이터 가져오기
    async def get_nearby_spaces(
        self, longitude: float, latitude: float, radius: float
    ) -> List[Dict]:
        nearby_space_cursor = self.db.spaces.find(
            {
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude],
                        },
                        "$maxDistance": radius * 1000,  # km 변환
                    }
                }
            }
        )

        nearby_spaces = await nearby_space_cursor.to_list(length=None)
        for space in nearby_spaces:
            space["space_id"] = str(space["_id"])
            del space["_id"]

        if not nearby_spaces:
            self._logger.info(f"인근 공간이 없습니다.")
            self._logger.info(f"lat:{latitude}, long:{longitude}")
            raise HTTPException(status_code=404, detail="인근 공간이 없습니다.")
        return nearby_spaces
