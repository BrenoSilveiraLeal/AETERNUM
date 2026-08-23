from dataclasses import dataclass


@dataclass(frozen=True)
class CVMSource:
    name: str = "CVM Dados Abertos"
    url: str = "https://dados.cvm.gov.br/dados/"
    status: str = "PUBLIC_DATA_CATALOG"


class CVMProvider:
    """Catalog boundary for official CVM open datasets; no invented API routes."""

    source = CVMSource()

    def available_datasets(self) -> list[dict[str, str]]:
        return [{"name": "Companhias abertas", "identifier": "CIA_ABERTA", "url": self.source.url}, {"name": "Atos declaratórios", "identifier": "ATO_DECLR", "url": self.source.url}]
