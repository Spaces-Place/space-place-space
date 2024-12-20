from typing import Optional
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from utils.database_config import DatabaseConfig
from utils.logger import Logger


class MongoDB:
    _instance: Optional['MongoDB'] = None
    
    def __init__(self):
        self._db_config = DatabaseConfig().get_db_config()
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._logger = Logger.setup_logger()

    async def connect(self):
        if not self.client:
            try:
                self.client = AsyncIOMotorClient(self._build_connection_string())
                self.db = self.client[self._db_config.dbname]
                
                self._logger.info('몽고DB 연결 중...')
                await self.client.admin.command('ismaster')
                self._logger.info('몽고DB 연결 성공')
            except Exception as e:
                await self.close()
                self._logger.error(f"MongoDB 연결 실패: {str(e)}")
                raise HTTPException(status_code=500, detail="데이터베이스 연결 실패")

    def _build_connection_string(self) -> str:
        host = self._db_config.host
        dbname = self._db_config.dbname
        username = self._db_config.username
        password = self._db_config.password
        options = self._db_config.options or ""
        return f"mongodb://{username}:{password}@{host}/{dbname}{options}"

    async def initialize(self):
        try:
            # 인덱스 생성(위치 기반 데이터 조회 시 필요)
            existing_indexes = await self.db.spaces.list_indexes().to_list(None)
            index_exists = False
            
            for index in existing_indexes:
                if "location_2dsphere" in index["name"]:
                    index_exists = True
                    break
            
            # 인덱스가 없을 때만 생성
            if not index_exists:
                self._logger.info(f"location, 2dsphere 인덱스 생성")
                await self.db.spaces.create_index([("location", "2dsphere")])            

            return self.db
        
        except Exception as e:
            self._logger.error(f"DB 초기화 중 오류가 발생했습니다.: {e}")
            raise HTTPException(status_code=500, detail="내부적으로 오류가 발생했습니다.")
    
    async def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    @classmethod
    async def get_instance(cls) -> 'MongoDB':
        if not cls._instance:
            cls._instance = MongoDB()
            await cls._instance.connect()
        return cls._instance


async def get_mongodb() -> AsyncIOMotorDatabase:
    mongodb = await MongoDB.get_instance()
    if mongodb.db is None:
        mongodb._logger.error(f"데이터베이스가 초기화되지 않았습니다.")
        raise HTTPException(status_code=500, detail="내부적으로 오류가 발생했습니다.")
    return mongodb.db