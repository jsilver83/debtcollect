from admin_numeric_filter.admin import SliderNumericFilter, NumericFilterModelAdmin
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin

from .forms import InsuranceDocumentForm
from .models import *


class InsuranceDocumentInline(admin.TabularInline):
    model = InsuranceDocument
    form = InsuranceDocumentForm
    fields = ('document', 'title', 'type')
    readonly_fields = ('created_on', )


class ScheduledPaymentInline(admin.TabularInline):
    model = ScheduledPayment
    fields = ('amount', 'scheduled_date', 'created_on', 'created_by', 'received_on', 'received_by')
    readonly_fields = ('created_on', )


class InsuranceDebtResource(resources.ModelResource):
    class Meta:
        model = InsuranceDebt
        # import_id_fields = ('id',)
        fields = ('id', 'sub_contract', 'type', 'type_justification', 'status', 'status_comments', 'debt',
                  'assignee', 'driver_government_id', 'driver_full_name', 'insurer_full_name', 'driver_mobile',
                  'accident_location', 'accident_date', 'client_notes', 'notes', )
        skip_unchanged = True
        report_skipped = True

    def dehydrate_debt(self, insurance_debt):
        return insurance_debt.debt.amount


class InsuranceDebtAdmin(ImportExportMixin, NumericFilterModelAdmin):
    list_display = ('id', 'sub_contract', 'type', 'status', 'debt', 'assignee', 'driver_government_id',
                    'insurer_full_name', 'driver_full_name', 'driver_mobile', 'created_on', 'updated_on', 'updated_by')
    list_editable = ('type', 'status', 'assignee')
    date_hierarchy = 'created_on'
    readonly_fields = ['created_on', 'created_by', 'updated_on', 'updated_by', ]
    search_fields = ('id', 'driver_government_id', 'driver_full_name',
                     'insurer_full_name', 'driver_mobile', 'accident_location')
    list_filter = ('type', 'status', 'sub_contract', 'assignee', ('debt', SliderNumericFilter), )
    resource_class = InsuranceDebtResource

    inlines = [
        InsuranceDocumentInline,
        ScheduledPaymentInline,
    ]


class InsuranceContractAdmin(NumericFilterModelAdmin):
    list_display = ('insurance_company', 'employee_name', 'start_date', 'end_date',
                    'contract_soft_copy', 'agreed_cut', 'signed_on', 'signed_by', 'created_on', 'created_by')
    date_hierarchy = 'created_on'
    search_fields = ('insurance_company__name_ar', 'insurance_company__name_en', 'employee_name',
                     'employee_contact_details', 'details', 'agreed_cut', )
    list_filter = ('insurance_company', 'agreed_cut', )


class InsuranceSubContractAdmin(NumericFilterModelAdmin):
    list_display = ('contract', 'employee_name', 'sub_contract_soft_copy', 'agreed_cut', 'signed_on', 'signed_by',
                    'created_on', 'created_by')
    date_hierarchy = 'created_on'
    search_fields = ('contract__insurance_company__name_ar', 'contract__insurance_company__name_en', 'employee_name',
                     'employee_contact_details', 'details', 'agreed_cut', )
    list_filter = ('contract__insurance_company', 'agreed_cut', )


admin.site.register(InsuranceContract, InsuranceContractAdmin)
admin.site.register(InsuranceSubContract, InsuranceSubContractAdmin)
admin.site.register(InsuranceDebt, InsuranceDebtAdmin)
