from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

from routers.space import space_router
from utils import mongodb
from utils.mongodb import MongoDB, get_mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongodb
    env_type = (
        ".env.development"
        if os.getenv("APP_ENV") == "development"
        else ".env.production"
    )
    load_dotenv(env_type)

    mongodb = await MongoDB.get_instance()

    try:
        await mongodb.initialize()
        print("데이터베이스가 성공적으로 초기화되었습니다.")
        yield
    finally:
        await mongodb.close()
        MongoDB._instance = None


app = FastAPI(title="공간 API", version="ver.1", lifespan=lifespan)

app.include_router(space_router, prefix="/api/v1/spaces")


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    return {"status": "ok"}


FastAPIInstrumentor.instrument_app(app)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: 허용하는 URL 넣어야함
    allow_credentials=False,
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
