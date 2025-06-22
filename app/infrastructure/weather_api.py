# weather_api.py
# Adapter para consumir OpenWeatherMap API

import os
import httpx
import logging
from app.core.config import get_settings
from app.core.errors import CustomAPIException

logger = logging.getLogger()


async def obtener_clima(ciudad: str, pais: str) -> dict:
    api_key = os.getenv("OPENWEATHERMAP_API_KEY") or get_settings()["OPENWEATHERMAP_API_KEY"]
    logger.info(f"Usando API key para OpenWeatherMap: {api_key[:6]}... (longitud: {len(api_key)})")
    if not api_key:
        logger.error("La clave de API de OpenWeatherMap no está configurada.")
        raise CustomAPIException("La clave de API de OpenWeatherMap no está configurada.", 500)
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?q={ciudad},{pais}&appid={api_key}&units=metric&lang=es"
    )
    logger.info(f"Consultando OpenWeatherMap con url: {url}")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=5)
            logger.info(f"Respuesta OpenWeatherMap status: {resp.status_code}")
            logger.info(f"OpenWeatherMap body: {resp.text}")
            data = resp.json()
        if resp.status_code != 200:
            logger.error(f"Error de OpenWeatherMap: {data.get('message', 'Error desconocido')}")
            raise CustomAPIException(f"Error de OpenWeatherMap: {data.get('message', 'Error desconocido')}", 502)
        logger.info(f"Clima obtenido: temp={data['main']['temp']}, condicion={data['weather'][0]['description']}")
        return {
            "temperatura_actual": data["main"]["temp"],
            "condicion": data["weather"][0]["description"].capitalize()
        }
    except httpx.RequestError:
        logger.exception("No se pudo conectar con el servicio de clima.")
        raise CustomAPIException("No se pudo conectar con el servicio de clima.", 502)
    except Exception as e:
        logger.exception(f"Error inesperado al consultar el clima: {str(e)}")
        raise CustomAPIException(f"Error inesperado al consultar el clima: {str(e)}", 500)
