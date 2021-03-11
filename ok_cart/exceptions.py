from django.core.exceptions import ValidationError

__all__ = (
    'CartException',
)


class CartException(ValidationError):
    pass
