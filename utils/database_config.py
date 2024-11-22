import os
from typing import Dict


class DatabaseConfig:
    def __init__(self, env_type: str):
        self.env_type = env_type

    def get_db_config(self) -> Dict[str, str]:
        if self.env_type == 'development':
            return {
                'host': os.getenv('SPACE_DB_HOST'),
                'dbname': os.getenv('SPACE_DB_NAME'),
                'password': os.getenv('SPACE_DB_PASSWORD')
            }
        else:
            from utils.aws_ssm import ParameterStore
            from utils.credential import Credential

            credentials = Credential.get_credentials()
            parameter_store = ParameterStore(credentials)

            return {
                'host': parameter_store.get_parameter("SPACE_DB_HOST"),
                'dbname': parameter_store.get_parameter("SPACE_DB_NAME"),
                'password': parameter_store.get_parameter("SPACE_DB_PASSWORD")
            }
        