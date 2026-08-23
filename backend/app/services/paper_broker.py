from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import MarketQuote, PaperOrder, Position


class PaperExecutionError(ValueError):
    pass


def execute_order(db: Session, order: PaperOrder) -> PaperOrder:
    if order.status != "SIMULATED":
        raise PaperExecutionError("A ordem não está aguardando execução")
    quote = db.scalar(select(MarketQuote).where(MarketQuote.symbol == order.symbol).order_by(MarketQuote.collected_at.desc()))
    if quote is None or quote.status not in {"OK", "SUCCESS"}:
        raise PaperExecutionError("Não existe cotação verificável para executar esta ordem")
    price = quote.value
    if order.order_type == "LIMIT":
        if order.side == "BUY" and price > (order.limit_price or 0):
            raise PaperExecutionError("Preço limite de compra ainda não atingido")
        if order.side == "SELL" and price < (order.limit_price or 0):
            raise PaperExecutionError("Preço limite de venda ainda não atingido")

    position = db.scalar(select(Position).where(Position.symbol == order.symbol))
    if position is None:
        position = Position(symbol=order.symbol, quantity=0, average_price=0, current_price=price, mode="PAPER")
        db.add(position)
    if order.side == "BUY":
        total_cost = position.quantity * position.average_price + order.quantity * price
        position.quantity += order.quantity
        position.average_price = total_cost / position.quantity
    else:
        if order.quantity > position.quantity:
            raise PaperExecutionError("Venda PAPER excede a posição disponível")
        position.quantity -= order.quantity
        if position.quantity == 0:
            position.average_price = 0
    position.current_price = price
    order.status = "FILLED"
    order.filled_price = price
    order.executed_at = datetime.now(timezone.utc)
    return order
