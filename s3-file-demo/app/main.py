from fastapi import FastAPI

from .database import Base, engine
from .routers import files as files_router

# 启动时建表（demo 用；生产推荐 Alembic）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="S3 File Demo", version="0.1.0")
app.include_router(files_router.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
