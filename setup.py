from setuptools import setup, find_packages

pkj_name = 'ok_cart'

setup(
    name='django-ok-cart',
    version='0.0.3',
    long_description_content_type='text/x-rst',
    packages=[pkj_name] + [pkj_name + '.' + x for x in find_packages(pkj_name)],
    include_package_data=True,
)
