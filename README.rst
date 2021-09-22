=============================
django-ok-cart |PyPI version|
=============================

|Upload Python Package| |Code Health| |Python Versions| |PyPI downloads| |license| |Project Status|

Django Cart.

Installation
============

Install with pip:

.. code:: shell

    $ pip install django-ok-cart djangorestframework


Update INSTALLED_APPS:

.. code:: python

    INSTALLED_APPS = [
        ...
        'ok_cart',
        'rest_framework',
        ...
    ]


Apply migrations:

.. code:: shell

    python manage.py migrate


Available settings
==================

``CART_ADD_PIPELINES`` - Functions to run after adding each passed item to the cart.

.. code:: python

    # settings.py

    CART_ADD_PIPELINES = (
       'apps.store.contrib.cart.pipelines.save_shop_id_to_cart_parameters',
    )

    # apps.store.contrib.cart.pipelines.py

    def save_shop_id_to_cart_parameters(
            cart: 'Cart',
            user: 'User',
            content_object: 'Model',
            cart_item: 'CartItem',
            cart_group: 'CartGroup',
            **kwargs
    ):
        if isinstance(content_object, Product) and cart_group:
            cart_group.parameters['shop_id'] = content_object.shop_id
            cart_group.save(update_fields=['parameters'])
            cart_item.parameters['shop_id'] = content_object.shop_id
            cart_item.save(update_fields=['parameters'])


``CART_POST_ADD_PIPELINES`` - Functions to run after adding all passed items to the cart. 

Note: To save cart items prices you need to implement your custom pipeline like in example below.

.. code:: python

    # settings.py

    CART_POST_ADD_PIPELINES = (
       'apps.store.contrib.cart.pipelines.apply_product_prices_to_cart',
    )

    # apps.store.contrib.cart.pipelines.py

    from ok_cart.selectors import get_cart_items_by_cart
    from apps.store.models import Product
    from apps.store.selectors import get_product_price
    from shared.utils import get_content_type

    def get_product_cart_items(
            *,
            cart: 'Cart',
            with_related: bool = True
    ) -> 'QuerySet':
        cart_items = (
            get_cart_items_by_cart(
                cart=cart,
                with_related=with_related
            )
            .filter(
                content_type=get_content_type(Product)
            )
        )

        return cart_items

    def get_cart_item_price(
            *,
            content_object: 'Model',
            user: 'User',
            cart: 'Cart',
            **kwargs
    ) -> Decimal:
        """
        Return price for specific type of object
        """
        price = None

        if isinstance(content_object, Product):
            price = get_product_price(product=content_object)

        return price

    def apply_product_prices_to_cart(
            *,
            cart: 'Cart',
            user: 'User',
            **kwargs
    ):
        cart_items = (
            get_product_cart_items(
                cart=cart,
                with_related=False
            )
        )

        for cart_item in cart_items:
            price = (
                get_cart_item_price(
                    content_object=cart_item.content_object,
                    user=user,
                    cart=cart,
                )
            )
            cart_item.price = price
            cart_item.save()


``CART_ELEMENT_REPRESENTATION_SERIALIZERS`` - Serializers to represent cart items objects.

.. code:: python

    # settings.py

    CART_ELEMENT_REPRESENTATION_SERIALIZERS = {
        'store.Product': 'api.rest.store.serializers.product.retrieve.ProductCartRetrieveSerializer',
    }


``CART_ELEMENT_ALLOWED_TYPES`` - Tuple of tuples of cart items allowed types.

.. code:: python

    # settings.py

    CART_ELEMENT_ALLOWED_TYPES = (
        ('store', 'product'),
    )


``CART_PRICE_PROCESSOR`` - Function to modify cart prices, like converting to another currency.

.. code:: python

    # settings.py

    CART_PRICE_PROCESSOR = 'apps.store.contrib.cart.cart_price_processor'

    # apps.store.contrib.cart.price.py

    def cart_price_processor(
            *,
            request,
            price
    ):
        return price


``CART_BASE_API_VIEW`` - Base API View for your cart views.

.. code:: python

    # settings.py

    CART_BASE_API_VIEW = 'apps.store.contrib.cart.StandardsMixin'


