from django.contrib import admin
from reversion.admin import VersionAdmin
from django.utils.translation import ugettext_lazy as _
from .models import *


class FundRequestAdmin(VersionAdmin):
    list_display = ('justification', 'approved_amount', 'requester', 'request_date')


class TransactionAdmin(VersionAdmin):
    list_display = ('title', 'fund_request', 'amount', 'type')


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['reference', 'title_ar', 'title_en', 'description_ar', 'description_en', 'amount', 'status',
                    'created_on']


admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(FundRequest, FundRequestAdmin)
admin.site.register(Transaction, TransactionAdmin)
