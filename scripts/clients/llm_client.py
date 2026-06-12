import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from scripts.config.queries import PROMPTS

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

logger = logging.getLogger(__name__)

LLM_BASE_URL = "https://apps.fi-group.com/api/openai/chat/completions"
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")


def chat_completion(messages: list[dict], model: str = "Embeddings") -> dict:
    """
    Envía una lista de mensajes al LLM y devuelve la respuesta JSON completa.

    Args:
        messages (list[dict]): Lista de mensajes en formato OpenAI
                               (ej. [{"role": "user", "content": "..."}]).
        model (str): Identificador del modelo a usar. Por defecto "Embeddings".

    Returns:
        dict: Respuesta completa de la API en formato JSON.

    Raises:
        requests.exceptions.HTTPError: Si la API devuelve un código de error HTTP.
    """
    headers = {
        "Authorization": LLM_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
    }
    response = requests.post(LLM_BASE_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()


def ask(prompt: str, model: str = "Performance") -> str:
    """
    Envía un mensaje de usuario y devuelve únicamente el texto de respuesta del asistente.

    Args:
        prompt (str): Texto del mensaje a enviar al modelo.
        model (str): Identificador del modelo a usar. Por defecto "Performance".

    Returns:
        str: Texto de la respuesta generada por el asistente.
    """
    messages = [{"role": "user", "content": prompt}]
    result = chat_completion(messages, model=model)
    return result["choices"][0]["message"]["content"]


def summarize_news(titulo: str, contenido: str) -> str:
    """
    Genera un resumen de una noticia a partir de su título y contenido usando el LLM.

    Args:
        titulo (str): Título de la noticia (corresponde a la columna 'Título' del DataFrame).
        contenido (str): Cuerpo del artículo (corresponde a la columna 'Contenido' del DataFrame).

    Returns:
        str: Texto con el resumen generado por el modelo.
    """
    prompt = PROMPTS["summarize_news"].format(titulo=titulo, contenido=contenido)
    return ask(prompt)