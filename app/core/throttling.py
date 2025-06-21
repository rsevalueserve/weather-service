# throttling.py
# Implementación y configuración de throttling (slowapi)
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])


def register_throttling(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


async def _rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded
) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "detail": (
                "Se ha excedido el límite de tasa. "
                "Máximo 5 consultas por minuto por IP."
            )
        }
    )
