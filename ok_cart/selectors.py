from typing import TYPE_CHECKING, Tuple, Union

from django.db.models import Q

from .entities import CartPriceInfo
from .models import Cart, CartItem
from .settings import settings

if TYPE_CHECKING:
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import QuerySet
    from django.http.request import HttpRequest

__all__ = (
    'get_cart_from_request',
    'get_or_create_user_cart',
    'get_or_create_anonymous_cart',
    'get_cart_quantity_and_total_price',
    'get_cart_item',
    'get_cart_items_by_cart',
)


def get_cart_from_request(
        *,
        request: 'HttpRequest',
        cart_queryset: 'QuerySet' = Cart.objects.open().optimized(),
        auto_create: bool = True
) -> 'Cart':
    """
    Fetch cart from database or create a new one based on cookie
    """
    if request.user.is_authenticated:
        cart, _ = get_or_create_user_cart(
            user=request.user,
            session_key=request.session.session_key,
            cart_queryset=cart_queryset,
            auto_create=auto_create
        )
    else:
        if request.session.session_key is None:
            request.session.create()

        cart, _ = get_or_create_anonymous_cart(
            session_key=request.session.session_key,
            cart_queryset=cart_queryset,
            auto_create=auto_create
        )
    return cart


def get_or_create_user_cart(
        *,
        user,
        session_key: str = '',
        cart_queryset: 'QuerySet' = Cart.objects.open().optimized(),
        auto_create: 'bool' = False
) -> Tuple['Cart', bool]:
    """
    Return an active cart for a user or create it
    """
    if auto_create:
        return cart_queryset.update_or_create(
            user=user,
            defaults={
                'session_key': session_key
            }
        )

    return (
        cart_queryset.filter(user=user).first(),
        False
    )


def get_or_create_anonymous_cart(
        *,
        session_key: str,
        cart_queryset: 'QuerySet' = Cart.objects.open().optimized(),
        auto_create: bool = False
) -> Tuple['Cart', bool]:
    """
    Return an active cart for an anonymous user or create it
    """
    if auto_create:
        return cart_queryset.get_or_create(
            session_key=session_key
        )

    return (
        cart_queryset.filter(
            session_key=session_key
        ).first(),
        False
    )


def get_cart_quantity_and_total_price(
        *,
        request: 'HttpRequest',
) -> 'CartPriceInfo':
    """
    Return total price and quantity for a current cart
    """
    cart = get_cart_from_request(
        request=request,
        cart_queryset=Cart.objects.open().only(
            'quantity',
            'total_price',
        ),
        auto_create=False
    )
    if cart:
        quantity = cart.quantity
        total_price = cart.total_price
    else:
        quantity = total_price = 0

    return CartPriceInfo(
        quantity=quantity,
        total_price=total_price
    )


def get_total_price(*, request: 'HttpRequest', cart: 'Cart'):
    price = cart.total_price

    return settings.PRICE_PROCESSOR(
        request=request,
        price=price
    )


def get_cart_item(
        *,
        cart: 'Cart',
        content_type: 'ContentType',
        object_id: Union[str, int]
) -> 'CartItem':
    cart_item: 'CartItem' = (
        CartItem.objects.filter(
            groups__cart=cart,
            content_type=content_type,
            object_id=object_id,
        )
        .first()
    )
    return cart_item


def get_cart_items_by_cart(
        *,
        cart: 'Cart',
        with_related: bool = True
) -> 'QuerySet':
    query = Q(groups__cart=cart)

    if with_related:
        query |= Q(related_groups__cart=cart)

    cart_items = CartItem.objects.filter(query)

    return cart_items
