from django.db import models
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from projects.models import *


class Document(models.Model):
    class DocumentStatus:
        IN_ARCHIVE = _('In Archive')
        OUT_WITH_EMPLOYEE = _('Out With An Employee')
        OUT_WITH_CLIENT = _('Out With A Client')

    document = models.FileField(_('Document Upload'), null=True, blank=False)
    project = models.ForeignKey('projects.Project', related_name='documents',
                                on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Project'))
    title_ar = models.CharField(_('Title'), max_length=100, blank=False, null=True)
    title_en = models.CharField(_('Title (English)'), max_length=100, blank=True, null=True)
    description_ar = models.TextField(_('Description'), blank=False, null=True)
    description_en = models.TextField(_('Description (English)'), blank=True, null=True)
    type = models.CharField(_('Type'), max_length=100, null=True, blank=False)
    uploaded_on = models.DateTimeField(_('Uploaded On'), auto_now_add=True)
    uploaded_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=False,
                                    related_name='uploaded_documents',
                                    verbose_name=_('Uploaded By'))
    updated_on = models.DateTimeField(_('Updated On'), auto_now=True)
    updated_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=False,
                                   # related_name='',
                                   verbose_name=_('Updated By'))

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    @property
    def title(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.title_ar
        else:
            return self.title_en

    @property
    def description(self):
        lang = translation.get_language()
        if lang == "ar":
            return self.description_ar
        else:
            return self.description_en

    title.fget.short_description = _('Title')
    title.fget.short_description = _('Description')

    def __str__(self):
        return self.title

    def get_status(self):
        receiving_party_role = getattr(self.movements.first(),
                                       'receiving_party_role',
                                       DocumentMovement.ArchiveRoles.ARCHIVE)
        if receiving_party_role == DocumentMovement.ArchiveRoles.ARCHIVE:
            return Document.DocumentStatus.IN_ARCHIVE
        elif receiving_party_role == DocumentMovement.ArchiveRoles.CLIENT:
            return Document.DocumentStatus.OUT_WITH_CLIENT
        elif receiving_party_role == DocumentMovement.ArchiveRoles.EMPLOYEE:
            return Document.DocumentStatus.OUT_WITH_EMPLOYEE


class DocumentMovement(models.Model):
    class ArchiveRoles:
        CLIENT = 'CLIENT'
        ARCHIVE = 'ARCHIVE'
        EMPLOYEE = 'EMPLOYEE'

        @classmethod
        def choices(cls):
            return (
                (cls.CLIENT, _('Client')),
                (cls.ARCHIVE, _('Archive')),
                (cls.EMPLOYEE, _('Employee')),
            )

    class MovementTypes:
        INBOX = _('Inbox')
        OUTBOX = _('Outbox')
        NA = _('N/A')

        @classmethod
        def choices(cls):
            return (
                (cls.INBOX, cls.INBOX),
                (cls.OUTBOX, cls.OUTBOX),
                (cls.NA, cls.NA),
            )

    document = models.ForeignKey('Document', related_name='movements',
                                 on_delete=models.CASCADE, null=False, blank=False, verbose_name=_('Document'))
    description = models.CharField(_('Description'), null=True, blank=False, max_length=255)
    original_document = models.BooleanField(_('Original Document?'), default=False,
                                            help_text=_('Are you actually moving the original document or just '
                                                        'a copy?'))
    handing_party = models.ForeignKey('projects.Person', related_name='handed_documents',
                                      verbose_name=_('Handing Party'),
                                      on_delete=models.SET_NULL, null=True, blank=False)
    handing_party_role = models.CharField(_('Handing Party Role'), max_length=20, null=True, blank=True,
                                          choices=ArchiveRoles.choices())
    receiving_party = models.ForeignKey('projects.Person', related_name='received_documents',
                                        verbose_name=_('Receiving Party'),
                                        on_delete=models.SET_NULL, null=True, blank=False)
    receiving_party_role = models.CharField(_('Receiving Party Role'), max_length=20, null=True, blank=False,
                                            choices=ArchiveRoles.choices())
    movement_date = models.DateTimeField(_('Movement Date'), null=True, blank=False)

    class Meta:
        verbose_name = _('Document Movement')
        verbose_name_plural = _('Document Movements')
        ordering = ['-movement_date']

    def type(self):
        if self.handing_party_role == DocumentMovement.ArchiveRoles.ARCHIVE and self.receiving_party_role in (
                DocumentMovement.ArchiveRoles.EMPLOYEE, DocumentMovement.ArchiveRoles.CLIENT):
            return DocumentMovement.MovementTypes.OUTBOX
        elif self.receiving_party_role == DocumentMovement.ArchiveRoles.ARCHIVE and self.handing_party_role in (
                DocumentMovement.ArchiveRoles.EMPLOYEE,
                DocumentMovement.ArchiveRoles.CLIENT):
            return DocumentMovement.MovementTypes.INBOX
        else:
            return DocumentMovement.MovementTypes.NA

    def get_absolute_url(self):
        return reverse_lazy('archive_listing')

    def get_document_check_in_url(self):
        return reverse_lazy('new_document_movement', args=(self.document.pk, 'inbox'))

    def get_document_check_out_url(self):
        return reverse_lazy('new_document_movement', args=(self.document.pk, 'outbox'))

    def get_update_url(self):
        return self.get_absolute_url()
