import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from djmoney.money import Money

from projects.tables import BaseTableWithCommands, SummingColumn
from .models import *


class TransactionAmountColumn(tables.Column):
    def render_footer(self, bound_column, table):
        suma = Money(amount='0.00', currency='SAR')
        for row in table.data:
            if row.handing_party_role == Transaction.AccountingRoles.ACCOUNTING \
                    and row.receiving_party_role != Transaction.AccountingRoles.ACCOUNTING:
                suma -= bound_column.accessor.resolve(row)
            elif row.receiving_party_role == Transaction.AccountingRoles.ACCOUNTING \
                    and row.handing_party_role != Transaction.AccountingRoles.ACCOUNTING:
                suma += bound_column.accessor.resolve(row)
        return suma


class FundRequestTable(BaseTableWithCommands):
    approval_link = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name='')
    transaction_link = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name='')

    class Meta:
        model = FundRequest
        fields = ['project', 'requester', 'amount', 'justification', 'request_date', 'approval_status',
                  'approved_amount', 'approved_by', 'approval_comments', 'approval_date', ]
        attrs = {'class': 'table table-striped table-bordered'}

    def __init__(self, *args, **kwargs):
        self.accounting = False
        if 'accounting' in kwargs:
            self.accounting = kwargs.pop('accounting')
        super(FundRequestTable, self).__init__(*args, **kwargs)
        if not self.can_approve():
            self.exclude += ('approval_link',)
        if not self.accounting:
            self.exclude += ('project',)

    def can_approve(self):
        return self.employee.user.groups.filter(name__in=['Admins', 'Accounting']).exists() \
               or self.employee.user.is_superuser

    def can_make_transaction(self):
        return self.can_approve()

    def render_approval_link(self, *args, **kwargs):
        record = kwargs.pop('record')
        command = '<a href="%s" class="btn btn-warning btn-xs"><i class="fa fa-calculator"></i> %s</a>' \
                  % (record.get_approval_url(), _('Approve'))
        return format_html(command)

    def render_transaction_link(self, *args, **kwargs):
        record = kwargs.pop('record')
        command = ''
        if record.approval_status == FundRequest.Statuses.APPROVED:
            command = '<a class="btn btn-app" href="%s"><span class="badge bg-red">%d</span>' \
                      '<i class="fa fa-money"></i> %s</a>' % (record.get_new_expense_url(),
                                                              record.transactions.count(),
                                                              _('New Expense'))
        return format_html(command)


class InvoiceTable(BaseTableWithCommands):
    payment_link = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name='')

    class Meta:
        model = Invoice
        fields = ['reference', 'title', 'client', 'amount', 'date', 'status', ]
        sequence = ('reference', 'title', 'client', 'amount', 'date', 'status', 'payment_link')
        attrs = {'class': 'table table-striped table-bordered'}

    def __init__(self, *args, **kwargs):
        super(InvoiceTable, self).__init__(*args, **kwargs)
        if not self.can_pay():
            self.exclude += ('payment_link',)

    def can_pay(self):
        return self.employee.user.groups.filter(name__in=['Admins', 'Accounting']).exists() \
               or self.employee.user.is_superuser

    def render_payment_link(self, *args, **kwargs):
        record = kwargs.pop('record')
        command = ''
        if record.status == Invoice.Statuses.PENDING:
            command = '<a class="btn btn-app" href="%s"><span class="badge bg-red">%d</span>' \
                      '<i class="fa fa-money"></i> %s</a>' % (record.get_new_payment_url(),
                                                              record.transactions.count(),
                                                              _('New Payment'))
        return format_html(command)

    def order_title(self, queryset, is_descending):
        lang = translation.get_language()
        if lang == "ar":
            queryset = queryset.order_by(('-' if is_descending else '') + 'title_ar')
        else:
            queryset = queryset.order_by(('-' if is_descending else '') + 'title_en')
        return queryset, True


class TransactionTable(BaseTableWithCommands):
    project = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name=_('Project'))
    amount = TransactionAmountColumn()

    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'description', 'invoice', 'fund_request', 'handing_party',
                  'receiving_party', 'transaction_date', 'type', 'transaction_type']
        sequence = ('project', 'title', 'amount', 'description', 'invoice', 'fund_request', 'handing_party',
                    'receiving_party', 'type', 'transaction_type', 'transaction_date')
        attrs = {'class': 'table table-striped table-bordered'}

    def __init__(self, *args, **kwargs):
        super(TransactionTable, self).__init__(*args, **kwargs)

    def value_amount(self, value, **kwargs):
        record = kwargs.pop('record')
        return ''

    def render_project(self, value, **kwargs):
        record = kwargs.pop('record')
        try:
            if record.fund_request.project:
                return format_html('<button type="button" class="btn btn-default" '
                                   'data-toggle="tooltip" data-placement="left" title="" data-original-title="%s">%s'
                                   '</button>' % (_('Fund Request'), record.fund_request.project))
        except AttributeError:
            try:
                if record.invoice.project:
                    return format_html('<button type="button" class="btn btn-default" '
                                       'data-toggle="tooltip" data-placement="left" title="" data-original-title="%s">'
                                       '%s</button>' % (_('Invoice'), record.invoice.project))
            except AttributeError:
                return ''

    def render_handing_party(self, value, **kwargs):
        record = kwargs.pop('record')
        return format_html('<button type="button" class="btn btn-default" data-toggle="tooltip" data-placement="left" '
                           'title="" data-original-title="%s">%s</button>' % (record.get_handing_party_role_display(),
                                                                              value))

    def render_receiving_party(self, value, **kwargs):
        record = kwargs.pop('record')
        return format_html('<button type="button" class="btn btn-default" data-toggle="tooltip" data-placement="left" '
                           'title="" data-original-title="%s">%s</button>' % (record.get_receiving_party_role_display(),
                                                                              value))

    def render_transaction_type(self, value):
        if value == Transaction.TransactionTypes.CREDIT:
            return format_html('<h4 class="label label-success"><i class="fa fa-download"></i> %s</h4>' % (value,))
        elif value == Transaction.TransactionTypes.DEBIT:
            return format_html('<h4 class="label label-danger"><i class="fa fa-upload"></i> %s</h4>' % (value,))
        else:
            return format_html('<h4 class="label label-default">%s</h4>' % (value,))

    def order_type(self, queryset, is_descending):
        return queryset, True

    def order_transaction_type(self, queryset, is_descending):
        return queryset, True

    def order_title(self, queryset, is_descending):
        lang = translation.get_language()
        if lang == "ar":
            queryset = queryset.order_by(('-' if is_descending else '') + 'title_ar')
        else:
            queryset = queryset.order_by(('-' if is_descending else '') + 'title_en')
        return queryset, True
