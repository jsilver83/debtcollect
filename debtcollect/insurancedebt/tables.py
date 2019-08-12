import django_tables2 as tables
from django.utils import formats
from django.utils.html import format_html

from django.utils.translation import ugettext_lazy as _

from projects.tables import BaseTableWithCommands
from .models import *


class InsuranceDebtTable(BaseTableWithCommands):
    class Meta:
        model = InsuranceDebt
        fields = ['debt_no', 'type', 'status', 'debt', 'driver_government_id', 'driver_mobile', 'accident_date', ]
        attrs = {'class': 'table table-striped table-bordered',
                 'id': 'datatable'}

    def can_view(self):
        return True


class ScheduledPaymentTable(BaseTableWithCommands):
    receive_link = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name='')

    class Meta:
        model = ScheduledPayment
        fields = ['pk', 'amount', 'scheduled_date', 'payment_method', 'received_on', 'received_by', ]
        attrs = {'class': 'table table-striped table-bordered',
                 'id': 'datatable'}

    def can_view(self):
        return True

    def render_receive_link(self, *args, **kwargs):
        record = kwargs.pop('record')
        if not record.received_on:
            commands = '<a href="%s" class="btn btn-success btn-xs"><i class="fa fa-money"></i> %s</a>' \
                       % (record.get_receive_url(), _('Receive'))
            return format_html(commands)
        else:
            return ''


class InsuranceDocumentTable(BaseTableWithCommands):
    class Meta:
        model = InsuranceDocument
        fields = ['document', 'title', 'type', 'created_on', 'created_by', ]
        attrs = {'class': 'table table-striped table-bordered',
                 'id': 'datatable'}

    def can_view(self):
        return False
