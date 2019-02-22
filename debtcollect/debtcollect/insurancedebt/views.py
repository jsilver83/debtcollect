from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import CreateView, UpdateView, FormView
from django_tables2 import MultiTableMixin

from debtcollect.utils import get_model_details
from projects.views import BaseListingView, BaseFormMixin
from .filters import *
from .forms import *
from .tables import *


class DebtCollectorMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=[UserGroups.DEBT_COLLECTORS_GROUP,
                                                         UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP,
                                                         UserGroups.DEBT_COLLECTING_ADMINS_GROUP]).exists() \
               or self.request.user.is_superuser


class DebtCollectSupervisorAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=[UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP,
                                                         UserGroups.DEBT_COLLECTING_ADMINS_GROUP]).exists() \
               or self.request.user.is_superuser


class DebtCollectingAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name=UserGroups.DEBT_COLLECTING_ADMINS_GROUP).exists() \
               or self.request.user.is_superuser


class InsuranceDebtListing(DebtCollectorMixin, BaseListingView):
    model = InsuranceDebt
    template_name = "insurancedebt/insurance_debt_listing.html"

    def get_queryset(self):
        employee, s = Employee.objects.get_or_create(user=self.request.user)

        if self.request.user.groups.filter(name=UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP).exists():
            return self.model.objects.filter(assignee__supervisor=employee)
        elif self.request.user.groups.filter(name=UserGroups.DEBT_COLLECTORS_GROUP).exists():
            return self.model.objects.filter(assignee=employee)
        else:
            return self.model.objects.all()

    def get_table_class(self):
        return InsuranceDebtTable

    def get_context_data(self, **kwargs):
        context = super(InsuranceDebtListing, self).get_context_data(**kwargs)

        context['header_title'] = _('Insurance Debts Listing')
        context['new_project_text'] = _('New Insurance Debt')
        context['search_form'] = BaseCrispySearchForm

        return context

    def get_filterset_class(self):
        return InsuranceDebtFilter


class NewInsuranceDebtView(SuccessMessageMixin, DebtCollectorMixin, BaseFormMixin, CreateView):
    template_name = 'insurancedebt/insurance_debt_form.html'
    success_message = _('Insurance Debt was created successfully')
    form_class = InsuranceDebtForm

    def form_valid(self, form):
        employee, created = Employee.objects.get_or_create(user=self.request.user)
        instance = form.save(commit=False)
        instance.created_by = employee
        self.success_url = reverse_lazy('insurance_debt_listing')
        return super(NewInsuranceDebtView, self).form_valid(form)


class UpdateInsuranceDebtView(SuccessMessageMixin, DebtCollectorMixin, BaseFormMixin, MultiTableMixin, UpdateView):
    template_name = 'insurancedebt/insurance_debt_form.html'
    success_message = _('Insurance Debt was updated successfully')
    form_class = InsuranceDebtForm
    model = InsuranceDebt

    def get_tables(self):
        print(self.get_object())
        docs = InsuranceDocument.objects.filter(insurance_debt=self.object)
        return [
            InsuranceDocumentTable(docs, user=self.request.user),
        ]


class NewInsuranceDocumentView(SuccessMessageMixin, DebtCollectorMixin, BaseFormMixin, CreateView):
    template_name = 'insurancedebt/form.html'
    success_message = _('Insurance Document was created successfully')
    form_class = InsuranceDocumentForm

    def get_success_url(self):
        return reverse_lazy('update_insurance_debt', args=(self.kwargs['insurance_debt_pk']))

    def form_valid(self, form):
        employee, created = Employee.objects.get_or_create(user=self.request.user)
        instance = form.save(commit=False)
        instance.uploaded_by = employee
        instance.insurance_debt = get_object_or_404(InsuranceDebt, pk=self.kwargs['insurance_debt_pk'])
        return super(NewInsuranceDocumentView, self).form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class CommentPostedSuccessfully(View):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _('Comment was posted successfully'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class ClientLoginView(SuccessMessageMixin, FormView):
    template_name = 'insurancedebt/client_login.html'
    form_class = ClientLoginForm
    success_url = reverse_lazy('client_area')
    success_message = _('Successful login')

    def form_valid(self, form):
        debt = InsuranceDebt.objects.filter(pk=form.cleaned_data.get('request_id'),
                                            driver_mobile=form.cleaned_data['mobile'], )

        if debt:
            self.request.session['debt_pk'] = debt.first().pk
        return super().form_valid(form)


class ClientAreaView(SuccessMessageMixin, UserPassesTestMixin, FormView):
    template_name = 'insurancedebt/client_area.html'
    form_class = ClientAreaForm
    success_message = _('You submitted your action/choice successfully')
    success_url = reverse_lazy('client_area')
    debt = None
    login_url = reverse_lazy('client_login')

    def test_func(self):
        return self.request.session.get('debt_pk', 0)

    def dispatch(self, request, *args, **kwargs):
        self.debt = get_object_or_404(InsuranceDebt, pk=self.request.session.get('debt_pk', 0))
        return super(ClientAreaView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientAreaView, self).get_context_data(**kwargs)
        context['object'] = self.debt
        context['docs'] = self.debt.documents.all()
        context['debt_details'] = get_model_details(self.debt,
                                                    ['id', 'status', 'status_comments', 'insurancedocument',
                                                     'debt_currency', 'assignee', 'created_on', 'created_by',
                                                     'updated_on', 'updated_by'])
        context['title'] = _('Insurance Debt Details')

        if self.debt.status != InsuranceDebt.Statuses.NEW:
            context['form'] = None

        return context

    def form_valid(self, form):

        return super(ClientAreaView, self).form_valid(form)
