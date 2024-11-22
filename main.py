from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo.errors import OperationFailure

from routers.space import space_router
from utils.mongodb import get_database


app = FastAPI(title="공간 API", version="ver.1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    env_type = '.env.development' if os.getenv('APP_ENV') == 'development' else '.env.production'
    load_dotenv(env_type)

    db = await get_database()
    
    try:
        existing_indexes = await db.spaces.list_indexes().to_list(None)
        index_exists = False
        
        for index in existing_indexes:
            if "location_2dsphere" in index["name"]:
                index_exists = True
                break
        
        # 인덱스가 없을 때만 생성
        if not index_exists:
            await db.spaces.create_index([("location", "2dsphere")])
            
    except OperationFailure as e:
        pass
        # print(f"인덱스 생성 오류 : {e}")
    
    yield

    await db.client.close()

# FastAPI 앱 인스턴스 생성
app = FastAPI(lifespan=lifespan)

app.include_router(space_router, prefix="/api/v1/spaces")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: 허용하는 URL 넣어야함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
