# endpoints.py
# Aquí defines tu endpoint /clima-info

from fastapi import APIRouter, Request
from app.use_cases.clima_info import obtener_clima_info
from app.domain.models import ClimaInfoResponse
import requests

router = APIRouter()


def get_public_ip() -> str:
    try:
        resp = requests.get("https://api.ipify.org?format=json", timeout=5)
        return resp.json().get("ip", "127.0.0.1")
    except Exception:
        return "127.0.0.1"


@router.get("/clima-info", response_model=ClimaInfoResponse)
def get_clima_info(request: Request):
    # Si la IP es localhost, intenta obtener la IP pública real
    ip = request.headers.get("x-forwarded-for") or request.client.host
    if ip.startswith("127.") or ip == "::1":
        ip = get_public_ip()
    result = obtener_clima_info(ip)
    return result
