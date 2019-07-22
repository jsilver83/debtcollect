from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from projects.models import Employee
from debtcollect.utils import UserGroups


class DebtCollectMixin:
    employee = None

    def get(self, request, *args, **kwargs):
        self.employee, created = Employee.objects.get_or_create(user=self.request.user)
        if created:
            self.employee.name_ar = '%s %s' % (self.request.user.first_name, self.request.user.last_name)
            self.employee.name_en = '%s %s' % (self.request.user.first_name, self.request.user.last_name)
            self.employee.save()

        return super().get(request, *args, **kwargs)


class DebtCollectorMixin(DebtCollectMixin, LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=[UserGroups.DEBT_COLLECTORS_GROUP,
                                                         UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP,
                                                         UserGroups.DEBT_COLLECTING_ADMINS_GROUP]).exists() \
               or self.request.user.is_superuser


class DebtCollectSupervisorAdminMixin(DebtCollectMixin, LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=[UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP,
                                                         UserGroups.DEBT_COLLECTING_ADMINS_GROUP]).exists() \
               or self.request.user.is_superuser


class DebtCollectingAdminMixin(DebtCollectMixin, LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name=UserGroups.DEBT_COLLECTING_ADMINS_GROUP).exists() \
               or self.request.user.is_superuser