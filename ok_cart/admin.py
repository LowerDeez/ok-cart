from django.contrib import admin

from .models import Cart, CartItem, CartGroup

__all__ = (
    'CartAdmin',
    'CartGroupAdmin',
    'CartGroupAdminInline',
    'CartItemAdmin'
)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_per_page = 25


@admin.register(CartGroup)
class CartGroupAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'cart',
        'price'
    ]
    list_filter = [
        'cart'
    ]
    list_select_related = [
        'cart',
        'cart__user'
    ]
    list_per_page = 25


class CartGroupAdminInline(admin.StackedInline):
    model = CartGroup
    extra = 0
    readonly_fields = [
        'base',
        'relations'
    ]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [
        CartGroupAdminInline
    ]
    list_display = [
        'user',
        'status',
        'updated_at'
    ]
    list_editable = [
        'status'
    ]
    list_filter = [
        'user',
        'status'
    ]
    list_select_related = [
        'user'
    ]
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
