from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, UpdateView, CreateView
from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, SingleTableMixin
from django.contrib.auth.models import User as MyUser
from accounting.forms import NewFundRequestForm
from accounting.tables import *
from archive.models import DocumentMovement
from archive.tables import DocumentMovementTable
from insurancedebt.mixins import DebtCollectingAdminMixin
from .filters import ProjectFilter, CaseFilter, ClientFilter, OrganizationFilter, EmployeeFilter, LookupFilter, \
    UserFilter, ConsultationFilter, PaperworkFilter
from .forms import *
from .tables import *


class BaseLawyerMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admins', 'Lawyers']).exists() \
               or self.request.user.is_superuser


class BaseAdminView(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admins']).exists() \
               or self.request.user.is_superuser


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'projects/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['reminders'] = Reminder.get_upcoming_reminders(self.request.user)
        return context


class BaseListingView(SingleTableMixin, FilterView):
    model = None
    table_class = None
    table_pagination = {
        'per_page': 10
    }
    filterset_class = None
    template_name = ''
    strict = False

    def get_queryset(self):
        return self.model.objects.all()

    def get_table_kwargs(self):
        kwargs = super(BaseListingView, self).get_table_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BaseListingView, self).get_context_data(**kwargs)

        context['search_form'] = BaseCrispySearchForm

        return context


class ProjectListing(BaseLawyerMixin, BaseListingView):
    model = Project
    template_name = 'projects/projects_listing.html'

    def get_queryset(self):
        p_type = self.kwargs['p_type']

        if p_type.lower() == 'case':
            self.model = Case
        elif p_type.lower() == 'paperwork':
            self.model = Paperwork
        else:
            self.model = Consultation

        if self.request.user.groups.filter(name='Admins').exists() or self.request.user.is_superuser:
            return self.model.objects.all()
        else:
            return self.model.objects.filter(main_assignee=self.employee)

    def get_table_class(self):
        p_type = self.kwargs['p_type']

        if p_type.lower() == 'case':
            return CaseTable
        elif p_type.lower() == 'paperwork':
            return PaperworkTable
        else:
            return ConsultationTable

    def get_context_data(self, **kwargs):
        context = super(ProjectListing, self).get_context_data(**kwargs)

        p_type = self.kwargs['p_type']

        context['p_type'] = p_type

        if p_type.lower() == 'case':
            context['header_title'] = _('Cases')
            context['new_project_text'] = _('New Case')
        elif p_type.lower() == 'paperwork':
            context['header_title'] = _('Paperwork Projects')
            context['new_project_text'] = _('New Paperwork Project')
        else:
            context['header_title'] = _('Consultations')
            context['new_project_text'] = _('New Consultation')

        context['search_form'] = BaseCrispySearchForm

        return context

    def get_filterset_class(self):
        p_type = self.kwargs['p_type']

        if p_type.lower() == 'case':
            return CaseFilter
        elif p_type.lower() == 'paperwork':
            return PaperworkFilter
        else:
            return ConsultationFilter


