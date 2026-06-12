import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

# Rutas base relativas al script
_SCRIPTS_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _SCRIPTS_DIR.parent
OUTPUT_DIR = _ROOT_DIR / "output"
LOGS_DIR = _ROOT_DIR / "logs"
RESOURCES_DIR = _SCRIPTS_DIR / "resources"

from clients import DataverseClient, BDNSClient, GRANTSClient, fetch_news_for_account, summarize_news
from config import (
    QUERIES,
    COLUMNS_HISTORICO,
    COLUMNS_HISTORICO_LLAMADAS,
    COLUMNS_HISTORICO_SERVICIOS,
    COLUMNS_HISTORICO_BDNS,
    COLUMNS_GRANTS,
    COLUMNS_LLAMADAS_ESTADO_CALIENTE,
    COLUMNS_LEADS,
    COLUMNS_OPORTUNIDADES_ABIERTAS,
    COLUMNS_OFERTAS_PENDIENTES,
    COLUMNS_LLAMADAS_ENTRE_FECHAS,
    COLUMNS_CITAS_CANCELADAS_CURRENT_YEAR
)
from utils import chunk_array, export_to_excel, get_week_range, json_to_dataframe, process_dataframe, join_tagged_values, join_sql_values, map_sector_grants

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def fetch_bdns(sql_client, columns: dict, chunks: list) -> pd.DataFrame:
    """
    Consulta la base de datos BDNS en bloques de NIFs y devuelve un DataFrame consolidado.

    Args:
        sql_client: Cliente SQL activo (SQLClient con contexto abierto).
        columns (dict): Mapeo de columnas destino → origen para procesar el DataFrame.
        chunks (list): Lista de subarreglos de NIFs a consultar por bloque.

    Returns:
        pd.DataFrame: DataFrame consolidado con los datos BDNS, o vacío si no hay resultados.
    """
    bloques = []
    total = 0
    logger.info("Haciendo peticiones BDNS en %d bloques...", len(chunks))
    for idx, bloque in enumerate(chunks, start=1):
        logger.info("Bloque %d/%d", idx, len(chunks))
        query = QUERIES["Detalle de las Ayudas"].format(nifs=join_sql_values(bloque))
        df = sql_client.execute_query(query)
        bloques.append(df)
        total += len(df)
        logger.info("Registros BDNS obtenidos en bloque %d: %d", idx, len(df))
    logger.info("Total de registros BDNS obtenidos: %d", total)

    if not bloques:
        logger.warning("No se obtuvieron datos de BDNS")
        return pd.DataFrame()

    df_total = process_dataframe(pd.concat(bloques, ignore_index=True), columns)
    logger.info("DataFrame BDNS total: %d filas", len(df_total))
    return df_total


def fetch_historico(client, entity: str, query_key: str, columns: dict, chunks: list, label: str, **query_params) -> pd.DataFrame:
    """
    Consulta el histórico de una entidad Dataverse en bloques de cuentas.

    Args:
        client: Instancia de DataverseClient.
        entity (str): Nombre de la entidad Dataverse (ej. "appointments", "phonecalls").
        query_key (str): Clave del diccionario QUERIES con la plantilla FetchXML a usar.
        columns (dict): Mapeo de columnas destino → origen para procesar el DataFrame.
        chunks (list): Lista de subarreglos de IDs de cuenta a consultar por bloque.
        label (str): Etiqueta descriptiva del tipo de dato (ej. "citas", "llamadas").
        **query_params: Parámetros adicionales para formatear la plantilla FetchXML
                        (ej. fechaInicio, fechaFin).

    Returns:
        pd.DataFrame: DataFrame consolidado con los registros históricos, o vacío si no hay resultados.
    """
    bloques = []
    total = 0
    logger.info("Haciendo peticiones de %s en %d bloques...", label, len(chunks))
    for idx, bloque in enumerate(chunks, start=1):
        logger.info("Bloque %d/%d", idx, len(chunks))
        query = QUERIES[query_key].format(cuentasIds=join_tagged_values(bloque, "value"), **query_params)
        df = json_to_dataframe(client.send_request(entity, query))
        bloques.append(df)
        total += len(df)
        logger.info("%s obtenidos en bloque %d: %d", label.capitalize(), idx, len(df))
    logger.info("Total de %s históricos obtenidos: %d", label, total)

    if not bloques:
        logger.warning("No se obtuvieron datos históricos de %s", label)
        return pd.DataFrame()

    df_total = process_dataframe(pd.concat(bloques, ignore_index=True), columns)
    logger.info("DataFrame histórico de %s total: %d filas", label, len(df_total))
    return df_total


