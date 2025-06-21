# config.py
# Configuración general y variables de entorno
import os
from dotenv import load_dotenv

load_dotenv()


def get_settings():
    return {
        "OPENWEATHERMAP_API_KEY": os.getenv("OPENWEATHERMAP_API_KEY", "")
    }
