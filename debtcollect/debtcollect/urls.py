from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path, reverse_lazy

from insurancedebt import views
from insurancedebt.forms import MyAuthenticationForm, MyPasswordChangeForm

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('comments/', include('django_comments.urls')),

    path('debts/', views.InsuranceDebtListing.as_view(), name='home'),
    path('employee-login/', LoginView.as_view(form_class=MyAuthenticationForm), name='login'),
    path('employee-logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path(
        'change-password/',
        PasswordChangeView.as_view(template_name='insurancedebt/form.html',
                                   form_class=MyPasswordChangeForm,
                                   success_url=reverse_lazy('password_change_done')),
        name='change_password',
    ),
    path(
        'change-password-done/',
        PasswordChangeDoneView.as_view(template_name='insurancedebt/password_change_done.html'),
        name='password_change_done',
    ),

    path('', views.ClientLoginView.as_view(), name='home'),
    path('login/', views.ClientLoginView.as_view(), name='client_login'),
    path('logout/', views.ClientLogout.as_view(), name='client_logout'),
    path('client-area/', views.ClientAreaView.as_view(), name='client_area'),

    path('insurance/', include('insurancedebt.urls')),

    path('projects/', include('projects.urls')),

    path('archive/', include('archive.urls')),

    path('accounting/', include('accounting.urls')),

    path('tellme/', include("tellme.urls")),

    path('app/', include('app.urls')),
    path('temp/', include('app.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
