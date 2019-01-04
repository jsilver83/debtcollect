import django_filters as filters
from django.db.models import Q

from django.utils.translation import ugettext_lazy as _

from .models import *


MOVEMENT_TYPES = (
    (_('INBOX'))
)

class DocumentMovementFilter(filters.FilterSet):
    # general_search = filters.CharFilter(method='custom_name_filter', label=_('Name (Arabic or English)'))
    type = filters.ChoiceFilter(choices=DocumentMovement.MovementTypes.choices(),
                                label=_('Type'), method='custom_type_filter')

    class Meta:
        model = DocumentMovement
        fields = {
            'document__type': ['exact'],
            'original_document': ['exact'],
            'document__project': ['exact'],
            # 'handing_party_role': ['exact'],
            # 'receiving_party_role': ['exact'],
        }

    def custom_type_filter(self, queryset, name, value):
        if value == DocumentMovement.MovementTypes.INBOX:
            return queryset.filter(receiving_party_role=DocumentMovement.ArchiveRoles.ARCHIVE,
                                   handing_party_role__in=(DocumentMovement.ArchiveRoles.EMPLOYEE,
                                                           DocumentMovement.ArchiveRoles.CLIENT))
        elif value == DocumentMovement.MovementTypes.OUTBOX:
            return queryset.filter(handing_party_role=DocumentMovement.ArchiveRoles.ARCHIVE,
                                   receiving_party_role__in=(DocumentMovement.ArchiveRoles.EMPLOYEE,
                                                             DocumentMovement.ArchiveRoles.CLIENT))
        else:
            return queryset

    def __init__(self, *args, **kwargs):
        super(DocumentMovementFilter, self).__init__(*args, **kwargs)
        # self.filters['organization__isnull'].label = _('Individuals')
