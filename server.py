from __future__ import annotations

import asyncio
import logging
import sys
import uuid
from pathlib import Path
from typing import Any


from fastmcp import FastMCP
from fastapi import HTTPException
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth import BearerTokenMiddleware
from config import load_settings
from service import ExcelService
from scripts.realtime_query_service import DataverseRealtimeService

from scripts.config.dictionary import SECTORES


settings = load_settings()

_EXCEL_PATH = (
    Path(settings.excel_path)
    if settings.excel_path
    else Path(__file__).resolve().parent / "output" / "citas.xlsx"
)

SERVICE = ExcelService(_EXCEL_PATH)
REALTIME_SERVICE = DataverseRealtimeService(Path(__file__).resolve().parent / "xml_queries")

# --- Extracción asíncrona ---
TASK_LOGS_DIR = Path("logs/tasks")
TASK_LOGS_DIR.mkdir(parents=True, exist_ok=True)
tasks = {}
# ── Rutas HTTP personalizadas ─────────────────────────────────────────────────


mcp = FastMCP(name=settings.app_name, version=settings.server_version)

# --- Endpoint: Lanzar extracción en background ---
logger = logging.getLogger(settings.app_name)


def _normalize_email(email: str) -> str:
    return email.strip().replace("@epsa.com", "@fi-group.com")

async def monitor_process(task_id: str, process: asyncio.subprocess.Process, log_file):
    """Espera a que el proceso termine para evitar zombies y cierra el archivo."""
    try:
        return_code = await process.wait()
        if task_id in tasks:
            tasks[task_id]["status"] = "completed" if return_code == 0 else "failed"
            tasks[task_id]["return_code"] = return_code
    finally:
        log_file.close()

def _capabilities() -> dict[str, Any]:
    return {
        "app": settings.app_name,
        "version": settings.server_version,
        "mcp_path": settings.mcp_path,
        "transport": settings.transport,
        "auth_mode": settings.auth_mode,
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
            "get_cuentas_sin_llamar",
            "get_citas_semanales_realtime",
            "get_citas_por_comercial_semana_en_curso_realtime",
            "get_citas_por_gestor_semana_en_curso_realtime",
            "get_citas_por_comercial_realtime",
            "get_citas_por_gestor_realtime",
            "get_citas_por_cuenta_realtime",
            "get_llamadas_semanales_realtime",
            "get_llamadas_por_comercial_semana_en_curso_realtime",
            "get_llamadas_por_gestor_semana_en_curso_realtime",
            "get_llamadas_por_comercial_realtime",
            "get_llamadas_por_gestor_realtime",
            "get_llamadas_por_cuenta_realtime",
            "get_xml_queries_realtime",
            "run_xml_query_realtime",
        ],
    }


# ── Rutas HTTP personalizadas ─────────────────────────────────────────────────

@mcp.custom_route("/", methods=["GET"], include_in_schema=False)
async def root(_request: Request) -> JSONResponse:
    return JSONResponse({
        "name": settings.app_name,
        "version": settings.server_version,
        "mcp_url": settings.mcp_path,
        "health_url": "/health",
    })


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def health(_request: Request) -> JSONResponse:
    return JSONResponse({
        "status": "ok",
        "app": settings.app_name,
        "excel_exists": _EXCEL_PATH.exists(),
        "excel_path": str(_EXCEL_PATH),
        "auth_mode": settings.auth_mode,
        "mcp_path": settings.mcp_path,
    })


@mcp.custom_route("/v1/capabilities", methods=["GET"], include_in_schema=False)
async def capabilities_route(_request: Request) -> JSONResponse:
    return JSONResponse(_capabilities())


@mcp.custom_route("/extract-data", methods=["POST"])
async def run_extract_async(_request: Request) -> JSONResponse:
    script_path = Path("scripts/script_main.py")
    
    # Validar existencia del script
    if not script_path.is_file():
        raise HTTPException(status_code=500, detail="Script de extracción no encontrado.")

    task_id = str(uuid.uuid4())
    log_path = TASK_LOGS_DIR / f"{task_id}.log"

    try:
        # Abrir archivo de log sin bloquear el loop de eventos
        log_file = open(log_path, "w", encoding="utf-8")
        
        # Ejecución asíncrona no bloqueante
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(script_path),
            stdout=log_file,
            stderr=log_file
        )
        
        # Registrar la tarea y programar la limpieza del proceso en background
        tasks[task_id] = {
            "pid": process.pid, 
            "log": str(log_path),
            "status": "running"
        }
        
        # Crear tarea en background para liberar recursos del SO al finalizar
        asyncio.create_task(monitor_process(task_id, process, log_file))

        return JSONResponse({
            "status": "success",
            "task_id": task_id, 
            "log_path": str(log_path)
        })

    except Exception as e:
        logger.error(f"Error al iniciar la tarea {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al iniciar la extracción.")
    
