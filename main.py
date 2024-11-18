from typing import List, Optional
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from routers.space import space_router


app = FastAPI(title="공간 API", version="ver.1")

app.include_router(space_router, prefix="/api/v1/spaces")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: 허용하는 URL 넣어야함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Item(BaseModel):
    name: str
    description: Optional[str] = None

class DataModel(BaseModel):
    items: List[Item]
    title: str

@app.post("/upload/")
async def upload(data: DataModel, file: UploadFile = File(...)):
    file_location = f"files/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return JSONResponse(content={"message": "파일 업로드 성공", "data": data.dict()})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
