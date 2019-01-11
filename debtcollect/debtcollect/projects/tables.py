import django_tables2 as tables
from django.utils import formats
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User as MyUser
from accounting.models import Transaction
from .models import *


class SummingColumn(tables.Column):
    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)


class BaseTableWithCommands(tables.Table):
    audit_data = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name='')
    view_link = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name='')
    update_link = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name='')
    delete_link = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name='')

    def render_view_link(self, *args, **kwargs):
        record = kwargs.pop('record')
        commands = '<a href="%s" class="btn btn-primary btn-xs"><i class="fa fa-folder"></i> %s</a>' \
                   % (record.get_absolute_url(), _('View'))
        return format_html(commands)

    def render_update_link(self, *args, **kwargs):
        record = kwargs.pop('record')
        commands = '<a href="%s" class="btn btn-info btn-xs"><i class="fa fa-pencil"></i> %s</a>' \
                   % (record.get_update_url(), _('Edit'))
        return format_html(commands)

    def render_delete_link(self, *args, **kwargs):
        record = kwargs.pop('record')
        commands = '<a href="%s" class="btn btn-danger btn-xs"><i class="fa fa-trash-o"></i> %s</a>' \
                   % (record.get_absolute_url(), _('Delete'))
        return format_html(commands)

    def render_audit_data(self, *args, **kwargs):
        try:
            record = kwargs.pop('record')
            commands = '<button type="button" ' \
                       'class="btn btn-secondary" ' \
                       'data-html="true"  ' \
                       'data-trigger="focus" ' \
                       'data-container="body" ' \
                       'data-toggle="popover" ' \
                       'data-placement="bottom" ' \
                       'data-content="<b>%s:<b> %s<br><b>%s:<b> %s<hr><b>%s:<b> %s<br><b>%s:<b> %s">' \
                       '<i class="fa fa-comment-o"></i> %s' \
                       '</button>' % (_('Created By'),
                                      record.created_by,
                                      _('Created On'),
                                      formats.date_format(record.created_on, 'DATETIME_FORMAT'),
                                      _('Updated By'),
                                      record.updated_by,
                                      _('Updated On'),
                                      formats.date_format(record.updated_on, 'DATETIME_FORMAT'),
                                      _('Audit'))
            return format_html(commands)
        except AttributeError:
            return ''

    def __init__(self, *args, **kwargs):
        self.employee, d = Employee.objects.get_or_create(user=kwargs.pop('user'))
        super(BaseTableWithCommands, self).__init__(*args, **kwargs)

        self.exclude = ()
        if not self.can_view():
            self.exclude = self.exclude + ('view_link',)

        if not self.can_update():
            self.exclude = self.exclude + ('update_link',)

        if not self.can_delete():
            self.exclude = self.exclude + ('delete_link',)

        if not self.can_see_audit_data():
            self.exclude = self.exclude + ('audit_data',)

    def can_view(self):
        return False

    def can_update(self):
        return False

    def can_delete(self):
        return False

    def can_see_audit_data(self):
        return True


class ProjectTable(BaseTableWithCommands):
    title = tables.Column(verbose_name=_('Title'))

    class Meta:
        model = Project
        fields = ['title', 'status', 'main_assignee', 'client', ]
        exclude = ['id']
        attrs = {'class': 'table table-striped table-bordered',
                 # 'id': 'datatable',
                 }

    def render_client(self, value):
        if value.client.organization:
            return format_html('%s<br><small>%s</small>' % (value.client, value.client.organization))
        else:
            return value.client

    def order_title(self, queryset, is_descending):
        lang = translation.get_language()
        if lang == "ar":
            queryset = queryset.order_by(('-' if is_descending else '') + 'title_ar')
        else:
            queryset = queryset.order_by(('-' if is_descending else '') + 'title_en')
        return queryset, True

    def can_view(self):
        return True

        # def __init__(self, *args, **kwargs):
        #     super(ProjectTable, self).__init__(*args, **kwargs)
        # self.columns['title'].orderable = False


class CaseTable(ProjectTable):
    class Meta(ProjectTable.Meta):
        model = Case
        fields = ProjectTable.Meta.fields + ['client_role', 'type', 'case_reference', 'court']


