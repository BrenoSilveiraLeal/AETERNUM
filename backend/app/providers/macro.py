from dataclasses import dataclass
from datetime import date, datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json


@dataclass(frozen=True)
class IndicatorRecord:
    code: str
    name: str
    value: float
    reference_date: date
    published_at: datetime
    source: str
    source_url: str


class BancoCentralSGSProvider:
    """Official SGS adapter boundary. Series codes must be explicitly configured by the caller."""
    name = "Banco Central do Brasil — SGS"
    base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs."

    def get_series(self, code: int, start: date, end: date) -> list[IndicatorRecord]:
        url = f"{self.base_url}{code}/dados?formato=json&dataInicial={start:%d/%m/%Y}&dataFinal={end:%d/%m/%Y}"
        try:
            request = Request(url, headers={"Accept": "application/json"})
            with urlopen(request, timeout=15) as response:
                rows = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError("Fonte indisponível. Nenhum dado foi inventado.") from exc
        records = []
        for row in rows:
            reference = datetime.strptime(row["data"], "%d/%m/%Y").date()
            records.append(IndicatorRecord(str(code), f"SGS {code}", float(row["valor"].replace(",", ".")), reference, datetime.now(timezone.utc), self.name, url))
        return records
