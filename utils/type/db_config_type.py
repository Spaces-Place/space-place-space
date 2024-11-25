from dataclasses import dataclass


@dataclass
class DBConfig:
    host: str
    dbname: str
    username: str
    password: str