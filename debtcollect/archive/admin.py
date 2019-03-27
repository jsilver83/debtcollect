from django.contrib import admin
from reversion.admin import VersionAdmin
from django.utils.translation import ugettext_lazy as _
from .models import *


class DocumentMovementAdmin(VersionAdmin):
    list_display = ('id', 'document', 'type', 'movement_date')


admin.site.register(Document)
admin.site.register(DocumentMovement, DocumentMovementAdmin)
