from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .selectors import get_or_create_anonymous_cart, get_or_create_user_cart
from .services import merge
from .settings import settings

__all__ = (
    'user_logged_in_handler',
)


@receiver(user_logged_in)
def user_logged_in_handler(request, user, **kwargs):
    """
    Retrieve anonymous cart by old session key
    Merge anonymous cart with user's cart
    """
    if not settings.MERGE_ENABLED:
        return

    old_session_key = request.session.get_old_session_key()

    if old_session_key:
        previous_cart, _ = get_or_create_anonymous_cart(session_key=old_session_key)

        if previous_cart:
            user_cart, _ = get_or_create_user_cart(user=user)

            if previous_cart.pk != user_cart.pk:
                merge(carts=[user_cart, previous_cart])
