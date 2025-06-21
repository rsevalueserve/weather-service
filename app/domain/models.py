# models.py
# Estructuras para tu respuesta, entidades simples

from pydantic import BaseModel


class OrigenConsulta(BaseModel):
    ip: str
    ciudad: str
    region: str
    pais: str


class ClimaInfoResponse(BaseModel):
    pais: str
    capital: str
    region: str
    poblacion: int
    temperatura_actual: float
    condicion: str
    moneda: str
    origen_consulta: OrigenConsulta
