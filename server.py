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
from scripts.realtime_query_service import DataverseRealtimeService, SQLRealtimeService, PlanCuentasService
from scripts.clients.news_client import fetch_news_for_account

from scripts.utils import get_current_date, get_week_range

from scripts.config.dictionary import SECTORES


settings = load_settings()

_EXCEL_PATH = (
    Path(settings.excel_path)
    if settings.excel_path
    else Path(__file__).resolve().parent / "output" / "citas.xlsx"
)

SERVICE = ExcelService(_EXCEL_PATH)
REALTIME_SERVICE = DataverseRealtimeService(Path(__file__).resolve().parent / "py_queries")
SQL_SERVICE = SQLRealtimeService()
PLAN_CUENTAS_SERVICE = PlanCuentasService()

# --- Extracción asíncrona ---
TASK_LOGS_DIR = Path("logs/tasks")
TASK_LOGS_DIR.mkdir(parents=True, exist_ok=True)
tasks = {}
# ── Rutas HTTP personalizadas ─────────────────────────────────────────────────


mcp = FastMCP(name=settings.app_name, version=settings.server_version)

# --- Endpoint: Lanzar extracción en background ---
logger = logging.getLogger(settings.app_name)


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
            "get_ofertas_pendientes",
            "get_convocatorias_abiertas",
            "get_subvenciones_bdns",
            "get_resumen_noticias",
            "get_cuentas_sin_llamar",
            "get_cuentas_pendientes_de_llamar",
            "get_citas_semanales_realtime",
            "get_citas_12va_semana_atras_realtime",
            "get_citas_por_comercial_semana_en_curso_realtime",
            "get_citas_por_comercial_12va_semana_atras_realtime",
            "get_citas_por_gestor_semana_en_curso_realtime",
            "get_citas_por_gestor_12va_semana_atras_realtime",
            "get_citas_por_comercial_realtime",
            "get_citas_por_gestor_realtime",
            "get_citas_por_cuenta_realtime",
            "get_llamadas_semanales_realtime",
            "get_llamadas_por_comercial_semana_en_curso_realtime",
            "get_llamadas_por_gestor_semana_en_curso_realtime",
            "get_llamadas_por_comercial_realtime",
            "get_llamadas_por_gestor_realtime",
            "get_llamadas_por_cuenta_realtime",            
            "get_servicios_de_oportunidad_por_comercial_realtime",            
            "get_servicios_de_oportunidad_por_gestor_realtime",
            "get_servicios_de_oportunidad_por_cuenta_realtime",            
            "get_llamadas_abiertas_realtime",            
            "get_llamadas_abiertas_por_cuenta_realtime",            
            "get_llamadas_abiertas_por_comercial_realtime",            
            "get_llamadas_abiertas_por_gestor_realtime",            
            "get_leads_abiertos_por_comercial_realtime",            
            "get_leads_abiertos_por_gestor_realtime",            
            "get_leads_abiertos_por_cuenta_realtime",  
            "get_servicios_de_oportunidad_abierta_por_comercial_realtime",
            "get_servicios_de_oportunidad_abierta_por_gestor_realtime",
            "get_servicios_de_oportunidad_abierta_por_cuenta_realtime",
            "get_get_citas_con_interes_futuro_por_comercial",
            "get_get_citas_con_interes_futuro_por_gestor",
            "get_get_citas_con_interes_futuro_por_cuenta",          
            "get_ayudas_percibidas_bdns",
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
    
@mcp.tool
def obtener_diccionario() -> str:
    """Devuelve el diccionario de sectores FI y sectores GRANTS."""
    return SECTORES


@mcp.tool(
    description="""
    Devuelve las convocatorias de subvenciones abiertas para el sector indicado.

    ⚠️ IMPORTANTE — NORMALIZACIÓN DEL SECTOR (obligatoria antes de llamar al método):

    1. El parámetro `sector_grants` recibido del usuario PUEDE estar en inglés, español o cualquier idioma,
       y puede ser una descripción coloquial, abreviada o no reconocida exactamente.

    2. Para normalizar el sector, DEBES realizar los siguientes pasos:

       a) Obtén el diccionario de sectores invocando el recurso: resource://obtener-diccionario
          Este diccionario tiene dos columnas: CRM (nombre original del sector) y GRANTS (nombre normalizado).

       b) Busca un MATCH EXACTO comparando el input contra la columna CRM:
          - Si encuentra match → usa el valor correspondiente de la columna GRANTS como parámetro final.

       c) Si NO hay match exacto, busca el nombre CRM MÁS SEMEJANTE/ASEMEJADO al input del usuario:
          - Considera similitud textual, traducciones aproximadas, variaciones de mayúsculas/minúsculas,
            caracteres especiales, o nombres alternativos del mismo sector.
          - Usa el valor GRANTS asociado al CRM más parecido.

       d) Como fallback FINAL, si no hay semejanza clara posible → usa el valor `sector_grants` tal cual llegó.

    3. Con el sector NORMALIZADO resultante, ejecuta la consulta SQL de convocatorias abiertas.

Por cada convocatoria retorna:
- SECTOR: Sector al que aplica la convocatoria.
- TÍTULO: Título o nombre de la convocatoria de subvención.

Args:
    sector_grants: Nombre del sector ingresado por el usuario (puede estar en inglés, español,
                   abreviado, o no reconocido). Ejemplos válidos: "Aeroespacial", "aerospace",
                   "Aeronautical - Space", "Espacio", "Energy", etc.

Returns:
    Lista de convocatorias abiertas que coinciden con el sector normalizado.

Use este recurso cuando el usuario/comercial/gestor de cuenta quiera consultar las convocatorias
en las que una cuenta puede encajar según su sector. SIEMPRE normaliza el sector mediante el
diccionario antes de ejecutar la consulta.
"""
)
def get_convocatorias_abiertas(sector_grants: str) -> list[dict]:
    return SQL_SERVICE.get_convocatorias_abiertas(sector_grants)


