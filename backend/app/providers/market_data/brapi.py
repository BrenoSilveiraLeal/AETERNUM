from datetime import date, datetime, timezone
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .base import MarketDataProvider, MarketRecord, ProviderNotConfigured, ProviderUnavailable


class BrapiProvider(MarketDataProvider):
    """Free JSON market data adapter; never executes orders."""

    name = "brapi.dev (free market data)"
    free_symbols = {"PETR4", "VALE3", "MGLU3", "ITUB4"}

    def __init__(self, base_url: str, token: str | None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _get(self, path: str, params: dict[str, str]):
        url = f"{self.base_url}/{path.lstrip('/')}?{urlencode(params)}"
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=15) as response:
                return url, json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderUnavailable("Fonte brapi indisponível ou sem cobertura para este ativo.") from exc

    def get_history(self, symbol: str, start_date: date, end_date: date) -> list[MarketRecord]:
        normalized = symbol.upper()
        if not self.token and normalized not in self.free_symbols:
            raise ProviderNotConfigured("Integração ainda não configurada para este ativo; a brapi exige token fora do conjunto gratuito de teste.")
        url, payload = self._get("v2/stocks/historical", {"symbols": normalized, "startDate": start_date.isoformat(), "endDate": end_date.isoformat(), "sortOrder": "asc"})
        result = (payload.get("results") or [{}])[0]
        rows = ((result.get("data") or {}).get("historicalDataPrice") or [])
        records = []
        for row in rows:
            value = row.get("adjustedClose", row.get("close"))
            timestamp = row.get("date")
            if value is None or timestamp is None:
                continue
            records.append(MarketRecord(normalized, float(value), self.name, url, datetime.fromtimestamp(float(timestamp), timezone.utc), datetime.now(timezone.utc), "HISTORICAL", True, row))
        if not records:
            raise ProviderUnavailable("Nenhum histórico retornado pela brapi para este ativo.")
        return records

    def get_quote(self, symbol: str) -> MarketRecord:
        normalized = symbol.upper()
        if not self.token and normalized not in self.free_symbols:
            raise ProviderNotConfigured("Integração ainda não configurada para este ativo; a brapi exige token fora do conjunto gratuito de teste.")
        url, payload = self._get("v2/stocks/quote", {"symbols": normalized})
        result = (payload.get("results") or [{}])[0]
        data = result.get("data") or {}
        value = data.get("regularMarketPrice")
        if value is None:
            raise ProviderUnavailable("Nenhuma cotação retornada pela brapi para este ativo.")
        source_timestamp = datetime.fromisoformat(str(data.get("regularMarketTime")).replace("Z", "+00:00")) if data.get("regularMarketTime") else datetime.now(timezone.utc)
        return MarketRecord(normalized, float(value), self.name, url, source_timestamp, datetime.now(timezone.utc), "QUOTE", True, data)

    def get_company(self, symbol: str) -> dict:
        raise ProviderUnavailable("Perfil de empresa ainda não foi habilitado neste adaptador.")

    def get_indicators(self, symbol: str) -> dict:
        raise ProviderUnavailable("Indicadores ainda não foram habilitados neste adaptador.")

    def get_market_status(self) -> dict:
        return {"provider": self.name, "status": "AVAILABLE_WITH_LIMITS", "real_orders": False}
