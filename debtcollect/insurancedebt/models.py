from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money


class InsuranceContract(models.Model):
    insurance_company = models.ForeignKey('projects.Organization', null=True, blank=False, on_delete=models.SET_NULL,
                                          related_name='contracts', verbose_name=_('Insurance Company'), )
    employee_name = models.CharField(_('Employee Name'), max_length=200, null=True, blank=False,
                                     help_text=_('The insurance company employee who signed the contract from their '
                                                 'side'), )
    employee_contact_details = models.TextField(_('Employee Contact Details'), null=True, blank=True, )
    start_date = models.DateTimeField('Start Date', null=True, blank=False, )
    end_date = models.DateTimeField('End Date', null=True, blank=False, )
    contract_soft_copy = models.FileField(_('Contract Soft Copy'), null=True, blank=True, )
    details = models.TextField(_('Contract Details'), null=True, blank=True, )
    agreed_cut = models.DecimalField(_('Agreed Cut'), null=True, blank=False,
                                     decimal_places=settings.DECIMAL_PLACES, max_digits=settings.MAX_DIGITS, )
    signed_on = models.DateTimeField(_('Signed On'), auto_now=True)
    signed_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name=_('Signed By'),
                                  related_name="signed_contracts", )
    created_on = models.DateTimeField(_('Created On'), auto_now_add=True)
    created_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Created By'),
                                   related_name="created_contracts", )

    class Meta:
        verbose_name = _('Insurance Contract')
        verbose_name_plural = _('Insurance Contracts')
        ordering = ('-signed_on', 'created_on',)

    def __str__(self):
        return '%s %%%s' % (self.insurance_company, str(self.agreed_cut))


class InsuranceSubContract(models.Model):
    contract = models.ForeignKey('InsuranceContract', null=True, blank=False, on_delete=models.SET_NULL,
                                 related_name='sub_contracts', verbose_name=_('Contract'), )
    sub_contract_soft_copy = models.FileField(_('Sub-Contract Soft Copy'), null=True, blank=True, )
    employee_name = models.CharField(_('Employee Name'), max_length=200, null=True, blank=False,
                                     help_text=_('The insurance company employee who signed the contract from their '
                                                 'side'), )
    employee_contact_details = models.TextField(_('Employee Contact Details'), null=True, blank=True, )
    details = models.TextField(_('Sub-Contract Details'), null=True, blank=True, )
    agreed_cut = models.DecimalField(_('Agreed Cut'), null=True, blank=False,
                                     decimal_places=settings.DECIMAL_PLACES, max_digits=settings.MAX_DIGITS,
                                     help_text=_('This cut will take precedence over the parent-contract cut'), )
    signed_on = models.DateTimeField(_('Signed On'), auto_now=True)
    signed_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name=_('Signed By'),
                                  related_name="signed_subcontracts", )
    created_on = models.DateTimeField(_('Created On'), auto_now_add=True)
    created_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Created By'),
                                   related_name="created_subcontracts", )

    class Meta:
        verbose_name = _('Insurance Sub-Contract')
        verbose_name_plural = _('Insurance Sub-Contracts')
        ordering = ('-signed_on', 'created_on',)

    def __str__(self):
        if self.contract:
            return '%s %%%s' % (self.contract.insurance_company, str(self.agreed_cut),)
        else:
            return 'INVALID'


