import os


class EnvConfig:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnvConfig, cls).__new__(cls)

        return cls._instance

    """
    개발/운영 환경 여부
    """

    def __init__(self):
        self.environment = os.getenv("APP_ENV")

    @property
    def is_development(self) -> bool:
        return self.environment == "development"