def fetch_grants(grants_client, columns: dict) -> pd.DataFrame:
    """
    Consulta la base de datos GRANTS y devuelve un DataFrame procesado por sector.

    Args:
        grants_client: Cliente SQL activo (GRANTSClient con contexto abierto).
        columns (dict): Mapeo de columnas destino → origen para procesar el DataFrame.

    Returns:
        pd.DataFrame: DataFrame con los datos de convocatorias GRANTS, o vacío si no hay resultados.
    """
    logger.info("Haciendo petición GRANTS...")
    df = grants_client.execute_query(QUERIES["Grants por Sector"])
    logger.info("Registros GRANTS obtenidos: %d", len(df))
    if df.empty:
        logger.warning("No se obtuvieron datos de GRANTS")
        return pd.DataFrame()
    df_total = process_dataframe(df, columns)
    logger.info("DataFrame GRANTS total: %d filas", len(df_total))
    return df_total


def fetch_noticias(df: pd.DataFrame, column: str, max_results: int = 10, date_from: str | None = None, date_to: str | None = None) -> pd.DataFrame:
    """
    Obtiene noticias recientes para cada cuenta única presente en `df`.

    Args:
        df (pd.DataFrame): DataFrame que contiene los nombres de las cuentas.
        column (str): Nombre de la columna con los nombres de las cuentas.
        max_results (int): Número máximo de noticias a obtener por cuenta. Por defecto 10.
        date_from (str | None): Fecha de inicio en formato MM/DD/YYYY. None = 12 meses atrás.
        date_to (str | None): Fecha de fin en formato MM/DD/YYYY. None = hoy.

    Returns:
        pd.DataFrame: DataFrame con las noticias encontradas (columnas: NOMBRE_DE_LA_CUENTA,
                      Título, Fuente, Fecha, URL, Contenido), o vacío si no hay datos.
    """
    if df.empty or column not in df.columns:
        logger.warning("No se pueden obtener noticias: el DataFrame está vacío o no contiene la columna '%s'.", column)
        return pd.DataFrame()

    cuentas = df[column].dropna().unique()
    logger.info("Obteniendo noticias para %d cuentas únicas...", len(cuentas))
    rows = []
    for idx, cuenta in enumerate(cuentas, start=1):
        logger.info("  [%d/%d] %s", idx, len(cuentas), cuenta)
        rows.extend(fetch_news_for_account(cuenta, max_results=max_results, date_from=date_from, date_to=date_to))
    df_noticias = pd.DataFrame(rows)
    logger.info("Total noticias obtenidas: %d", len(df_noticias))
    return df_noticias


