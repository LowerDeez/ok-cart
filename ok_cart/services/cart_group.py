from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import CartGroup

__all__ = (
    'delete_cart_group',
)


def delete_cart_group(*, cart_group: 'CartGroup'):
    if cart_group.base:
        cart_group.base.delete()

    cart_group.relations.all().delete()

    cart_group.delete()
