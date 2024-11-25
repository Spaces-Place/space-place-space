from dataclasses import dataclass


@dataclass
class AWSCredentials:
    access_key: str
    secret_key: str
    region: str