class InsuranceDebt(models.Model):
    class Statuses:
        NEW = 'NEW'
        IN_PROGRESS = 'IN_PROGRESS'
        IN_PROGRESS_INSTALLMENTS = 'IN_PROGRESS_INSTALLMENTS'
        FINISHED = 'FINISHED'
        DELAYED = 'DELAYED'
        CANCELLED = 'CANCELLED'
        CANCELLED_WRONG_PERSON = 'CANCELLED_WRONG_PERSON'
        CANCELLED_WONT_PAY = 'CANCELLED_WONT_PAY'

        @classmethod
        def choices(cls):
            return (
                (cls.NEW, _('New')),
                (cls.IN_PROGRESS, _('In Progress')),
                (cls.IN_PROGRESS_INSTALLMENTS, _('In Progress (Installments)')),
                (cls.FINISHED, _('Finished')),
                (cls.DELAYED, _('Delayed')),
                (cls.CANCELLED_WRONG_PERSON, _('Cancelled (Wrong Person)')),
                (cls.CANCELLED_WONT_PAY, _('Cancelled (Client will NOT pay)')),
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

    sub_contract = models.ForeignKey('InsuranceSubContract', null=True, blank=False, on_delete=models.SET_NULL,
                                     related_name='insurance_debts', verbose_name=_('Sub-Contract'))
    legacy_system_no = models.SmallIntegerField(_('Legacy System No'), null=True, blank=True)
    ref_no = models.CharField(_('Insurance Company Reference No'), max_length=200, null=True, blank=True)
    type = models.CharField(_('Type'), max_length=100, null=True, blank=False,
                            choices=Types.choices(), default=Types.TRAFFIC)
    type_justification = models.TextField(_('Type Justification'), blank=True, null=True)
    status = models.CharField(_('Status'), max_length=50, null=True, blank=False,
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
    insurer_full_name = models.CharField(_('Insurer Full Name'), max_length=200, null=True, blank=True, )
    driver_mobile = models.CharField(_('Driver Mobile'), max_length=20, null=True, blank=False,
                                     help_text=_('format: 05XXXXXXXX'),
                                     validators=[
                                         RegexValidator(
                                             '^(05|٠٥)\d{8}$',
                                             message=_('You have entered an invalid mobile number')
                                         ),
                                     ], )
    vehicle_plate_no = models.CharField(_('Vehicle Plate NO'), null=True, blank=True, max_length=20)
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

    class Meta:
        verbose_name = _('Insurance Debt')
        verbose_name_plural = _('Insurance Debts')
        ordering = ('-updated_on', 'created_on',)

    def debt_no(self):
        return self.legacy_system_no if self.legacy_system_no else self.pk

    def __str__(self):
        return '%s %s %s' % (self.driver_full_name, str(self.debt), self.type)

    def get_absolute_url(self):
        return reverse_lazy('update_insurance_debt', args=(self.pk,))

    def get_update_url(self):
        return self.get_absolute_url()

    def get_remaining_unpaid_debt(self):
        received_payments = self.scheduled_payments.filter(received_on__isnull=False)
        if received_payments:
            return self.debt - \
                   Money(received_payments.aggregate(Sum('amount')).get('amount__sum'), self.debt.currency)
        else:
            return self.debt

    def get_remaining_unscheduled_debt(self):
        scheduled_payments = self.scheduled_payments.all()
        if scheduled_payments:
            return self.debt - \
                   Money(scheduled_payments.aggregate(Sum('amount')).get('amount__sum'), self.debt.currency)
        else:
            return self.debt

    def can_change_scheduled_payment(self, payment, new_amount):
        scheduled_payments = self.scheduled_payments.exclude(pk=payment.pk)
        if scheduled_payments:
            return (new_amount + Money(scheduled_payments.aggregate(Sum('amount')).get('amount__sum'), self.debt.currency)) <= self.debt
        else:
            return True


InsuranceDebt._meta.get_field('id').verbose_name = _('Debt No')


class InsuranceDocument(models.Model):
    insurance_debt = models.ForeignKey('InsuranceDebt', related_name='documents',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name=_('Insurance Debt'))
    # TODO: apply restriction of file types and size
    document = models.FileField(_('Document Upload'), null=True, blank=False)
    title = models.CharField(_('Title'), max_length=100, blank=False, null=True)
    description = models.TextField(_('Description'), blank=True, null=True)
    type = models.CharField(_('Type'), max_length=100, null=True, blank=False)
    created_on = models.DateTimeField(_('Uploaded On'), auto_now_add=True)
    created_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=False,
                                   related_name='uploaded_insurance_debt_documents',
                                   verbose_name=_('Uploaded By'))
    updated_on = models.DateTimeField(_('Updated On'), auto_now=True)
    updated_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=False,
                                   related_name='updated_insurance_debt_documents',
                                   verbose_name=_('Updated By'))

    class Meta:
        verbose_name = _('Insurance Document')
        verbose_name_plural = _('Insurance Documents')
        ordering = ('created_on', 'type',)

    def __str__(self):
        return '%s (%s) %s' % (self.title, self.type, str(self.insurance_debt))


class ScheduledPayment(models.Model):
    class PaymentMethods:
        TRANSFER_TO_GULF_DEBT = 'TRANSFER_TO_GULF_DEBT'
        TRANSFER_TO_COMPANY = 'TRANSFER_TO_COMPANY'

        @classmethod
        def choices(cls):
            return (
                (cls.TRANSFER_TO_GULF_DEBT, _('Bank transfer to Gulf Debt account')),
                (cls.TRANSFER_TO_COMPANY, _('Bank transfer to the insurance company account')),
            )

    insurance_debt = models.ForeignKey('InsuranceDebt', related_name='scheduled_payments',
                                       on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name=_('Insurance Debt'))
    amount = MoneyField(_('Amount'), null=True, blank=False,
                        default=0, default_currency='SAR',
                        decimal_places=settings.DECIMAL_PLACES, max_digits=settings.MAX_DIGITS, )
    scheduled_date = models.DateField(_('Scheduled Date'), null=True, blank=False, )

    created_on = models.DateTimeField(_('Scheduled On'), auto_now_add=True)
    created_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Scheduled By'),
                                   related_name='scheduled_payments', )

    received_on = models.DateTimeField(_('Received On'), null=True, blank=True, )
    received_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name=_('Received By'),
                                    related_name='received_payments', )
    payment_method = models.CharField(_('Payment Methods'), null=True, blank=True, max_length=100,
                                      choices=PaymentMethods.choices())
    # TODO: apply restriction of file types and size
    proof_of_payment = models.FileField(_('Proof Of Payment'), null=True, blank=True)

    updated_on = models.DateTimeField(_('Updated On'), auto_now=True)
    updated_by = models.ForeignKey('projects.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Updated By'),
                                   related_name='updated_payments', )

    class Meta:
        verbose_name = _('Scheduled Payment')
        verbose_name_plural = _('Scheduled Payments')
        ordering = ('scheduled_date', 'received_on')

    def __str__(self):
        return '%s (%s) %s' % (self.amount, self.scheduled_date, str(self.insurance_debt))

    def get_absolute_url(self):
        return reverse_lazy('update_scheduled_payment', args=(self.pk,))

    def get_receive_url(self):
        return reverse_lazy('receive_scheduled_payment', args=(self.pk,))

    def get_update_url(self):
        return self.get_absolute_url()

    def is_late(self):
        return self.received_on is None and self.scheduled_date < timezone.now().date()
