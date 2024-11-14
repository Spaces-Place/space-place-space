from motor.motor_asyncio import AsyncIOMotorClient
from utils.aws_ssm_key import get_space_db_host, get_space_db_name

# MongoDB 클라이언트 생성
async def get_database():
    client = AsyncIOMotorClient(get_space_db_host())
    return client[get_space_db_name()]
