"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import uwsgidecorators
import logging

logger = logging.getLogger('django')


def load_instrumentation():
    try:
        logger.warning('INSIDE WSGI.PY:: attempting to load auto-instrumentation')
        from opentelemetry.instrumentation.auto_instrumentation import sitecustomize
    except ImportError:
        logger.warning('auto-instrumentation not available')
        pass


# UNCOMMENT THE FOLLOWING LINE TO LOAD ADOT PYTHON INSTRUMENTATION
load_instrumentation()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = get_wsgi_application()
