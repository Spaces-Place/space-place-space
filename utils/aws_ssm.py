import boto3
from fastapi import HTTPException, status

from utils.credential import Credential


class ParameterStore:

    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParameterStore, cls).__new__(cls)
            credentials = Credential.get_credentials()
            cls._client = boto3.client(
                'ssm',
                aws_access_key_id=credentials.access_key,
                aws_secret_access_key=credentials.secret_key,
                region_name=credentials.region
            )
            
        return cls._instance
    
    def get_parameter(self, key_name: str, with_decryption: bool = False) -> str:
        try:
            parameter = self._client.get_parameter(Name=key_name, WithDecryption=with_decryption)
            return parameter['Parameter']['Value']
        except self._client.exceptions.ParameterNotFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{parameter}는 정의되어 있지 않습니다."
            )
        except self._client.exceptions.InvalidKeyId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"복호화에 사용된 KMS 키가 잘못되었습니다."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"파라미터 조회 중 오류가 발생했습니다.{e}"
            )
