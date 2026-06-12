import os
from pathlib import Path

from dotenv import load_dotenv

from .sql_client import SQLClient

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class BDNSClient(SQLClient):
    """
    Cliente para la base de datos BDNS. Usa ActiveDirectory Password Authentication.
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
        Inicializa el cliente BDNS construyendo la cadena de conexión ODBC.

        Los parámetros son opcionales; si no se proporcionan se leen de las
        variables de entorno: BDNS_SERVER, BDNS_DATABASE, BDNS_USERNAME,
        BDNS_PASSWORD y SQL_DRIVER.

        Args:
            server (str | None): Nombre o IP del servidor SQL.
            database (str | None): Nombre de la base de datos.
            username (str | None): Usuario de Active Directory.
            password (str | None): Contraseña del usuario.
            driver (str | None): Nombre del driver ODBC instalado.
        """
        server = server or os.environ["BDNS_SERVER"]
        database = database or os.environ["BDNS_DATABASE"]
        username = username or os.environ["BDNS_USERNAME"]
        password = password or os.environ["BDNS_PASSWORD"]
        driver = driver or os.environ.get("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "Encrypt=yes;"
            "Authentication=ActiveDirectoryPassword;"
            "TrustServerCertificate=no;"
            "Connection Timeout=60;"
        )
        super().__init__(connection_string)
