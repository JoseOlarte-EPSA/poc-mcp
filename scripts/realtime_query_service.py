from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from scripts.clients.dataverse import DataverseClient
from scripts.config.columns import COLUMNS, COLUMNS_HISTORICO_LLAMADAS
from scripts.utils import json_to_dataframe, process_dataframe


_PLACEHOLDER_RE = re.compile(r"\{\{\s*(.*?)\s*\}\}")


class DataverseRealtimeService:
    """Ejecuta consultas FetchXML en tiempo real a partir de plantillas en disco."""

    def __init__(self, xml_root: Path, client: DataverseClient | None = None) -> None:
        self.xml_root = xml_root
        self.client = client

        # Alias para placeholders heredados en XML existentes.
        self.placeholder_aliases = {
            "ismael.olmedo@fi-group.com": "email",
            "nombre de la cuenta": "nombre_cuenta",
        }

        self.catalog: dict[str, dict[str, Any]] = {
            "citas_semana_en_curso": {
                "entity_name": "appointments",
                "xml_path": self.xml_root / "citas" / "citas_semana_en_curso.xml",
                "columns_map": COLUMNS,
            },
            "citas_por_comercial_semana_en_curso": {
                "entity_name": "appointments",
                "xml_path": self.xml_root / "citas" / "citas_por_comercial_semana_en_curso.xml",
                "columns_map": COLUMNS,
            },
            "citas_por_gestor_semana_en_curso": {
                "entity_name": "appointments",
                "xml_path": self.xml_root / "citas" / "citas_por_gestor_semana_en_curso.xml",
                "columns_map": COLUMNS,
            },
            "citas_por_comercial": {
                "entity_name": "appointments",
                "xml_path": self.xml_root / "citas" / "citas_por_comercial.xml",
                "columns_map": COLUMNS,
            },
            "citas_por_gestor": {
                "entity_name": "appointments",
                "xml_path": self.xml_root / "citas" / "citas_por_gestor.xml",
                "columns_map": COLUMNS,
            },
            "citas_por_cuenta": {
                "entity_name": "appointments",
                "xml_path": self.xml_root / "citas" / "citas_por_cuenta.xml",
                "columns_map": COLUMNS,
            },
            "llamadas_semana_en_curso": {
                "entity_name": "phonecalls",
                "xml_path": self.xml_root / "llamadas" / "llamadas_semana_en_curso.xml",
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_comercial_semana_en_curso": {
                "entity_name": "phonecalls",
                "xml_path": self.xml_root / "llamadas" / "llamadas_por_comercial_semana_en_curso.xml",
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_gestor_semana_en_curso": {
                "entity_name": "phonecalls",
                "xml_path": self.xml_root / "llamadas" / "llamadas_por_gestor_semana_en_curso.xml",
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_comercial": {
                "entity_name": "phonecalls",
                "xml_path": self.xml_root / "llamadas" / "llamadas_por_comercial.xml",
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_gestor": {
                "entity_name": "phonecalls",
                "xml_path": self.xml_root / "llamadas" / "llamadas_por_gestor.xml",
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
            "llamadas_por_cuenta": {
                "entity_name": "phonecalls",
                "xml_path": self.xml_root / "llamadas" / "llamadas_por_cuenta.xml",
                "columns_map": COLUMNS_HISTORICO_LLAMADAS,
            },
        }

        self._validate_catalog()

    def _validate_catalog(self) -> None:
        missing_files = [
            key for key, meta in self.catalog.items() if not Path(meta["xml_path"]).is_file()
        ]
        if missing_files:
            joined = ", ".join(sorted(missing_files))
            raise FileNotFoundError(f"No se encontraron plantillas XML para: {joined}")

    def _load_xml_template(self, query_key: str) -> str:
        if query_key not in self.catalog:
            raise KeyError(f"Query key no soportada: {query_key}")

        xml_path = Path(self.catalog[query_key]["xml_path"])
        return xml_path.read_text(encoding="utf-8")

    def _resolve_placeholder_name(self, placeholder_name: str) -> str:
        return self.placeholder_aliases.get(placeholder_name, placeholder_name)

    def _render_template(self, template: str, params: dict[str, Any]) -> str:
        placeholders = _PLACEHOLDER_RE.findall(template)
        if not placeholders:
            return template

        missing: list[str] = []
        rendered = template

        for raw_name in placeholders:
            canonical_name = self._resolve_placeholder_name(raw_name)
            value = params.get(canonical_name, params.get(raw_name))
            if value is None:
                missing.append(canonical_name)
                continue

            # Escape XML entities to avoid invalid FetchXML when values include &, <, >.
            safe_value = escape(str(value).strip())
            rendered = re.sub(
                rf"\{{\{{\s*{re.escape(raw_name)}\s*\}}\}}",
                safe_value,
                rendered,
            )

        if missing:
            required = ", ".join(sorted(set(missing)))
            raise ValueError(f"Faltan parametros para la query: {required}")

        return rendered

    def execute_query(self, query_key: str, **params: Any) -> list[dict]:
        meta = self.catalog.get(query_key)
        if meta is None:
            raise KeyError(f"Query key no soportada: {query_key}")

        template = self._load_xml_template(query_key)
        fetch_xml = self._render_template(template, params)
        client = self.client or DataverseClient()
        raw_response = client.send_request(meta["entity_name"], fetch_xml)

        df = json_to_dataframe(raw_response)
        processed = process_dataframe(df, meta["columns_map"])
        return processed.where(processed.notna(), None).to_dict(orient="records")

    def get_citas_semana_en_curso(self) -> list[dict]:
        return self.execute_query("citas_semana_en_curso")

    def get_citas_por_comercial_semana_en_curso(self, email: str) -> list[dict]:
        return self.execute_query("citas_por_comercial_semana_en_curso", email=email)

    def get_citas_por_gestor_semana_en_curso(self, email: str) -> list[dict]:
        return self.execute_query("citas_por_gestor_semana_en_curso", email=email)

    def get_citas_por_comercial(self, email: str) -> list[dict]:
        return self.execute_query("citas_por_comercial", email=email)

    def get_citas_por_gestor(self, email: str) -> list[dict]:
        return self.execute_query("citas_por_gestor", email=email)

    def get_citas_por_cuenta(self, nombre_cuenta: str) -> list[dict]:
        return self.execute_query("citas_por_cuenta", nombre_cuenta=nombre_cuenta)

    def get_llamadas_semana_en_curso(self) -> list[dict]:
        return self.execute_query("llamadas_semana_en_curso")

    def get_llamadas_por_comercial_semana_en_curso(self, email: str) -> list[dict]:
        return self.execute_query("llamadas_por_comercial_semana_en_curso", email=email)

    def get_llamadas_por_gestor_semana_en_curso(self, email: str) -> list[dict]:
        return self.execute_query("llamadas_por_gestor_semana_en_curso", email=email)

    def get_llamadas_por_comercial(self, email: str) -> list[dict]:
        return self.execute_query("llamadas_por_comercial", email=email)

    def get_llamadas_por_gestor(self, email: str) -> list[dict]:
        return self.execute_query("llamadas_por_gestor", email=email)

    def get_llamadas_por_cuenta(self, nombre_cuenta: str) -> list[dict]:
        return self.execute_query("llamadas_por_cuenta", nombre_cuenta=nombre_cuenta)