@mcp.resource("diccionario://sectores")
def obtener_diccionario() -> str:
    """Carga y devuelve el diccionario de sectores FI y sectores GRANTS."""
    return SECTORES

@mcp.tool
def get_citas_semanales(email: str, userType: str) -> list[dict]:
    """
    Reuniones abiertas o programadas cuyo propietario de la cita sea el usuario con fecha de celebración la semana en curso. Por cada cita retorna:
    - NÚMERO_DE_CUENTA: Número identificador de la cuenta en CRM.
    - NIF: NIF fiscal de la cuenta.
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - SCORE_INICIAL: Puntuación inicial de la cuenta.
    - GROUP_ALIAS: Alias del grupo comercial asignado.
    - FECHA_DE_LA_CITA: Fecha y hora de inicio de la cita (ISO 8601).
    - CONTACTO_PRINCIPAL: Nombre completo del contacto principal.
    - CARGO_CONTACTO: Cargo o puesto del contacto principal.
    - TELEFONO_CONTACTO: Teléfono del contacto principal.
    - INDUSTRIA_FI: Industria FI asignada a la cuenta.
    - SECTOR_FI: Sector FI asignado a la cuenta.
    - SECTOR_GRANTS: Sector usado para buscar convocatorias/ayudas/subvenciones.
    - COMENTARIOS: Comentarios o resultado de la cita.
    - CUENTA_ID: GUID de la cuenta en Dataverse.
    - COMERCIAL: Correo del comercial responsable de la cita.
    Usa el siguiente formato para responder:
        -	Día y hora de la cita
        -	Nombre de cuenta, Alias group y score inicial.
            o	Contacto, cargo y teléfono
            o	Comentarios de la cita
            o	Resumen del histórico de actividad
            o	Industria FI y Ayudas presentadas
            o	Competidor, fecha del registro y en qué servicio.
            o	Noticias
            o	Argumentos y estrategia/Encaje en ayudas.
    Args:
        email: Correo electrónico del usuario en sesión.
        userType: Tipo de usuario en sesión. COMERCIAL o GESTOR.
    Returns:
        Lista de registros de citas de la semana en curso del usuario.
    """
    return SERVICE.read_by_email("CITAS SEMANALES", email=_normalize_email(email), column_name=userType)


@mcp.tool
def get_citas_12_semanas(email: str,  userType: str) -> list[dict]:
    """
    Reuniones completadas cuyo propietario de la cita sea el usuario con fecha de celebración 12 semanas atrás respecto a la semana en curso. Por cada cita retorna:
    - NÚMERO_DE_CUENTA: Número identificador de la cuenta en CRM.
    - NIF: NIF fiscal de la cuenta.
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - SCORE_INICIAL: Puntuación inicial de la cuenta.
    - GROUP_ALIAS: Alias del grupo comercial asignado.
    - FECHA_DE_LA_CITA: Fecha y hora de inicio de la cita (ISO 8601).
    - CONTACTO_PRINCIPAL: Nombre completo del contacto principal.
    - CARGO_CONTACTO: Cargo o puesto del contacto principal.
    - TELEFONO_CONTACTO: Teléfono del contacto principal.
    - INDUSTRIA_FI: Industria FI asignada a la cuenta.
    - SECTOR_FI: Sector FI asignado a la cuenta.
    - COMENTARIOS: Comentarios o resultado de la cita.
    - CUENTA_ID: GUID de la cuenta en Dataverse.
    - COMERCIAL: Correo del comercial responsable de la cita.
    Usa el siguiente formato para responder:
        -	Día y hora de la cita
        -	Nombre de cuenta, Alias group y score inicial.
            o	Contacto, cargo y teléfono
            o	Comentarios de la cita
            o	Resumen del histórico de actividad
            o	Industria FI y Ayudas presentadas
            o	Competidor, fecha del registro y en qué servicio.
            o	Noticias
            o	Argumentos y estrategia/Encaje en ayudas.
    Args:
        email: Correo electrónico del usuario en sesión.
        userType: Tipo de usuario en sesión. COMERCIAL o GESTOR.
    Returns:
        Lista de citas de la doceava semana anterior del usuario.
    """
    return SERVICE.read_by_email("CITAS 12 SEMANAS ATRAS", email=_normalize_email(email), column_name=userType)


