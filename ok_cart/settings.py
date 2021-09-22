from collections import Iterable
from typing import Any

from django.conf import settings as django_settings
from django.utils.module_loading import import_string

__all__ = (
    'LazySetting',
    'LazySettings',
    'settings'
)


class LazySetting:
    """
    A proxy to a named Django setting.
    """

    def __init__(
            self,
            name: str = None,
            importable: bool = False,
            default: Any = None
    ):
        self.name = name
        self.default = default
        self.importable = importable

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name

        self.name = f'CART_{self.name}'

    def __get__(self, obj, cls):
        if obj is None:
            return self

        setting = self.get_setting_value(obj)

        if self.importable:
            return self.import_setting(setting)

        return setting

    def get_setting_value(self, obj):
        obj_settings = obj._settings

        if isinstance(obj_settings, dict):
            setting = obj_settings.get(self.name, self.default)
        else:
            setting = getattr(obj_settings, self.name, self.default)

        return setting

    def import_setting(self, setting: Any):
        if setting is None:
            return setting
        elif isinstance(setting, str):
            return import_string(setting)
        elif isinstance(setting, dict):
            return {
                key: import_string(value)
                for key, value in setting.items()
            }
        elif isinstance(setting, Iterable):
            return [import_string(item) for item in setting]

        return setting


class LazySettings:
    """
    A proxy to your app specific django settings.
    Settings are resolved at runtime, allowing tests
    to change settings at runtime.
    """

    def __init__(self, global_settings):
        self._settings = global_settings

    ADD_PIPELINES = LazySetting(
        default=[],
        importable=True,
    )
    POST_ADD_PIPELINES = LazySetting(
        default=[],
        importable=True,
    )
    CART_ITEM_QUANTITY_VALIDATORS = LazySetting(
        default=[],
        importable=True,
    )
    ELEMENT_REPRESENTATION_SERIALIZERS = LazySetting(
        default={},
        importable=True
    )
    ELEMENT_ALLOWED_TYPES = LazySetting(
        default=(),
        importable=False
    )
    PRICE_PROCESSOR = LazySetting(
        default=lambda request, price: price,
        importable=True
    )
    BASE_API_VIEW = LazySetting(
        importable=True
    )
    GETTER = LazySetting(
        default='ok_cart.selectors.get_cart_from_request',
        importable=True
    )
    VIEW_RESPONSE_MODIFIER = LazySetting(
        default=lambda request, cart, serializer: serializer.data,
        importable=True
    )
    MERGE_ENABLED = LazySetting(
        default=False,
        importable=False
    )


cart_settings = getattr(django_settings, 'CART', django_settings)

settings = LazySettings(cart_settings)
