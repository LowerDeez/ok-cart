from typing import Dict, TYPE_CHECKING, Tuple

from django.conf import settings

from ..models import CartGroup, CartItem

if TYPE_CHECKING:
    from django.db.models import Model
    from ..models import Cart

__all__ = (
    'create_cart_item',
    'update_cart_item',
    'delete_cart_item',
)


def create_cart_item(
        *,
        cart: 'Cart',
        user: 'settings.AUTH_USER_MODEL',
        content_object: 'Model',
        quantity: int = 1,
        parameters: Dict = None
) -> Tuple['CartItem', 'CartGroup']:
    cart_item = CartItem.objects.create(
        content_object=content_object,
        quantity=quantity,
        parameters=parameters or {}
    )

    cart_group = CartGroup.objects.create(
        cart=cart,
        base=cart_item,
        parameters=parameters or {}
    )

    return cart_item, cart_group


def update_cart_item(
        *,
        cart_item: 'CartItem',
        cart: 'Cart',
        user: settings.AUTH_USER_MODEL,
        quantity: int = None,
        parameters: Dict = None
):
    if quantity:
        cart_item.quantity = quantity

    if parameters:
        cart_item.parameters = parameters

    cart_item.save()


def delete_cart_item(*, cart_item: 'CartItem'):
    cart_item.groups.all().delete()
    cart_item.delete()