@mcp.tool
def get_historico_citas(email: str, userType: str) -> list[dict]:
    """
    Resumen de las citas en base a las reuniones celebradas en los 3 últimos años. Por cada cita retorna:
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - ASUNTO: Asunto o título de la cita.
    - FECHA_DE_LA_CITA: Fecha y hora de inicio de la cita (ISO 8601).
    - CONTACTO_PRINCIPAL: Nombre completo del contacto principal.
    - ASISTENTES: Nombres de los asistentes a la cita.
    - COMENTARIOS: Comentarios o resultado de la cita.
    - COMERCIAL: Correo del comercial responsable de las cita.
    Usa el siguiente formato para responder:
    -	Fecha de celebración de la cita
    -	Nombre de cuenta, Alias group y score inicial.
        o	Contacto, cargo y teléfono
        o	Comentarios de la cita
    Args:
        email: Correo electrónico del usuario en sesión.
        userType: Tipo de usuario en sesión. COMERCIAL o GESTOR.
    Returns:
        Lista de registros históricos de citas del usuario.
    """
    return SERVICE.read_by_email("HISTORICO DE CITAS", email=_normalize_email(email), column_name=userType)


@mcp.tool
def get_historico_llamadas(email: str, userType: str) -> list[dict]:
    """
    Resumen de las llamadas en base a los 3 últimos años. Por cada llamada retorna:
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - REFERENTE_A: Entidad u oportunidad a la que hace referencia la llamada.
    - NÚMERO_TELÉFONO: Número de teléfono marcado.
    - ASUNTO: Asunto o motivo de la llamada.
    - FECHA_FIN_REAL: Fecha y hora de finalización real de la llamada (ISO 8601).
    - TIPO: Tipo de llamada (entrante / saliente).
    - RESULTADO: Resultado registrado de la llamada.
    - COMERCIAL: Correo del comercial responsable de la llamada.
    Args:
        email: Correo electrónico del usuario en sesión.
        userType: Tipo de usuario en sesión. COMERCIAL o GESTOR.
    Returns:
        Lista de registros históricos de llamadas del usuario.
    """
    return SERVICE.read_by_email("HISTORICO DE LLAMADAS", email=_normalize_email(email), column_name=userType)


@mcp.tool
def get_historico_opps(email: str, userType: str) -> list[dict]:
    """
    Resumen de las ofertas lanzadas, las oportunidades 'Inactivas'/'Activas' deben ser retornadas como 'Perdidas'/'En curso' respectivamente. Por cada oferta retorna:
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - SERVICIO: Tipo de servicio de la oportunidad.
    - FECHA: Fecha de creación del servicio (ISO 8601).
    - RAZÓN_DEL_ESTADO: Razón del estado actual del servicio.
    - ESTADO: Estado actual del servicio (activo / inactivo).
    - OPORTUNIDAD: Nombre de la oportunidad asociada.
    - PROBABILIDAD: Probabilidad de éxito estimada.
    - COMPETIDOR: Nombre del competidor identificado.
    - FECHA_DE_CREACIÓN_COMPETENCIA: Fecha de registro del competidor (ISO 8601).
    - ÁREA: Área de servicio FI.
    - COMERCIAL: Correo del comercial responsable de la oferta.
    Args:
        email: Correo electrónico del usuario en sesión.
        userType: Tipo de usuario en sesión. COMERCIAL o GESTOR.
    Returns:
        Lista de registros históricos de oportunidades del usuario.          
    """
    return SERVICE.read_by_email("HISTORICO DE OPPS", email=_normalize_email(email), column_name=userType)


