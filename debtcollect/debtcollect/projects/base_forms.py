from crispy_forms.bootstrap import FormActions, StrictButton
from crispy_forms.layout import Submit, Layout, ButtonHolder, Fieldset, Button, HTML
from crispy_forms.helper import FormHelper

from django.utils.translation import ugettext_lazy as _

from .models import Employee


class BaseCrispyForm:

    def __init__(self, *args, **kwargs):
        super(BaseCrispyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # self.helper.form_class = 'form-horizontal form-label-left'
        self.helper.label_class = 'col-lg-4 col-md-5 col-xs-5'
        self.helper.field_class = 'col-lg-7 col-md-7 col-xs-7'


class BaseCrispySearchForm(BaseCrispyForm):

    def __init__(self, *args, **kwargs):
        super(BaseCrispySearchForm, self).__init__(*args, **kwargs)
        # self.helper.add_input(Submit('search', _('Search'), css_class='btn btn-primary'))
        self.helper.form_method = 'get'


class BaseUpdatedByForm(BaseCrispyForm):

    def __init__(self, *args, **kwargs):
        self.user = None
        self.employee = None

        if kwargs.get('user'):
            self.user = kwargs.pop('user')
            self.employee = Employee.get_employee(self.user)
        super(BaseUpdatedByForm, self).__init__(*args, **kwargs)
        self.helper.add_input(Submit('submit', _('Submit')))

    def save(self, commit=True):
        instance = super(BaseUpdatedByForm, self).save(commit=False)
        instance.updated_by = self.employee
        if commit:
            instance.save()
        return instance
