# ipinfo_api.py
# Adapter para consumir ipinfo.io o ip-api.com

import httpx


async def obtener_info_ip(ip: str) -> dict:
    url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=5)
        data = resp.json()
    if data.get("status") != "success":
        raise Exception("No se pudo obtener información de la IP")
    return {
        "ciudad": data.get("city", "Desconocido"),
        "region": data.get("regionName", "Desconocido"),
        "pais": data.get("countryCode", "Desconocido")
    }
