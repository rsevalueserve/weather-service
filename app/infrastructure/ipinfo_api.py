# ipinfo_api.py
# Adapter para consumir ipinfo.io o ip-api.com

import logging
import httpx
import os

logger = logging.getLogger("uvicorn")
LOG_FILE = "/tmp/ipinfo_debug.log"


def log_to_file(msg: str):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")


async def obtener_info_ip(ip: str) -> dict:
    logger.info(f"[INFO] Entrando a obtener_info_ip con ip={ip}")
    log_to_file(f"[INFO] Entrando a obtener_info_ip con ip={ip}")
    url = (
        f"http://ip-api.com/json/{ip}?fields="
        "status,country,countryCode,regionName,city"
    )
    try:
        logger.info(f"[INFO] Consultando ip-api.com con url={url}")
        log_to_file(f"[INFO] Consultando ip-api.com con url={url}")
        logger.info("[DEBUG] Antes de hacer la petición HTTP a ip-api.com")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=5)
        logger.info("[DEBUG] Después de hacer la petición HTTP a ip-api.com")
        logger.info(f"[INFO] ip-api.com status: {resp.status_code}")
        logger.info(f"[INFO] ip-api.com body: {resp.text}")
        log_to_file(f"[INFO] ip-api.com status: {resp.status_code}")
        log_to_file(f"[INFO] ip-api.com body: {resp.text}")
        data = resp.json()
        logger.info(f"[INFO] Respuesta de ip-api.com para {ip}: {data}")
        log_to_file(f"[INFO] Respuesta de ip-api.com para {ip}: {data}")
        if data.get("status") != "success":
            logger.error(f"[ERROR] Fallo ip-api.com para {ip}: {data}")
            log_to_file(f"[ERROR] Fallo ip-api.com para {ip}: {data}")
            raise Exception(f"No se pudo obtener información de la IP. Respuesta: {data}")
        logger.info(
            f"[INFO] Geolocalización exitosa: ciudad={data.get('city')}, "
            f"region={data.get('regionName')}, pais={data.get('countryCode')}"
        )
        log_to_file(
            f"[INFO] Geolocalización exitosa: ciudad={data.get('city')}, "
            f"region={data.get('regionName')}, pais={data.get('countryCode')}"
        )
        return {
            "ciudad": data.get("city", "Desconocido"),
            "region": data.get("regionName", "Desconocido"),
            "pais": data.get("countryCode", "Desconocido")
        }
    except Exception as e:
        logger.exception(f"[EXCEPTION] Tipo: {type(e)} | Error consultando ip-api.com para {ip}: {e}")
        log_to_file(f"[EXCEPTION] Tipo: {type(e)} | Error consultando ip-api.com para {ip}: {e}")
        raise Exception(f"No se pudo obtener información de la IP. Tipo: {type(e)} | {e}")
