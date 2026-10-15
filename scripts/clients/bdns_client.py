import os
from pathlib import Path

from dotenv import load_dotenv

from .sql_client import SQLClient

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class BDNSClient(SQLClient):
    """
    Cliente para el endpoint SQL de Fabric (warehouse oro, esquema `bdns`).
    Autentica con una aplicación registrada (service principal) usando el modo
    nativo Authentication=ActiveDirectoryServicePrincipal de ODBC Driver 18.
    """

    def __init__(
        self,
        server: str | None = None,
        database: str | None = None,
        tenant_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        driver: str | None = None,
    ):
        """
        Inicializa el cliente BDNS construyendo la cadena de conexión ODBC.

        Los parámetros son opcionales; si no se proporcionan se leen de las
        variables de entorno: FABRIC_SQL_ENDPOINT, FABRIC_DATABASE,
        FABRIC_TENANT_ID, FABRIC_CLIENT_ID, FABRIC_CLIENT_SECRET y SQL_DRIVER.

        Args:
            server (str | None): Endpoint SQL, p.ej. empresa.datawarehouse.fabric.microsoft.com.
            database (str | None): Nombre del warehouse o lakehouse (base de datos).
            tenant_id (str | None): ID del directorio (tenant) donde está registrada la app.
            client_id (str | None): Application (client) ID de la aplicación registrada.
            client_secret (str | None): Secreto (credential tipo password) de la aplicación.
            driver (str | None): Nombre del driver ODBC instalado (18.1 o superior).
        """
        server = server or os.environ["FABRIC_SQL_ENDPOINT"]
        database = database or os.environ["FABRIC_DATABASE"]
        tenant_id = tenant_id or os.environ["FABRIC_TENANT_ID"]
        client_id = client_id or os.environ["FABRIC_CLIENT_ID"]
        client_secret = client_secret or os.environ["FABRIC_CLIENT_SECRET"]
        driver = driver or os.environ.get("SQL_DRIVER", "ODBC Driver 18 for SQL Server")
        # tenant_id se valida (debe existir en el entorno); en este modo el driver
        # lo resuelve del token y el UID es solo el client_id (igual que FabricClient
        # de IN Focus).
        uid = client_id
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Authentication=ActiveDirectoryServicePrincipal;"
            f"UID={uid};"
            f"PWD={client_secret};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            # Fabric sirve el certificado *.datawarehouse.fabric.microsoft.com en este puerto.
            "HostNameInCertificate=*.datawarehouse.fabric.microsoft.com;"
            "Connection Timeout=60;"
        )
        super().__init__(connection_string)
