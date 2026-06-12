from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

from config import load_settings
from service import ExcelService


settings = load_settings()

_EXCEL_PATH = (
    Path(settings.excel_path)
    if settings.excel_path
    else Path(__file__).resolve().parent / "output" / "citas.xlsx"
)
SERVICE = ExcelService(_EXCEL_PATH)

app = FastAPI(
    title=settings.app_name,
    version=settings.server_version,
    description="API REST alternativa al servidor MCP para el proyecto CRM PoC.",
)


def _handle(fn, *args, **kwargs) -> Any:
    try:
        return fn(*args, **kwargs)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "excel_exists": _EXCEL_PATH.exists(),
        "excel_path": str(_EXCEL_PATH),
    }


@app.get("/v1/capabilities")
def capabilities() -> dict:
    return {
        "app": settings.app_name,
        "version": settings.server_version,
        "tools": [
            "get_citas_semanales",
            "get_citas_12_semanas",
            "get_historico_citas",
            "get_historico_llamadas",
            "get_historico_opps",
            "get_llamadas_abiertas",
            "get_leads_abiertos",
            "get_oportunidades_abiertas",
            "get_ofertas_pendientes",
            "get_convocatorias_abiertas",
            "get_subvenciones_bdns",
            "get_resumen_noticias",
        ],
    }


@app.get("/v1/citas-semanales")
def get_citas_semanales(email: str) -> list[dict]:
    """Citas de la semana actual para el usuario indicado."""
    return _handle(SERVICE.read_by_email, "CITAS SEMANALES", email)


@app.get("/v1/citas-12-semanas")
def get_citas_12_semanas(email: str) -> list[dict]:
    """Citas de la doceava semana anterior para el usuario indicado."""
    return _handle(SERVICE.read_by_email, "CITAS 12 SEMANAS ATRAS", email)


@app.get("/v1/historico-citas")
def get_historico_citas(email: str) -> list[dict]:
    """Histórico de citas (últimos 3 años) para el usuario indicado."""
    return _handle(SERVICE.read_by_email, "HISTORICO DE CITAS", email)


@app.get("/v1/historico-llamadas")
def get_historico_llamadas(email: str) -> list[dict]:
    """Histórico de llamadas (últimos 3 años) para el usuario indicado."""
    return _handle(SERVICE.read_by_email, "HISTORICO DE LLAMADAS", email)


@app.get("/v1/historico-opps")
def get_historico_opps(email: str) -> list[dict]:
    """Histórico de servicios de oportunidades para el usuario indicado."""
    return _handle(SERVICE.read_by_email, "HISTORICO DE OPPS", email)


@app.get("/v1/llamadas-abiertas")
def get_llamadas_abiertas(email: str) -> list[dict]:
    """Llamadas abiertas para el usuario indicado."""
    return _handle(SERVICE.read_by_email, "LLAMADAS ABIERTAS", email)


@app.get("/v1/leads-abiertos")
def get_leads_abiertos(email: str) -> list[dict]:
    """Leads abiertos asignados al usuario indicado."""
    return _handle(SERVICE.read_by_email, "LEADS ABIERTOS", email)


@app.get("/v1/oportunidades-abiertas")
def get_oportunidades_abiertas(email: str) -> list[dict]:
    """Oportunidades abiertas asignadas al usuario indicado."""
    return _handle(SERVICE.read_by_email, "OPORTUNIDADES ABIERTAS", email)


@app.get("/v1/ofertas-pendientes")
def get_ofertas_pendientes(email: str) -> list[dict]:
    """Ofertas pendientes asignadas al usuario indicado."""
    return _handle(SERVICE.read_by_email, "OFERTAS PENDIENTES", email)


@app.get("/v1/convocatorias-abiertas")
def get_convocatorias_abiertas(sector_grants: str) -> list[dict]:
    """Convocatorias de subvenciones abiertas para el sector indicado."""
    return _handle(SERVICE.read_by_sector, sector_grants)


@app.get("/v1/subvenciones-bdns")
def get_subvenciones_bdns(nif: str) -> list[dict]:
    """Subvenciones BDNS recibidas por la cuenta con el NIF indicado."""
    return _handle(SERVICE.read_by_nif, nif)


@app.get("/v1/resumen-noticias")
def get_resumen_noticias(nombre_cuenta: str) -> list[dict]:
    """Resumen de noticias para la cuenta indicada."""
    return _handle(SERVICE.read_by_cuenta, nombre_cuenta)
