from .mt5 import MetaTraderBroker


def get_mt5_broker() -> MetaTraderBroker:
    return MetaTraderBroker()
