import logging
import boto3
from fastapi import HTTPException, status

from utils.credential import Credential


class ParameterStore:

    _instance = None
    _logger = logging.getLogger()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ParameterStore, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self._cached_parameters = {}
        credentials = Credential.get_credentials()
        self._client = boto3.client(
            "ssm",
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            region_name=credentials.region,
        )
        self._initialized = True

    def get_parameter(self, key_name: str, with_decryption: bool = False) -> str:
        if key_name in self._cached_parameters:
            return self._cached_parameters[key_name]
        try:
            parameter = self._client.get_parameter(
                Name=key_name, WithDecryption=with_decryption
            )
            value = parameter["Parameter"]["Value"]
            self._cached_parameters[key_name] = value
            self._logger.info(f"파라미터 조회 성공: {parameter['Parameter']['Value']}")

            return value
        except self._client.exceptions.ParameterNotFound:
            self._logger.warning(f"{parameter}는 정의되어 있지 않습니다.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{parameter}는 정의되어 있지 않습니다.",
            )
        except self._client.exceptions.InvalidKeyId:
            self._logger.warning(f"복호화에 사용된 KMS 키가 잘못되었습니다.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"복호화에 사용된 KMS 키가 잘못되었습니다.",
            )
        except Exception as e:
            self._logger.warning(f"파라미터 조회 중 오류가 발생했습니다.{e}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"파라미터 조회 중 오류가 발생했습니다.{e}",
            )
