from django.urls import path

from . import views

urlpatterns = [
    path('', views.InsuranceDebtListing.as_view(), name='insurance_debt_listing'),
    path('new-insurance-debt/', views.NewInsuranceDebtView.as_view(), name='new_insurance_debt'),
    path('insurance-debt/<int:pk>/', views.UpdateInsuranceDebtView.as_view(), name='update_insurance_debt'),
    path('new-insurance-document/<int:insurance_debt_pk>/', views.NewInsuranceDocumentView.as_view(),
         name='new_insurance_document'),
    path('new-scheduled-payment/<int:insurance_debt_pk>/', views.NewScheduledPaymentView.as_view(),
         name='new_scheduled_payment'),
    path('scheduled-payment/<int:pk>/', views.UpdateScheduledPaymentView.as_view(),
         name='update_scheduled_payment'),
    path('scheduled-payment/<int:pk>/receive/', views.ReceiveScheduledPaymentView.as_view(),
         name='receive_scheduled_payment'),
    path('comment-success/', views.CommentPostedSuccessfully.as_view(), name='comment_success'),
]
