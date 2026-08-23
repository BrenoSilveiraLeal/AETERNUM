import json
from datetime import date, datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .base import MarketDataProvider, MarketRecord, ProviderNotConfigured, ProviderUnavailable


class DadosDeMercadoProvider(MarketDataProvider):
    name = "Dados de Mercado"

    def __init__(self, base_url: str, token: str | None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _get(self, path: str, params: dict[str, str] | None = None):
        if not self.token:
            raise ProviderNotConfigured("Integração ainda não configurada.")
        url = f"{self.base_url}/{path.lstrip('/')}"
        if params:
            url += "?" + urlencode(params)
        request = Request(url, headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"})
        try:
            with urlopen(request, timeout=15) as response:
                return url, json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderUnavailable("Fonte indisponível. Nenhum dado foi inventado.") from exc

    def get_history(self, symbol: str, start_date: date, end_date: date) -> list[MarketRecord]:
        url, payload = self._get(f"tickers/{symbol.upper()}/quotes", {"period_init": start_date.isoformat(), "period_end": end_date.isoformat()})
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        records = []
        for row in rows:
            timestamp = datetime.fromisoformat(str(row["date"]).replace("Z", "+00:00"))
            value = row.get("close")
            if value is None:
                continue
            records.append(MarketRecord(symbol.upper(), float(value), self.name, url, timestamp, datetime.now(timezone.utc), "HISTORICAL", True, row))
        if not records:
            raise ProviderUnavailable("Fonte indisponível. Nenhum dado foi inventado.")
        return records

    def get_quote(self, symbol: str) -> MarketRecord:
        today = date.today()
        return self.get_history(symbol, today, today)[-1]

    def get_company(self, symbol: str) -> dict:
        url, payload = self._get("companies")
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        match = next((row for row in rows if row.get("b3_trade_name", "").upper() == symbol.upper()), None)
        if not match:
            raise ProviderUnavailable("Empresa não encontrada na fonte configurada.")
        return {"source": self.name, "source_url": url, "collected_at": datetime.now(timezone.utc).isoformat(), "data": match}

    def get_indicators(self, symbol: str) -> dict:
        raise ProviderUnavailable("Indicadores específicos ainda não foram habilitados neste adaptador.")

    def get_market_status(self) -> dict:
        raise ProviderUnavailable("Status do mercado ainda não foi habilitado neste adaptador.")
