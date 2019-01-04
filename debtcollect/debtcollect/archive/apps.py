from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ArchiveConfig(AppConfig):
    name = 'archive'
    verbose_name = _('Archive')
