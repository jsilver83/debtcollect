import django_filters as filters

from dal import autocomplete
from django.db.models import Q
from django import forms
from django.contrib.auth.models import User as MyUser
from django.utils.translation import ugettext_lazy as _

from .models import *


class InsuranceDebtFilter(filters.FilterSet):
    class Meta:
        model = InsuranceDebt
        fields = {
            'type': ['exact'],
            'status': ['exact'],
            'driver_government_id': ['icontains'],
            'driver_mobile': ['icontains'],
        }

    # def custom_title_filter(self, queryset, name, value):
    #     return queryset.filter(Q(title_ar__icontains=value) | Q(title_en__icontains=value))

    # def __init__(self, *args, **kwargs):
    #     super(ProjectFilter, self).__init__(*args, **kwargs)
    #     self.filters['client'].widget = autocomplete.ModelSelect2(url='client-autocomplete', )
