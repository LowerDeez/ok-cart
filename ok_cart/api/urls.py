from django.urls import path, include

from .views import (
    CartChangeAPIView,
    CartClearAPIView,
    CartRetrieveAPIView,
    CartQuantityRetrieveAPIView,
)

app_name = 'cart-api'

urlpatterns = [
    path('cart/', include([
        path('change/', CartChangeAPIView.as_view(), name='change'),
        path('clear/', CartClearAPIView.as_view(), name='clear'),
        path('retrieve/', CartRetrieveAPIView.as_view(), name='retrieve'),
        path('quantity/', CartQuantityRetrieveAPIView.as_view(), name='quantity'),
    ])),
]