class BaseFormMixin(object):

    def get_form_kwargs(self):
        kwargs = super(BaseFormMixin, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class NewProjectView(SuccessMessageMixin, BaseLawyerMixin, BaseFormMixin, CreateView):
    template_name = 'projects/new-project.html'
    success_message = _('Project was created successfully')

    def get_form_class(self):
        p_type = self.kwargs['p_type']

        if p_type.lower() == 'case':
            return CaseForm
        elif p_type.lower() == 'paperwork':
            return PaperworkForm
        else:
            return ConsultationForm

    def form_valid(self, form):
        employee, created = Employee.objects.get_or_create(user=self.request.user)
        instance = form.save(commit=False)
        instance.created_by = employee
        self.success_url = reverse_lazy('case_listing', args=(type(instance).__name__, ))
        return super(NewProjectView, self).form_valid(form)


class UpdateProjectView(SuccessMessageMixin, MultiTableMixin, BaseLawyerMixin, BaseFormMixin, UpdateView):
    template_name = 'projects/update-project.html'
    success_message = _('Project was updated successfully')

    # TODO: remove the ugly nested try ... excepts
    def get_object(self, queryset=None):
        try:
            project = Project.objects.get(pk=self.kwargs['pk'])

            try:
                if hasattr(project.case, 'pk'):
                    return project.case
            except Case.DoesNotExist:
                try:
                    if hasattr(project.consultation, 'pk'):
                        return project.consultation
                except Consultation.DoesNotExist:
                    try:
                        if hasattr(project.paperwork, 'pk'):
                            return project.paperwork
                    except Paperwork.DoesNotExist:
                        pass
        except Project.DoesNotExist:
            pass

    def get_success_url(self):
        return reverse_lazy('case_listing', args=(type(self.object).__name__, ))

    def get_form_class(self):
        if isinstance(self.object, Case):
            return CaseForm
        else:
            return ProjectForm

    def get_tables(self):
        fund_requests = FundRequest.objects.filter(project=self.get_object())
        docs_movements = DocumentMovement.objects.filter(document__project=self.get_object())
        invoices = Invoice.objects.filter(project=self.get_object())
        employee, d = Employee.objects.get_or_create(user=self.request.user)
        reminders = Reminder.objects.filter(project=self.get_object(),
                                            whom_to_remind=employee)
        return [
            FundRequestTable(fund_requests, user=self.request.user),
            DocumentMovementTable(docs_movements, user=self.request.user),
            InvoiceTable(invoices, user=self.request.user),
            ReminderTable(reminders, user=self.request.user, project_page=True),
        ]

    # TODO: implement case ownership check
    def test_func(self):
        return super(UpdateProjectView, self).test_func()


class NewFundRequestView(SuccessMessageMixin, BaseLawyerMixin, BaseFormMixin, CreateView):
    form_class = NewFundRequestForm
    template_name = 'projects/new-project.html'
    success_message = _('Fund request was submitted successfully. Check later for approval status')

    def get_form_kwargs(self):
        kwargs = super(NewFundRequestView, self).get_form_kwargs()
        kwargs['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('update_project', args=(self.kwargs['pk'], ))


class NewUpdateView(SuccessMessageMixin, BaseLawyerMixin, BaseFormMixin, CreateView):
    form_class = NewUpdateForm
    template_name = 'projects/new-project.html'
    success_message = _('Update was submitted successfully.')

    def get_form_kwargs(self):
        kwargs = super(NewUpdateView, self).get_form_kwargs()
        kwargs['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('update_project', args=(self.kwargs['pk'], ))


class ClientListingView(BaseLawyerMixin, BaseListingView):
    model = Client
    table_class = ClientTable
    filterset_class = ClientFilter
    template_name = 'projects/clients_listing.html'


class ClientView(SuccessMessageMixin, BaseLawyerMixin, BaseFormMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('clients')
    success_message = _('Client info was updated successfully')


class NewClientView(BaseLawyerMixin, BaseFormMixin, CreateView):
    form_class = ClientForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('clients')
    success_message = _('Client was added successfully')


class OrganizationListingView(DebtCollectingAdminMixin, BaseLawyerMixin, BaseListingView):
    model = Organization
    table_class = OrganizationTable
    filterset_class = OrganizationFilter
    template_name = 'projects/organizations_listing.html'


class CourtsListing(BaseLawyerMixin, BaseListingView):
    model = Court
    table_class = CourtTable
    filterset_class = OrganizationFilter
    template_name = 'projects/courts_listing.html'


class OrganizationView(SuccessMessageMixin, DebtCollectingAdminMixin, BaseLawyerMixin, BaseFormMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('organizations')
    success_message = _('Organization info was updated successfully')


class NewOrganizationView(DebtCollectingAdminMixin, BaseLawyerMixin, BaseFormMixin, CreateView):
    form_class = OrganizationForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('organizations')
    success_message = _('Organization was added successfully')


class NewCourtView(BaseLawyerMixin, BaseFormMixin, CreateView):
    form_class = CourtForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('courts')
    success_message = _('Organization was added successfully')


class NewReminderView(SuccessMessageMixin, BaseLawyerMixin, BaseFormMixin, CreateView):
    form_class = NewReminderForm
    template_name = 'projects/form.html'
    success_message = _('Reminder was created successfully.')

    def get_form_kwargs(self):
        kwargs = super(NewReminderView, self).get_form_kwargs()
        kwargs['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def get_success_url(self):
        return reverse_lazy('update_project', args=(self.kwargs['pk'], ))


class EmployeesListingView(DebtCollectingAdminMixin, BaseAdminView, BaseListingView):
    model = Employee
    table_class = EmployeeTable
    filterset_class = EmployeeFilter
    template_name = 'projects/employees_listing.html'


class NewEmployeeView(SuccessMessageMixin, DebtCollectingAdminMixin, BaseAdminView, BaseFormMixin, CreateView):
    form_class = NewEmployeeForm
    template_name = 'projects/form.html'
    success_message = _('Employee was created successfully.')
    success_url = reverse_lazy('employees')


class EmployeeView(SuccessMessageMixin, DebtCollectingAdminMixin, BaseAdminView, BaseFormMixin, UpdateView):
    model = Employee
    form_class = NewEmployeeForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('employees')
    success_message = _('Employee info was updated successfully')


class LookupsListingView(DebtCollectingAdminMixin, BaseAdminView, BaseListingView):
    model = Lookup
    table_class = LookupTable
    filterset_class = LookupFilter
    template_name = 'projects/lookups_listing.html'


class NewLookupView(SuccessMessageMixin, DebtCollectingAdminMixin, BaseAdminView, CreateView):
    model = Lookup
    form_class = LookupForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('lookups')
    success_message = _('Lookup was added successfully')


class UpdateLookupView(SuccessMessageMixin, DebtCollectingAdminMixin, BaseAdminView, UpdateView):
    model = Lookup
    form_class = LookupForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('lookups')
    success_message = _('Lookup was updated successfully')


class UsersListingView(DebtCollectingAdminMixin, BaseAdminView, BaseListingView):
    model = MyUser
    table_class = UserTable
    filterset_class = UserFilter
    template_name = 'projects/users_listing.html'


class NewUserView(DebtCollectingAdminMixin, SuccessMessageMixin, BaseAdminView, CreateView):
    model = MyUser
    form_class = MyUserCreationForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('users')
    success_message = _('User was added successfully')


class UpdateUserView(DebtCollectingAdminMixin, SuccessMessageMixin, BaseAdminView, UpdateView):
    model = MyUser
    form_class = MyUserChangeForm
    template_name = 'projects/form.html'
    success_url = reverse_lazy('users')
    success_message = _('User was updated successfully')
