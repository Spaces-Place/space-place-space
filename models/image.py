from pydantic import BaseModel

class Image(BaseModel):
    filename: str
    original_filename: int