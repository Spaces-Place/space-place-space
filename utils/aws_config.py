import os
from typing import Dict, Optional
from dotenv import load_dotenv
from fastapi import HTTPException, status


class AWSConfig:
    _instance: Optional['AWSConfig'] = None
    _initialized: bool = False
    _credentials: Optional[Dict] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self._load_environment()
        self._initialized = True
        self._credentials: None
        self._region = os.getenv("REGION_NAME")
        self.bucket_name = os.getenv("SPACE_S3_BUCKET_NAME")

    # 환경 설정
    def _load_environment(self):
        env_file = '.env.development' if os.getenv('APP_ENV') == 'development' else '.env.production'
        load_dotenv(env_file)
        self._is_development = env_file == '.env.development'

    # 자격 증명
    def get_credentials(self):
        if self._credentials is None:
            
            if os.getenv('ENV') == 'development':
                self._credentials = {
                    'aws_access_key': os.getenv('SPACE_ACCESS_KEY'),
                    'aws_secret_key': os.getenv('SPACE_SECRET_KEY'),
                    'aws_region': self._region
                }

            else:
                try:
                    with open("/etc/secret-volume/access", "r") as access_file:
                        self._credentials['access_key'] = access_file.read().strip()

                    with open("/etc/secret-volume/secret", "r") as secret_file:
                        self._credentials['secret_key'] = secret_file.read().strip()
                    
                    self._credentials['aws_region'] = self._region
                except FileNotFoundError as e:
                    print(f"파일을 찾을 수 없습니다: {e}")
                except Exception as e:
                    print(f"오류 발생: {e}")


        return self._credentials

    # 환경에 따른 값 추출
    def _get_config_value(self, name: str) -> str:
        if self._is_development:
            return os.getenv(name)
        else:
            return self._get_parameter_from_ssm(name)

    # SSM
    def _get_parameter_from_ssm(self, name: str) -> str:
        from services.aws_service import AWSService

        aws_service = AWSService()
        ssm = aws_service.get_ssm_client()

        try:
            parameter = ssm.get_parameter(Name=name, WithDecryption=True)
            return parameter['Parameter']['Value']
        except ssm.exceptions.ParameterNotFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{name} parameter does not exist in AWS SSM."
            )
        except ssm.exceptions.InvalidKeyId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid KMS key used for decrypting {name}."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve {name} from AWS SSM: {e}"
            )

    # DB
    def get_db_config(self):
        return {
            'name': self._get_config_value("SPACE_DB_NAME"),
            'host': self._get_config_value("SPACE_DB_HOST"),
            'password': self._get_config_value("SPACE_DB_PASSWORD"),
        }

    # JWT 시크릿
    def get_jwt_secret(self):
        return self._get_config_value("USER_JWT_SECRET")
    

def get_aws_config() -> AWSConfig:
    return AWSConfig()