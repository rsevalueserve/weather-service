# clima_info.py
# Orquesta la lógica para reunir toda la información de las APIs

from app.infrastructure.weather_api import obtener_clima
from app.infrastructure.country_api import obtener_info_pais
from app.infrastructure.ipinfo_api import obtener_info_ip
from app.domain.models import ClimaInfoResponse, OrigenConsulta


async def obtener_clima_info(ip: str) -> ClimaInfoResponse:
    # 1. Obtener info geográfica de la IP
    ip_info = await obtener_info_ip(ip)
    # ip_info debe tener: ciudad, region, pais (código)

    # 2. Obtener info del país
    country_info = await obtener_info_pais(ip_info['pais'])
    # country_info: capital, region, poblacion, moneda

    # 3. Obtener clima de la capital
    clima = await obtener_clima(country_info['capital'], country_info['pais'])
    # clima: temperatura_actual, condicion

    # 4. Construir respuesta
    origen = OrigenConsulta(
        ip=ip,
        ciudad=ip_info['ciudad'],
        region=ip_info['region'],
        pais=ip_info['pais']
    )
    response = ClimaInfoResponse(
        pais=country_info['pais'],
        capital=country_info['capital'],
        region=country_info['region'],
        poblacion=country_info['poblacion'],
        temperatura_actual=clima['temperatura_actual'],
        condicion=clima['condicion'],
        moneda=country_info['moneda'],
        origen_consulta=origen
    )
    return response
