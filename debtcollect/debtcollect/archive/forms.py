from dal import autocomplete

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_addanother.widgets import AddAnotherWidgetWrapper

from projects.base_forms import *
from .models import *


class NewDocumentAndMovementForm(BaseUpdatedByForm, forms.ModelForm):
    document_upload = forms.FileField(label=_('Document Upload'), required=True)
    project = forms.ModelChoiceField(label=_('Project'), required=True, queryset=Project.objects.all(),
                                     widget=autocomplete.ModelSelect2(url='project-autocomplete'))
    title_ar = forms.CharField(label=_('Title'), max_length=100, required=True,
                               help_text=_('Document Title'))
    title_en = forms.CharField(label=_('Title (English)'), max_length=100, required=False)
    description_ar = forms.CharField(label=_('Description'), required=True, help_text=_('Document Description'))
    description_en = forms.CharField(label=_('Description (English)'), required=False)
    type = forms.ChoiceField(label=_('Type'), required=True,
                             choices=Lookup.get_lookup_choices(Lookup.LookupTypes.DOCUMENT_TYPE))

    class Meta:
        model = DocumentMovement
        fields = ['project', 'document_upload', 'title_ar', 'title_en', 'description_ar', 'description_en', 'type',
                  'description', 'original_document', 'handing_party', 'handing_party_role', 'movement_date']
        labels = {
            'description': _('Movement Description'),
            'type': _('Document Type'),
        }

        help_texts = {
            'description': _('Describe the movement of the document not the document itself'),
        }

        widgets = {
            'handing_party': autocomplete.ModelSelect2(url='person-autocomplete', ),
        }

    def __init__(self, *args, **kwargs):
        super(NewDocumentAndMovementForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget = \
            forms.Select(choices=Lookup.get_lookup_choices(Lookup.LookupTypes.DOCUMENT_TYPE))
        self.fields['project'].queryset = Project.objects.all()

    def save(self, commit=True):
        instance = super(NewDocumentAndMovementForm, self).save(commit=False)
        document = Document()
        document.document = self.cleaned_data['document_upload']
        document.title_ar = self.cleaned_data['title_ar']
        document.title_en = self.cleaned_data['title_en']
        document.description_ar = self.cleaned_data['description_ar']
        document.description_en = self.cleaned_data['description_en']
        document.type = self.cleaned_data['type']
        document.project = self.cleaned_data['project']
        document.uploaded_by = self.employee
        document.uploaded_on = timezone.now
        document.updated_by = self.employee
        document.updated_on = timezone.now
        document.save()

        instance.document = document
        instance.receiving_party = self.employee
        instance.receiving_party_role = DocumentMovement.ArchiveRoles.ARCHIVE
        # instance.created_by = self.employee
        # instance.created_on = timezone.now

        if commit:
            instance.save()

        return instance


class NewMovementForADocumentForm(BaseUpdatedByForm, forms.ModelForm):

    class Meta:
        model = DocumentMovement
        fields = ['description', 'original_document', 'handing_party', 'handing_party_role',
                  'receiving_party', 'receiving_party_role', 'movement_date']
        labels = {
            'description': _('Movement Description'),
        }

        help_texts = {
            'description': _('Describe the movement of the document not the document itself'),
        }

    def __init__(self, *args, **kwargs):
        self.document = Document.objects.get(pk=kwargs.pop('doc_pk'))
        self.move_type = kwargs.pop('move_type')
        super(NewMovementForADocumentForm, self).__init__(*args, **kwargs)
        if self.move_type.lower() == 'inbox':
            del self.fields['receiving_party']
            del self.fields['receiving_party_role']
        elif self.move_type.lower() == 'outbox':
            del self.fields['handing_party']
            del self.fields['handing_party_role']

    def save(self, commit=True):
        instance = super(NewMovementForADocumentForm, self).save(commit=False)
        if self.move_type.lower() == 'inbox':
            instance.receiving_party = self.employee
            instance.receiving_party_role = DocumentMovement.ArchiveRoles.ARCHIVE
        elif self.move_type.lower() == 'outbox':
            instance.handing_party = self.employee
            instance.handing_party_role = DocumentMovement.ArchiveRoles.ARCHIVE
        instance.document = self.document

        if commit:
            instance.save()

        return instance