def run(config: dict) -> None:
    """
    Orquesta la ejecución de todos los procesos de extracción y exportación según la configuración.

    Cada proceso puede activarse o desactivarse de forma independiente mediante las claves
    booleanas del diccionario `config`. Los resultados de cada proceso activo se consolidan
    en hojas de un fichero Excel de salida (`citas.xlsx`).

    Args:
        config (dict): Diccionario de configuración con las siguientes claves:
            - RUN_REUNIONES_AGENDADAS_SEMANA_ACTUAL (bool): Extrae las citas de la semana en curso.
            - RUN_REUNIONES_AGENDADAS_12 _SEMANAS_ATRAS (bool): Extrae las citas de hace 12 semanas.
            - RUN_HISTORICO_CITAS (bool): Extrae el histórico de citas (3 años).
            - RUN_HISTORICO_LLAMADAS (bool): Extrae el histórico de llamadas (3 años).
            - RUN_HISTORICO_SERVICIOS (bool): Extrae el histórico de servicios/oportunidades.
            - RUN_LLAMADAS_ABIERTAS (bool): Extrae llamadas en estado de proceso de venta.
            - RUN_OPORTUNIDADES_ABIERTAS (bool): Extrae oportunidades de servicio abiertas.
            - RUN_OFERTAS_PENDIENTES (bool): Extrae ofertas pendientes en las últimas 12 semanas.
            - RUN_LEADS (bool): Extrae leads abiertos.
            - RUN_BDNS (bool): Consulta subvenciones BDNS por NIF.
            - RUN_GRANTS (bool): Consulta convocatorias GRANTS por sector.
            - RUN_LLAMADAS_AÑO (bool): Extrae todas las llamadas del año en curso.
            - RUN_NOTICIAS (bool): Obtiene noticias recientes por nombre de cuenta.
            - NOTICIAS_MAX_RESULTS (int): Número máximo de noticias por cuenta.
            - NOTICIAS_DATE_FROM (str | None): Fecha inicio para noticias (MM/DD/YYYY).
            - NOTICIAS_DATE_TO (str | None): Fecha fin para noticias (MM/DD/YYYY).
            - PLAN_CUENTAS_PATH (str): Ruta al fichero Excel con el plan de cuentas anual.
    """
    # ── Configurar log a fichero ──────────────────────────────────────────────
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"logs_{datetime.now().strftime('%Y-%m-%d')}.txt"
    _file_handler = logging.FileHandler(log_file, encoding="utf-8")
    _file_handler.setLevel(logging.INFO)
    _file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logging.getLogger().addHandler(_file_handler)
    logger.info("Log iniciado en '%s'", log_file)
    # ─────────────────────────────────────────────────────────────────────────

    client = DataverseClient()
    sheets = {}
    errors: dict[str, str] = {}
    start_current, end_current = get_week_range(0)

    # GRANTS
    if config["RUN_GRANTS"]:
        try:
            with GRANTSClient() as grants_client:
                sheets["CONVOCATORIAS ABIERTAS"] = fetch_grants(grants_client, COLUMNS_GRANTS)
        except Exception as e:
            logger.error("Proceso GRANTS falló: %s", e, exc_info=True)
            errors["GRANTS"] = str(e)

    # Semana actual (base para históricos y BDNS)
    df_current_processed = pd.DataFrame()
    needs_semana_actual = any(config[k] for k in (
        "RUN_REUNIONES_AGENDADAS_SEMANA_ACTUAL", "RUN_HISTORICO_CITAS", "RUN_HISTORICO_LLAMADAS",
        "RUN_HISTORICO_SERVICIOS", "RUN_BDNS", "RUN_OPORTUNIDADES_ABIERTAS", "RUN_LEADS"
    ))
    if needs_semana_actual:
        try:
            query_current = QUERIES["Reuniones Agendadas entre Fechas"].format(fechaInicio=start_current, fechaFin=end_current)
            result_current = client.send_request("appointments", query_current)
            df_current_processed = process_dataframe(json_to_dataframe(result_current))
            logger.info("Citas semana actual: %d", len(df_current_processed))
            if config["RUN_REUNIONES_AGENDADAS_SEMANA_ACTUAL"]:
                df_current_processed = map_sector_grants(df_current_processed, crm_column="SECTOR_FI")
                sheets["CITAS SEMANALES"] = df_current_processed
        except Exception as e:
            logger.error("Proceso Semana Actual falló: %s", e, exc_info=True)
            errors["Semana Actual"] = str(e)

    # Noticias por cuenta
    if config["RUN_NOTICIAS"]:
        try:
            df_noticias = fetch_noticias(
                df_current_processed, "NOMBRE_DE_LA_CUENTA",
                max_results=config["NOTICIAS_MAX_RESULTS"],
                date_from=config["NOTICIAS_DATE_FROM"],
                date_to=config["NOTICIAS_DATE_TO"],
            )
            # sheets["Noticias"] = df_noticias
            if not df_noticias.empty:
                logger.info("Generando resúmenes de noticias...")
                df_resumenes = df_noticias.copy()
                df_resumenes["Resumen"] = df_resumenes.apply(
                    lambda row: summarize_news(row["Título"], row["Contenido"]), axis=1
                )
                sheets["RESUMEN DE NOTICIAS"] = df_resumenes
        except Exception as e:
            logger.error("Proceso Noticias falló: %s", e, exc_info=True)
            errors["Noticias"] = str(e)

    # 12 semanas atrás
    if config["RUN_REUNIONES_AGENDADAS_12 _SEMANAS_ATRAS"]:
        try:
            start_12_weeks, end_12_weeks = get_week_range(12)
            query_12_weeks = QUERIES["Reuniones Agendadas entre Fechas"].format(fechaInicio=start_12_weeks, fechaFin=end_12_weeks)
            result_12_weeks = client.send_request("appointments", query_12_weeks)
            try:
                df_12_weeks_processed = process_dataframe(json_to_dataframe(result_12_weeks))
                logger.info("Citas agendadas 12 semanas atrás: %d", len(df_12_weeks_processed))
            except ValueError as error:
                logger.warning("No se pudo convertir la respuesta a JSON: %s", error)
                df_12_weeks_processed = pd.DataFrame()
            sheets["CITAS 12 SEMANAS ATRAS"] = df_12_weeks_processed
        except Exception as e:
            logger.error("Proceso 12 Semanas Atras falló: %s", e, exc_info=True)
            errors["12 Semanas Atras"] = str(e)

    # Históricos (citas, llamadas, servicios)
    if config["RUN_HISTORICO_CITAS"] or config["RUN_HISTORICO_LLAMADAS"] or config["RUN_HISTORICO_SERVICIOS"]:
        try:
            unique_cuentas = df_current_processed["CUENTA_ID"].unique()
            start_3_years, _ = get_week_range(157)
            chunks = chunk_array(unique_cuentas, 15)
            fecha_params = {
                "fechaInicio": str(start_3_years) + "T00:00:00.0000000Z",
                "fechaFin": str(end_current) + "T23:59:59.9999999Z"
            }

            if config["RUN_HISTORICO_CITAS"]:
                try:
                    sheets["HISTORICO DE CITAS"] = fetch_historico(client, "appointments", "Resumen de Citas Celebradas", COLUMNS_HISTORICO, chunks, "citas", **fecha_params)
                except Exception as e:
                    logger.error("Proceso Historicos de citas falló: %s", e, exc_info=True)
                    errors["Historicos de citas"] = str(e)

            if config["RUN_HISTORICO_LLAMADAS"]:
                try:
                    sheets["HISTORICO DE LLAMADAS"] = fetch_historico(client, "phonecalls", "Resumen de Llamadas Celebradas", COLUMNS_HISTORICO_LLAMADAS, chunks, "llamadas", **fecha_params)
                except Exception as e:
                    logger.error("Proceso Historicos de llamadas falló: %s", e, exc_info=True)
                    errors["Historicos de llamadas"] = str(e)

            if config["RUN_HISTORICO_SERVICIOS"]:
                try:
                    sheets["HISTORICO DE OPPS"] = fetch_historico(client, "iav_opportunityservices", "Resumen de Ofertas Lanzadas", COLUMNS_HISTORICO_SERVICIOS, chunks, "servicios")
                except Exception as e:
                    logger.error("Proceso Historicos de servicios falló: %s", e, exc_info=True)
                    errors["Historicos de servicios"] = str(e)

        except Exception as e:
            logger.error("Preparación de históricos falló (sin datos base): %s", e, exc_info=True)
            errors["Historicos (preparación)"] = str(e)

    # Oportunidades en proceso de venta
    if config["RUN_LLAMADAS_ABIERTAS"]:
        try:
            result_oportunidades = client.send_request("phonecalls", QUERIES["Llamadas Abiertas"].format(currentDate=datetime.now().strftime("%Y-%m-%d")))
            df_oportunidades = process_dataframe(json_to_dataframe(result_oportunidades), COLUMNS_LLAMADAS_ESTADO_CALIENTE)
            logger.info("Llamadas abiertas con estado caliente: %d", len(df_oportunidades))
            sheets["LLAMADAS ABIERTAS"] = df_oportunidades
        except Exception as e:
            logger.error("Proceso Llamadas Estado Caliente falló: %s", e, exc_info=True)
            errors["Llamadas Estado Caliente"] = str(e)

    # Leads abiertos
    if config["RUN_LEADS"]:
        try:
            result_leads = client.send_request("leads", QUERIES["Leads Abiertos"])
            df_leads = process_dataframe(json_to_dataframe(result_leads), COLUMNS_LEADS)
            logger.info("Leads abiertos: %d", len(df_leads))
            sheets["LEADS ABIERTOS"] = df_leads
        except Exception as e:
            logger.error("Proceso Leads falló: %s", e, exc_info=True)
            errors["Leads"] = str(e)

    # Oportunidades abiertas (servicios)
    if config["RUN_OPORTUNIDADES_ABIERTAS"]:
        try:
            result_op_abiertas = client.send_request("iav_opportunityservices", QUERIES["Oportunidades Abiertas"])
            df_op_abiertas = process_dataframe(json_to_dataframe(result_op_abiertas), COLUMNS_OPORTUNIDADES_ABIERTAS)
            logger.info("Oportunidades abiertas: %d", len(df_op_abiertas))
            sheets["OPORTUNIDADES ABIERTAS"] = df_op_abiertas
        except Exception as e:
            logger.error("Proceso Oportunidades Abiertas falló: %s", e, exc_info=True)
            errors["Oportunidades Abiertas"] = str(e)

    # Ofertas pendientes
    if config["RUN_OFERTAS_PENDIENTES"]:
        try:
            start_12_weeks, end_12_weeks = get_week_range(12)
            query_ofertas = QUERIES["Ofertas Pendientes"].format(fechaInicio=start_12_weeks, fechaFin=end_current)
            result_ofertas = client.send_request("appointments", query_ofertas)
            df_ofertas = process_dataframe(json_to_dataframe(result_ofertas), COLUMNS_OFERTAS_PENDIENTES)
            logger.info("Oportunidades abiertas: %d", len(df_op_abiertas))
            sheets["OFERTAS PENDIENTES"] = df_ofertas
        except Exception as e:
            logger.error("Ofertas Pendientes: %s", e, exc_info=True)
            errors["Ofertas Pendientes"] = str(e)

    # BDNS
    if config["RUN_BDNS"]:
        try:
            unique_nifs = df_current_processed["NIF"].dropna().unique()
            nif_chunks = chunk_array(unique_nifs, 15)
            with BDNSClient() as sql_client:
                sheets["SUBVENCIONES BDNS"] = fetch_bdns(sql_client, COLUMNS_HISTORICO_BDNS, nif_chunks)
        except Exception as e:
            logger.error("Proceso BDNS falló: %s", e, exc_info=True)
            errors["BDNS"] = str(e)

    # Llamadas en el año
    if config["RUN_LLAMADAS_AÑO"]:
        try:
            year = datetime.now().year
            fecha_fin = str(end_current) + "T23:59:59Z"
            query_llamadas = QUERIES["Llamadas entre Fechas"].format(fechaInicio=year, fechaFin=fecha_fin)
            result_llamadas = client.send_request("phonecalls", query_llamadas)
            df_llamadas = process_dataframe(json_to_dataframe(result_llamadas), COLUMNS_LLAMADAS_ENTRE_FECHAS)
            # sheets["Llamadas Año"] = df_llamadas

            # Cuentas del plan que NO han tenido llamadas en el año
            df_plan = pd.read_excel(config["PLAN_CUENTAS_PATH"], dtype=str)
            numeros_con_llamada = set(df_llamadas["NÚMERO_DE_CUENTA"].dropna().str.strip())
            df_sin_llamada = df_plan[
                ~df_plan["Número de cuenta"].str.strip().isin(numeros_con_llamada)
            ].copy()
            df_sin_llamada["Gasto anual I+D+i"] = pd.to_numeric(
                df_sin_llamada["Gasto anual I+D+i"].str.replace(",", ".").str.replace("[^0-9.]", "", regex=True),
                errors="coerce"
            )
            df_sin_llamada = df_sin_llamada.sort_values("Gasto anual I+D+i", ascending=False)
            df_sin_llamada = map_sector_grants(df_sin_llamada, crm_column="Sector FI")
            logger.info("Cuentas sin llamada en el año: %d", len(df_sin_llamada))
            sheets["CUENTAS SIN LLAMAR"] = df_sin_llamada
        except Exception as e:
            logger.error("Proceso Llamadas Año falló: %s", e, exc_info=True)
            errors["Llamadas Año"] = str(e)

    if config["RUN_CITAS_AÑO_ACTUAL_CANCELADAS"]:
        try:
            year = datetime.now().year
            result_citas_canceladas = client.send_request("appointments", QUERIES["Citas Canceladas entre Fechas"].format(fechaInicio=year, fechaFin=start_current))
            df_citas_canceladas = process_dataframe(json_to_dataframe(result_citas_canceladas), COLUMNS_CITAS_CANCELADAS_CURRENT_YEAR)
            logger.info("Citas canceladas en el año actual: %d", len(df_citas_canceladas))
            sheets["CITAS CANCELADAS"] = df_citas_canceladas
        except Exception as e:
            logger.error("Proceso Citas canceladas en el año actual falló: %s", e, exc_info=True)
            errors["Citas canceladas en el año actual"] = str(e)
    
    if config["RUN_CITAS_COMPLETADAS_6_MESES_ATRAS"]:
        try:
            start_25_weeks, end_25_weeks = get_week_range(25)
            query_25_weeks = QUERIES["Citas de Cuentas con último contacto hace 6 meses"].format(fechaInicio=start_25_weeks, fechaFin=end_25_weeks)
            result_25_weeks = client.send_request("appointments", query_25_weeks)
            try:
                df_25_weeks_processed = process_dataframe(json_to_dataframe(result_25_weeks))
                logger.info("Citas completadas 6 meses atrás: %d", len(df_25_weeks_processed))
            except ValueError as error:
                logger.warning("No se pudo convertir la respuesta a JSON: %s", error)
                df_25_weeks_processed = pd.DataFrame()
            sheets["CITAS 6 MESES ATRAS"] = df_25_weeks_processed
        except Exception as e:
            logger.error("Citas de Cuentas con último contacto hace 6 meses falló: %s", e, exc_info=True)
            errors["Citas de Cuentas con último contacto hace 6 meses Atras"] = str(e)
    
    # Resumen de errores
    if errors:
        logger.warning(
            "Procesos con fallos (%d/%d): %s",
            len(errors),
            sum(config[k] for k in config if k.startswith("RUN_")),
            list(errors.keys()),
        )

    # Exportar a Excel
    if sheets:
        output_path = OUTPUT_DIR / "citas.xlsx"
        export_to_excel(sheets, str(output_path))
        logger.info("Datos exportados a '%s'", output_path)
    else:
        logger.warning("No hay procesos activos. Activa al menos uno en la sección CONFIGURACIÓN.")


