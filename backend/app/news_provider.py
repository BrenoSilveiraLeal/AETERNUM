from typing import Any

import httpx

from .config import settings


class NewsProvider:
    """Boundary for licensed/official news APIs; no scraping or fake endpoints."""

    name = "unconfigured"

    def search(self, query: str) -> list[dict[str, str]]:
        raise NotImplementedError("Configure an authorized news provider in the backend")


class NewsAPIProvider(NewsProvider):
    name = "newsapi"

    def search(self, query: str) -> list[dict[str, Any]]:
        if not settings.news_api_key:
            raise RuntimeError("NEWS_API_KEY não configurada")
        try:
            response = httpx.get(f"{settings.news_api_url.rstrip('/')}/everything", params={"q": query, "language": "pt", "sortBy": "publishedAt", "pageSize": 100, "apiKey": settings.news_api_key}, timeout=20)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise RuntimeError(f"Provedor de notícias indisponível: {exc}") from exc
        return [article for article in payload.get("articles", []) if article.get("title") and article.get("url")]


def get_news_provider() -> NewsProvider:
    if settings.news_provider.casefold() == "newsapi":
        return NewsAPIProvider()
    raise RuntimeError("Nenhum provedor de notícias autorizado está configurado")
