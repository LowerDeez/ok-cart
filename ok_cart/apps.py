from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


class CartConfig(AppConfig):
    name = 'ok_cart'
    verbose_name = pgettext_lazy('Cart', 'Cart')

    def ready(self):
        from . import handlers