@mcp.tool
def get_llamadas_abiertas(email: str, userType: str) -> list[dict]:
    """
    Llamadas abiertas o no realizadas aún cuyo propietario sea el usuario. Por cada llamada retorna:
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - SCORE_INICIAL: Puntuación inicial de la cuenta.
    - GROUP_ALIAS: Alias del grupo comercial asignado.
    - ÚLTIMO_CONTACTO: Fecha del último contacto registrado (ISO 8601).
    - INDUSTRIA_FI: Industria FI asignada a la cuenta.
    - DESCRIPCIÓN: Descripción o notas de la llamada.
    - COMERCIAL: Correo del comercial responsable de la llamada.
    Args:
        email: Correo electrónico del usuario en sesión.
        userType: Tipo de usuario en sesión. COMERCIAL o GESTOR.
    Returns:
        Lista de registros de llamadas abiertas del usuario.          
    """
    return SERVICE.read_by_email("LLAMADAS ABIERTAS", email=_normalize_email(email), column_name=userType)


@mcp.tool
def get_leads_abiertos(email: str, userType: str) -> list[dict]:
    """
    Leads abiertos cuyo propietario sea el usuario. Por cada lead retorna:
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - SCORE_INICIAL: Puntuación inicial de la cuenta.
    - GROUP_ALIAS: Alias del grupo comercial asignado.
    - ÚLTIMO_CONTACTO: Fecha del último contacto registrado (ISO 8601).
    - INDUSTRIA_FI: Industria FI asignada a la cuenta.
    - SOURCE_CHANNEL: Canal de origen del lead.
    - CAMPAÑA_DE_ORIGEN: Nombre de la campaña que originó el lead.
    - COMENTARIOS_DE_LEAD: Comentarios internos sobre el lead.
    - CREADO: Fecha de creación del lead (ISO 8601).
    - COMERCIAL: Correo del comercial responsable del lead.
    Usa el siguiente formato para responder:
    -	Nombre de cuenta, Alias group y score inicial.
        o	Contacto principal, cargo y teléfono
        o	Resumen del histórico de actividad de CRM
        o	Industria FI – Top sectorial
        o	Fecha de último contacto
        o	Source Channel
        o	Campaña de origen
        o	Comentarios del lead
    Args:
        email: Correo electrónico del usuario en sesión.
        userType: Tipo de usuario en sesión. COMERCIAL o GESTOR.
    Returns:
        Lista de registros de leads abiertos del usuario.      
    """
    return SERVICE.read_by_email("LEADS ABIERTOS", email=_normalize_email(email), column_name=userType)


@mcp.tool
def get_oportunidades_abiertas(email: str, userType: str) -> list[dict]:
    """
    Servicios de oportunidad abiertos cuyo propietario sea el usuario. Por cada servicio retorna:
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - TIPO_DE_SERVICIO: Tipo de servicio de la oportunidad.
    - ÁREA_DE_SERVICIO: Área de servicio FI.
    - TIPO_DE_CONTRATO: Modalidad de contrato (fijo, porcentaje, etc.).
    - PREVISIÓN_DE_HONORARIOS: Honorarios previstos para FI.
    - FECHA_DE_CREACIÓN: Fecha de creación de la oportunidad (ISO 8601).
    - PROBABILIDAD: Probabilidad de éxito estimada.
    - SECTOR_FI: Sector FI asignado a la cuenta.
    - COMERCIAL: Correo del comercial responsable del servicio.
    Usa el siguiente formato de respuesta:
    -	Nombre de cuenta y fecha de creación de la oferta y probabilidad.
        o	Tipo de servicio y área del servicio
        o	Tipo de contrato y previsión de honorarios
    Args:
        email: Correo electrónico del usuario en sesión.
        userType: Tipo de usuario en sesión. COMERCIAL o GESTOR.
    Returns:
        Lista de servicios de oportunidades abiertas del usuario.
    """
    return SERVICE.read_by_email("OPORTUNIDADES ABIERTAS", email=_normalize_email(email), column_name=userType)


@mcp.tool
def get_ofertas_pendientes(email: str, userType: str) -> list[dict]:
    """
    Reuniones completadas con resultado “interés en el futuro”. Por cada reunión retorna:
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - FECHA_DE_ÚLTIMA_REUNIÓN: Fecha de la última reunión (ISO 8601).
    - COMENTARIOS: Comentarios o resultado de la última cita.
    - CONTACTO_PRINCIPAL: Nombre completo del contacto principal.
    - COMERCIAL: Correo del comercial responsable de la oferta.
    Usa el siguiente formato de respuesta:
    -	Nombre de cuenta
        o	Contacto principal, cargo y teléfono de última reunión.
        o	Fecha de última reunión
        o	Comentarios de última reunión
    Args:
        email: Correo electrónico del usuario en sesión.
        userType: Tipo de usuario en sesión. COMERCIAL o GESTOR.
    Returns:
        Lista de registros de ofertas pendientes del usuario.          
    """
    return SERVICE.read_by_email("OFERTAS PENDIENTES", email=_normalize_email(email), column_name=userType)


