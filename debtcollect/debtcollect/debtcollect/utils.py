from django.utils.translation import ugettext_lazy as _


class UserGroups:
    ADMINS_GROUP = 'Admins'
    LAWYERS_GROUP = 'Lawyers'
    ARCHIVE_GROUP = 'Archive'
    ACCOUNTING_GROUP = 'Accounting'
    DEBT_COLLECTORS_GROUP = 'Debt Collectors'
    DEBT_COLLECTING_SUPERVISORS_GROUP = 'Debt Collect Supervisors'
    DEBT_COLLECTING_ADMINS_GROUP = 'Debt Collect Admins'


# Note: dummy class to translate strings in django-filters
class FilterTranslation:
    contains = _('contains')
