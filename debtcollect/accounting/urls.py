from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^invoices/$', views.InvoiceListingView.as_view(), name='invoice_listing'),
    url(r'^invoice/$', views.NewInvoiceView.as_view(), name='new_invoice'),
    url(r'^project_invoice/(?P<project_pk>\d+)/$', views.NewInvoiceView.as_view(), name='new_project_invoice'),
    url(r'^invoice/(?P<pk>\d+)/$', views.UpdateInvoiceView.as_view(), name='update_invoice'),
    url(r'^new_payment/(?P<invoice_pk>\d+)/$', views.NewPaymentView.as_view(), name='new_payment'),

    url(r'^fund_requests/$', views.FundRequestListingView.as_view(), name='fund_request_listing'),
    url(r'^approve_request/(?P<pk>\d+)/$', views.FundRequestApprovalView.as_view(), name='approve_fund_request'),
    url(r'^new_expense/(?P<fund_request_pk>\d+)/$', views.NewExpenseView.as_view(), name='new_expense'),

    url(r'', views.TransactionListingView.as_view(), name='transaction_listing'),
]

