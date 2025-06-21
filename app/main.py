# main.py
# Arranque de la app FastAPI

from fastapi import FastAPI
from app.core.errors import add_global_exception_handlers
from app.core.throttling import register_throttling
from slowapi.middleware import SlowAPIMiddleware
from app.api.v1.endpoints import router as v1_router

app = FastAPI(title="Weather Info Microservice")

# Registrar throttling y errores globales
register_throttling(app)
add_global_exception_handlers(app)
app.add_middleware(SlowAPIMiddleware)

app.include_router(v1_router, prefix="/api/v1")
