from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin

from .forms import MyUserCreationForm, MyUserChangeForm, OrganizationForm, NationalityForm, CourtForm, ClientPopupForm
from .views import BaseFormMixin, BaseAdminView, BaseLawyerMixin


class NewUserView(BaseAdminView, CreatePopupMixin, CreateView):
    form_class = MyUserCreationForm
    template_name = 'projects/plain-form.html'


class ChangeUserView(BaseAdminView, UpdatePopupMixin, UpdateView):
    form_class = MyUserChangeForm
    template_name = 'projects/plain-form.html'


class NewClientPopupView(LoginRequiredMixin, CreatePopupMixin, BaseFormMixin, CreateView):
    form_class = ClientPopupForm
    template_name = 'projects/plain-form.html'


class NewOrganizationPopupView(LoginRequiredMixin, CreatePopupMixin, BaseFormMixin, CreateView):
    form_class = OrganizationForm
    template_name = 'projects/plain-form.html'


class NewCourtPopupView(BaseLawyerMixin, CreatePopupMixin, BaseFormMixin, CreateView):
    form_class = CourtForm
    template_name = 'projects/plain-form.html'


class NewNationalityPopupView(LoginRequiredMixin, CreatePopupMixin, BaseFormMixin, CreateView):
    form_class = NationalityForm
    template_name = 'projects/plain-form.html'
