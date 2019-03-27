from crispy_forms.bootstrap import AppendedText
from crispy_forms.layout import Submit, Layout, ButtonHolder, Fieldset
from django import forms
from crispy_forms.helper import FormHelper
from django.utils import timezone

from django.utils.translation import ugettext_lazy as _

from projects.base_forms import BaseUpdatedByForm
from .models import *


class NewFundRequestForm(BaseUpdatedByForm, forms.ModelForm):
    class Meta:
        model = FundRequest
        fields = ['amount', 'justification', 'justification_proof']

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(NewFundRequestForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(NewFundRequestForm, self).save(commit=False)
        instance.project = self.project
        instance.requester = self.employee
        instance.request_date = timezone.now()
        instance.created_on = timezone.now()
        instance.created_by = self.employee

        if commit:
            instance.save()

        return instance


class ApproveFundRequestForm(BaseUpdatedByForm, forms.ModelForm):
    class Meta:
        model = FundRequest
        fields = '__all__'
        exclude = ['created_on', 'created_by', 'updated_on', 'updated_by', 'project', 'amount',
                   'requester', 'request_date', 'justification', 'justification_proof', ]

    def __init__(self, *args, **kwargs):
        super(ApproveFundRequestForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field in ['approved_by', 'approval_date']:
                self.fields[field].disabled = True

    def save(self, commit=True):
        instance = super(ApproveFundRequestForm, self).save(commit=False)
        instance.approved_by = self.employee
        instance.approval_date = timezone.now()

        if commit:
            instance.save()

        return instance


class NewInvoiceForm(BaseUpdatedByForm, forms.ModelForm):

    class Meta:
        model = Invoice
        fields = '__all__'
        exclude = ['status', 'created_on', 'created_by', 'updated_on', 'updated_by']

    def __init__(self, *args, **kwargs):
        self.project = 0
        if 'project' in kwargs:
            self.project = kwargs.pop('project')
        super(NewInvoiceForm, self).__init__(*args, **kwargs)
        if self.project:
            del self.fields['project']

    def save(self, commit=True):
        instance = super(NewInvoiceForm, self).save(commit=False)
        instance.status = Invoice.Statuses.NEW
        instance.created_on = timezone.now()
        instance.created_by = self.employee
        if self.project:
            instance.project = self.project

        if commit:
            instance.save()

        return instance


class InvoiceForm(BaseUpdatedByForm, forms.ModelForm):

    class Meta:
        model = Invoice
        fields = '__all__'
        exclude = ['created_on', 'created_by', 'updated_on', 'updated_by']


class NewExpenseForm(BaseUpdatedByForm, forms.ModelForm):

    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ['created_on', 'created_by', 'updated_on', 'updated_by', 'invoice',
                   'fund_request', 'handing_party', 'handing_party_role', 'receiving_party', 'receiving_party_role']

    def __init__(self, *args, **kwargs):
        self.project = 0
        self.fund_request = FundRequest.objects.get(pk=kwargs.pop('fund_request_pk'))
        super(NewExpenseForm, self).__init__(*args, **kwargs)
        self.initial['amount'] = self.fund_request.approved_amount
        self.initial['title_ar'] = self.fund_request.justification

    def save(self, commit=True):
        instance = super(NewExpenseForm, self).save(commit=False)
        instance.fund_request = self.fund_request
        instance.handing_party = self.employee
        instance.handing_party_role = Transaction.AccountingRoles.ACCOUNTING
        instance.receiving_party = self.fund_request.requester
        instance.receiving_party_role = Transaction.AccountingRoles.EMPLOYEE

        instance.created_on = timezone.now()
        instance.created_by = self.employee

        if commit:
            instance.save()

        return instance


class NewPaymentForm(BaseUpdatedByForm, forms.ModelForm):

    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ['created_on', 'created_by', 'updated_on', 'updated_by', 'invoice',
                   'fund_request', 'handing_party', 'handing_party_role', 'receiving_party', 'receiving_party_role']

    def __init__(self, *args, **kwargs):
        self.project = 0
        self.invoice = Invoice.objects.get(pk=kwargs.pop('invoice_pk'))
        super(NewPaymentForm, self).__init__(*args, **kwargs)
        self.initial['amount'] = self.invoice.amount
        self.initial['title_ar'] = self.invoice.title_ar
        self.initial['title_en'] = self.invoice.title_en
        self.initial['description_ar'] = self.invoice.description_ar
        self.initial['description_en'] = self.invoice.description_en

    def save(self, commit=True):
        instance = super(NewPaymentForm, self).save(commit=False)
        instance.invoice = self.invoice
        instance.handing_party = self.invoice.client
        instance.handing_party_role = Transaction.AccountingRoles.CLIENT
        instance.receiving_party = self.employee
        instance.receiving_party_role = Transaction.AccountingRoles.ACCOUNTING

        instance.created_on = timezone.now()
        instance.created_by = self.employee

        if commit:
            instance.save()

        return instance
