from datetime import date, timedelta

from ..providers.market_data import ProviderNotConfigured, ProviderUnavailable, get_market_provider


def collect_market_snapshot(symbols: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        provider = get_market_provider()
    except ProviderNotConfigured as exc:
        return {"status": str(exc)}
    for symbol in symbols:
        try:
            record = provider.get_history(symbol, date.today() - timedelta(days=1), date.today())[-1]
            result[symbol] = f"{record.status}:{record.collected_at.isoformat()}"
        except ProviderUnavailable as exc:
            result[symbol] = str(exc)
    return result
