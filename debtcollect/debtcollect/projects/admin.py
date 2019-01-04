from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin
from reversion.admin import VersionAdmin
from django.utils.translation import ugettext_lazy as _

from django import forms

from .models import *
from archive.models import *


class ReminderItemInline(admin.TabularInline):
    model = Reminder
    fields = ('title_ar', 'title_en', 'whom_to_remind', 'date', 'type')


class DocumentItemInline(admin.TabularInline):
    model = Document
    fields = ('document', 'title_ar', 'title_en', 'type')


class CaseAdmin(VersionAdmin):
    list_display = ('title', 'type', 'client', 'main_assignee', 'created_on', 'updated_by')
    date_hierarchy = 'created_on'
    inlines = [
        DocumentItemInline,
        ReminderItemInline,
    ]


class ClientAdmin(VersionAdmin):
    list_display = ('organization',)


class EmployeeAdmin(VersionAdmin):
    list_display = ('name',)


class ReminderAdmin(VersionAdmin):
    list_display = ('title', 'whom_to_remind', 'date', 'type')


class NationalityAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'nationality_ar', 'nationality_en', 'show', 'display_order')
    search_fields = ['nationality_en']


class LookupResource(resources.ModelResource):
    class Meta:
        model = Lookup
        import_id_fields = ('id',)
        fields = ('id', 'lookup_type', 'lookup_value_ar', 'lookup_value_en', 'show', 'display_order')
        skip_unchanged = True
        report_skipped = True


class LookupAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('lookup_type', 'lookup_value_ar', 'lookup_value_en', 'show', 'display_order')
    list_filter = ('lookup_type',)
    resource_class = LookupResource


class UpdateAdminForm(forms.ModelForm):

    class Meta:
        model = Update
        fields = '__all__'


class UpdateAdmin(admin.ModelAdmin):
    form = UpdateAdminForm
    list_display = ['summary_ar', 'summary_en', 'details_ar', 'details_en', 'date', 'attachments', 'inform_the_client']


class OrganizationAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name_ar', 'name_en', 'type', 'phone', 'city', 'created_on', 'updated_by')
    search_fields = ['name_ar', 'name_en']
    list_filter = ('type', 'city',)


class CourtAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name_ar', 'name_en', 'type', 'phone', 'city', 'created_on', 'updated_by')
    search_fields = ['name_ar', 'name_en']
    list_filter = ('type', 'city',)


admin.site.site_header = _('Law Firm')
admin.site.index_title = _('System Administration')
admin.site.site_title = _('Administration')

admin.site.register(Reminder, ReminderAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Lookup, LookupAdmin)
admin.site.register(Nationality, NationalityAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Update, UpdateAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Court, CourtAdmin)
