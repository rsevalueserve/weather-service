# errors.py
# Definición de errores custom

# Implementación pendiente

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError as FastAPIValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware


class CustomAPIException(Exception):
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code


def add_global_exception_handlers(app):
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)}
        )

    @app.exception_handler(FastAPIValidationError)
    async def validation_exception_handler(request: Request, exc: FastAPIValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )

    @app.exception_handler(CustomAPIException)
    async def custom_api_exception_handler(request: Request, exc: CustomAPIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
