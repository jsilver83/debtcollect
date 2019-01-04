from django import template
from django.core.exceptions import ObjectDoesNotExist


register = template.Library()


@register.inclusion_tag('sidebar.html', takes_context=True)
def sidebar_navigation_menu(context):
    user = context['request'].user

    admin = user.groups.filter(name__in=['Admins']).exists() or user.is_superuser
    lawyer = user.groups.filter(name__in=['Admins', 'Lawyers']).exists() or user.is_superuser
    accounting = user.groups.filter(name__in=['Admins', 'Accounting']).exists() or user.is_superuser
    archive = user.groups.filter(name__in=['Admins', 'Archive']).exists() or user.is_superuser

    return {
        'request': context['request'],
        'user': user,
        'admin': admin,
        'lawyer': lawyer,
        'accounting': accounting,
        'archive': archive,
    }
