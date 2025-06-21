import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_clima_info_success(monkeypatch):
    # Mock correcto: sobre el endpoint, no solo el use case
    import app.api.v1.endpoints as endpoints
    monkeypatch.setattr(endpoints, "obtener_clima_info", lambda ip: {
        "pais": "Argentina",
        "capital": "Buenos Aires",
        "region": "Americas",
        "poblacion": 45376763,
        "temperatura_actual": 22.5,
        "condicion": "Despejado",
        "moneda": "ARS",
        "origen_consulta": {
            "ip": ip,
            "ciudad": "Buenos Aires",
            "region": "Buenos Aires",
            "pais": "AR"
        }
    })
    response = client.get("/api/v1/clima-info", headers={"x-forwarded-for": "8.8.8.8"})
    assert response.status_code == 200
    data = response.json()
    assert data["pais"] == "Argentina"
    assert data["origen_consulta"]["ip"] == "8.8.8.8"


def test_clima_info_rate_limit():
    # Realiza 6 peticiones rápidas para forzar el rate limit
    for _ in range(5):
        client.get("/api/v1/clima-info", headers={"x-forwarded-for": "1.2.3.4"})
    response = client.get("/api/v1/clima-info", headers={"x-forwarded-for": "1.2.3.4"})
    assert response.status_code == 429
    # Acepta ambos mensajes posibles
    assert (
        "consultas por minuto" in response.text or
        "Rate limit exceeded" in response.text
    )