class ConsultationTable(ProjectTable):
    class Meta(ProjectTable.Meta):
        model = Consultation


class PaperworkTable(ProjectTable):
    class Meta(ProjectTable.Meta):
        model = Paperwork


class ReminderTable(BaseTableWithCommands):
    title = tables.Column(verbose_name=_('Title'))
    description = tables.Column(verbose_name=_('Description'))

    class Meta:
        model = Reminder
        fields = ['title', 'description', 'whom_to_remind', 'date', 'type', 'project',
                  'last_seen_on', ]
        attrs = {'class': 'table table-striped table-bordered', }

    def can_see_audit_data(self):
        return False

    def __init__(self, *args, **kwargs):
        self.project_page = False
        self.project_page = kwargs.pop('project_page')
        super(ReminderTable, self).__init__(*args, **kwargs)
        if self.project_page:
            self.exclude += ('project', )


class ClientTable(BaseTableWithCommands):
    personal_email = tables.EmailColumn()
    name = tables.Column(verbose_name=_('Name'))
    # organization = tables.RelatedLinkColumn()

    class Meta:
        model = Client
        fields = ['name', 'organization', 'mobile', 'work_phone', 'personal_email', 'gender', 'nationality']
        attrs = {'class': 'table table-striped table-bordered', }

    def order_name(self, queryset, is_descending):
        lang = translation.get_language()
        if lang == "ar":
            queryset = queryset.order_by(('-' if is_descending else '') + 'name_ar')
        else:
            queryset = queryset.order_by(('-' if is_descending else '') + 'name_en')
        return queryset, True


class OrganizationTable(BaseTableWithCommands):
    name = tables.Column(verbose_name=_('Name'))

    class Meta:
        model = Organization
        fields = ['name', 'type', 'phone', 'website', 'city', ]
        attrs = {'class': 'table table-striped table-bordered', }

    def order_name(self, queryset, is_descending):
        lang = translation.get_language()
        if lang == "ar":
            queryset = queryset.order_by(('-' if is_descending else '') + 'name_ar')
        else:
            queryset = queryset.order_by(('-' if is_descending else '') + 'name_en')
        return queryset, True


class CourtTable(OrganizationTable):
    class Meta(OrganizationTable.Meta):
        model = Court


class UserTable(BaseTableWithCommands):
    class Meta:
        model = MyUser
        fields = ['username', 'email', 'is_active', 'employee', 'employee.mobile' ]
        attrs = {'class': 'table table-striped table-bordered', }

    def render_update_link(self, *args, **kwargs):
        record = kwargs.pop('record')
        commands = '<a href="%s" class="btn btn-info btn-xs"><i class="fa fa-pencil"></i> %s</a>' \
                   % (reverse_lazy('update-user', args=[record.pk]), _('Edit'))
        return format_html(commands)

    def can_update(self):
        return True


class EmployeeTable(BaseTableWithCommands):
    name = tables.Column(verbose_name=_('Name'))

    class Meta:
        model = Employee
        fields = ['name', 'job_description', 'mobile', 'user.email', 'user.is_active',
                  'monthly_salary', ]
        attrs = {'class': 'table table-striped table-bordered', }

    def order_name(self, queryset, is_descending):
        lang = translation.get_language()
        if lang == "ar":
            queryset = queryset.order_by(('-' if is_descending else '') + 'name_ar')
        else:
            queryset = queryset.order_by(('-' if is_descending else '') + 'name_en')
        return queryset, True

    def can_update(self):
        return True


class LookupTable(BaseTableWithCommands):
    lookup_value = tables.Column(verbose_name=_('Lookup Value'))

    class Meta:
        model = Lookup
        fields = ['lookup_type', 'lookup_value', 'show', 'display_order']
        attrs = {'class': 'table table-striped table-bordered', }

    def order_lookup_value(self, queryset, is_descending):
        lang = translation.get_language()
        if lang == "ar":
            queryset = queryset.order_by(('-' if is_descending else '') + 'lookup_value_ar')
        else:
            queryset = queryset.order_by(('-' if is_descending else '') + 'lookup_value_en')
        return queryset, True

    def can_update(self):
        return True
