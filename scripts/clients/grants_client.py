import os
from pathlib import Path

from dotenv import load_dotenv

from .sql_client import SQLClient

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class GRANTSClient(SQLClient):
    """
    Cliente para la base de datos GRANTS. Usa SQL Server Authentication estándar.
    """

    def __init__(
        self,
        server: str | None = None,
        database: str | None = None,
        username: str | None = None,
        password: str | None = None,
        driver: str | None = None,
    ):
        """
        Inicializa el cliente GRANTS construyendo la cadena de conexión ODBC.

        Los parámetros son opcionales; si no se proporcionan se leen de las
        variables de entorno: GRANTS_SERVER, GRANTS_DATABASE, GRANTS_USERNAME,
        GRANTS_PASSWORD y SQL_DRIVER.

        Args:
            server (str | None): Nombre o IP del servidor SQL.
            database (str | None): Nombre de la base de datos.
            username (str | None): Usuario SQL.
            password (str | None): Contraseña del usuario.
            driver (str | None): Nombre del driver ODBC instalado.
        """
        server = server or os.environ["GRANTS_SERVER"]
        database = database or os.environ["GRANTS_DATABASE"]
        username = username or os.environ["GRANTS_USERNAME"]
        password = password or os.environ["GRANTS_PASSWORD"]
        driver = driver or os.environ.get("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=60;"
        )
        super().__init__(connection_string)
