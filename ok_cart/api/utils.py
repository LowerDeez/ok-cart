from typing import Dict, TYPE_CHECKING, Type

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from ..settings import settings

if TYPE_CHECKING:
    from django.db.models import Model

__all__ = (
    'cart_element_representation_serializer',
    'get_base_api_view'
)


def cart_element_representation_serializer(
        value: Type['Model'],
        serializer_context: Dict
):
    serializers = settings.ELEMENT_REPRESENTATION_SERIALIZERS

    for model_path, serializer_class in serializers.items():
        model_class = apps.get_model(model_path)

        if isinstance(value, model_class):
            return serializer_class(
                instance=value,
                context=serializer_context
            )

    raise Exception(_('Unexpected type of cart element'))


def get_base_api_view():
    """
    Returns custom pagination class, set in settings
    """
    BaseAPIView = settings.BASE_API_VIEW

    if BaseAPIView is None:
        class BaseAPIView:
            pass

    return BaseAPIView
