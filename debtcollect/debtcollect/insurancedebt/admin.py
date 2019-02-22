from django.contrib import admin

from .forms import InsuranceDocumentForm
from .models import *


class InsuranceDocumentInline(admin.TabularInline):
    model = InsuranceDocument
    form = InsuranceDocumentForm
    fields = ('document', 'title', 'type')


class InsuranceDebtAdmin(admin.ModelAdmin):
    list_display = ('type', 'status', 'debt', 'assignee', 'driver_government_id', 'driver_full_name',
                    'insurer_full_name', 'driver_mobile', 'accident_location', 'accident_date', 'updated_by')
    date_hierarchy = 'created_on'
    readonly_fields = ['created_on', 'created_by', 'updated_on', 'updated_by', ]

    inlines = [
        InsuranceDocumentInline,
    ]


admin.site.register(InsuranceDebt, InsuranceDebtAdmin)
