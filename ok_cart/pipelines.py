from typing import Dict, Iterable, Optional, TYPE_CHECKING

from django.conf import settings as django_settings

from .settings import settings

if TYPE_CHECKING:
    from django.db.models import Model
    from .models import Cart, CartItem, CartGroup

__all__ = (
    'run_add_pipelines',
    'run_post_add_pipelines',
)


def run_add_pipelines(
        *,
        cart: 'Cart',
        user: django_settings.AUTH_USER_MODEL,
        content_object: 'Model',
        cart_item: 'CartItem',
        cart_group: Optional['CartGroup'],
        quantity: int,
        parameters: Dict,
        **kwargs
):
    """
    Run pipelines after adding each passed item to the cart
    """
    for func in settings.ADD_PIPELINES:
        # cart item wasn't deleted
        if cart_item.pk:
            func(
                cart=cart,
                user=user,
                content_object=content_object,
                cart_item=cart_item,
                cart_group=cart_group,
                quantity=quantity,
                parameters=parameters,
                **kwargs
            )


def run_post_add_pipelines(
        *,
        cart: 'Cart',
        user: django_settings.AUTH_USER_MODEL,
        cart_items: Iterable['CartItem'] = None,
        **kwargs
):
    """
    Run pipelines after adding all passed items to the cart
    """
    for func in settings.POST_ADD_PIPELINES:
        func(
            cart=cart,
            user=user,
            cart_items=cart_items,
            **kwargs
        )
