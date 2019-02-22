from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from simplemathcaptcha.fields import MathCaptchaField

from debtcollect.utils import UserGroups, parse_non_standard_numerals
from projects.base_forms import *
from projects.models import Lookup
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
            del (self.fields['status'])
            del (self.fields['status_comments'])
            del (self.fields['assignee'])


class InsuranceDocumentForm(BaseUpdatedByForm, forms.ModelForm):
    class Meta:
        model = InsuranceDocument
        fields = '__all__'
        exclude = ['insurance_debt', 'uploaded_by', 'updated_by', ]

    def __init__(self, *args, **kwargs):
        super(InsuranceDocumentForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget = \
            forms.Select(choices=Lookup.get_lookup_choices(Lookup.LookupTypes.INSURANCE_DOCUMENT_TYPE))


class ClientLoginForm(BaseCrispyForm, forms.Form):
    mobile = forms.CharField(label=_('Your Mobile'), required=True, max_length=20, help_text=_('format: 05XXXXXXXX'),
                             validators=[
                                 RegexValidator(
                                     '^(05|٠٥)\d{8}$',
                                     message=_('You have entered an invalid mobile number')
                                 ),
                             ], )
    request_id = forms.IntegerField(label=_('Request ID'), required=True, )
    captcha = MathCaptchaField()

    def clean(self):
        cleaned_data = super(ClientLoginForm, self).clean()
        mobile = cleaned_data.get("mobile", "0")
        request_id = cleaned_data.get("request_id", "0")

        debt = InsuranceDebt.objects.filter(pk=request_id, driver_mobile=mobile).exists()

        if not debt:
            raise forms.ValidationError(_('Entered login data do NOT match with our records. Kindly try again!'))

        return cleaned_data

    def clean_mobile(self):
        return parse_non_standard_numerals(self.cleaned_data.get("mobile"))


class ClientAreaForm(BaseCrispyForm, forms.Form):
    class ClientChoices:
        WANT_TO_PAY = 'WANT_TO_PAY'
        WANT_TO_PAY_INSTALLMENTS = 'WANT_TO_PAY_INSTALLMENTS'
        WONT_PAY = 'WONT_PAY'
        WRONG_PERSON = 'WRONG_PERSON'

        @classmethod
        def choices(cls):
            return (
                (cls.WANT_TO_PAY, _('I want to pay')),
                (cls.WANT_TO_PAY_INSTALLMENTS, _('I want to pay with installments')),
                (cls.WONT_PAY, _('I wont pay')),
                (cls.WRONG_PERSON, _('This is the wrong person')),
            )

    client_choice = forms.ChoiceField(label=_('Your Action/Response'), required=True, choices=ClientChoices.choices(),
                                      widget=forms.RadioSelect)
    justification = forms.CharField(label=_('Justification'), widget=forms.Textarea, required=False,
                                    help_text=_('Enter any justifications you think is appropriate for your choice'))

    def clean(self):
        cleaned_data = super(ClientAreaForm, self).clean()
        client_choice = cleaned_data.get('client_choice')
        justification = cleaned_data.get('justification')
        if client_choice in [ClientAreaForm.ClientChoices.WONT_PAY, ClientAreaForm.ClientChoices.WRONG_PERSON] and not justification:
            raise ValidationError(_('Kindly enter justification for your action/choice'))

        return cleaned_data
