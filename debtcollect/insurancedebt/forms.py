from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

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
        exclude = ['insurance_debt', 'created_by', 'updated_by', ]

    def __init__(self, *args, **kwargs):
        super(InsuranceDocumentForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget = \
            forms.Select(choices=Lookup.get_lookup_choices(Lookup.LookupTypes.INSURANCE_DOCUMENT_TYPE))


class ScheduledPaymentForm(BaseUpdatedByForm, forms.ModelForm):
    class Meta:
        model = ScheduledPayment
        fields = ['amount', 'scheduled_date']

    def __init__(self, *args, **kwargs):
        self.insurance_debt = None
        if kwargs.get('insurance_debt'):
            self.insurance_debt = kwargs.pop('insurance_debt')

        super(ScheduledPaymentForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self.insurance_debt = self.instance.insurance_debt
            if self.instance.received_on:
                self.fields['amount'].widget.attrs.update({'disabled': True})
                self.fields['scheduled_date'].widget.attrs.update({'disabled': True})

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if self.instance.pk:
            if self.insurance_debt.can_change_scheduled_payment(self.instance, amount):
                raise ValidationError(_('Entered amount is higher than the remaining amount of the debt'))
        else:
            if amount > self.insurance_debt.get_remaining_unscheduled_debt():
                raise ValidationError(_('Entered amount is higher than the remaining amount of the debt'))

        return amount


class ScheduledPaymentReceiveForm(BaseUpdatedByForm, forms.ModelForm):
    class Meta:
        model = ScheduledPayment
        fields = ['payment_method', 'received_on', 'proof_of_payment', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].required = True
        self.fields['received_on'].required = True


class MyAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(MyAuthenticationForm, self).__init__(*args, **kwargs)
        if not settings.DISABLE_CAPTCHA:
            self.fields['captcha'] = ReCaptchaField(widget=ReCaptchaV2Checkbox, label=_('Confirmation Code'))


class ClientLoginForm(BaseCrispyForm, forms.Form):
    mobile = forms.CharField(label=_('Your Mobile'), required=True, max_length=20, help_text=_('format: 05XXXXXXXX'),
                             validators=[
                                 RegexValidator(
                                     '^(05|٠٥)\d{8}$',
                                     message=_('You have entered an invalid mobile number')
                                 ),
                             ], )
    request_id = forms.IntegerField(label=_('Request ID'), required=True, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.DISABLE_CAPTCHA:
            self.fields['captcha'] = ReCaptchaField(widget=ReCaptchaV2Checkbox, label=_('Confirmation Code'))

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
        if (client_choice in [ClientAreaForm.ClientChoices.WONT_PAY,
                              ClientAreaForm.ClientChoices.WRONG_PERSON] and not justification):
            raise ValidationError(_('Kindly enter justification for your action/choice'))

        return cleaned_data
