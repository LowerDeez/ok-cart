from django.db import models

from .consts import CART_STATUS_OPENED, CART_STATUS_CLOSED

__all__ = (
    'CartQueryset',
)


class CartQueryset(models.QuerySet):
    """
    A specialized queryset for dealing with carts.
    """

    def anonymous(self):
        """
        Return unassigned carts.
        """
        return self.filter(user=None)

    def open(self):
        """
        Return opened carts.
        """
        return self.filter(status=CART_STATUS_OPENED)

    def closed(self):
        """
        Return closed carts.
        """
        return (
            self.filter(status=CART_STATUS_CLOSED)
        )

    def open_with_user(self):
        """
        Return open carts with users
        """
        return self.open().filter(user__isnull=False)

    def optimized(self):
        return (
            self
            .prefetch_related(
                'groups',
                'groups__base',
                'groups__relations',
            )
        )
