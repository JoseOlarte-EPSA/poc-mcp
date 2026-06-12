import json
import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

logger = logging.getLogger(__name__)


class DataverseClient:
    """
    Cliente para interactuar con Dataverse mediante FetchXML.
    """

    def __init__(self, url: str | None = None, timeout: int | None = None):
        """
        Inicializa el cliente Dataverse.

        Los parámetros son opcionales; si no se proporcionan se leen de las
        variables de entorno: DATAVERSE_URL y TIMEOUT.

        Args:
            url (str | None): URL base del endpoint Dataverse.
            timeout (int | None): Tiempo máximo de espera en segundos para cada petición.
        """
        self.url = url or os.environ["DATAVERSE_URL"]
        self.timeout = timeout or int(os.environ.get("TIMEOUT", "300"))

    def send_request(self, entity_name: str, fetch_xml: str) -> str:
        """
        Envía una solicitud HTTP a Dataverse usando FetchXML.

        Args:
            entity_name (str): Nombre de la entidad.
            fetch_xml (str): Consulta FetchXML.

        Returns:
            str: Respuesta del servidor.

        Raises:
            RuntimeError: Si ocurre un error en la solicitud HTTP.
        """
        data = {
            "entityName": entity_name,
            "fetchXml": fetch_xml
        }

        try:
            response = requests.post(
                self.url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data),
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error al enviar la solicitud a Dataverse [{entity_name}]: {e}") from e
