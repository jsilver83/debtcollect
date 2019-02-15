import django_tables2 as tables
from django.utils import formats
from django.utils.html import format_html

from django.utils.translation import ugettext_lazy as _

from projects.tables import BaseTableWithCommands
from .models import *


class InsuranceDebtTable(BaseTableWithCommands):
    class Meta:
        model = InsuranceDebt
        fields = ['pk', 'type', 'status', 'debt', 'driver_government_id', 'driver_mobile', 'accident_date', ]
        attrs = {'class': 'table table-striped table-bordered',
                 'id': 'datatable'}

    def can_view(self):
        return True


class InsuranceDocumentTable(BaseTableWithCommands):
    class Meta:
        model = InsuranceDocument
        fields = ['document', 'title', 'type', 'uploaded_on', 'uploaded_by', ]
        attrs = {'class': 'table table-striped table-bordered',
                 'id': 'datatable'}

    def can_view(self):
        return False
