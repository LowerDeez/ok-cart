import json

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from .utils import cart_element_representation_serializer

__all__ = (
    'JSONStringField',
    'ContentTypeNaturalKeyField',
    'CartItemElementRelatedField',
    'ContentTypeSerializerField'
)


class JSONStringField(serializers.JSONField):
    def to_representation(self, value):
        if not value:
            return value

        try:
            return json.loads(value)
        except TypeError as e:
            return value


class ContentTypeNaturalKeyField(serializers.CharField):
    default_error_messages = {
        'invalid': _(
            'Must be a valid natural key format: '
            '`app_label.model`. Your value: {value}'
        ),
        'not_exist': _(
            'Content type for natural key '
            '`{value}` does not exist.'
        )
    }

    def to_internal_value(self, data):
        try:
            app_label, model = data.split('.')
        except ValueError:
            self.fail('invalid', value=data)
        try:
            ct: 'ContentType' = (
                ContentType.objects
                .get_by_natural_key(
                    app_label,
                    model
                )
            )
        except ContentType.DoesNotExist:
            self.fail('not_exist', value=data)

        return ct


class CartItemElementRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return (
            cart_element_representation_serializer(
                value=value,
                serializer_context=self.context
            ).data
        )


class ContentTypeSerializerField(serializers.Serializer):
    type = ContentTypeNaturalKeyField(write_only=True)
    id = serializers.CharField(write_only=True)

    class Meta:
        fields = [
            'type',
            'id',
        ]

    def __init__(self, *args, **kwargs):
        self.natural_keys = kwargs.pop('natural_keys', [])
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        data = super().validate(attrs)

        ct: 'ContentType' = data['type']

        if (
                self.natural_keys
                and ct.natural_key() not in self.natural_keys
        ):
            raise serializers.ValidationError({
                'type': _('Not allowed type')
            })

        try:
            content_object = (
                ct.get_object_for_this_type(pk=data['id'])
            )
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                'id': _('Invalid object id.')
            })
        else:
            data['content_object'] = content_object

        return data
