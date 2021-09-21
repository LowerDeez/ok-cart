from dataclasses import dataclass

__all__ = (
    'CartPriceInfo',
)


@dataclass
class CartPriceInfo:
    total_price: float
    quantity: int