@mcp.tool
def get_convocatorias_abiertas(sector_grants: str) -> list[dict]:
    """
    Devuelve las convocatorias de subvenciones abiertas para el sector indicado. Los sectores están en ingles, así que haz la respectiva traducción. Puedes usar el diccionario de sectores para saber a que sector se hace referencia. Por cada convocatoria retorna:
    - SECTOR: Sector al que aplica la convocatoria.
    - TÍTULO: Título o nombre de la convocatoria de subvención.
    Args:
        sector_grants: Valor del sector en formato GRANTS (columna SECTOR_GRANTS de CITAS SEMANALES).

    Returns:
        Lista de convocatorias abiertas que coinciden con el sector.
    """
    return SERVICE.read_by_sector(sector_grants)


@mcp.tool
def get_subvenciones_bdns(nif: str) -> list[dict]:
    """
    Ayudas o subvenciones percibidas los 3 últimos años según el NIF de la cuenta. Por cada Ayuda retorna:
    - NIF: NIF fiscal del beneficiario.
    - BENEFICIARIO: Nombre del beneficiario de la subvención.
    - ORGANISMO: Organismo público concedente.
    - FONDOS_A_PRESTAMO: Importe concedido en forma de préstamo.
    - FONDOS_A_SUBVENCIÓN: Importe concedido en forma de subvención directa.
    Args:
        nif: NIF de la cuenta (columna NIF de CITAS SEMANALES).
    Returns:
        Lista de registros BDNS correspondientes al NIF.
    """
    return SERVICE.read_by_nif(nif)


@mcp.tool
def get_resumen_noticias(nombre_cuenta: str) -> list[dict]:
    """
    Noticias de actualidad de las compañías con las que el comercial se va a reunir esa semana. Por cada noticia retorna:
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - Título: Titular de la noticia.
    - Fuente: Medio o fuente de la noticia.
    - Fecha: Fecha de publicación de la noticia.
    - URL: Enlace a la noticia original.
    - Contenido: Texto extraído del artículo.
    - Resumen: Resumen generado por el LLM a partir del contenido.

    Args:
        nombre_cuenta: Nombre de la cuenta (columna NOMBRE_DE_LA_CUENTA de CITAS SEMANALES).

    Returns:
        Lista de registros de noticias resumidas correspondientes a la cuenta.
    """
    return SERVICE.read_by_cuenta(nombre_cuenta)


@mcp.tool
def get_cuentas_sin_llamar(nombre_usuario: str) -> list[dict]:
    """
    Devuelve el resumen de las cuentas sin llamar en el año en curso provenientes del plan estrategico para el usuario. Por cada cuenta retorna:
    - NÚMERO_DE_CUENTA: Número identificador de la cuenta en CRM.
    - NIF: NIF fiscal de la cuenta.
    - NOMBRE_DE_LA_CUENTA: Nombre de la empresa o cuenta.
    - SCORE_INICIAL: Puntuación inicial de la cuenta.
    - GROUP_ALIAS: Alias del grupo comercial asignado.
    - Gasto anual I+D+i: Gasto Anual en I+D+i.
    - TELEFONO_CONTACTO: Teléfono del contacto principal.
    - INDUSTRIA_FI: Industria FI asignada a la cuenta.
    - SECTOR_FI: Sector FI asignado a la cuenta.
    - SECTOR_GRANTS: Sector usado para buscar convocatorias/ayudas/subvenciones.
    - FECHA DE ÚLTIMO CONTACTO: Fecha de último contacto con la cuenta.
    - COMERCIAL: Correo del comercial responsable de la cuenta.
    Usa el siguiente formato para responder:
    -	Nombre de cuenta, Alias group y score inicial.
        o	Contacto, cargo y teléfono
        o	Resumen del histórico de actividad de CRM
        o	Industria FI + TOP Sectorial
        o	Noticias
        o	Argumentos y estrategia/Encaje en ayudas 

    Args:
        nombre_usuario: Nombre del usuario en sesion.
    Returns:
        Lista de registros de cuentas sin llamar.          
    """
    return SERVICE.read_by_cuenta_without_calls(nombre_usuario)


