from decimal import Decimal
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import BrinIndex
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.encoding import smart_str
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy

from .consts import CART_STATUS_OPENED, CART_STATUS_CHOICES
from .querysets import CartQueryset

__all__ = (
    'TimestampsMixin',
    'Cart',
    'CartGroup',
    'CartItem',
)


class TimestampsMixin(models.Model):
    """
    Timestamps abstract model

    Attrs:
        created_at (DateTimeField): created_at timestamp
        updated_at (DateTimeField): updated_at timestamp
    """
    created_at = models.DateTimeField(
        pgettext_lazy("Cart", 'Created at'),
        auto_now_add=True,
        editable=False
    )
    updated_at = models.DateTimeField(
        pgettext_lazy("Cart", 'Updated at'),
        auto_now=True,
        editable=False
    )

    class Meta:
        abstract = True
        indexes = (
            BrinIndex(fields=['created_at']),
        )
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.pk:
            now_ = now()
            self.created_at = now_
            self.updated_at = now_

        return super().save(*args, **kwargs)


class Cart(TimestampsMixin):
    uuid = models.UUIDField(
        default=uuid4,
        editable=False,
        primary_key=True,
    )
    status = models.CharField(
        pgettext_lazy("Cart", "Status"),
        choices=CART_STATUS_CHOICES,
        default=CART_STATUS_OPENED,
        max_length=10,
    )
    user = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        related_name='carts',
        on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy("Cart", "User"),
    )
    session_key = models.CharField(
        pgettext_lazy('Cart', 'Session key'),
        blank=True,
        max_length=255,
    )
    quantity = models.PositiveIntegerField(
        pgettext_lazy("Cart", "Total quantity"),
        default=0
    )
    total_price = models.DecimalField(
        pgettext_lazy("Cart", "Total price"),
        decimal_places=2,
        default=Decimal('0.0'),
        max_digits=20,
    )
    parameters = JSONField(
        blank=True,
        default=dict
    )

    objects = CartQueryset.as_manager()

    class Meta(TimestampsMixin.Meta):
        verbose_name = pgettext_lazy("Cart", "Cart")
        verbose_name_plural = pgettext_lazy("Cart", "Carts")

    def __str__(self) -> str:
        if self.user_id:
            return smart_str(self.user)

        return self.session_key

    def __iter__(self):
        return iter(self.groups.all())


class CartGroup(TimestampsMixin):
    """
    Group model

    Attrs:
        cart (ForeignKey): cart
        base (ForeignKey): base element
        relations (M2M): related elements
        price (DecimalField): price of content object instance
    """
    cart = models.ForeignKey(
        'ok_cart.Cart',
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name=pgettext_lazy("Cart", "Cart"),
    )
    base = models.ForeignKey(
        'ok_cart.CartItem',
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name=pgettext_lazy("Cart", "Base item")
    )
    relations = models.ManyToManyField(
        'ok_cart.CartItem',
        blank=True,
        related_name='related_groups',
        verbose_name=pgettext_lazy("Cart", "Related items")
    )
    price = models.DecimalField(
        pgettext_lazy('Cart', 'Price'),
        decimal_places=2,
        default=0,
        max_digits=20,
    )
    parameters = JSONField(
        blank=True,
        default=dict
    )

    class Meta(TimestampsMixin.Meta):
        verbose_name = pgettext_lazy("Cart", "Cart group")
        verbose_name_plural = pgettext_lazy("Cart", "Cart groups")

    def __str__(self) -> str:
        return str(self.pk)


class CartItem(TimestampsMixin):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=pgettext_lazy(
            'Cart',
            'Related object\'s type (model)'
        ),
        help_text=pgettext_lazy(
            'Cart',
            "Please select the type (model) "
            "for the relation, you want to build."
        ),

    )
    object_id = models.CharField(
        pgettext_lazy("Cart", "Object ID"),
        help_text=pgettext_lazy(
            "Cart",
            "Please enter the ID of the related object."
        ),
        max_length=255
    )
    content_object = GenericForeignKey()
    price = models.DecimalField(
        pgettext_lazy('Cart', 'Price'),
        decimal_places=2,
        default=0,
        max_digits=20,
    )
    quantity = models.PositiveIntegerField(
        pgettext_lazy("Cart", "Quantity"),
        default=0
    )
    parameters = JSONField(
        blank=True,
        default=dict
    )

    class Meta(TimestampsMixin.Meta):
        verbose_name = pgettext_lazy("Cart", "Cart item")
        verbose_name_plural = pgettext_lazy("Cart", "Cart items")

    def __str__(self) -> str:
        return smart_str(self.content_object)
