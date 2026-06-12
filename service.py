from __future__ import annotations

from pathlib import Path

import pandas as pd


class ExcelService:
    """Centraliza la lectura del fichero Excel generado por el proceso semanal."""

    def __init__(self, excel_path: Path) -> None:
        self.excel_path = excel_path

    def _check_exists(self) -> None:
        if not self.excel_path.exists():
            raise FileNotFoundError(f"El fichero Excel no existe: {self.excel_path}")

    def read_by_email(self, sheet_name: str, email: str, column_name: str) -> list[dict]:
        """Lee una hoja del Excel y filtra los registros por el tipo de usuario, usando la columna COMERCIAL O GESTOR (userType)."""
        self._check_exists()
        df = pd.read_excel(self.excel_path, sheet_name=sheet_name, dtype=str)
        if column_name not in df.columns:
            raise ValueError(f"La hoja '{sheet_name}' no contiene la columna '{column_name}'.")
        filtered = df[df[column_name].str.lower() == email.strip().lower()]
        return filtered.where(pd.notna(filtered), other=None).to_dict(orient="records")

    def read_by_sector(self, sector_grants: str) -> list[dict]:
        """Lee la hoja CONVOCATORIAS ABIERTAS y filtra por la columna SECTOR."""
        self._check_exists()
        df = pd.read_excel(self.excel_path, sheet_name="CONVOCATORIAS ABIERTAS", dtype=str)
        if "SECTOR" not in df.columns:
            raise ValueError("La hoja 'CONVOCATORIAS ABIERTAS' no contiene la columna 'SECTOR'.")
        filtered = df[df["SECTOR"].str.lower() == sector_grants.strip().lower()]
        return filtered.where(pd.notna(filtered), other=None).to_dict(orient="records")

    def read_by_nif(self, nif: str) -> list[dict]:
        """Lee la hoja SUBVENCIONES BDNS y filtra por la columna NIF."""
        self._check_exists()
        df = pd.read_excel(self.excel_path, sheet_name="SUBVENCIONES BDNS", dtype=str)
        if "NIF" not in df.columns:
            raise ValueError("La hoja 'SUBVENCIONES BDNS' no contiene la columna 'NIF'.")
        filtered = df[df["NIF"].str.lower() == nif.strip().lower()]
        return filtered.where(pd.notna(filtered), other=None).to_dict(orient="records")

    def read_by_cuenta(self, nombre_cuenta: str) -> list[dict]:
        """Lee la hoja RESUMEN DE NOTICIAS y filtra por la columna NOMBRE_DE_LA_CUENTA."""
        self._check_exists()
        df = pd.read_excel(self.excel_path, sheet_name="RESUMEN DE NOTICIAS", dtype=str)
        if "NOMBRE_DE_LA_CUENTA" not in df.columns:
            raise ValueError("La hoja 'RESUMEN DE NOTICIAS' no contiene la columna 'NOMBRE_DE_LA_CUENTA'.")
        filtered = df[df["NOMBRE_DE_LA_CUENTA"].str.lower() == nombre_cuenta.strip().lower()]
        return filtered.where(pd.notna(filtered), other=None).to_dict(orient="records")
    
    def read_by_cuenta_without_calls(self, nombre_usuario: str) -> list[dict]:
        """Lee la hoja CUENTAS SIN LLAMAR y filtra por la columna Gestor de Cuenta."""
        self._check_exists()
        df = pd.read_excel(self.excel_path, sheet_name="CUENTAS SIN LLAMAR", dtype=str)
        if "Gestor de Cuenta" not in df.columns:
            raise ValueError("La hoja 'CUENTAS SIN LLAMAR' no contiene la columna 'Gestor de Cuenta'.")
        filtered = df[df["Gestor de Cuenta"].str.lower() == nombre_usuario.strip().lower()]
        return filtered.where(pd.notna(filtered), other=None).to_dict(orient="records")
