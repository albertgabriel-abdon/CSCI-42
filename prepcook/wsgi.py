"""
WSGI config for prepcook project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demosite.settings')

application = get_wsgi_application()

try:
    call_command('createsuperuser_if_none')
except Exception as e:

    import logging
    logger = logging.getLogger(__name__)
    logger.exception('Error creating superuser: %s', e)