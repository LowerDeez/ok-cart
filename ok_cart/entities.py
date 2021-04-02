from dataclasses import dataclass

__all__ = (
    'CartInfo',
)


@dataclass
class CartInfo:
    total_price: float
    quantity: int
