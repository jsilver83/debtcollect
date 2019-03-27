import django_tables2 as tables
from django.utils import formats
from django.utils.html import format_html

from django.utils.translation import ugettext_lazy as _

from projects.tables import BaseTableWithCommands
from .models import *


class DocumentMovementTable(BaseTableWithCommands):
    uploaded_document = tables.FileColumn(verify_exists=True, accessor='document.document')
    move_link = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name='')
    type = tables.TemplateColumn('{{ html }}', orderable=False, verbose_name=_('Movement Type'))

    class Meta:
        model = DocumentMovement
        fields = ['document.pk', 'document.project', 'document', 'uploaded_document', 'document.type', 'type',
                  'handing_party', 'receiving_party','movement_date', 'original_document', ]
        attrs = {'class': 'table table-striped table-bordered',
                 'id': 'datatable'}

    def render_type(self, value):
        if value == DocumentMovement.MovementTypes.INBOX:
            return format_html('<h4 class="label label-success"><i class="fa fa-download"></i> %s</h4>' % (value, ))
        elif value == DocumentMovement.MovementTypes.OUTBOX:
            return format_html('<h4 class="label label-danger"><i class="fa fa-upload"></i> %s</h4>' % (value, ))
        else:
            return format_html('<h4 class="label label-default">%s</h4>' % (value, ))

    def render_handing_party(self, value, **kwargs):
        record = kwargs.pop('record')
        return format_html('<button type="button" class="btn btn-default" data-toggle="tooltip" data-placement="left" '
                           'title="" data-original-title="%s">%s</button>'%(record.get_handing_party_role_display(),
                                                                            value))

    def render_receiving_party(self, value, **kwargs):
        record = kwargs.pop('record')
        return format_html('<button type="button" class="btn btn-default" data-toggle="tooltip" data-placement="left" '
                           'title="" data-original-title="%s">%s</button>'%(record.get_receiving_party_role_display(),
                                                                            value))
    def render_move_link(self, *args, **kwargs):
        record = kwargs.pop('record')
        if record.document.get_status() == Document.DocumentStatus.IN_ARCHIVE:
            commands = '<a href="%s" class="btn btn-danger btn-xs"><i class="fa fa-chevron-circle-up"></i> %s</a>' \
                       % (record.get_document_check_out_url(), _('Check Out'))
            return format_html(commands)
        elif record.document.get_status() in (Document.DocumentStatus.OUT_WITH_EMPLOYEE,
                                              Document.DocumentStatus.OUT_WITH_CLIENT):
            commands = '<a href="%s" class="btn btn-success btn-xs"><i class="fa fa-chevron-circle-down"></i> %s</a>' \
                       % (record.get_document_check_in_url(), _('Check In'))
            return format_html(commands)

    def render_audit_data(self, *args, **kwargs):
        try:
            record = kwargs.pop('record')
            commands = '<button type="button" ' \
                       'class="btn btn-secondary" ' \
                       'data-html="true"  ' \
                       'data-trigger="focus" ' \
                       'data-container="body" ' \
                       'data-toggle="popover" ' \
                       'data-placement="bottom" ' \
                       'data-content="<b>%s:<b> %s<br><b>%s:<b> %s<hr><b>%s:<b> %s<br><b>%s:<b> %s">' \
                       '<i class="fa fa-comment-o"></i> %s' \
                       '</button>' % (_('Uploaded By'),
                                      record.document.uploaded_by,
                                      _('Uploaded On'),
                                      formats.date_format(record.document.uploaded_on, 'DATETIME_FORMAT'),
                                      _('Updated By'),
                                      record.document.updated_by,
                                      _('Updated On'),
                                      formats.date_format(record.document.updated_on, 'DATETIME_FORMAT'),
                                      _('Audit'))
            return format_html(commands)
        except AttributeError:
            return ''

    def can_view(self):
        return False

    def can_move(self):
        return self.employee.user.groups.filter(name__in=['Admins', 'Archive']).exists() \
               or self.employee.user.is_superuser

    def __init__(self, *args, **kwargs):
        super(DocumentMovementTable, self).__init__(*args, **kwargs)
        if not self.can_move():
            self.exclude = self.exclude + ('move_link',)

