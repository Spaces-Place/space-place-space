from motor.motor_asyncio import AsyncIOMotorClient
from services.aws_service import get_aws_service


# MongoDB 클라이언트 생성
async def get_database() -> AsyncIOMotorClient:
    aws_service = get_aws_service()
    db_config = aws_service.get_db_config() # DB 설정 가져오기
    client = AsyncIOMotorClient(db_config['host'])
    return client[db_config['dbname']]