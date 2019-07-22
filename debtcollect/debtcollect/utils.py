import requests
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


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


# safe parsing of integers
def try_parse_int(str_to_int):
    try:
        return int(str_to_int)
    except:
        return


# convert strings with non standard numerals to standard numerals while preserving initial zeroes
# like ۰۰۰۱ or ٠٠٠١ or ໐໐໐໑ will be converted to 0001
def parse_non_standard_numerals(str_numerals):
    # print(str_numerals)
    if str_numerals:
        new_string = ''
        for single_char in str_numerals:
            new_string += str(try_parse_int(single_char))

        return new_string
    else:
        return ''


def get_model_object_details(model_obj, excluded_fields):
    details = []
    for x in model_obj._meta.get_fields():
        if x.name not in excluded_fields and hasattr(x, 'verbose_name') and getattr(model_obj, x.name, ''):
            if getattr(model_obj, 'get_' + x.name + '_display', ''):
                details.append({'field': x.verbose_name, 'value': getattr(model_obj, 'get_' + x.name + '_display', '')})
            else:
                details.append({'field': x.verbose_name, 'value': getattr(model_obj, x.name, '')})
    return details


class SMS(object):
    sms_messages = {
        'new_debt': _('You are obliged to settle an insurance debt (No: %(debt_id)'
                      'for more details visit: http://sys.fhol.com.sa'),
        'new_notifications': _('You have new notifications for insurance debt (No: %(debt_id)'
                               'for more details visit: http://sys.fhol.com.sa'),
    }

    # using UNIFONIC gateway to send SMS
    @staticmethod
    def send_sms(mobile, body):
        if settings.DISABLE_SMS:
            return None

        try:
            r = requests.post('http://api.unifonic.com/rest/Messages/Send',
                              data={'AppSid': settings.UNIFONIC_APP_SID,
                                    'Recipient': mobile,
                                    'Body': body,
                                    'SenderID': 'KFUPMQabool'})  # It was KFUPM-ADM
            return r
        except:  # usually TimeoutError but made it general so it will never raise an exception
            pass

    @staticmethod
    def send_sms_registration_success(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['registration_success']))
