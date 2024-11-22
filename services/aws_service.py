import os
import boto3
from typing import Dict

from utils.aws_ssm import ParameterStore
from utils.credential import Credential
from utils.database_config import DatabaseConfig


class AWSService:
    def __init__(self):
        self._credentials = Credential.get_credentials()
        self._parameter_store = ParameterStore(self._credentials)
        self._database_config = DatabaseConfig(os.getenv('APP_ENV'))

    # 서비스별 client 생성
    def create_client(self, service_name: str):
        return boto3.client(
            service_name,
            aws_access_key_id=self._credentials.access_key,
            aws_secret_access_key=self._credentials.secret_key,
            region_name=self._credentials.region
        )

    # S3
    def get_s3_config(self) -> Dict:
        return {
            "s3_client": self.create_client('s3'),
            "bucket": os.getenv('SPACE_S3_BUCKET_NAME')
        }
    
    # SSM
    # def get_ssm_client(self):
    #     return self.create_client('ssm')

    # DB
    def get_db_config(self) -> Dict:
        return self._database_config.get_db_config()
    
    # JWT
    def get_jwt_secret(self) -> str:
        return self._parameter_store.get_parameter("USER_JWT_SECRET")
    
def get_aws_service() -> AWSService:
    return AWSService()