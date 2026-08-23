from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree

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


class OfficialRSSProvider(NewsProvider):
    """Free public feeds from official Brazilian institutions."""

    name = "rss"

    def search(self, query: str) -> list[dict[str, Any]]:
        terms = {term.casefold() for term in query.replace("/", " ").split() if len(term) > 3}
        articles: list[dict[str, Any]] = []
        for feed_url in (item.strip() for item in settings.news_rss_urls.split(",")):
            if not feed_url:
                continue
            try:
                response = httpx.get(feed_url, timeout=15, follow_redirects=True)
                response.raise_for_status()
                root = ElementTree.fromstring(response.content)
            except (httpx.HTTPError, ElementTree.ParseError):
                continue
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                description = (item.findtext("description") or "").strip()
                haystack = f"{title} {description}".casefold()
                if not title or not link or (terms and not any(term in haystack for term in terms)):
                    continue
                published = (item.findtext("pubDate") or "").strip()
                articles.append({
                    "title": title,
                    "url": link,
                    "description": description[:4000] or None,
                    "publishedAt": published or datetime.now(timezone.utc).isoformat(),
                    "source": {"name": urlparse(feed_url).hostname or "Fonte oficial"},
                })
        return articles


def get_news_provider() -> NewsProvider:
    if settings.news_provider.casefold() == "newsapi":
        return NewsAPIProvider()
    if settings.news_provider.casefold() == "rss":
        return OfficialRSSProvider()
    raise RuntimeError("Nenhum provedor de notícias autorizado está configurado")
