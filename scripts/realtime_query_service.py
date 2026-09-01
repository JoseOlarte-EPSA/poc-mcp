from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from scripts.clients.bdns_client import BDNSClient
from scripts.clients.grants_client import GRANTSClient
from scripts.clients.dataverse import DataverseClient
from scripts.config.columns import (
    COLUMNS,
    COLUMNS_HISTORICO_BDNS,
    COLUMNS_HISTORICO_LLAMADAS,
    COLUMNS_HISTORICO_SERVICIOS,
    COLUMNS_LLAMADAS_ESTADO_CALIENTE,
    COLUMNS_LEADS,
    COLUMNS_OPORTUNIDADES_ABIERTAS,
    COLUMNS_OFERTAS_PENDIENTES,
    COLUMNS_CUENTAS_LLAMADAS_ANO_EN_CURSO,
)
from scripts.utils import json_to_dataframe, process_dataframe
from py_queries.CITAS import (
    CITAS_SEMANA_EN_CURSO,
    CITAS_12VA_SEMANA_ATRAS,
    CITAS_POR_CUENTA,
    CITAS_POR_NIF,
    CITAS_POR_COMERCIAL,
    CITAS_POR_COMERCIAL_SEMANA_EN_CURSO,
    CITAS_POR_COMERCIAL_12VA_SEMANA_ATRAS,
    CITAS_POR_GESTOR,
    CITAS_POR_GESTOR_SEMANA_EN_CURSO,
    CITAS_POR_GESTOR_12VA_SEMANA_ATRAS,
    CITAS_CON_INTERES_FUTURO_POR_COMERCIAL,
    CITAS_CON_INTERES_FUTURO_POR_GESTOR,
    CITAS_CON_INTERES_FUTURO_POR_CUENTA,
    CITAS_CON_INTERES_FUTURO_POR_NIF,
    CITAS_ABIERTAS_POR_COMERCIAL_SEMANA_EN_CURSO,
    CITAS_ABIERTAS_POR_GESTOR_SEMANA_EN_CURSO,
    CITAS_CANCELADAS_POR_COMERCIAL_ANO_EN_CURSO,
    CITAS_CANCELADAS_POR_GESTOR_ANO_EN_CURSO,
    CITAS_CANCELADAS_POR_CUENTA_ANO_EN_CURSO,
    CITAS_CANCELADAS_POR_NIF_ANO_EN_CURSO,
    CITAS_POR_COMERCIAL_SIN_LLAMADA_POSTERIOR_6_MESES,
    CITAS_POR_GESTOR_SIN_LLAMADA_POSTERIOR_6_MESES,
)
from py_queries.LLAMADAS import (
    LLAMADAS_SEMANA_EN_CURSO,
    LLAMADAS_POR_CUENTA,
    LLAMADAS_POR_NIF,
    LLAMADAS_POR_COMERCIAL,
    LLAMADAS_POR_COMERCIAL_SEMANA_EN_CURSO,
    LLAMADAS_POR_GESTOR,
    LLAMADAS_POR_GESTOR_SEMANA_EN_CURSO,
    LLAMADAS_ABIERTAS,
    LLAMADAS_ABIERTAS_POR_COMERCIAL,
    LLAMADAS_ABIERTAS_POR_CUENTA,
    LLAMADAS_ABIERTAS_POR_NIF,
    LLAMADAS_ABIERTAS_POR_GESTOR,
)
from py_queries.OPORTUNIDADES import (
    SERVICIOS_DE_OPORTUNIDAD_POR_COMERCIAL,
    SERVICIOS_DE_OPORTUNIDAD_POR_GESTOR,
    SERVICIOS_DE_OPORTUNIDAD_POR_CUENTA,
    SERVICIOS_DE_OPORTUNIDAD_POR_NIF,
    SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_COMERCIAL,
    SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_GESTOR,
    SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_CUENTA,
    SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_NIF,
)
from py_queries.LEADS import (
    LEADS_ABIERTOS_POR_COMERCIAL,
    LEADS_ABIERTOS_POR_GESTOR,
    LEADS_ABIERTOS_POR_CUENTA,
    LEADS_ABIERTOS_POR_NIF,
)
from py_queries.CUENTAS import (
    CUENTAS_LLAMADAS_ANO_EN_CURSO,
)
from py_queries.APP_GRANTS import GRANTS_BY_SECTOR
from py_queries.AYUDAS import DETALLE_DE_AYUDAS


