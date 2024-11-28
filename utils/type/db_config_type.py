from dataclasses import dataclass
from typing import Optional 


@dataclass
class DBConfig:
    host: str
    dbname: str
    username: str
    password: str
    options: Optional[str] = None