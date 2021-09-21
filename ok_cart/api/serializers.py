from rest_framework import serializers

from .fields import (
    JSONStringField,
    CartItemElementRelatedField,
    ContentTypeSerializerField
)
from ..models import Cart, CartItem, CartGroup
from ..settings import settings

__all__ = (
    'CartItemElementSerializer',
    'CartChangeSerializer',
    'CartItemRetrieveSerializer',
    'CartGroupRetrieveSerializer',
    'CartRetrieveSerializer',
    'CartQuantityRetrieveSerializer'
)


class CartItemElementSerializer(serializers.ModelSerializer):
    element = ContentTypeSerializerField(
        natural_keys=settings.ELEMENT_ALLOWED_TYPES,
        write_only=True
    )
    quantity = serializers.IntegerField(default=1)

    class Meta:
        model = CartItem
        fields = [
            'element',
            'parameters',
            'quantity'
        ]


class CartChangeSerializer(serializers.ModelSerializer):
    entities = CartItemElementSerializer(many=True)

    class Meta:
        model = Cart
        fields = [
            'entities'
        ]


class CartItemRetrieveSerializer(serializers.ModelSerializer):
    element = CartItemElementRelatedField(
        read_only=True,
        source='content_object'
    )
    price = serializers.SerializerMethodField()
    parameters = JSONStringField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'element',
            'quantity',
            'price',
            'parameters'
        ]

    def get_price(self, cart_item: 'CartItem'):
        price = cart_item.price

        return settings.PRICE_PROCESSOR(
            request=self.context['request'],
            price=price
        )


class CartGroupRetrieveSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    base = CartItemRetrieveSerializer()
    relations = CartItemRetrieveSerializer(many=True)
    parameters = JSONStringField()

    class Meta:
        model = CartGroup
        fields = [
            'id',
            'price',
            'base',
            'relations',
            'parameters'
        ]

    def get_price(self, cart_group: 'CartGroup'):
        price = cart_group.price

        return settings.PRICE_PROCESSOR(
            request=self.context['request'],
            price=price
        )


class CartRetrieveSerializer(serializers.ModelSerializer):
    groups = CartGroupRetrieveSerializer(many=True)
    total_price = serializers.SerializerMethodField()
    parameters = JSONStringField()

    class Meta:
        model = Cart
        fields = [
            'groups',
            'quantity',
            'total_price',
            'parameters',
        ]

    def get_total_price(self, cart: 'Cart'):
        price = cart.total_price

        return settings.PRICE_PROCESSOR(
            request=self.context['request'],
            price=price
        )


class CartQuantityRetrieveSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'quantity',
            'total_price',
        ]

    def get_total_price(self, cart: 'Cart'):
        price = cart.total_price

        return settings.PRICE_PROCESSOR(
            request=self.context['request'],
            price=price
        )