_PLACEHOLDER_RE = re.compile(r"\{\s*(\w+)\s*\}")


class DataverseRealtimeService:
    """Ejecuta consultas FetchXML en tiempo real a partir de plantillas en disco."""

    def __init__(self, xml_root: Path | None = None, client: DataverseClient | None = None) -> None:
        self.xml_root = xml_root
        self.client = client or DataverseClient()

        self.catalog: dict[str, dict[str, Any]] = {
            "citas_semana_en_curso": {
                "entity_name": "appointments",
                "template": CITAS_SEMANA_EN_CURSO,
                "columns_map": COLUMNS,
            },
            "citas_por_comercial_semana_en_curso": {
                "entity_name": "appointments",
                "template": CITAS_POR_COMERCIAL_SEMANA_EN_CURSO,
                "columns_map": COLUMNS,
            },
            "citas_12va_semana_atras": {
                "entity_name": "appointments",
                "template": CITAS_12VA_SEMANA_ATRAS,
                "columns_map": COLUMNS,
            },
            "citas_por_comercial_12va_semana_atras": {
                "entity_name": "appointments",
                "template": CITAS_POR_COMERCIAL_12VA_SEMANA_ATRAS,
                "columns_map": COLUMNS,
            },
            "citas_por_gestor_12va_semana_atras": {
                "entity_name": "appointments",
                "template": CITAS_POR_GESTOR_12VA_SEMANA_ATRAS,
                "columns_map": COLUMNS,
            },
            "citas_por_gestor_semana_en_curso": {
                "entity_name": "appointments",
                "template": CITAS_POR_GESTOR_SEMANA_EN_CURSO,
                "columns_map": COLUMNS,
            },
            "citas_por_comercial": {
                "entity_name": "appointments",
                "template": CITAS_POR_COMERCIAL,
                "columns_map": COLUMNS,
            },
            "citas_por_gestor": {
                "entity_name": "appointments",
                "template": CITAS_POR_GESTOR,
                "columns_map": COLUMNS,
            },
            "citas_por_cuenta": {
                "entity_name": "appointments",
                "template": CITAS_POR_CUENTA,
                "columns_map": COLUMNS,
            },
            "citas_por_nif": {
                "entity_name": "appointments",
                "template": CITAS_POR_NIF,
                "columns_map": COLUMNS,
            },
            "llamadas_semana_en_curso": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_SEMANA_EN_CURSO,
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_comercial_semana_en_curso": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_POR_COMERCIAL_SEMANA_EN_CURSO,
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_gestor_semana_en_curso": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_POR_GESTOR_SEMANA_EN_CURSO,
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_comercial": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_POR_COMERCIAL,
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_gestor": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_POR_GESTOR,
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_cuenta": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_POR_CUENTA,
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_nif": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_POR_NIF,
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "servicios_de_oportunidad_por_comercial": {
                "entity_name": "iav_opportunityservices",
                "template": SERVICIOS_DE_OPORTUNIDAD_POR_COMERCIAL,
                "columns_map": COLUMNS_HISTORICO_SERVICIOS,
            },
            "servicios_de_oportunidad_por_gestor": {
                "entity_name": "iav_opportunityservices",
                "template": SERVICIOS_DE_OPORTUNIDAD_POR_GESTOR,
                "columns_map": COLUMNS_HISTORICO_SERVICIOS,
            },
            "servicios_de_oportunidad_por_cuenta": {
                "entity_name": "iav_opportunityservices",
                "template": SERVICIOS_DE_OPORTUNIDAD_POR_CUENTA,
                "columns_map": COLUMNS_HISTORICO_SERVICIOS,
            },
            "servicios_de_oportunidad_por_nif": {
                "entity_name": "iav_opportunityservices",
                "template": SERVICIOS_DE_OPORTUNIDAD_POR_NIF,
                "columns_map": COLUMNS_HISTORICO_SERVICIOS,
            },
            "llamadas_abiertas": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_ABIERTAS,
                "columns_map": COLUMNS_LLAMADAS_ESTADO_CALIENTE,
            },            
            "llamadas_abiertas_por_cuenta": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_ABIERTAS_POR_CUENTA,
                "columns_map": COLUMNS_LLAMADAS_ESTADO_CALIENTE,
            },
            "llamadas_abiertas_por_nif": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_ABIERTAS_POR_NIF,
                "columns_map": COLUMNS_LLAMADAS_ESTADO_CALIENTE,
            },
            "llamadas_abiertas_por_comercial": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_ABIERTAS_POR_COMERCIAL,
                "columns_map": COLUMNS_LLAMADAS_ESTADO_CALIENTE,
            },
            "llamadas_abiertas_por_gestor": {
                "entity_name": "phonecalls",
                "template": LLAMADAS_ABIERTAS_POR_GESTOR,
                "columns_map": COLUMNS_LLAMADAS_ESTADO_CALIENTE,
            },
            "leads_abiertos_por_comercial": {
                "entity_name": "leads",
                "template": LEADS_ABIERTOS_POR_COMERCIAL,
                "columns_map": COLUMNS_LEADS,
            },
            "leads_abiertos_por_gestor": {
                "entity_name": "leads",
                "template": LEADS_ABIERTOS_POR_GESTOR,
                "columns_map": COLUMNS_LEADS,
            },
            "leads_abiertos_por_cuenta": {
                "entity_name": "leads",
                "template": LEADS_ABIERTOS_POR_CUENTA,
                "columns_map": COLUMNS_LEADS,
            },
            "leads_abiertos_por_nif": {
                "entity_name": "leads",
                "template": LEADS_ABIERTOS_POR_NIF,
                "columns_map": COLUMNS_LEADS,
            },
            "servicios_de_oportunidad_abierta_por_comercial": {
                "entity_name": "iav_opportunityservices",
                "template": SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_COMERCIAL,
                "columns_map": COLUMNS_OPORTUNIDADES_ABIERTAS,
            },
            "servicios_de_oportunidad_abierta_por_gestor": {
                "entity_name": "iav_opportunityservices",
                "template": SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_GESTOR,
                "columns_map": COLUMNS_OPORTUNIDADES_ABIERTAS,
            },
            "servicios_de_oportunidad_abierta_por_cuenta": {
                "entity_name": "iav_opportunityservices",
                "template": SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_CUENTA,
                "columns_map": COLUMNS_OPORTUNIDADES_ABIERTAS,
            },
            "servicios_de_oportunidad_abierta_por_nif": {
                "entity_name": "iav_opportunityservices",
                "template": SERVICIOS_DE_OPORTUNIDAD_ABIERTA_POR_NIF,
                "columns_map": COLUMNS_OPORTUNIDADES_ABIERTAS,
            },
            "citas_con_interes_futuro_por_comercial": {
                "entity_name": "appointments",
                "template": CITAS_CON_INTERES_FUTURO_POR_COMERCIAL,
                "columns_map": COLUMNS_OFERTAS_PENDIENTES,
            },
            "citas_con_interes_futuro_por_gestor": {
                "entity_name": "appointments",
                "template": CITAS_CON_INTERES_FUTURO_POR_GESTOR,
                "columns_map": COLUMNS_OFERTAS_PENDIENTES,
            },
            "citas_con_interes_futuro_por_cuenta": {
                "entity_name": "appointments",
                "template": CITAS_CON_INTERES_FUTURO_POR_CUENTA,
                "columns_map": COLUMNS_OFERTAS_PENDIENTES,
            },
            "citas_con_interes_futuro_por_nif": {
                "entity_name": "appointments",
                "template": CITAS_CON_INTERES_FUTURO_POR_NIF,
                "columns_map": COLUMNS_OFERTAS_PENDIENTES,
            },
            "cuentas_llamadas_ano_en_curso": {
                "entity_name": "accounts",
                "template": CUENTAS_LLAMADAS_ANO_EN_CURSO,
                "columns_map": COLUMNS_CUENTAS_LLAMADAS_ANO_EN_CURSO,
            },            
            "citas_abiertas_por_comercial_semana_en_curso": {
                "entity_name": "appointments",
                "template": CITAS_ABIERTAS_POR_COMERCIAL_SEMANA_EN_CURSO,
                "columns_map": COLUMNS,
            },
            "citas_abiertas_por_gestor_semana_en_curso": {
                "entity_name": "appointments",
                "template": CITAS_ABIERTAS_POR_GESTOR_SEMANA_EN_CURSO,
                "columns_map": COLUMNS,
            },
            "citas_canceladas_por_comercial_ano_en_curso": {
                "entity_name": "appointments",
                "template": CITAS_CANCELADAS_POR_COMERCIAL_ANO_EN_CURSO,
                "columns_map": COLUMNS,
            },
            "citas_canceladas_por_gestor_ano_en_curso": {
                "entity_name": "appointments",
                "template": CITAS_CANCELADAS_POR_GESTOR_ANO_EN_CURSO,
                "columns_map": COLUMNS,
            },
            "citas_canceladas_por_cuenta_ano_en_curso": {
                "entity_name": "appointments",
                "template": CITAS_CANCELADAS_POR_CUENTA_ANO_EN_CURSO,
                "columns_map": COLUMNS,
            },            
            "citas_canceladas_por_nif_ano_en_curso": {
                "entity_name": "appointments",
                "template": CITAS_CANCELADAS_POR_NIF_ANO_EN_CURSO,
                "columns_map": COLUMNS,
            },
            "citas_por_comercial_sin_llamada_posterior_6_meses": {
                "entity_name": "appointments",
                "template": CITAS_POR_COMERCIAL_SIN_LLAMADA_POSTERIOR_6_MESES,
                "columns_map": COLUMNS,
            },
            "citas_por_gestor_sin_llamada_posterior_6_meses": {
                "entity_name": "appointments",
                "template": CITAS_POR_GESTOR_SIN_LLAMADA_POSTERIOR_6_MESES,
                "columns_map": COLUMNS,
            },
        }


    def execute_query(self, query_name: str, **kwargs: str) -> list[dict]:
        entry = self.catalog[query_name]
        entity_name: str = entry["entity_name"]
        template: str = entry["template"]
        columns_map: dict = entry["columns_map"]

        fetch_xml = _PLACEHOLDER_RE.sub(
            lambda m: escape(kwargs[m.group(1)]),
            template,
        )

        raw = self.client.send_request(entity_name, fetch_xml)
        df = json_to_dataframe(raw)
        df = process_dataframe(df, columns_map)
        return df.to_dict(orient="records")

    def get_citas_semana_en_curso(self) -> list[dict]:
        return self.execute_query("citas_semana_en_curso")
    
    def get_citas_12va_semana_atras(self, START_DATE: str, END_DATE: str) -> list[dict]:
        return self.execute_query("citas_12va_semana_atras", START_DATE=START_DATE, END_DATE=END_DATE)

    def get_citas_por_comercial_semana_en_curso(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_por_comercial_semana_en_curso", EMAIL_USUARIO=EMAIL_USUARIO)

    def get_citas_por_gestor_semana_en_curso(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_por_gestor_semana_en_curso", EMAIL_USUARIO=EMAIL_USUARIO)

    def get_citas_por_comercial(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_por_comercial", EMAIL_USUARIO=EMAIL_USUARIO)

    def get_citas_por_comercial_12va_semana_atras(self, START_DATE: str, END_DATE: str, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_por_comercial_12va_semana_atras", START_DATE=START_DATE, END_DATE=END_DATE, EMAIL_USUARIO=EMAIL_USUARIO)

    def get_citas_por_gestor_12va_semana_atras(self, START_DATE: str, END_DATE: str, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_por_gestor_12va_semana_atras", START_DATE=START_DATE, END_DATE=END_DATE, EMAIL_USUARIO=EMAIL_USUARIO)

    def get_citas_por_gestor(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_por_gestor", EMAIL_USUARIO=EMAIL_USUARIO)

    def get_citas_por_cuenta(self, NOMBRE_DE_CUENTA: str) -> list[dict]:
        return self.execute_query("citas_por_cuenta", NOMBRE_DE_CUENTA=NOMBRE_DE_CUENTA)
    
    def get_citas_por_nif(self, NIF: str) -> list[dict]:
        return self.execute_query("citas_por_nif", NIF=NIF)

    def get_llamadas_semana_en_curso(self) -> list[dict]:
        return self.execute_query("llamadas_semana_en_curso")

    def get_llamadas_por_comercial_semana_en_curso(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("llamadas_por_comercial_semana_en_curso", EMAIL_USUARIO=EMAIL_USUARIO)

    def get_llamadas_por_gestor_semana_en_curso(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("llamadas_por_gestor_semana_en_curso", EMAIL_USUARIO=EMAIL_USUARIO)

    def get_llamadas_por_comercial(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("llamadas_por_comercial", EMAIL_USUARIO=EMAIL_USUARIO)

    def get_llamadas_por_gestor(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("llamadas_por_gestor", EMAIL_USUARIO=EMAIL_USUARIO)

    def get_llamadas_por_cuenta(self, NOMBRE_DE_CUENTA: str) -> list[dict]:
        return self.execute_query("llamadas_por_cuenta", NOMBRE_DE_CUENTA=NOMBRE_DE_CUENTA)

    def get_llamadas_por_nif(self, NIF: str) -> list[dict]:
        return self.execute_query("llamadas_por_nif", NIF=NIF)

    def get_servicios_de_oportunidad_por_comercial(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("servicios_de_oportunidad_por_comercial", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_servicios_de_oportunidad_por_gestor(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("servicios_de_oportunidad_por_gestor", EMAIL_USUARIO=EMAIL_USUARIO)

    def get_servicios_de_oportunidad_por_cuenta(self, NOMBRE_DE_CUENTA: str) -> list[dict]:
        return self.execute_query("servicios_de_oportunidad_por_cuenta", NOMBRE_DE_CUENTA=NOMBRE_DE_CUENTA)

    def get_servicios_de_oportunidad_por_nif(self, NIF: str) -> list[dict]:
        return self.execute_query("servicios_de_oportunidad_por_nif", NIF=NIF)
    
    def get_llamadas_abiertas(self, CURRENT_DATE: str) -> list[dict]:
        return self.execute_query("llamadas_abiertas", CURRENT_DATE=CURRENT_DATE)
    
    def get_llamadas_abiertas_por_cuenta(self, NOMBRE_DE_CUENTA: str, CURRENT_DATE: str) -> list[dict]:
        return self.execute_query("llamadas_abiertas_por_cuenta", NOMBRE_DE_CUENTA=NOMBRE_DE_CUENTA, CURRENT_DATE=CURRENT_DATE)
    
    def get_llamadas_abiertas_por_nif(self, NIF: str, CURRENT_DATE: str) -> list[dict]:
        return self.execute_query("llamadas_abiertas_por_nif", NIF=NIF, CURRENT_DATE=CURRENT_DATE)
    
    def get_llamadas_abiertas_por_comercial(self, EMAIL_USUARIO: str, CURRENT_DATE: str) -> list[dict]:
        return self.execute_query("llamadas_abiertas_por_comercial", EMAIL_USUARIO=EMAIL_USUARIO, CURRENT_DATE=CURRENT_DATE)
    
    def get_llamadas_abiertas_por_gestor(self, EMAIL_USUARIO: str, CURRENT_DATE: str) -> list[dict]:
        return self.execute_query("llamadas_abiertas_por_gestor", EMAIL_USUARIO=EMAIL_USUARIO, CURRENT_DATE=CURRENT_DATE)
    
    def get_leads_abiertos_por_comercial(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("leads_abiertos_por_comercial", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_leads_abiertos_por_gestor(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("leads_abiertos_por_gestor", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_leads_abiertos_por_cuenta(self, NOMBRE_DE_CUENTA: str) -> list[dict]:
        return self.execute_query("leads_abiertos_por_cuenta", NOMBRE_DE_CUENTA=NOMBRE_DE_CUENTA)
    
    def get_leads_abiertos_por_nif(self, NIF: str) -> list[dict]:
        return self.execute_query("leads_abiertos_por_nif", NIF=NIF)
    
    def get_servicios_de_oportunidad_abierta_por_gestor(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("servicios_de_oportunidad_abierta_por_gestor", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_servicios_de_oportunidad_abierta_por_comercial(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("servicios_de_oportunidad_abierta_por_comercial", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_servicios_de_oportunidad_abierta_por_cuenta(self, NOMBRE_DE_CUENTA: str) -> list[dict]:
        return self.execute_query("servicios_de_oportunidad_abierta_por_cuenta", NOMBRE_DE_CUENTA=NOMBRE_DE_CUENTA)
    
    def get_servicios_de_oportunidad_abierta_por_nif(self, NIF: str) -> list[dict]:
        return self.execute_query("servicios_de_oportunidad_abierta_por_nif", NIF=NIF)
    
    def get_citas_con_interes_futuro_por_comercial(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_con_interes_futuro_por_comercial", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_citas_con_interes_futuro_por_gestor(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_con_interes_futuro_por_gestor", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_citas_con_interes_futuro_por_cuenta(self, NOMBRE_DE_CUENTA: str) -> list[dict]:
        return self.execute_query("citas_con_interes_futuro_por_cuenta", NOMBRE_DE_CUENTA=NOMBRE_DE_CUENTA)
    
    def get_citas_con_interes_futuro_por_nif(self, NIF: str) -> list[dict]:
        return self.execute_query("citas_con_interes_futuro_por_nif", NIF=NIF)
    
    def get_cuentas_llamadas_ano_en_curso(self) -> list[dict]:
        return self.execute_query("cuentas_llamadas_ano_en_curso")
    
    def get_citas_abiertas_por_comercial_semana_en_curso(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_abiertas_por_comercial_semana_en_curso", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_citas_abiertas_por_gestor_semana_en_curso(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_abiertas_por_gestor_semana_en_curso", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_citas_canceladas_por_comercial_ano_en_curso(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_canceladas_por_comercial_ano_en_curso", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_citas_canceladas_por_gestor_ano_en_curso(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_canceladas_por_gestor_ano_en_curso", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_citas_canceladas_por_cuenta_ano_en_curso(self, NOMBRE_DE_CUENTA: str) -> list[dict]:
        return self.execute_query("citas_canceladas_por_cuenta_ano_en_curso", NOMBRE_DE_CUENTA=NOMBRE_DE_CUENTA)
    
    def get_citas_canceladas_por_nif_ano_en_curso(self, NIF: str) -> list[dict]:
        return self.execute_query("citas_canceladas_por_nif_ano_en_curso", NIF=NIF)
    
    def get_citas_por_comercial_sin_llamada_posterior_6_meses(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_por_comercial_sin_llamada_posterior_6_meses", EMAIL_USUARIO=EMAIL_USUARIO)
    
    def get_citas_por_gestor_sin_llamada_posterior_6_meses(self, EMAIL_USUARIO: str) -> list[dict]:
        return self.execute_query("citas_por_comercial_sin_llamada_posterior_6_meses", EMAIL_USUARIO=EMAIL_USUARIO)


class SQLRealtimeService:
    """Ejecuta consultas SQL en tiempo real a partir de plantillas en disco."""

    def __init__(self, bdns_client: BDNSClient | None = None, grants_client: GRANTSClient | None = None) -> None:
        self.bdns_client = bdns_client or BDNSClient()
        self.grants_client = grants_client or GRANTSClient()

        self.catalog: dict[str, dict[str, Any]] = {
            "detalle_ayudas": {
                "template": DETALLE_DE_AYUDAS,
                "columns_map": COLUMNS_HISTORICO_BDNS,
                "client_type": "bdns",
            },
            "convocatorias_abiertas": {
                "template": GRANTS_BY_SECTOR,
                "columns_map": {
                    "TÍTULO": "Title",
                    "SECTOR": "Name",
                },
                "client_type": "grants",
            },
        }

    def execute_query(self, query_name: str, **kwargs: str) -> list[dict]:
        entry = self.catalog[query_name]
        template: str = entry["template"]
        columns_map: dict = entry["columns_map"]
        client_type: str = entry.get("client_type", "bdns")

        # Sanitizar valores
        sanitized = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                sanitized[key] = f"'{value.replace("'", "''")}'"
            else:
                sanitized[key] = value

        sql = template.format(**sanitized)

        # Seleccionar el cliente según el tipo de consulta
        client = self.grants_client if client_type == "grants" else self.bdns_client

        with client as db_client:
            df = db_client.execute_query(sql)

        # Renombrar columnas según el mapeo
        if columns_map:
            reverse_map = {v: k for k, v in columns_map.items()}
            df.rename(columns=reverse_map, inplace=True)

        return df.to_dict(orient="records")

    def get_detalle_ayudas(self, ACCOUNT_NIF: str) -> list[dict]:
        return self.execute_query("detalle_ayudas", ACCOUNT_NIF=ACCOUNT_NIF)

    def get_convocatorias_abiertas(self, SECTOR_GRANTS: str) -> list[dict]:
        return self.execute_query("convocatorias_abiertas", SECTOR_GRANTS=SECTOR_GRANTS)


# ── Plan de Cuentas Service ────────────────────────────────────────────────

import pandas as pd


class PlanCuentasService:
    """Lee y filtra el fichero 'plan de cuentas.xlsx'."""

    COLUMNS_CONFIG = ["NIF", "Número de cuenta", "Nombre de cuenta", "Group Alias", "Sector FI", "Gasto anual I+D+i", "Gestor de Cuenta"]

    def __init__(self, excel_path: Path | None = None) -> None:
        self.excel_path = excel_path or Path(__file__).resolve().parent.parent / "scripts" / "resources" / "plan de cuentas.xlsx"

    def _check_exists(self) -> None:
        if not self.excel_path.exists():
            raise FileNotFoundError(f"El fichero del plan de cuentas no existe: {self.excel_path}")

    def get_cuentas_por_gestor(self, nombre_usuario: str) -> list[dict]:
        """Filtra la hoja 'CUENTAS COMERCIAL - ADMIN' por la columna 'Gestor de Cuenta' y devuelve solo las columnas configuradas."""
        self._check_exists()
        df = pd.read_excel(self.excel_path, sheet_name="CUENTAS COMERCIAL - ADMIN", dtype=str)
        col = "Gestor de Cuenta"
        if col not in df.columns:
            raise ValueError(f"La hoja 'CUENTAS COMERCIAL - ADMIN' no contiene la columna '{col}'.")
        filtered = df[df[col].str.lower() == nombre_usuario.strip().lower()]
        
        missing = set(self.COLUMNS_CONFIG) - set(filtered.columns)
        if missing:
            raise ValueError(f"Columnas faltantes en la hoja: {missing}")
        
        selected = filtered[self.COLUMNS_CONFIG]
        return selected.where(pd.notna(selected), other=None).to_dict(orient="records")

    def get_cuentas_pendientes_de_llamar(self, gestor: str, dataverse_service: DataverseRealtimeService) -> list[dict]:
        """
        Retorna las cuentas asignadas a un gestor según el plan de cuentas oficial
        que aún no han sido llamadas en el año actual (según Dataverse).

        Args:
            gestor: Correo electrónico o nombre del gestor de cuenta.
            dataverse_service: Instancia de DataverseRealtimeService para consultar llamadas.

        Returns:
            Lista de cuentas pendientes de llamar.
        """
        # Obtener todas las cuentas del plan para este gestor
        df_plan = pd.read_excel(self.excel_path, sheet_name="CUENTAS COMERCIAL - ADMIN", dtype=str)
        
        col_gestor = "Gestor de Cuenta"
        if col_gestor not in df_plan.columns:
            raise ValueError(f"La hoja 'CUENTAS COMERCIAL - ADMIN' no contiene la columna '{col_gestor}'.")
        
        df_gestor = df_plan[df_plan[col_gestor].str.lower() == gestor.strip().lower()].copy()
        
        if df_gestor.empty:
            #logger.warning("No se encontraron cuentas para el gestor '%s' en el plan de cuentas.", gestor)
            return []
        
        # Obtener conjunto de números de cuenta ya llamadas este año desde Dataverse
        cuentas_llamadas = dataverse_service.get_cuentas_llamadas_ano_en_curso()
        numeros_con_llamada = set()
        for cuenta in cuentas_llamadas:
            num = cuenta.get("NÚMERO_DE_CUENTA")
            if num:
                numeros_con_llamada.add(num.strip().lower())
        
        # Filtrar: solo cuentas que tienen número Y NO están en llamadas
        numero_col = "Número de cuenta"
        if numero_col not in df_gestor.columns:
            raise ValueError(f"La hoja 'CUENTAS COMERCIAL - ADMIN' no contiene la columna '{numero_col}'.")
        
        df_gestor[numero_col.lower()] = df_gestor[numero_col].astype(str).str.lower().str.strip()
        df_sin_llamar = df_gestor[~df_gestor[numero_col.lower()].isin(numeros_con_llamada)].drop(columns=[numero_col.lower()], errors="ignore").copy()
        
        #logger.info("Cuentas del gestor '%s': total=%d | ya_llamadas=%d | pendientes=%d",
        #           gestor, len(df_gestor), len(numeros_con_llamada & set(df_gestor[numero_col].astype(str).str.lower().str.strip())),
        #           len(df_sin_llamar))
        
        # Seleccionar solo las columnas configuradas
        missing_cols = set(self.COLUMNS_CONFIG) - set(df_sin_llamar.columns)
        if missing_cols:
            raise ValueError(f"Columnas faltantes en la hoja: {missing_cols}")
        
        selected = df_sin_llamar[self.COLUMNS_CONFIG]
        return selected.where(pd.notna(selected), other=None).to_dict(orient="records")