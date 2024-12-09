from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from routers.space import space_router
from utils import mongodb
from utils.logger import Logger
from utils.mongodb import MongoDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongodb
    env_type = '.env.development' if os.getenv('APP_ENV') == 'development' else '.env.production'
    load_dotenv(env_type)

    mongodb = await MongoDB.get_instance()

    try:
        await mongodb.initialize()
        yield
    finally:
        await mongodb.close()
        MongoDB._instance = None

app = FastAPI(title="공간 API", version="ver.1", lifespan=lifespan)

app.include_router(space_router, prefix="/api/v1/spaces")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(logger: Logger = Depends(Logger.setup_logger)) -> dict:
    logger.info('health check')
    return {"status" : "ok"}

"""Trace"""
# OpenTelemetry
resource = Resource.create({ResourceAttributes.SERVICE_NAME: "space-service"})
trace_provider = TracerProvider(resource=resource)

# 템포에 데이터 전송을 위한 OLTP span Exporter
tempo_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
span_processor = BatchSpanProcessor(tempo_exporter)
trace_provider.add_span_processor(span_processor) # Span 프로세서 추가

trace.set_tracer_provider(trace_provider)

FastAPIInstrumentor.instrument_app(app, excluded_urls="client/.*/health")
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app) # 메트릭(/metrics) 노출

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: 허용하는 URL 넣어야함
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
