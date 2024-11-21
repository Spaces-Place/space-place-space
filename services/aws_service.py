import boto3
from typing import Dict


class AWSService:
    _instance = None
    _clients = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        from utils.aws_config import get_aws_config
        self.config = get_aws_config()

    # 서비스별 client 생성
    def _create_client(self, service_name: str):
        credentials = self.config.get_credentials()
        return boto3.client(
            service_name,
            aws_access_key_id=credentials['aws_access_key'],
            aws_secret_access_key=credentials['aws_secret_key'],
            region_name=credentials['aws_region']
        )

    # 서비스
    def get_client(self, service_name: str):
        if service_name not in self._clients:
            self._clients[service_name] = self._create_client(service_name)
        return self._clients[service_name]

    # S3
    def get_s3_config(self) -> Dict:
        return {
            "s3_client": self.get_client('s3'),
            "bucket": self.config.bucket_name
        }
    
    # SSM
    def get_ssm_client(self):
        return self.get_client('ssm')
    
def get_aws_service() -> AWSService:
    return AWSService()