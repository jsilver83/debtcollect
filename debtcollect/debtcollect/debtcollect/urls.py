"""gentella URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import login, logout

urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^comments/', include('django_comments.urls')),

    url(r'^$', login, name='login'),
    url(r'^logout/$', logout, {'next_page': 'login'}, name='logout'),

    url(r'^insurance/', include('insurancedebt.urls')),

    url(r'^projects/', include('projects.urls')),

    url(r'^archive/', include('archive.urls')),

    url(r'^accounting/', include('accounting.urls')),

    url(r'^tellme/', include("tellme.urls")),

    url(r'^app/', include('app.urls')),
    url(r'^temp/', include('app.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
