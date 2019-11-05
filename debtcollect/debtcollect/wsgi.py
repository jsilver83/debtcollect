"""
WSGI config for gentella project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gentella.settings")

application = get_wsgi_application()

try:
    ####################################
    # Creating initial user groups     #
    # This code will execute once only #
    # TODO: FIX LATER not working      #
    ####################################
    from .utils import UserGroups
    from django.contrib.auth.models import Group

    admins_group, created = Group.objects.get_or_create(name=UserGroups.ADMINS_GROUP)
    lawyers_group, created = Group.objects.get_or_create(name=UserGroups.LAWYERS_GROUP)
    archive_group, created = Group.objects.get_or_create(name=UserGroups.ARCHIVE_GROUP)
    accounting_group, created = Group.objects.get_or_create(name=UserGroups.ACCOUNTING_GROUP)
    debt_collectors_group, created = Group.objects.get_or_create(name=UserGroups.DEBT_COLLECTORS_GROUP)
    debt_collecting_supervisors_group, created = Group.objects.get_or_create(
        name=UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP)
    debt_collecting_admins_group, created = Group.objects.get_or_create(name=UserGroups.DEBT_COLLECTING_ADMINS_GROUP)
except Exception as e:
    print(e)
