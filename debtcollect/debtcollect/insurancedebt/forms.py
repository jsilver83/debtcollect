from dal import autocomplete

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_addanother.widgets import AddAnotherWidgetWrapper

from projects.models import Lookup
from projects.base_forms import *
from debtcollect.utils import UserGroups
from .models import *


class InsuranceDebtForm(BaseUpdatedByForm, forms.ModelForm):
    class Meta:
        model = InsuranceDebt
        fields = '__all__'
        exclude = ['updated_by', 'created_by', ]

    def __init__(self, *args, **kwargs):
        super(InsuranceDebtForm, self).__init__(*args, **kwargs)
        if not (self.employee.user.groups.filter(
                name__in=[UserGroups.DEBT_COLLECTING_ADMINS_GROUP,
                          UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP]).exists() or self.employee.user.is_superuser):
            del(self.fields['status'])
            del(self.fields['status_comments'])
            del(self.fields['assignee'])


class InsuranceDocumentForm(BaseUpdatedByForm, forms.ModelForm):
    class Meta:
        model = InsuranceDocument
        fields = '__all__'
        exclude = ['insurance_debt', 'uploaded_by', 'updated_by', ]

    def __init__(self, *args, **kwargs):
        super(InsuranceDocumentForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget = \
            forms.Select(choices=Lookup.get_lookup_choices(Lookup.LookupTypes.INSURANCE_DOCUMENT_TYPE))
