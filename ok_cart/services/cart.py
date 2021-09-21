from typing import Dict, TYPE_CHECKING, Optional, Tuple, Union

from django.conf import settings

from ..consts import CART_STATUS_CLOSED
from ..models import Cart, CartItem, CartGroup
from ..selectors import (
    get_cart_item,
    get_cart_items_by_cart
)
from ..services.cart_item import (
    create_cart_item,
    delete_cart_item,
    update_cart_item
)
from ..settings import settings as cart_settings

if TYPE_CHECKING:
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Model

__all__ = (
    'add_item_to_cart',
    'clear_cart',
    'close_cart',
    'cart_is_empty',
)


def add_item_to_cart(
        *,
        cart: 'Cart',
        user: 'settings.AUTH_USER_MODEL',
        content_type: 'ContentType',
        object_id: Union[int, str],
        content_object: 'Model',
        quantity: int = 1,
        parameters: Dict = None
) -> Tuple['CartItem', Optional['CartGroup']]:
    """
    Add object to cart by given content type and object's id
    """
    cart_item: 'CartItem' = get_cart_item(
        cart=cart,
        content_type=content_type,
        object_id=object_id
    )
    cart_group = None

    if cart_item:
        cart_item.quantity += quantity

        for validator in cart_settings.CART_ITEM_QUANTITY_VALIDATORS:
            validator(
                cart_item=cart_item
            )

        if cart_item.quantity <= 0:
            delete_cart_item(
                cart_item=cart_item
            )

            if cart_is_empty(cart=cart):
                clear_cart(cart=cart)

        else:
            update_cart_item(
                cart_item=cart_item,
                cart=cart,
                user=user,
                parameters=parameters
            )
    else:
        cart_item, cart_group = create_cart_item(
            cart=cart,
            user=user,
            content_object=content_object,
            quantity=quantity,
            parameters=parameters
        )

    return cart_item, cart_group


def clear_cart(*, cart: 'Cart') -> None:
    get_cart_items_by_cart(cart=cart).delete()
    CartGroup.objects.filter(cart=cart).delete()
    cart.quantity = 0
    cart.total_price = 0
    cart.save(update_fields=['quantity', 'total_price'])


def close_cart(*, cart: 'Cart') -> None:
    cart.status = CART_STATUS_CLOSED
    cart.save(update_fields=[
        'status',
    ])


def cart_is_empty(*, cart: 'Cart') -> bool:
    return not (
        CartItem.objects
        .filter(
            groups__cart=cart,
        )
        .exists()
    )
