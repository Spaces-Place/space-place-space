import os
from utils.aws_ssm import ParameterStore
from utils.env_config import EnvConfig
from utils.logger import Logger
from utils.type.db_config_type import DBConfig


class DatabaseConfig:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConfig, cls).__new__(cls)
            cls._env_config = EnvConfig()
            cls._parameter_store = ParameterStore()
            cls._logger = Logger.setup_logger()
        return cls._instance

    def get_db_config(self) -> DBConfig:

        if self._env_config.is_development:
            return DBConfig(
                host=os.getenv("SPACE_DB_HOST"),
                dbname=os.getenv("SPACE_DB_NAME"),
                username=os.getenv("SPACE_DB_USERNAME"),
                password=os.getenv("SPACE_DB_PASSWORD"),
            )
        else:
            return DBConfig(
                host=self._parameter_store.get_parameter("SPACE_DB_HOST"),
                dbname=self._parameter_store.get_parameter("SPACE_DB_NAME"),
                username=self._parameter_store.get_parameter("SPACE_DB_USERNAME"),
                password=self._parameter_store.get_parameter("SPACE_DB_PASSWORD", True),
                options=self._parameter_store.get_parameter("SPACE_DB_OPTIONS"),
            )
