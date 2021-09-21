from typing import TYPE_CHECKING

from django.db.models import (
    DecimalField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
)

from ..models import CartItem
from ..selectors import get_cart_items_by_cart

if TYPE_CHECKING:
    from decimal import Decimal
    from ..models import Cart, CartGroup

__all__ = (
    'update_cart_group_price',
    'calculate_cart_group_quantity',
    'update_cart_quantity_and_total_price'
)


def update_cart_group_price(
        *, cart_group: 'CartGroup'
) -> None:
    cart_items_total_price = (
        CartItem.objects
        .filter(
            Q(groups=cart_group) |
            Q(related_groups=cart_group)
        )
        .aggregate(
            total_price=Sum(
                ExpressionWrapper(
                    F('price') * F('quantity'),
                    output_field=DecimalField()
                )
            )
        )['total_price'] or 0
    )
    cart_group.price = cart_items_total_price
    cart_group.save(update_fields=[
        'price'
    ])


def calculate_cart_group_quantity(
        *, cart_group: 'CartGroup'
) -> 'Decimal':
    cart_items_total_quantity = (
        CartItem.objects
        .filter(
            Q(groups=cart_group) |
            Q(related_groups=cart_group)
        )
        .aggregate(
            total_quantity=Sum('quantity')
        )['total_quantity'] or 0
    )
    # TODO: save quantity to DB?
    return cart_items_total_quantity


def update_cart_quantity_and_total_price(
        *, cart: 'Cart'
) -> None:
    # calculate price only for product variants
    cart_items_total_price_and_quantity = (
        get_cart_items_by_cart(cart=cart)
        .aggregate(
            total_quantity=Sum('quantity'),
            total_price=Sum(
                ExpressionWrapper(
                    F('price') * F('quantity'),
                    output_field=DecimalField()
                )
            )
        )
    )
    quantity = (
        cart_items_total_price_and_quantity['total_quantity']
        or 0
    )
    total_price = (
        cart_items_total_price_and_quantity['total_price']
        or 0
    )

    cart.total_price = total_price
    cart.quantity = quantity
    cart.save()

    for group in cart.groups.all():
        update_cart_group_price(cart_group=group)
