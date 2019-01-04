import django_filters as filters
from django.db.models import Q

from django.utils.translation import ugettext_lazy as _

from .models import *


class InvoiceFilter(filters.FilterSet):
    general_search = filters.CharFilter(method='custom_general_filter', label=_('Search in Name Or Description'))

    class Meta:
        model = Invoice
        fields = {
            'reference': ['icontains'],
            'status': ['exact'],
            'client': ['exact'],
        }

    def custom_general_filter(self, queryset, name, value):
        return queryset.filter(Q(name_ar__icontains=value)
                               | Q(name_en__icontains=value)
                               | Q(description_ar__icontains=value)
                               |  Q(description_en__icontains=value))

    def __init__(self, *args, **kwargs):
        super(InvoiceFilter, self).__init__(*args, **kwargs)


class FundRequestFilter(filters.FilterSet):

    class Meta:
        model = FundRequest
        fields = {
            'approval_status': ['exact'],
            'approved_by': ['exact'],
            'project': ['exact'],
        }


def get_lookup_choices(add_dashes=True):
    try:
        choices = Project.objects.all()

        ch = [(o.pk, str(o)) for o in choices]
        return ch
    except:
        return [('--', '--')]


class TransactionFilter(filters.FilterSet):
    custom_project = filters.ChoiceFilter(choices=get_lookup_choices(add_dashes=False), label=_('Project'),
                                          method='custom_project_filter')
    general_search = filters.CharFilter(method='custom_general_filter', label=_('Search in Name Or Description'))
    date_range = filters.DateFromToRangeFilter('transaction_date')

    class Meta:
        model = Transaction
        fields = {
            'handing_party_role': ['exact'],
            'receiving_party_role': ['exact'],
        }

    def custom_general_filter(self, queryset, name, value):
        return queryset.filter(Q(name_ar__icontains=value)
                               | Q(name_en__icontains=value)
                               | Q(description_ar__icontains=value)
                               | Q(description_en__icontains=value))

    def custom_project_filter(self, queryset, name, value):
        return queryset.filter(Q(invoice__project=value)
                               | Q(fund_request__project=value))
