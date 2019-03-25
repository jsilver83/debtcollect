from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import CreateView, UpdateView, FormView
from django_tables2 import MultiTableMixin

from debtcollect.utils import get_model_details
from .mixins import DebtCollectorMixin
from projects.views import BaseListingView, BaseFormMixin
from .filters import *
from .forms import *
from .tables import *


class InsuranceDebtListing(DebtCollectorMixin, BaseListingView):
    model = InsuranceDebt
    template_name = "insurancedebt/insurance_debt_listing.html"

    def get_queryset(self):
        employee, s = Employee.objects.get_or_create(user=self.request.user)

        if self.request.user.groups.filter(name=UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP).exists():
            return self.model.objects.filter(Q(assignee__supervisor=employee) | Q(assignee=employee))
        elif self.request.user.groups.filter(name=UserGroups.DEBT_COLLECTORS_GROUP).exists():
            return self.model.objects.filter(assignee=employee).exclude(
                status__in=[InsuranceDebt.Statuses.FINISHED,
                            InsuranceDebt.Statuses.CANCELLED_WONT_PAY,
                            InsuranceDebt.Statuses.CANCELLED,
                            InsuranceDebt.Statuses.CANCELLED_WRONG_PERSON, ])
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
        docs = self.object.documents.all()
        payments = self.object.scheduled_payments.all()

        return [
            InsuranceDocumentTable(docs, user=self.request.user),
            ScheduledPaymentTable(payments, user=self.request.user),
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


class NewScheduledPaymentView(SuccessMessageMixin, DebtCollectorMixin, BaseFormMixin, CreateView):
    template_name = 'insurancedebt/form.html'
    success_message = _('Scheduled payment was created successfully')
    form_class = ScheduledPaymentForm

    insurance_debt = None

    def dispatch(self, request, *args, **kwargs):
        self.insurance_debt = get_object_or_404(InsuranceDebt, pk=self.kwargs['insurance_debt_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('update_insurance_debt', args=(self.kwargs['insurance_debt_pk']))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['insurance_debt'] = self.insurance_debt

        return kwargs

    def form_valid(self, form):
        employee, created = Employee.objects.get_or_create(user=self.request.user)
        instance = form.save(commit=False)
        instance.insurance_debt = self.insurance_debt
        instance.created_by = employee

        return super(NewScheduledPaymentView, self).form_valid(form)


class UpdateScheduledPaymentView(SuccessMessageMixin, DebtCollectorMixin, BaseFormMixin, UpdateView):
    template_name = 'insurancedebt/form.html'
    success_message = _('Scheduled payment was updated successfully')
    model = ScheduledPayment
    form_class = ScheduledPaymentForm

    def get_success_url(self):
        return reverse_lazy('update_insurance_debt', args=(self.object.insurance_debt.pk,))


class ReceiveScheduledPaymentView(SuccessMessageMixin, DebtCollectorMixin, BaseFormMixin, UpdateView):
    template_name = 'insurancedebt/form.html'
    success_message = _('Scheduled payment was received successfully')
    model = ScheduledPayment
    form_class = ScheduledPaymentReceiveForm

    def get_success_url(self):
        return reverse_lazy('update_insurance_debt', args=(self.object.insurance_debt.pk,))

    def form_valid(self, form):
        employee, created = Employee.objects.get_or_create(user=self.request.user)
        instance = form.save(commit=False)
        instance.received_by = employee

        return super().form_valid(form)


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
        try:
            self.debt = InsuranceDebt.objects.get(pk=self.request.session.get('debt_pk', 0))
        except:
            messages.error(request, _('Login first please'))
            return redirect('client_login')
        return super(ClientAreaView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientAreaView, self).get_context_data(**kwargs)
        context['object'] = self.debt
        context['docs'] = self.debt.documents.all()
        context['debt_details'] = get_model_details(self.debt,
                                                    ['id', 'status', 'status_comments', 'insurancedocument',
                                                     'debt_currency', 'assignee', 'created_on', 'created_by',
                                                     'updated_on', 'updated_by', 'sub_contract', ])
        context['title'] = _('Insurance Debt Details')
        context['debt_user'] = self.debt.insurer_full_name

        if self.debt.status != InsuranceDebt.Statuses.NEW:
            context['form'] = None

        return context

    def form_valid(self, form):
        client_choice = form.cleaned_data.get('client_choice')

        if client_choice in [ClientAreaForm.ClientChoices.WRONG_PERSON]:
            self.debt.status = InsuranceDebt.Statuses.CANCELLED_WRONG_PERSON
        elif client_choice in [ClientAreaForm.ClientChoices.WONT_PAY]:
            self.debt.status = InsuranceDebt.Statuses.CANCELLED_WONT_PAY
        elif client_choice in [ClientAreaForm.ClientChoices.WANT_TO_PAY]:
            self.debt.status = InsuranceDebt.Statuses.IN_PROGRESS
        elif client_choice in [ClientAreaForm.ClientChoices.WANT_TO_PAY_INSTALLMENTS]:
            self.debt.status = InsuranceDebt.Statuses.IN_PROGRESS_INSTALLMENTS

        self.debt.status_comments = _('The client chose this: [%s]' % client_choice)
        if form.cleaned_data.get('justification'):
            self.debt.client_notes = form.cleaned_data.get('justification')

        self.debt.updated_by = None

        self.debt.save()

        return super(ClientAreaView, self).form_valid(form)


class ClientLogout(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            del self.request.session['debt_pk']
        except KeyError:
            pass

        messages.success(request, _('Logged out successfully'))
        return redirect('client_login')
