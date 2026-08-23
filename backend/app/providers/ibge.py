import json
from urllib.request import Request, urlopen


class IBGESIDRAProvider:
    """SIDRA integration boundary; table/variable identifiers are always explicit."""
    name = "IBGE — SIDRA"
    base_url = "https://apisidra.ibge.gov.br/values"

    def build_query(self, table: str, variable: str, period: str) -> str:
        return f"{self.base_url}/t/{table}/p/{period}/v/{variable}"

    def get_values(self, table: str, variable: str, period: str) -> list[dict]:
        url = self.build_query(table, variable, period)
        try:
            request = Request(url, headers={"Accept": "application/json"})
            with urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError("Fonte IBGE indisponível. Nenhum dado foi inventado.") from exc
        return [{"source": self.name, "source_url": url, "value": row} for row in payload]
