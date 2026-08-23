"""Processo opcional de coleta; fontes indisponíveis nunca viram dados fictícios."""
import time
from datetime import date, timedelta

from ..config import settings
from ..providers.market_data import ProviderNotConfigured, ProviderUnavailable, get_market_provider


def run_once(symbols: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        provider = get_market_provider()
    except ProviderNotConfigured as exc:
        return {"status": str(exc)}
    for symbol in symbols:
        try:
            records = provider.get_history(symbol, date.today() - timedelta(days=1), date.today())
            result[symbol] = records[-1].status if records else "EMPTY"
        except ProviderUnavailable as exc:
            result[symbol] = str(exc)
    return result


def main() -> None:
    while True:
        print(run_once(["IBOV"]))
        time.sleep(max(settings.market_poll_interval_seconds, 30))


if __name__ == "__main__":
    main()
