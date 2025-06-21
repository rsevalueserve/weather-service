# weather_api.py
# Adapter para consumir OpenWeatherMap API

import os
import requests
from app.core.config import get_settings
from app.core.errors import CustomAPIException


def obtener_clima(ciudad: str, pais: str) -> dict:
    api_key = os.getenv("OPENWEATHERMAP_API_KEY") or get_settings()["OPENWEATHERMAP_API_KEY"]
    if not api_key:
        raise CustomAPIException("La clave de API de OpenWeatherMap no está configurada.", 500)
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?q={ciudad},{pais}&appid={api_key}&units=metric&lang=es"
    )
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if resp.status_code != 200:
            raise CustomAPIException(f"Error de OpenWeatherMap: {data.get('message', 'Error desconocido')}", 502)
        return {
            "temperatura_actual": data["main"]["temp"],
            "condicion": data["weather"][0]["description"].capitalize()
        }
    except requests.RequestException:
        raise CustomAPIException("No se pudo conectar con el servicio de clima.", 502)
    except Exception as e:
        raise CustomAPIException(f"Error inesperado al consultar el clima: {str(e)}", 500)
