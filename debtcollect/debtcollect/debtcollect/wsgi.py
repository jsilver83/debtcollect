"""
WSGI config for gentella project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.contrib.auth.models import Group

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gentella.settings")

application = get_wsgi_application()

####################################
# Creating initial user groups     #
# This code will execute once only #
####################################
created = False
admins_group, created = Group.objects.get_or_create(name='Admins')
lawyers_group, created = Group.objects.get_or_create(name='Lawyers')
archive_group, created = Group.objects.get_or_create(name='Archive')
accounting_group, created = Group.objects.get_or_create(name='Accounting')
