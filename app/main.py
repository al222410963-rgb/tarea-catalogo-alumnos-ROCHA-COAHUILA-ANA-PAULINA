"""Catálogo de Productos persistente."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  (registra las tablas en Base.metadata)
from .db import Base, engine
from .routers import productos, web


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Catálogo de Productos", version="0.4.0", lifespan=lifespan)
app.include_router(productos.router)
app.include_router(web.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
