from dataclasses import dataclass


@dataclass(frozen=True)
class OfficialSource:
    name: str
    identifier: str
    status: str = "NOT_CONFIGURED"


class B3Provider:
    source = OfficialSource("B3", "https://www.b3.com.br", "NOT_CONFIGURED")


class BancoCentralProvider:
    source = OfficialSource("Banco Central do Brasil", "SGS/Focus", "NOT_CONFIGURED")


class IBGEProvider:
    source = OfficialSource("IBGE", "SIDRA", "NOT_CONFIGURED")