if __name__ == "__main__":

    # ─────────────────────────────────────────────
    # CONFIGURACIÓN: activa/desactiva cada proceso
    # ─────────────────────────────────────────────
    CONFIG = {
        "RUN_REUNIONES_AGENDADAS_SEMANA_ACTUAL":                 True,
        "RUN_REUNIONES_AGENDADAS_12 _SEMANAS_ATRAS":             False,
        "RUN_HISTORICO_CITAS":                                   False,
        "RUN_HISTORICO_LLAMADAS":                                False,
        "RUN_HISTORICO_SERVICIOS":                               False,
        "RUN_LLAMADAS_ABIERTAS":                                 False, 
        "RUN_OPORTUNIDADES_ABIERTAS":                            False,
        "RUN_OFERTAS_PENDIENTES":                                False,
        "RUN_LEADS":                                             False, 
        "RUN_BDNS":                                              False,
        "RUN_GRANTS":                                            False,
        "RUN_LLAMADAS_AÑO":                                      False,
        
        "RUN_REUNIONES_AGENDADAS_SEMANA_ACTUAL_INSIDES":         False,#Este no es el mismo de los comerciales? Cual es la diferencia entre insides y comerciales en BD?
        "RUN_CITAS_AÑO_ACTUAL_CANCELADAS":                       False,
        "RUN_CITAS_COMPLETADAS_6_MESES_ATRAS":                   False,
                
        "RUN_NOTICIAS":                                          False,
        "NOTICIAS_MAX_RESULTS":                                  5,     # Noticias por cuenta
        "NOTICIAS_DATE_FROM":                                    None,  # Formato MM/DD/YYYY, None = 12 meses atrás
        "NOTICIAS_DATE_TO":                                      None,  # Formato MM/DD/YYYY, None = hoy
        "PLAN_CUENTAS_PATH":                                     RESOURCES_DIR / "plan de cuentas.xlsx",  # Ruta al plan de cuentas anual
    }
    # ─────────────────────────────────────────────

    run(CONFIG)