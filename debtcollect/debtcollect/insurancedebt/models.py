from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField


class InsuranceDebt(models.Model):
    class Statuses:
        NEW = 'NEW'
        IN_PROGRESS = 'IN_PROGRESS'
        FINISHED = 'FINISHED'
        DELAYED = 'DELAYED'
        CANCELLED = 'CANCELLED'

        @classmethod
        def choices(cls):
            return (
                (cls.NEW, _('New')),
                (cls.IN_PROGRESS, _('In Progress')),
                (cls.FINISHED, _('Finished')),
                (cls.DELAYED, _('Delayed')),
                (cls.CANCELLED, _('Cancelled')),
            )

    class Types:
        TRAFFIC = 'TRAFFIC'
        RETURNED = 'RETURNED'

        @classmethod
        def choices(cls):
            return (
                (cls.TRAFFIC, _('Traffic')),
                (cls.RETURNED, _('Returned')),
            )

    class Meta:
        verbose_name = _('Insurance Debt')
        verbose_name_plural = _('Insurance Debts')
        ordering = ('-updated_on', 'created_on',)

    type = models.CharField(_('Type'), max_length=100, null=True, blank=False,
                            choices=Types.choices(), default=Types.TRAFFIC)
    type_justification = models.TextField(_('Type Justification'), blank=True, null=True)
    status = models.CharField(_('Status'), max_length=20, null=True, blank=False,
                              choices=Statuses.choices(), default=Statuses.NEW)
    status_comments = models.CharField(_('Status Comments'), max_length=500, null=True, blank=True)
    debt = MoneyField(_('Debt Amount'), null=True, blank=False,
                      default=0, default_currency='SAR',
                      decimal_places=settings.DECIMAL_PLACES, max_digits=settings.MAX_DIGITS, )
    assignee = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=False,
                                 related_name='assigned_insurance_debts',
                                 verbose_name=_('Assignee'))
    driver_government_id = models.CharField(_('Driver Government ID'), max_length=20, null=True, blank=False,
                                            validators=[
                                                RegexValidator(
                                                    '^\d{9,11}$',
                                                    message=_("You have entered an invalid Government ID")
                                                ), ])
    driver_full_name = models.CharField(_('Driver Full Name'), max_length=200, null=True, blank=True, )
    insurer_full_name = models.CharField(_('Driver Full Name'), max_length=200, null=True, blank=True, )
    driver_mobile = models.CharField(_('Driver Mobile'), max_length=20, null=True, blank=False,
                                     help_text=_('format: 05XXXXXXXX'),
                                     validators=[
                                         RegexValidator(
                                             '^(05|٠٥)\d{8}$',
                                             message=_('You have entered an invalid mobile number')
                                         ),
                                     ], )
    accident_location = models.CharField(_('Accident Location'), max_length=200, null=True, blank=True, )
    accident_date = models.DateTimeField(_('Accident Date'), null=True, blank=True, )
    client_notes = models.TextField(_('Client Notes'), blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True, null=True)

    created_on = models.DateTimeField(_('Created On'), auto_now_add=True)
    created_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Created By'),
                                   related_name="created_debts", )
    updated_on = models.DateTimeField(_('Updated On'), auto_now=True)
    updated_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Updated By'),
                                   related_name="updated_debts", )

    def get_absolute_url(self):
        return reverse_lazy('update_insurance_debt', args=(self.pk,))

    def get_update_url(self):
        return self.get_absolute_url()


class InsuranceDocument(models.Model):
    document = models.FileField(_('Document Upload'), null=True, blank=False)
    insurance_debt = models.ForeignKey('InsuranceDebt', related_name='documents',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name=_('Insurance Debt'))
    title = models.CharField(_('Title'), max_length=100, blank=False, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    type = models.CharField(_('Type'), max_length=100, null=True, blank=False)
    uploaded_on = models.DateTimeField(_('Uploaded On'), auto_now_add=True)
    uploaded_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=False,
                                    related_name='uploaded_insurance_debt_documents',
                                    verbose_name=_('Uploaded By'))
    updated_on = models.DateTimeField(_('Updated On'), auto_now=True)
    updated_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=False,
                                   related_name='updated_insurance_debt_documents',
                                   verbose_name=_('Updated By'))

    class Meta:
        verbose_name = _('Insurance Document')
        verbose_name_plural = _('Insurance Documents')

    def __str__(self):
        return self.title
