from django.utils.translation import pgettext_lazy

__all__ = (
    'CART_STATUS_OPENED',
    'CART_STATUS_CLOSED',
    'CART_STATUS_CHOICES',
)

CART_STATUS_OPENED = 'opened'
CART_STATUS_CLOSED = 'closed'


CART_STATUS_CHOICES = (
    (CART_STATUS_OPENED, pgettext_lazy("Cart", "Open")),
    (CART_STATUS_CLOSED, pgettext_lazy("Cart", "Closed"))
)
