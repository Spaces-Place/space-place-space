import os
import boto3
from typing import Dict

from utils.aws_ssm import ParameterStore
from utils.credential import Credential
from utils.env_config import EnvConfig


class AWSService:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AWSService, cls).__new__(cls)
            cls._env_config = EnvConfig()
            cls._credentials = Credential.get_credentials()
            cls._parameter_store = ParameterStore()
            # cls._database_config = DatabaseConfig()
        return cls._instance

    # 서비스별 client 생성
    def create_client(self, service_name: str):
        return boto3.client(
            service_name,
            aws_access_key_id=self._credentials.access_key,
            aws_secret_access_key=self._credentials.secret_key,
            region_name=self._credentials.region,
        )

    # S3
    def get_s3_config(self) -> Dict:
        return {
            "s3_client": self.create_client("s3"),
            "bucket": os.getenv("SPACE_S3_BUCKET_NAME"),
        }

    # JWT
    def get_jwt_secret(self) -> str:
        if self._env_config.is_development:
            return os.getenv("USER_JWT_SECRET")
        else:
            return self._parameter_store.get_parameter("USER_JWT_SECRET")


def get_aws_service() -> AWSService:
    return AWSService()
