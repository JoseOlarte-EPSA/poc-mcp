import logging
import os
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

logger = logging.getLogger(__name__)

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", "")
SERPAPI_BASE_URL = "https://serpapi.com/search"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_news(
    query: str,
    api_key: str = SERPAPI_API_KEY,
    max_results: int = 10,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict]:
    """Queries SerpAPI Google News and returns a list of article dicts."""
    if date_from is None:
        date_from = (date.today() - timedelta(days=365)).strftime("%m/%d/%Y")
    if date_to is None:
        date_to = date.today().strftime("%m/%d/%Y")
    params = {
        "engine": "google_news",
        "q": query,
        "hl": "es",
        "gl": "es",
        "tbs": f"cdr:1,cd_min:{date_from},cd_max:{date_to}",
        "api_key": api_key,
    }
    try:
        response = requests.get(SERPAPI_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("news_results", [])[:max_results]
    except requests.exceptions.RequestException as exc:
        logger.warning("Error al obtener noticias para '%s': %s", query, exc)
        return []


def fetch_article_text(url: str, max_chars: int = 5000) -> str:
    """Fetches a URL and extracts visible text using BeautifulSoup."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        node = soup.find("article") or soup.find("main") or soup.body
        text = node.get_text(separator="\n", strip=True) if node else ""

        lines = [line for line in text.splitlines() if line.strip()]
        content = "\n".join(lines)
        return content[:max_chars] + ("..." if len(content) > max_chars else "")
    except Exception as exc:
        logger.warning("No se pudo obtener contenido de %s: %s", url, exc)
        return "---Contenido de Noticia no disponible (Usa la URL para obtener más información)---"


def fetch_news_for_account(
    account_name: str,
    api_key: str = SERPAPI_API_KEY,
    max_results: int = 10,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict]:
    """
    Fetches news for a given account name and returns a list of row dicts
    ready for a DataFrame, each including NOMBRE_DE_LA_CUENTA.
    """
    query = "Noticias de la empresa " + account_name
    articles = fetch_news(query, api_key=api_key, max_results=max_results, date_from=date_from, date_to=date_to)
    rows = []
    for article in articles:
        url = article.get("link", "")
        rows.append({
            "NOMBRE_DE_LA_CUENTA": account_name,
            "Título": article.get("title"),
            "Fuente": article.get("source", {}).get("name"),
            "Fecha": article.get("date"),
            "URL": url,
            "Contenido": fetch_article_text(url) if url else "",
        })
    return rows
