from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy, reverse
from django.utils.html import format_html
from django.views.generic import TemplateView, UpdateView, CreateView, FormView
from django.utils.translation import ugettext_lazy as _
from django_filters.views import FilterView
from django_tables2 import SingleTableView, MultiTableMixin, SingleTableMixin

from projects.views import BaseFormMixin
from .models import *
from .forms import *
from .tables import *
from .filters import *


class BaseArchiveMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admins', 'Archive']).exists() \
               or self.request.user.is_superuser


class DocumentMovementListingView(BaseArchiveMixin, SingleTableMixin, FilterView):
    model = DocumentMovement
    table_class = DocumentMovementTable
    table_pagination = {
        'per_page': 10
    }
    filterset_class = DocumentMovementFilter
    template_name = 'archive/document_movement_listing.html'

    def get_queryset(self):
        return DocumentMovement.objects.all()

    # def get_table(self):
    #     return self.table_class(self.get_queryset() , user=self.request.user)

    def get_table_kwargs(self):
        kwargs = super(DocumentMovementListingView, self).get_table_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DocumentMovementListingView, self).get_context_data(**kwargs)

        context['search_form'] = BaseCrispySearchForm

        return context


class NewDocumentView(BaseArchiveMixin, BaseFormMixin, CreateView):
    form_class = NewDocumentAndMovementForm
    template_name = 'archive/new_movement.html'
    success_url = reverse_lazy('archive_listing')
    success_message = _('Document was added and checked in successfully')


class NewMovementView(BaseArchiveMixin, BaseFormMixin, CreateView):
    form_class = NewMovementForADocumentForm
    template_name = 'archive/new_movement.html'
    success_url = reverse_lazy('archive_listing')
    success_message = _('Document was moved successfully')

    def get_form_kwargs(self):
        kwargs = super(NewMovementView, self).get_form_kwargs()
        kwargs['doc_pk'] = self.kwargs['doc_pk']
        kwargs['move_type'] = self.kwargs['move_type']
        return kwargs
