# endpoints.py
# Aquí defines tu endpoint /clima-info

from fastapi import APIRouter, Request
from app.use_cases.clima_info import obtener_clima_info
from app.domain.models import ClimaInfoResponse
from app.core.audit import audit_request
import requests

router = APIRouter()


def get_public_ip() -> str:
    try:
        resp = requests.get("https://api.ipify.org?format=json", timeout=5)
        return resp.json().get("ip", "127.0.0.1")
    except Exception:
        return "127.0.0.1"


@router.get("/clima-info", response_model=ClimaInfoResponse)
async def get_clima_info(request: Request):
    ip = request.headers.get("x-forwarded-for") or request.client.host
    # Si la IP es localhost, intenta obtener la IP pública real
    if ip.startswith("127.") or ip == "::1":
        ip = get_public_ip()
    result = await obtener_clima_info(ip)
    # Auditar consulta
    ip_info = {
        "ip": ip,
        "ciudad": getattr(result.origen_consulta, "ciudad", None),
        "region": getattr(result.origen_consulta, "region", None),
        "pais": getattr(result.origen_consulta, "pais", None)
    }
    audit_request(request, "/clima-info", dict(request.query_params), ip_info)
    return result