``CART_GETTER`` - Function to get or create cart. ``ok_cart.selectors.get_cart_from_request`` by default.

.. code:: python

    # settings.py

    CART_GETTER = 'apps.store.contrib.cart.selectors.cart_getter'

    # store.contrib.cart.selectors.py

    def cart_getter(
            *,
            request: 'HttpRequest',
            cart_queryset: 'QuerySet' = Cart.objects.open().optimized(),
            auto_create: bool = True
    ) -> 'Cart':
        pass


``CART_MERGE_ENABLED`` - Setting to enable carts merge during login/logout flow. To make it work properly, add this setting:

.. code:: python

    # settings.py

    SESSION_ENGINE = 'ok_cart.session_store'


Quickstart
==========

To enable cart views, add next URL patterns: 

.. code:: python

    urlpatterns = [
        ...
        path('', include('ok_cart.api.urls')),
    ]
    
    
Endpoints
*********

1. ``/api/v1/cart/change/`` - API View to add items to cart. ``type`` value is a structure like ``app_label.model_name``.
    
Possible payload:

.. code:: json

    {
        "entities": [
            {
                "element": {
                    "id":"9619f790-9a02-4ac3-ad34-22e4da3a6d54",
                    "type":"store.product"
                },
                "quantity":"1"
            }
        ]
    }


2. ``/api/v1/cart/clear/`` - API View to remove all items from cart.  


3. ``/api/v1/cart/quantity/`` - API View to get cart's quantity and total price.  
    
Possible result:

.. code:: json

    {
        "quantity": 3,
        "total_price": 750
    }


4. ``/api/v1/cart/retrieve/`` - API View to retrieve cart data.  
    
Possible result:

.. code:: json

    {
        "groups": [
            {
                "id": 34,
                "price": 750,
                "base": {
                    "element": {
                        "id": "9619f790-9a02-4ac3-ad34-22e4da3a6d54",
                        "caption": "Ноутбук",
                        "type": "store.product",
                        "props": {
                            "title": "Ноутбук",
                            "short_description": "Ноут для чайников",
                            "category": {
                                "id": 1,
                                "caption": "Ноутбуки и компьютеры",
                                "type": "store.category",
                                "props": {
                                    "id": 1,
                                    "label": "noutbuk-komp",
                                    "title": "Ноутбуки и компьютеры",
                                    "parent": null,
                                    "depth": 0
                                }
                            },
                            "image": {},
                            "shop": null,
                            "shop_identifier": "",
                            "price": 250,
                            "old_price": null,
                            "url": "/product/noutbuk-0c4qoewu-vxmong1s/"
                        }
                    },
                    "quantity": 3,
                    "price": 250,
                    "parameters": {
                        "shop_id": null
                    }
                },
                "relations": [],
                "parameters": {
                    "shop_id": null
                }
            }
        ],
        "quantity": 3,
        "total_price": 750,
        "parameters": {}
    }

    	
.. |PyPI version| image:: https://badge.fury.io/py/django-ok-cart.svg
   :target: https://badge.fury.io/py/django-ok-cart
.. |Upload Python Package| image:: https://github.com/LowerDeez/ok-cart/workflows/Upload%20Python%20Package/badge.svg
   :target: https://github.com/LowerDeez/ok-cart/
   :alt: Build status
.. |Code Health| image:: https://api.codacy.com/project/badge/Grade/e5078569e40d428283d17efa0ebf9d19
   :target: https://www.codacy.com/app/LowerDeez/ok-cart
   :alt: Code health
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/django-ok-cart.svg
   :target: https://pypi.org/project/django-ok-cart/
   :alt: Python versions
.. |license| image:: https://img.shields.io/pypi/l/django-ok-cart.svg
   :alt: Software license
   :target: https://github.com/LowerDeez/ok-cart/blob/master/LICENSE
.. |PyPI downloads| image:: https://img.shields.io/pypi/dm/django-ok-cart.svg
   :alt: PyPI downloads
.. |Project Status| image:: https://img.shields.io/pypi/status/django-ok-cart.svg
   :target: https://pypi.org/project/django-ok-cart/  
   :alt: Project Status
