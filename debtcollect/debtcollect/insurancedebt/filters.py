import django_filters as filters
from django.utils.translation import ugettext_lazy as _
from .models import *


class InsuranceDebtFilter(filters.FilterSet):

    class Meta:
        model = InsuranceDebt
        fields = {
            'sub_contract': ['exact'],
            'type': ['exact'],
            'status': ['exact'],
            'id': ['exact'],
            'driver_government_id': ['icontains'],
            'driver_mobile': ['icontains'],
        }

    # def custom_title_filter(self, queryset, name, value):
    #     return queryset.filter(Q(title_ar__icontains=value) | Q(title_en__icontains=value))

    # def __init__(self, *args, **kwargs):
    #     super(InsuranceDebtFilter, self).__init__(*args, **kwargs)
    #     self.filters['id'].label = _('Insurance Debt No')
