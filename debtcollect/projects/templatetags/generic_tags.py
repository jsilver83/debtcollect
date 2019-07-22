from django import template
from django.core.exceptions import ObjectDoesNotExist

from debtcollect.utils import UserGroups

register = template.Library()


@register.inclusion_tag('sidebar.html', takes_context=True)
def sidebar_navigation_menu(context):
    user = context['request'].user

    admin = user.groups.filter(name=UserGroups.ADMINS_GROUP).exists() or user.is_superuser
    lawyer = user.groups.filter(name__in=[UserGroups.ADMINS_GROUP, UserGroups.LAWYERS_GROUP]).exists() or user.is_superuser
    accounting = user.groups.filter(name__in=[UserGroups.ADMINS_GROUP, UserGroups.ACCOUNTING_GROUP]).exists() or user.is_superuser
    archive = user.groups.filter(name__in=[UserGroups.ADMINS_GROUP, UserGroups.ARCHIVE_GROUP]).exists() or user.is_superuser
    debt_admin = user.groups.filter(name__in=[UserGroups.ADMINS_GROUP, UserGroups.DEBT_COLLECTING_ADMINS_GROUP]).exists() or user.is_superuser
    debt_supervisor = user.groups.filter(name__in=[UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP]).exists() or debt_admin
    debt_user = user.groups.filter(name__in=[UserGroups.DEBT_COLLECTORS_GROUP]).exists() or debt_supervisor

    return {
        'request': context['request'],
        'user': user,
        'admin': admin,
        'lawyer': lawyer,
        'accounting': accounting,
        'archive': archive,
        'debt_admin': debt_admin,
        'debt_supervisor': debt_supervisor,
        'debt_user': debt_user,
    }