@mcp.tool(
    description="""
    Busca noticias en internet acerca de una cuenta específica. 

    Argumentos de entrada:
    - nombre_cuenta (string): Nombre de cuenta en el CRM.

    Consulta en internet noticias asociadas a la cuenta mencionada. Extrae eltTítulo, la fuente, Fecha de publicación, URL de la noticia, y su contenido.

    Utiliza este recurso cuando el usuario/comercial/gestor de cuenta  pregunte por artículos, noticias o información relevante que le ayude a preparar su estrategía comercial.
    """ 
)
def get_resumen_noticias(nombre_cuenta: str) -> list[dict]:
    return fetch_news_for_account(account_name=nombre_cuenta)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las cuentas llamadas en el año en curso. Por cada cuenta retorna:
    - NÚMERO_DE_CUENTA: Número identificador de la cuenta en CRM.   
    - NOMBRE DE CUENTA: Nombre de la cuenta en CRM.        
    """
)
def get_cuentas_llamadas_ano_en_curso() -> list[dict]:
    return REALTIME_SERVICE.get_cuentas_llamadas_ano_en_curso()


@mcp.tool(
    description="""
    Obtiene el listado completo de cuentas asignadas a un gestor de cuenta específico
    según el plan de cuentas oficial.

    Argumentos de entrada:
    - nombre_usuario (string): Correo electrónico o nombre del gestor de cuenta a filtrar.

    Por cada cuenta retorna:
    - Datos de la cuenta (Nº, nombre, sector, etc.).
    - Gestor de Cuenta asignado.
    - Comercial asignado.

    Utiliza este recurso cuando el usuario necesite consultar su cartera oficial de cuentas
    asignadas según el plan de cuentas.
    """
)
def get_cuentas_por_gestor_plan_cuentas(nombre_usuario: str) -> list[dict]:
    return PLAN_CUENTAS_SERVICE.get_cuentas_por_gestor(nombre_usuario)


@mcp.tool(
    description="""
    Herramienta que compara las cuentas asignadas a un gestor basandose en su nombre según el plan de cuentas oficial
    con las cuentas que ya han sido llamadas en el año actual, y retorna únicamente
    las cuentas **pendientes de llamar**.

    Argumentos de entrada:
    - nombre_gestor (string, requerido): Nombre del gestor de cuenta cuyo listado 
      de cuentas pendientes se desea obtener.

    Información retornada por cada cuenta pendiente:
    - NIF
    - Número de cuenta
    - Nombre de la cuenta
    - Group Alias
    - Sector FI
    - Gasto anual I+D+i
    - Gestor de Cuenta asignado

    Instrucciones de uso:
    - Invoca esta herramienta inmediatamente cuando el usuario/gestor/comercial necesite identificar
      qué cuentas de su cartera aún no ha llamado este año.
    - Requiere obligatoriamente el nombre del gestor. Si no está presente en 
      el contexto o en el prompt inicial, preguntalo.

    Ejemplo de trigger: "¿Qué cuentas me faltan por llamar este año?"
    """
)
def get_cuentas_pendientes_de_llamar(nombre_gestor: str) -> list[dict]:
    """
    Busca las cuentas asignadas a un gestor basandose en su nombtre y retorna las cuentas asignadas que aún no han sido llamadas este año.
    Compara el plan de cuentas oficial contra las llamadas registradas en el año en curso.
    """
    if not nombre_gestor or not nombre_gestor.strip():
        raise ValueError("El parámetro 'gestor' es obligatorio.")
    
    return PLAN_CUENTAS_SERVICE.get_cuentas_pendientes_de_llamar(
        gestor=nombre_gestor.strip(),
        dataverse_service=REALTIME_SERVICE
    )


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las reuniones comerciales abiertas o programadas para la semana en curso de un usuario/comercial específico. 

    Argumentos de entrada:
    - email (string): Correo del comercial en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada cita:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la cita actual.
    5. Historial: Resumen acumulado de la actividad previa en el CRM.
    6. Contexto Técnico: Industria FI y el catálogo de Ayudas ya presentadas.
    7. Competencia: Competidor detectado, fecha de registro y servicio asociado.
    8. Actualidad: Noticias relevantes de la cuenta.
    9. Preparación: Argumentos de venta y la estrategia/encaje específico en ayudas para la reunión.

    Utiliza este recurso cuando el usuario/comercial pregunte por la agenda, el calendario, las reuniones semanales o necesite preparar los antecedentes y la estrategia de sus visitas de la semana actual.
    """    
)
def get_citas_por_comercial_semana_en_curso_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_citas_por_comercial_semana_en_curso(email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las reuniones comerciales abiertas o programadas para la decimo segunda semana anterior a la semana en curso de un usuario/comercial específico. 

    Argumentos de entrada:
    - email (string): Correo del comercial en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada cita:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la cita actual.
    5. Historial: Resumen acumulado de la actividad previa en el CRM.
    6. Contexto Técnico: Industria FI y el catálogo de Ayudas ya presentadas.
    7. Competencia: Competidor detectado, fecha de registro y servicio asociado.
    8. Actualidad: Noticias relevantes de la cuenta.
    9. Preparación: Argumentos de venta y la estrategia/encaje específico en ayudas para la reunión.

    Utiliza este recurso cuando el usuario/comercial pregunte por la agenda, el calendario, las reuniones de la docimo segunda semana anterior a la semana en curso o necesite recordar los antecedentes y la estrategia de sus visitas de la doceava semana anterior.
    """    
)
def get_citas_por_comercial_12va_semana_atras_realtime(email: str) -> list[dict]:
    start_week, end_week = get_week_range(12)
    return REALTIME_SERVICE.get_citas_por_comercial_12va_semana_atras(str(start_week)+"T00:00:00Z", str(end_week)+"T23:59:59Z", email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las reuniones comerciales abiertas o programadas para la semana en curso de un usuario/gestor de cuenta específico. 

    Argumentos de entrada:
    - email (string): Correo del gestor en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada cita:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la cita actual.
    5. Historial: Resumen acumulado de la actividad previa en el CRM.
    6. Contexto Técnico: Industria FI y el catálogo de Ayudas ya presentadas.
    7. Competencia: Competidor detectado, fecha de registro y servicio asociado.
    8. Actualidad: Noticias relevantes de la cuenta.
    9. Preparación: Argumentos de venta y la estrategia/encaje específico en ayudas para la reunión.

    Utiliza este recurso cuando el usuario/gestor de cuenta pregunte por la agenda, el calendario, las reuniones semanales o necesite preparar los antecedentes y la estrategia de sus cuentas de la semana actual.
    """    
)
def get_citas_por_gestor_semana_en_curso_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_citas_por_gestor_semana_en_curso(email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las reuniones comerciales abiertas o programadas para la decimo segunda semana anterior a la semana en curso de un usuario/gestor de cuenta específico. 

    Argumentos de entrada:
    - email (string): Correo del gestor en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada cita:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la cita actual.

    Utiliza este recurso cuando el usuario/gestor de cuenta pregunte por la agenda, el calendario, las reuniones semanales o necesite preparar los antecedentes y la estrategia de sus cuentas de la doceava semana anterior.
    """    
)
def get_citas_por_gestor_12va_semana_atras_realtime(email: str) -> list[dict]:
    start_week, end_week = get_week_range(12)
    return REALTIME_SERVICE.get_citas_por_gestor_12va_semana_atras(str(start_week)+"T00:00:00Z", str(end_week)+"T23:59:59Z", email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las reuniones comerciales abiertas o programadas de un usuario/comercial específico.

    Argumentos de entrada:
    - email (string): Correo del comercial en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada cita:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la cita actual.

    Utiliza este recurso cuando el usuario/comercial pregunte por la agenda, el calendario, las reuniones o necesite preparar los antecedentes y la estrategia de sus visitas.
    """    
)
def get_citas_por_comercial_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_citas_por_comercial(email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las reuniones comerciales abiertas o programadas de un usuario/gestor de cuenta específico. 

    Argumentos de entrada:
    - email (string): Correo del gestor en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada cita:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la cita actual.

    Utiliza este recurso cuando el usuario/gestor de cuenta pregunte por la agenda, el calendario, las reuniones semanales o necesite preparar los antecedentes y la estrategia de sus cuentas.
    """    
)
def get_citas_por_gestor_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_citas_por_gestor(email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las reuniones comerciales abiertas o programadas de una cuenta específica. 

    Argumentos de entrada:
    - nombre_cuenta (string): Nombre de la cuenta en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada cita:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la cita actual.

    Utiliza este recurso cuando el usuario/comercial/gestor de cuenta pregunte por la agenda, el calendario, las reuniones o necesite preparar los antecedentes y la estrategia para la cuenta.
    """    
)
def get_citas_por_cuenta_realtime(nombre_cuenta: str) -> list[dict]:
    return REALTIME_SERVICE.get_citas_por_cuenta(nombre_cuenta)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las llamadas comerciales abiertas o programadas para la semana en curso de un usuario/comercial específico. 

    Argumentos de entrada:
    - email (string): Correo del comercial en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada llamada:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la llamada actual.
    5. Historial: Resumen acumulado de la actividad previa en el CRM.
    6. Contexto Técnico: Industria FI y el catálogo de Ayudas ya presentadas.
    7. Actualidad: Noticias relevantes de la cuenta.
    8. Preparación: Argumentos de venta y la estrategia/encaje específico en ayudas para la reunión.

    Utiliza este recurso cuando el usuario/comercial pregunte por la agenda, el calendario, las llamadas semanales o necesite preparar los antecedentes y la estrategia de sus llamadas de la semana actual.
    """    
)
def get_llamadas_por_comercial_semana_en_curso_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_llamadas_por_comercial_semana_en_curso(email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las llamadas comerciales abiertas o programadas para la semana en curso de un usuario/gestor de cuenta específico. 

    Argumentos de entrada:
    - email (string): Correo del gestor en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada llamada:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la llamada actual.
    5. Historial: Resumen acumulado de la actividad previa en el CRM.
    6. Contexto Técnico: Industria FI y el catálogo de Ayudas ya presentadas.
    7. Actualidad: Noticias relevantes de la cuenta.
    8. Preparación: Argumentos de venta y la estrategia/encaje específico en ayudas para la reunión.

    Utiliza este recurso cuando el usuario/gestor de cuenta pregunte por la agenda, el calendario, las llamadas semanales o necesite preparar los antecedentes y la estrategia de sus cuentas de la semana actual.
    """    
)
def get_llamadas_por_gestor_semana_en_curso_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_llamadas_por_gestor_semana_en_curso(email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las llamadas comerciales abiertas o programadas de un usuario/comercial específico.

    Argumentos de entrada:
    - email (string): Correo del comercial en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada llamada:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la llamada actual.

    Utiliza este recurso cuando el usuario/comercial pregunte por la agenda, el calendario, las llamadas o necesite preparar los antecedentes y la estrategia de sus llamadas.
    """    
)
def get_llamadas_por_comercial_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_llamadas_por_comercial(email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las llamadas comerciales abiertas o programadas de un usuario/gestor de cuenta específico. 

    Argumentos de entrada:
    - email (string): Correo del gestor en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada llamada:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la llamada actual.

    Utiliza este recurso cuando el usuario/gestor de cuenta pregunte por la agenda, el calendario, las llamadas semanales o necesite preparar los antecedentes y la estrategia de sus cuentas.
    """    
)
def get_llamadas_por_gestor_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_llamadas_por_gestor(email)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las llamadas comerciales abiertas o programadas de una cuenta específica. 

    Argumentos de entrada:
    - nombre_cuenta (string): Nombre de la cuenta en el CRM.

    Este recurso consulta el CRM y extrae cronológicamente los siguientes datos clave para cada cita:
    1. Sincronización: Día y hora exacta de inicio de la celebración.
    2. Cliente: Nombre de la cuenta, Alias Group y su Score Inicial de negocio.
    3. Interlocutor: Nombre del contacto, cargo y teléfono directo.
    4. Notas: Comentarios específicos registrados para la llamada actual.

    Utiliza este recurso cuando el usuario/comercial/gestor de cuenta pregunte por la agenda, el calendario, las llamadas o necesite preparar los antecedentes y la estrategia para la cuenta.
    """    
)
def get_llamadas_por_cuenta_realtime(nombre_cuenta: str) -> list[dict]:
    return REALTIME_SERVICE.get_llamadas_por_cuenta(nombre_cuenta)


@mcp.tool(
    description= """
    Obtiene el listado completo de los servicios de oportunidad ofrecidos por un asesor comercial específico a partir de su correo electrónico.

    Argumentos de entrada:
    - email (string, requerido): Dirección de correo electrónico institucional del asesor comercial registrado en el CRM.

    Información que retorna la herramienta (Estructura de datos):
    Para cada servicio de oportunidad, la herramienta devuelve un objeto estructurado en tres niveles:
    1. Datos de la Oferta y Cuenta:
    - Nombre de cuenta: Razón social o nombre de la empresa cliente vinculada.
    - Fecha de creación de la oferta: Fecha en la que se registró la propuesta comercial en el CRM.
    - Probabilidad: Porcentaje o nivel estimado de éxito comercial para ganar este servicio.
    2. Clasificación del Negocio:
    - Tipo de servicio: Categoría o modalidad específica del servicio ofertado.
    - Área del servicio: División, sector o departamento de negocio asignado.
    3. Condiciones Financieras:
    - Tipo de contrato: Formato legal o modelo contractual propuesto para el servicio.
    - Previsión de honorarios: Estimación económica o ingresos proyectados para este negocio.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/comercial pregunte por sus servicios ofertados, propuestas en curso y probabilidades de sus oportunidades activas.
    - Requiere obligatoriamente el correo electrónico del comercial. Si no está presente en el contexto o en el prompt inicial, solicítalo amablemente al usuario antes de ejecutar la herramienta.
    """    
)
def get_servicios_de_oportunidad_por_comercial_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_servicios_de_oportunidad_por_comercial(email)


@mcp.tool(
    description= """
    Obtiene el listado completo de los servicios de oportunidad gestionados por un gestor de cuenta específico a partir de su correo electrónico.

    Argumentos de entrada:
    - email (string, requerido): Dirección de correo electrónico institucional del gestor de cuenta registrado en el CRM.

    Información que retorna la herramienta (Estructura de datos):
    Para cada servicio de oportunidad, la herramienta devuelve un objeto estructurado en tres niveles:
    1. Datos de la Oferta y Cuenta:
    - Nombre de cuenta: Razón social o nombre de la empresa cliente vinculada.
    - Fecha de creación de la oferta: Fecha en la que se registró la propuesta comercial en el CRM.
    - Probabilidad: Porcentaje o nivel estimado de éxito comercial para ganar este servicio.
    2. Clasificación del Negocio:
    - Tipo de servicio: Categoría o modalidad específica del servicio ofertado.
    - Área del servicio: División, sector o departamento de negocio asignado.
    3. Condiciones Financieras:
    - Tipo de contrato: Formato legal o modelo contractual propuesto para el servicio.
    - Previsión de honorarios: Estimación económica o ingresos proyectados para este negocio.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/gestor pregunte por los servicios ofertados, propuestas en curso y probabilidades de las oportunidades de sus cuentas activas.
    - Requiere obligatoriamente el correo electrónico del gestor. Si no está presente en el contexto o en el prompt inicial, solicítalo amablemente al usuario antes de ejecutar la herramienta.
    """  
)
def get_servicios_de_oportunidad_por_gestor_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_servicios_de_oportunidad_por_gestor(email)


@mcp.tool(
    description= """
    Obtiene el listado completo de los servicios de oportunidad ofrecidos a una cuenta especifica.

    Argumentos de entrada:
    - nombre_cuenta (string, requerido): Nombre de la cuenta registrado en el CRM.

    Información que retorna la herramienta (Estructura de datos):
    Para cada servicio de oportunidad, la herramienta devuelve un objeto estructurado en tres niveles:
    1. Datos de la Oferta y Cuenta:
    - Nombre de cuenta: Razón social o nombre de la empresa cliente vinculada.
    - Fecha de creación de la oferta: Fecha en la que se registró la propuesta comercial en el CRM.
    - Probabilidad: Porcentaje o nivel estimado de éxito comercial para ganar este servicio.
    2. Clasificación del Negocio:
    - Tipo de servicio: Categoría o modalidad específica del servicio ofertado.
    - Área del servicio: División, sector o departamento de negocio asignado.
    3. Condiciones Financieras:
    - Tipo de contrato: Formato legal o modelo contractual propuesto para el servicio.
    - Previsión de honorarios: Estimación económica o ingresos proyectados para este negocio.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/comercial/gestor pregunte por los servicios ofertados, propuestas en curso y probabilidades de las oportunidades de una cuenta especifica.
    - Requiere obligatoriamente el nombre de la cuenta a consultar. Si no está presente en el contexto o en el prompt inicial, solicítalo amablemente al usuario antes de ejecutar la herramienta.
    """  
)
def get_servicios_de_oportunidad_por_cuenta_realtime(nombre_cuenta: str) -> list[dict]:
    return REALTIME_SERVICE.get_servicios_de_oportunidad_por_cuenta(nombre_cuenta)


@mcp.tool(
    description="""
    Obtiene el listado completo de las llamadas abiertas registradas en CRM.
    """
)
def get_llamadas_abiertas_realtime() -> list[dict]:
    current_date = get_current_date()
    return REALTIME_SERVICE.get_llamadas_abiertas(current_date)


@mcp.tool(
    description= """
    Obtiene el listado completo de las llamadas abiertas registradas para una cuenta especifica en CRM.

    Argumentos de entrada:
    - nombre_cuenta (string, requerido): Nombre de la cuenta para filtrar los resultados.

    Información que retorna la herramienta (Estructura de datos):
    Para cada llamada abierta, la herramienta devuelve un objeto estructurado en tres niveles con las siguientes propiedades:
    1. Datos de la Cuenta y Priorización:
    - Nombre de la cuenta (NOMBRE_DE_LA_CUENTA): Razón social o nombre de la empresa cliente vinculada.
    - Score inicial (SCORE_INICIAL): Puntuación o calificación inicial asignada a la cuenta en el CRM.
    - Grupo (GROUP_ALIAS): Alias o nombre del grupo empresarial al que pertenece la cuenta.
    2. Estado de la Relación y Contexto:
    - Último contacto (ÚLTIMO_CONTACTO): Fecha de la última interacción o comunicación registrada con la cuenta.
    - Industria FI (INDUSTRIA_FI): Sector industrial o categoría financiera de la cuenta.
    - Descripción (DESCRIPCIÓN): Detalle, notas o contexto específico sobre el estado de la llamada abierta.
    3. Asignación del Equipo:
    - Comercial (COMERCIAL): Nombre de dominio del usuario comercial encargado de la cuenta.
    - Gestor (GESTOR): Nombre de dominio del usuario gestor responsable del seguimiento.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/comercial/gestor pregunte por llamadas pendientes, actividades abiertas, interacciones pendientes de una cuenta en especifico.
    - Si el usuario solicita el reporte general de llamadas abiertas sin especificar una cuenta, ejecuta la herramienta de inmediato para traer el listado completo. Si menciona un nombre ambiguo, solicita amablemente la aclaración del nombre de cuenta antes de realizar la consulta.
    """    
)
def get_llamadas_abiertas_por_cuenta_realtime(nombre_cuenta: str) -> list[dict]:
    current_date = get_current_date()
    return REALTIME_SERVICE.get_llamadas_abiertas_por_cuenta(nombre_cuenta, current_date)


@mcp.tool(
    description= """
    Obtiene el listado completo de las llamadas abiertas registradas para un usuario comercial en el CRM.

    Argumentos de entrada:
    - email (string, requerido): Email del comercial asignado para filtrar los resultados.

    Información que retorna la herramienta (Estructura de datos):
    Para cada llamada abierta, la herramienta devuelve un objeto estructurado en tres niveles con las siguientes propiedades:
    1. Datos de la Cuenta y Priorización:
    - Nombre de la cuenta (NOMBRE_DE_LA_CUENTA): Razón social o nombre de la empresa cliente vinculada.
    - Score inicial (SCORE_INICIAL): Puntuación o calificación inicial asignada a la cuenta en el CRM.
    - Grupo (GROUP_ALIAS): Alias o nombre del grupo empresarial al que pertenece la cuenta.
    2. Estado de la Relación y Contexto:
    - Último contacto (ÚLTIMO_CONTACTO): Fecha de la última interacción o comunicación registrada con la cuenta.
    - Industria FI (INDUSTRIA_FI): Sector industrial o categoría financiera de la cuenta.
    - Descripción (DESCRIPCIÓN): Detalle, notas o contexto específico sobre el estado de la llamada abierta.
    3. Asignación del Equipo:
    - Comercial (COMERCIAL): Nombre de dominio del usuario comercial encargado de la cuenta.
    - Gestor (GESTOR): Nombre de dominio del usuario gestor responsable del seguimiento.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/comercial pregunte por llamadas pendientes, actividades abiertas, interacciones pendientes de un usuario/comercial específico.
    - Si el usuario solicita el reporte general de llamadas abiertas sin especificar un comercial, ejecuta la herramienta de inmediato para traer el listado completo. Si menciona un nombre ambiguo, solicita amablemente la aclaración del dominio del comercial antes de realizar la consulta.
    """
)
def get_llamadas_abiertas_por_comercial_realtime(email: str) -> list[dict]:
    current_date = get_current_date()
    return REALTIME_SERVICE.get_llamadas_abiertas_por_comercial(email, current_date)


@mcp.tool(
    description= """
    Obtiene el listado completo de las llamadas abiertas registradas para las cuentas de un gestor de cuenta especifico en CRM.

    Argumentos de entrada:
    - email (string, requerido): Email del gestor asignado para filtrar los resultados.

    Información que retorna la herramienta (Estructura de datos):
    Para cada llamada abierta, la herramienta devuelve un objeto estructurado en tres niveles con las siguientes propiedades:
    1. Datos de la Cuenta y Priorización:
    - Nombre de la cuenta (NOMBRE_DE_LA_CUENTA): Razón social o nombre de la empresa cliente vinculada.
    - Score inicial (SCORE_INICIAL): Puntuación o calificación inicial asignada a la cuenta en el CRM.
    - Grupo (GROUP_ALIAS): Alias o nombre del grupo empresarial al que pertenece la cuenta.
    2. Estado de la Relación y Contexto:
    - Último contacto (ÚLTIMO_CONTACTO): Fecha de la última interacción o comunicación registrada con la cuenta.
    - Industria FI (INDUSTRIA_FI): Sector industrial o categoría financiera de la cuenta.
    - Descripción (DESCRIPCIÓN): Detalle, notas o contexto específico sobre el estado de la llamada abierta.
    3. Asignación del Equipo:
    - Comercial (COMERCIAL): Nombre de dominio del usuario comercial encargado de la cuenta.
    - Gestor (GESTOR): Nombre de dominio del usuario gestor responsable del seguimiento.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/gestor pregunte por llamadas pendientes, actividades abiertas, interacciones pendientes de las cuentas que gestiona.
    - Si el usuario solicita el reporte general de llamadas abiertas sin especificar un gestor, ejecuta la herramienta de inmediato para traer el listado completo. Si menciona un nombre ambiguo, solicita amablemente la aclaración del dominio del gestor antes de realizar la consulta.
    """    
)
def get_llamadas_abiertas_por_gestor_realtime(email: str) -> list[dict]:
    current_date = get_current_date()
    return REALTIME_SERVICE.get_llamadas_abiertas_por_cuenta(email, current_date)


@mcp.tool(
    description= """
    Obtiene el listado completo de los leads pendientes asignados a un usuario comercial en el CRM.

    Argumentos de entrada:
    - email (string, requerido): Email del comercial asignado para filtrar los resultados.

    Información que retorna la herramienta (Estructura de datos):
    Para cada registro de lead pendiente, la herramienta devuelve un objeto estructurado:
    1. Datos de la Cuenta y Priorización:
    - Nombre de la cuenta (NOMBRE_DE_LA_CUENTA): Razón social o nombre de la empresa cliente vinculada.
    - Score inicial (SCORE_INICIAL): Puntuación o calificación inicial asignada a la cuenta en el CRM.
    - Grupo (GROUP_ALIAS): Alias o nombre del grupo empresarial al que pertenece la cuenta.
    2. Estado de la Relación y Contexto de Origen:
    - Último contacto (ÚLTIMO_CONTACTO): Fecha de la última interacción o comunicación registrada con la cuenta.
    - Industria FI (INDUSTRIA_FI): Sector industrial o categoría financiera de la cuenta.
    - Canal de origen (SOURCE_CHANNEL): Medio o canal a través del cual se captó el lead.
    - Campaña de origen (CAMPAÑA_DE_ORIGEN): Nombre de la campaña de marketing vinculada al lead.
    - Comentarios de lead (COMENTARIOS_DE_LEAD): Detalle, notas o contexto específico de comentarios para la gestión del lead.
    - Fecha de creación (CREADO): Fecha de registro y alta del lead en el sistema CRM.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/comercial pregunte por sus leads pendientes, prospectos asignados, oportunidades sin resolver o tareas de captación pendientes de un usuario/comercial específico.
    - Si el usuario solicita el reporte de leads pendientes sin especificar un comercial, ejecuta la herramienta de inmediato para traer el listado general. Si menciona un nombre de usuario ambiguo, solicita amablemente la aclaración de su correo electrónico o dominio antes de realizar la consulta.
    """
)
def get_leads_abiertos_por_comercial_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_leads_abiertos_por_comercial(email)


@mcp.tool(
    description="""
    Obtiene el listado completo de los leads pendientes asignados a la cuenta de un usuario gestor en el CRM.

    Argumentos de entrada:
    - email (string, requerido): Email del gestor asignado a la cuenta del lead para filtrar los resultados.

    Información que retorna la herramienta (Estructura de datos):
    Para cada registro de lead pendiente, la herramienta devuelve un objeto estructurado:
    1. Datos de la Cuenta y Priorización:
    - Nombre de la cuenta (NOMBRE_DE_LA_CUENTA): Razón social o nombre de la empresa cliente vinculada.
    - Score inicial (SCORE_INICIAL): Puntuación o calificación inicial asignada a la cuenta en el CRM.
    - Grupo (GROUP_ALIAS): Alias o nombre del grupo empresarial al que pertenece la cuenta.
    2. Estado de la Relación y Contexto de Origen:
    - Último contacto (ÚLTIMO_CONTACTO): Fecha de la última interacción o comunicación registrada con la cuenta.
    - Industria FI (INDUSTRIA_FI): Sector industrial o categoría financiera de la cuenta.
    - Canal de origen (SOURCE_CHANNEL): Medio o canal a través del cual se captó el lead.
    - Campaña de origen (CAMPAÑA_DE_ORIGEN): Nombre de la campaña de marketing vinculada al lead.
    - Comentarios de lead (COMENTARIOS_DE_LEAD): Detalle, notas o contexto específico de comentarios para la gestión del lead.
    - Fecha de creación (CREADO): Fecha de registro y alta del lead en el sistema CRM.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/gestor pregunte por sus leads pendientes, prospectos asignados, oportunidades sin resolver o tareas de captación pendientes de las cuentas que gestiona.
    - Si el usuario solicita el reporte de leads pendientes sin especificar un comercial, ejecuta la herramienta de inmediato para traer el listado general. Si menciona un nombre de usuario ambiguo, solicita amablemente la aclaración de su correo electrónico o dominio antes de realizar la consulta.
    """
)
def get_leads_abiertos_por_gestor_realtime(email: str) -> list[dict]:
    return REALTIME_SERVICE.get_leads_abiertos_por_gestor(email)


@mcp.tool(
    description="""
    Obtiene el listado completo de los leads pendientes asignados a una cuenta en el CRM.

    Argumentos de entrada:
    - nombre_cuenta (string, requerido): Nombre de la cuenta del lead para filtrar los resultados.

    Información que retorna la herramienta (Estructura de datos):
    Para cada registro de lead pendiente, la herramienta devuelve un objeto estructurado:
    1. Datos de la Cuenta y Priorización:
    - Nombre de la cuenta (NOMBRE_DE_LA_CUENTA): Razón social o nombre de la empresa cliente vinculada.
    - Score inicial (SCORE_INICIAL): Puntuación o calificación inicial asignada a la cuenta en el CRM.
    - Grupo (GROUP_ALIAS): Alias o nombre del grupo empresarial al que pertenece la cuenta.
    2. Estado de la Relación y Contexto de Origen:
    - Último contacto (ÚLTIMO_CONTACTO): Fecha de la última interacción o comunicación registrada con la cuenta.
    - Industria FI (INDUSTRIA_FI): Sector industrial o categoría financiera de la cuenta.
    - Canal de origen (SOURCE_CHANNEL): Medio o canal a través del cual se captó el lead.
    - Campaña de origen (CAMPAÑA_DE_ORIGEN): Nombre de la campaña de marketing vinculada al lead.
    - Comentarios de lead (COMENTARIOS_DE_LEAD): Detalle, notas o contexto específico de comentarios para la gestión del lead.
    - Fecha de creación (CREADO): Fecha de registro y alta del lead en el sistema CRM.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/comercial/gestor pregunte por leads pendientes, prospectos asignados, oportunidades sin resolver o tareas de captación pendientes asociados a una cuenta.
    - Si el usuario solicita el reporte de leads pendientes sin especificar el nombre de la cuenta, ejecuta la herramienta de inmediato para traer el listado general. Si menciona un nombre de cuenta ambiguo, solicita amablemente la aclaración del nombre antes de realizar la consulta.
    """
)
def get_leads_abiertos_por_cuenta_realtime(nombre_cuenta: str) -> list[dict]:
    return REALTIME_SERVICE.get_leads_abiertos_por_cuenta(nombre_cuenta)


@mcp.tool(
    description="""
    Obtiene el listado completo de los servicios de oportunidad abiertos por un usuario/comercial específico a partir de su correo electrónico.

    Argumentos de entrada:
    - email (string, requerido): Email del comercial asignado al servicio de oportunidad para filtrar los resultados.

    Información que retorna la herramienta (Estructura de datos):
    Para cada registro de oportunidad abierta, la herramienta devuelve un objeto estructurado en tres niveles:
    1. Datos de la Oferta y Cuenta:
    - Nombre de la cuenta: Razón social o nombre de la empresa cliente vinculada.
    - Fecha de creación: Fecha en la que se registró la propuesta comercial en el CRM (createdon).
    - Probabilidad: Porcentaje o nivel estimado de éxito comercial para ganar este servicio.
    2. Clasificación del Negocio:
    - Tipo de servicio: Categoría o modalidad específica del servicio ofertado.
    - Área de servicio: División o departamento de negocio asignado.
    - Sector FI: Sector industrial o económico al que pertenece el cliente.
    3. Condiciones Financieras:
    - Tipo de contrato: Formato legal o modelo contractual propuesto para el servicio.
    - Previsión de honorarios: Estimación económica o ingresos proyectados para este negocio.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/comercial pregunte por sus oportunidades abiertas, su cartera actual en seguimiento o el estado de sus negocios activos.
    - Requiere obligatoriamente el correo electrónico del comercial. Si no está presente en el contexto o en el prompt inicial, solicítalo amablemente al usuario antes de ejecutar la herramienta.
    """
)
def get_servicios_de_oportunidad_abierta_por_comercial_realtime(email: str) -> list[dict]:
    """Consulta las servicios de oportunidad u ofertas ofrecidos a cuentas con oportunidades abiertas que ha creado el usuario."""
    return REALTIME_SERVICE.get_servicios_de_oportunidad_abierta_por_comercial(email)


@mcp.tool(
    description="""
    Obtiene el listado completo de los servicios de oportunidad abiertos asignados a las cuentas de un usuario/gestor de cuenta específico a partir de su correo electrónico.

    Argumentos de entrada:
    - email (string, requerido): Email del usuario/gestor asignado al servicio de oportunidad para filtrar los resultados.

    Información que retorna la herramienta (Estructura de datos):
    Para cada registro de oportunidad abierta, la herramienta devuelve un objeto estructurado en tres niveles:
    1. Datos de la Oferta y Cuenta:
    - Nombre de la cuenta: Razón social o nombre de la empresa cliente vinculada.
    - Fecha de creación: Fecha en la que se registró la propuesta comercial en el CRM (createdon).
    - Probabilidad: Porcentaje o nivel estimado de éxito comercial para ganar este servicio.
    2. Clasificación del Negocio:
    - Tipo de servicio: Categoría o modalidad específica del servicio ofertado.
    - Área de servicio: División o departamento de negocio asignado.
    - Sector FI: Sector industrial o económico al que pertenece el cliente.
    3. Condiciones Financieras:
    - Tipo de contrato: Formato legal o modelo contractual propuesto para el servicio.
    - Previsión de honorarios: Estimación económica o ingresos proyectados para este negocio.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/gestor pregunte por sus cuentas con oportunidades abiertas, su cartera actual en seguimiento o el estado de sus negocios activos.
    - Requiere obligatoriamente el correo electrónico del gestor. Si no está presente en el contexto o en el prompt inicial, solicítalo amablemente al usuario antes de ejecutar la herramienta.
    """
)
def get_servicios_de_oportunidad_abierta_por_gestor_realtime(email: str) -> list[dict]:
    """Consulta las servicios de oportunidad u ofertas ofrecidos a cuentas con oportunidades abiertas que gestiona el usuario."""
    return REALTIME_SERVICE.get_servicios_de_oportunidad_abierta_por_gestor(email)


@mcp.tool(
    description="""
    Obtiene el listado completo de los servicios de oportunidad abiertos asignados a una cuenta especifica.

    Argumentos de entrada:
    - nombre_cuenta (string, requerido): Nombre de la cuenta asociada al servicio de oportunidad para filtrar los resultados.

    Información que retorna la herramienta (Estructura de datos):
    Para cada registro de oportunidad abierta, la herramienta devuelve un objeto estructurado en tres niveles:
    1. Datos de la Oferta y Cuenta:
    - Nombre de la cuenta: Razón social o nombre de la empresa cliente vinculada.
    - Fecha de creación: Fecha en la que se registró la propuesta comercial en el CRM (createdon).
    - Probabilidad: Porcentaje o nivel estimado de éxito comercial para ganar este servicio.
    2. Clasificación del Negocio:
    - Tipo de servicio: Categoría o modalidad específica del servicio ofertado.
    - Área de servicio: División o departamento de negocio asignado.
    - Sector FI: Sector industrial o económico al que pertenece el cliente.
    3. Condiciones Financieras:
    - Tipo de contrato: Formato legal o modelo contractual propuesto para el servicio.
    - Previsión de honorarios: Estimación económica o ingresos proyectados para este negocio.

    Instrucciones de uso para el modelo (Triggering):
    - Invoca este recurso inmediatamente cuando el usuario/gestor pregunte por una cuenta con oportunidades abiertas.
    - Requiere obligatoriamente el nombre de la cuenta. Si no está presente en el contexto o en el prompt inicial, solicítalo amablemente al usuario antes de ejecutar la herramienta.
    """
)
def get_servicios_de_oportunidad_abierta_por_cuenta_realtime(nombre_cuenta: str) -> list[dict]:
    return REALTIME_SERVICE.get_servicios_de_oportunidad_abierta_por_cuenta(nombre_cuenta)


@mcp.tool(
    description= """    
    Obtiene el listado de reuniones comerciales pasadas cuyo resultado fue marcado como "interés en el futuro" para un usuario o comercial específico.

    Argumentos de entrada:
    - email (string): Correo del comercial en el CRM.

    Este recurso consulta el CRM y extrae las cuentas con oportunidades latentes, detallando los siguientes campos clave de su última interacción:
    1. NOMBRE_DE_LA_CUENTA: Nombre de la cuenta o empresa (`account.name`).
    2. FECHA_DE_ÚLTIMA_REUNIÓN: Fecha y hora de finalización de la cita (`scheduledend`).
    3. COMENTARIOS: Notas y comentarios sobre el resultado de la última reunión (`iav_resultcomments`).
    4. CONTACTO_PRINCIPAL: Nombre completo, cargo y teléfono del contacto principal (`contact.fullname`).
    5. COMERCIAL: Correo del comercial que generó o atendió la cita (`created_by.domainname`).
    6. GESTOR: Correo del gestor asignado actualmente a la cuenta (`user.domainname`).

    Utiliza este recurso cuando el comercial necesite hacer seguimiento a prospectos antiguos, rescatar leads con interés aplazado, o planificar campañas de re-impacto basadas en el histórico de reuniones con interés futuro.
    """    
)
def get_get_citas_con_interes_futuro_por_comercial(email: str) -> list[dict]:
    """Consulta las citas con resultado interés en el futuro que ha creado el usuario durante los últimos 3 meses."""
    return REALTIME_SERVICE.get_servicios_de_oportunidad_abierta_por_comercial(email)


@mcp.tool(
    description= """    
    Obtiene el listado de reuniones comerciales pasadas cuyo resultado fue marcado como "interés en el futuro" asociadas a las cuentas de un usuario/gestor de cuenta específico.

    Argumentos de entrada:
    - email (string): Correo del usuario/gestor de cuenta en el CRM.

    Este recurso consulta el CRM y extrae las cuentas con oportunidades latentes, detallando los siguientes campos clave de su última interacción:
    1. NOMBRE_DE_LA_CUENTA: Nombre de la cuenta o empresa (`account.name`).
    2. FECHA_DE_ÚLTIMA_REUNIÓN: Fecha y hora de finalización de la cita (`scheduledend`).
    3. COMENTARIOS: Notas y comentarios sobre el resultado de la última reunión (`iav_resultcomments`).
    4. CONTACTO_PRINCIPAL: Nombre completo, cargo y teléfono del contacto principal (`contact.fullname`).
    5. COMERCIAL: Correo del comercial que generó o atendió la cita (`created_by.domainname`).
    6. GESTOR: Correo del gestor asignado actualmente a la cuenta (`user.domainname`).

    Utiliza este recurso cuando el usuario/gestor de cuenta necesite hacer seguimiento a prospectos antiguos, rescatar leads con interés aplazado, o planificar campañas de re-impacto basadas en el histórico de reuniones con interés futuro.
    """    
)
def get_get_citas_con_interes_futuro_por_gestor(email: str) -> list[dict]:
    """Consulta las citas con resultado interés en el futuro que se han creado para cuentas que gestiona el usuario durante los últimos 3 meses."""
    return REALTIME_SERVICE.get_servicios_de_oportunidad_abierta_por_gestor(email)


@mcp.tool(
    description= """    
    Obtiene el listado de reuniones comerciales pasadas cuyo resultado fue marcado como "interés en el futuro" asociadas a una cuenta específica.

    Argumentos de entrada:
    - nombre_cuenta (string): Nombre de la cuenta en el CRM.

    Este recurso consulta el CRM y extrae las cuentas con oportunidades latentes, detallando los siguientes campos clave de su última interacción:
    1. NOMBRE_DE_LA_CUENTA: Nombre de la cuenta o empresa (`account.name`).
    2. FECHA_DE_ÚLTIMA_REUNIÓN: Fecha y hora de finalización de la cita (`scheduledend`).
    3. COMENTARIOS: Notas y comentarios sobre el resultado de la última reunión (`iav_resultcomments`).
    4. CONTACTO_PRINCIPAL: Nombre completo, cargo y teléfono del contacto principal (`contact.fullname`).
    5. COMERCIAL: Correo del comercial que generó o atendió la cita (`created_by.domainname`).
    6. GESTOR: Correo del gestor asignado actualmente a la cuenta (`user.domainname`).

    Utiliza este recurso cuando el usuario/comercial/gestor de cuenta necesite hacer seguimiento a prospectos antiguos, rescatar leads con interés aplazado, o planificar campañas de re-impacto basadas en el histórico de reuniones con interés futuro de una cuenta específica.
    """    
)
def get_get_citas_con_interes_futuro_por_cuenta(nombre_cuenta: str) -> list[dict]:
    """Consulta las citas con resultado interés en el futuro por cuenta durante los últimos 3 meses."""
    return REALTIME_SERVICE.get_servicios_de_oportunidad_abierta_por_cuenta(nombre_cuenta)


@mcp.tool(
    description="""
    Obtiene el listado completo y detallado de las ayudas o subvenciones percibidas los tres últimos años para una cuenta específica según su NIF. 

    Args:
        nif (str): NIF fiscal de la cuenta.

    Returns:
        Lista de dict con claves:
        - NIF: Código fiscal del beneficiario
        - BENEFICIARIO: Nombre del beneficiario
        - ORGANISMO: Organismo concedente
        - FONDOS_A_PRESTAMO: Importe en préstamos
        - FONDOS_A_SUBVENCIÓN: Importe en subvenciones
    """
)
def get_ayudas_percibidas_bdns(nif: str) -> list[dict]:
    return SQL_SERVICE.get_detalle_ayudas(nif.strip().upper())

@mcp.tool(description="Devuelve el listado de query keys XML disponibles para ejecución realtime.")
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
        params["email"] = email
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