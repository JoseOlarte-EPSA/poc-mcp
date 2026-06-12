import logging

import pandas as pd
import pyodbc

logger = logging.getLogger(__name__)


class SQLClient:
    """
    Clase base para clientes SQL Server. Gestiona la conexion y ejecucion de consultas.
    """

    def __init__(self, connection_string: str):
        """
        Args:
            connection_string (str): Cadena de conexión ODBC completa.
        """
        self.connection_string = connection_string
        self._conn = None

    def __enter__(self):
        """Abre la conexión al entrar en el bloque `with`."""
        self._conn = pyodbc.connect(self.connection_string)
        return self

    def __exit__(self, *args):
        """Cierra la conexión al salir del bloque `with`."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL y devuelve el resultado como DataFrame.

        Reutiliza la conexión activa si existe (modo context manager);
        en caso contrario abre y cierra una conexión temporal.

        Args:
            query (str): Sentencia SQL a ejecutar.

        Returns:
            pd.DataFrame: Resultado de la consulta.
        """
        if self._conn:
            return pd.read_sql(query, self._conn)
        with pyodbc.connect(self.connection_string) as conn:
            return pd.read_sql(query, conn)
