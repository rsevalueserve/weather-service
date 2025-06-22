# endpoints.py
# Aquí defines tu endpoint /clima-info

from fastapi import APIRouter, Request
from app.use_cases.clima_info import obtener_clima_info
from app.domain.models import ClimaInfoResponse
from app.core.audit import audit_request
import logging

router = APIRouter()


def get_public_ip() -> str:
    import requests
    try:
        resp = requests.get("https://api.ipify.org?format=json", timeout=5)
        return resp.json().get("ip", "127.0.0.1")
    except Exception:
        return "127.0.0.1"


def is_private_ip(ip: str) -> bool:
    # Valida que la IP sea IPv4 y maneja posibles errores de formato
    try:
        if ip == "::1":
            return True
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        if ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("127."):
            return True
        if ip.startswith("172."):
            second = int(parts[1])
            return 16 <= second <= 31
        return False
    except Exception:
        return False


@router.get("/clima-info", response_model=ClimaInfoResponse)
async def get_clima_info(request: Request):
    logger = logging.getLogger()
    ip = request.headers.get("x-forwarded-for") or request.client.host
    logger.info(f"IP recibida en request: {ip}")
    with open("/tmp/ip_debug.log", "a") as f:
        f.write(f"IP recibida en request: {ip}\n")
    # Si la IP es privada, intenta obtener la IP pública real
    if is_private_ip(ip):
        logger.info("La IP detectada es privada, se intentará obtener la IP pública real...")
        ip = get_public_ip()
        logger.info(f"IP pública obtenida: {ip}")
        with open("/tmp/ip_debug.log", "a") as f:
            f.write(f"IP pública obtenida: {ip}\n")
    else:
        logger.info("La IP detectada es pública, se usará directamente.")
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