@mcp.tool
def get_citas_semanales_realtime() -> list[dict]:
    """Consulta en tiempo real las citas de la semana en curso."""
    return REALTIME_SERVICE.get_citas_semana_en_curso()


@mcp.tool
def get_citas_por_comercial_semana_en_curso_realtime(email: str) -> list[dict]:
    """Consulta en tiempo real las citas de semana en curso por comercial."""
    return REALTIME_SERVICE.get_citas_por_comercial_semana_en_curso(_normalize_email(email))


@mcp.tool
def get_citas_por_gestor_semana_en_curso_realtime(email: str) -> list[dict]:
    """Consulta en tiempo real las citas de semana en curso por gestor."""
    return REALTIME_SERVICE.get_citas_por_gestor_semana_en_curso(_normalize_email(email))


@mcp.tool
def get_citas_por_comercial_realtime(email: str) -> list[dict]:
    """Consulta en tiempo real las citas por comercial."""
    return REALTIME_SERVICE.get_citas_por_comercial(_normalize_email(email))


@mcp.tool
def get_citas_por_gestor_realtime(email: str) -> list[dict]:
    """Consulta en tiempo real las citas por gestor."""
    return REALTIME_SERVICE.get_citas_por_gestor(_normalize_email(email))


@mcp.tool
def get_citas_por_cuenta_realtime(nombre_cuenta: str) -> list[dict]:
    """Consulta en tiempo real las citas por nombre de cuenta."""
    return REALTIME_SERVICE.get_citas_por_cuenta(nombre_cuenta)


@mcp.tool
def get_llamadas_semanales_realtime() -> list[dict]:
    """Consulta en tiempo real las llamadas de la semana en curso."""
    return REALTIME_SERVICE.get_llamadas_semana_en_curso()


@mcp.tool
def get_llamadas_por_comercial_semana_en_curso_realtime(email: str) -> list[dict]:
    """Consulta en tiempo real las llamadas de semana en curso por comercial."""
    return REALTIME_SERVICE.get_llamadas_por_comercial_semana_en_curso(_normalize_email(email))


@mcp.tool
def get_llamadas_por_gestor_semana_en_curso_realtime(email: str) -> list[dict]:
    """Consulta en tiempo real las llamadas de semana en curso por gestor."""
    return REALTIME_SERVICE.get_llamadas_por_gestor_semana_en_curso(_normalize_email(email))


@mcp.tool
def get_llamadas_por_comercial_realtime(email: str) -> list[dict]:
    """Consulta en tiempo real las llamadas por comercial."""
    return REALTIME_SERVICE.get_llamadas_por_comercial(_normalize_email(email))


@mcp.tool
def get_llamadas_por_gestor_realtime(email: str) -> list[dict]:
    """Consulta en tiempo real las llamadas por gestor."""
    return REALTIME_SERVICE.get_llamadas_por_gestor(_normalize_email(email))


@mcp.tool
def get_llamadas_por_cuenta_realtime(nombre_cuenta: str) -> list[dict]:
    """Consulta en tiempo real las llamadas por nombre de cuenta."""
    return REALTIME_SERVICE.get_llamadas_por_cuenta(nombre_cuenta)


@mcp.tool
def get_xml_queries_realtime() -> list[str]:
    """Devuelve el listado de query keys XML disponibles para ejecución realtime."""
    return sorted(REALTIME_SERVICE.catalog.keys())


@mcp.tool
def run_xml_query_realtime(
    query_key: str,
    email: str | None = None,
    nombre_cuenta: str | None = None,
) -> list[dict]:
    """Ejecuta una query XML realtime por clave con parámetros opcionales."""
    params: dict[str, str] = {}
    if email:
        params["email"] = _normalize_email(email)
    if nombre_cuenta:
        params["nombre_cuenta"] = nombre_cuenta
    return REALTIME_SERVICE.execute_query(query_key, **params)

# ── App con middleware opcional ───────────────────────────────────────────────

middleware = []
if settings.auth_enabled:
    middleware.append(
        Middleware(
            BearerTokenMiddleware,
            bearer_token=settings.bearer_token,
            protected_prefixes=(settings.mcp_path,),
        )
    )

app = mcp.http_app(
    path=settings.mcp_path,
    transport=settings.transport,
    middleware=middleware,
    json_response=True,
    stateless_http=True,
)