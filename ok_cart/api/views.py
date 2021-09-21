from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CartChangeSerializer,
    CartRetrieveSerializer,
    CartQuantityRetrieveSerializer
)
from .utils import get_base_api_view
from ..models import Cart
from ..pipelines import (
    run_add_pipelines,
    run_post_add_pipelines
)
from ..selectors import (
    get_cart_from_request,
)
from ..services import (
    add_item_to_cart,
    clear_cart,
    update_cart_quantity_and_total_price,
)
from ..settings import settings

__all__ = (
    'CartChangeAPIView',
    'CartClearAPIView',
    'CartRetrieveAPIView',
    'CartQuantityRetrieveAPIView',
)


class CartChangeAPIView(get_base_api_view(), GenericAPIView):
    permission_classes = (AllowAny, )
    queryset = Cart.objects.open().optimized()
    serializer_class = CartChangeSerializer

    def perform_action(self, serializer) -> 'Cart':
        entities = serializer.validated_data['entities']
        cart_queryset = self.get_queryset()
        cart = settings.GETTER(
            request=self.request,
            cart_queryset=cart_queryset,
        )
        user = self.request.user

        for entity in entities:
            content_object = entity['element']['content_object']
            cart_item, cart_group = add_item_to_cart(
                cart=cart,
                user=user,
                content_type=entity['element']['type'],
                object_id=entity['element']['id'],
                content_object=content_object,
                quantity=entity['quantity'],
                parameters=entity.get('parameters', {}),
            )
            run_add_pipelines(
                cart=cart,
                user=user,
                content_object=content_object,
                cart_item=cart_item,
                cart_group=cart_group,
                quantity=entity['quantity'],
                parameters=entity.get('parameters'),
                request=self.request
            )

        run_post_add_pipelines(
            cart=cart,
            user=user,
            request=self.request
        )

        cart = cart_queryset.get(pk=cart.pk)

        update_cart_quantity_and_total_price(cart=cart)

        return cart

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.perform_action(serializer)

        response_serializer = CartRetrieveSerializer(
            instance=cart,
            context=self.get_serializer_context()
        )

        data = settings.VIEW_RESPONSE_MODIFIER(
            request=request,
            cart=cart,
            serializer=response_serializer
        )

        return Response(
            data=data,
            status=status.HTTP_200_OK
        )


class CartClearAPIView(get_base_api_view(), APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        cart = (
            get_cart_from_request(
                request=request,
                auto_create=False
            )
        )

        if cart:
            clear_cart(cart=cart)

        return Response()


class CartRetrieveAPIView(get_base_api_view(), RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CartRetrieveSerializer
    queryset = Cart.objects.open().optimized()

    def get_object(self):
        return get_cart_from_request(
            request=self.request,
            cart_queryset=self.get_queryset(),
            auto_create=False
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = settings.VIEW_RESPONSE_MODIFIER(
            request=request,
            cart=instance,
            serializer=serializer
        )
        return Response(data)


class CartQuantityRetrieveAPIView(get_base_api_view(), RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CartQuantityRetrieveSerializer
    queryset = Cart.objects.open().only('quantity', 'total_price')

    def get_object(self):
        return get_cart_from_request(
            request=self.request,
            cart_queryset=self.get_queryset(),
            auto_create=False
        )
