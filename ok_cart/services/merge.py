from typing import Iterable, TYPE_CHECKING

from django.db import transaction

from ..pipelines import run_post_add_pipelines
from ..selectors import get_cart_items_by_cart
from ..services import add_item_to_cart, clear_cart, update_cart_quantity_and_total_price

if TYPE_CHECKING:
    from apps.cart.models import Cart

__all__ = (
    'merge',
)


@transaction.atomic()
def merge(*, carts: Iterable["Cart"], new_session_key: str = None):
    carts_iterator = iter(carts)

    main_cart = next(carts_iterator)

    for cart in carts_iterator:
        cart_items = get_cart_items_by_cart(cart=cart)

        for cart_item in cart_items:
            add_item_to_cart(
                cart=main_cart,
                user=main_cart.user,
                content_type=cart_item.content_type,
                object_id=cart_item.object_id,
                content_object=cart_item.content_object,
                quantity=cart_item.quantity,
                parameters=cart_item.parameters
            )

        # clear and delete old cart
        clear_cart(cart=cart)
        cart.delete()

    # apply all pipelines to new cart items
    run_post_add_pipelines(
        cart=main_cart,
        user=main_cart.user
    )

    # refresh cart to get actual groups for correct calculations
    main_cart.refresh_from_db()
    update_cart_quantity_and_total_price(cart=main_cart)

    if new_session_key:
        main_cart.session_key = new_session_key
        main_cart.save(update_fields=['session_key'])
