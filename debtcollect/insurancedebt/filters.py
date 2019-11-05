import django_filters as filters
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from .models import *


class InsuranceDebtFilter(filters.FilterSet):
    debt_no_filter = filters.CharFilter(label=_('Debt No'), method='custom_debt_no_filter')

    class Meta:
        model = InsuranceDebt
        fields = {
            'sub_contract': ['exact'],
            'type': ['exact'],
            'status': ['exact'],
            'driver_government_id': ['icontains'],
            'driver_mobile': ['icontains'],
            'ref_no': ['exact'],
        }

    def custom_debt_no_filter(self, queryset, name, value):
        return queryset.filter(Q(pk__exact=value) | Q(legacy_system_no__exact=value))

    # def __init__(self, *args, **kwargs):
    #     super(InsuranceDebtFilter, self).__init__(*args, **kwargs)
    #     self.filters['id'].label = _('Insurance Debt No')
