from dal import autocomplete
from django.db.models import Q

from .models import *


class ProjectAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Project.objects.none()

        qs = Project.objects.all()

        if self.q:
            lang = translation.get_language()
            if lang == "ar":
                qs = qs.filter(title_ar__icontains=self.q)
            else:
                qs = qs.filter(title_en__icontains=self.q)

        return qs


class ClientAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Client.objects.none()

        qs = Client.objects.all()

        if self.q:
            lang = translation.get_language()
            if lang == "ar":
                qs = qs.filter(Q(name_ar__icontains=self.q) | Q(organization__name_ar__icontains=self.q))
            else:
                qs = qs.filter(Q(name_en__icontains=self.q) | Q(organization__name_en__icontains=self.q))

        return qs


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Person.objects.none()

        qs = Person.objects.all()

        if self.q:
            lang = translation.get_language()
            if lang == "ar":
                qs = qs.filter(name_ar__icontains=self.q)
            else:
                qs = qs.filter(name_en__icontains=self.q)

        return qs


class OrganizationAutocomplete(autocomplete.Select2QuerySetView):
    org_class = Organization

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.org_class.objects.none()

        qs = self.org_class.objects.all()

        if self.q:
            lang = translation.get_language()
            if lang == "ar":
                qs = qs.filter(name_ar__icontains=self.q)
            else:
                qs = qs.filter(name_en__icontains=self.q)

        return qs


class CourtAutocomplete(OrganizationAutocomplete):
    org_class = Court
