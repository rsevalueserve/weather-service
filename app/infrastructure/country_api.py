# country_api.py
# Adapter para consumir REST Countries API

import requests


def obtener_info_pais(codigo_pais: str) -> dict:
    url = f"https://restcountries.com/v3.1/alpha/{codigo_pais}"
    resp = requests.get(url, timeout=5)
    data = resp.json()
    if not data or not isinstance(data, list):
        raise Exception("No se pudo obtener información del país")
    pais = data[0]
    return {
        "pais": pais.get("name", {}).get("common", "Desconocido"),
        "capital": pais.get("capital", ["Desconocido"])[0],
        "region": pais.get("region", "Desconocido"),
        "poblacion": pais.get("population", 0),
        "moneda": list(pais.get("currencies", {"Desconocido": {}}).keys())[0] if pais.get("currencies") else "Desconocido"
    }
