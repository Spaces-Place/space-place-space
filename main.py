from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
