from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from services.aws_service import AWSService, get_aws_service


class MongoDBClient:
    def __init__(self, aws_service: AWSService):
        self.aws_service = aws_service
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._connect()

    def _connect(self):
        db_config = self.aws_service.get_db_config()
        
        # 연결 문자열 생성 (인증 포함)
        connection_string = self._build_connection_string(db_config)
        
        try:
            self._client = AsyncIOMotorClient(connection_string)
            self._database = self._client[db_config['dbname']]
        except Exception as e:
            raise RuntimeError(f"MongoDB 연결 실패: {e}")
        
    def _build_connection_string(self, db_config: Dict[str, str]) -> str:
        # 개발 환경이나 비밀번호가 없는 경우 기본 호스트 사용
        if not db_config.get('password'):
            return db_config['host']
        
        # 인증 포함 연결 문자열 생성
        host = db_config['host']
        dbname = db_config['dbname']
        username = db_config['username']
        password = db_config['password']
        
    # 다양한 연결 문자열 형식 지원  
        if username and password:
            return f"mongodb://{username}:{password}@{host}:27017/{dbname}"
        return host

    @property
    def client(self) -> AsyncIOMotorClient:
        if not self._client:
            raise RuntimeError("MongoDB 클라이언트가 초기화되지 않았습니다.")
        return self._client

    @property
    def database(self) -> AsyncIOMotorDatabase:
        if not self._database:
            raise RuntimeError("MongoDB 데이터베이스가 초기화되지 않았습니다.")
        return self._database

    def get_collection(self, collection_name: str):
        return self.database[collection_name]

    def close(self):
        if self._client:
            self._client.close()

# 편의를 위한 팩토리 함수
def get_mongodb_client() -> MongoDBClient:
    aws_service = get_aws_service()
    return MongoDBClient(aws_service)

# 비동기 데이터베이스 가져오기 함수
async def get_database() -> AsyncIOMotorDatabase:
    mongodb_client = get_mongodb_client()
    return mongodb_client.database