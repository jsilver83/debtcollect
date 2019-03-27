from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.InsuranceDebtListing.as_view(), name='insurance_debt_listing'),
    url(r'^new-insurance-debt/$', views.NewInsuranceDebtView.as_view(), name='new_insurance_debt'),
    url(r'^insurance-debt/(?P<pk>\d+)/$', views.UpdateInsuranceDebtView.as_view(), name='update_insurance_debt'),
    url(r'^new-insurance-document/(?P<insurance_debt_pk>\d+)/$', views.NewInsuranceDocumentView.as_view(),
        name='new_insurance_document'),
    url(r'^new-scheduled-payment/(?P<insurance_debt_pk>\d+)/$', views.NewScheduledPaymentView.as_view(),
        name='new_scheduled_payment'),
    url(r'^scheduled-payment/(?P<pk>\d+)/$', views.UpdateScheduledPaymentView.as_view(),
        name='update_scheduled_payment'),
    url(r'^scheduled-payment/(?P<pk>\d+)/receive/$', views.ReceiveScheduledPaymentView.as_view(),
        name='receive_scheduled_payment'),
    url(r'^comment-success/$', views.CommentPostedSuccessfully.as_view(), name='comment_success'),
]
