from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from debtcollect.utils import UserGroups


class DebtCollectorMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=[UserGroups.DEBT_COLLECTORS_GROUP,
                                                         UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP,
                                                         UserGroups.DEBT_COLLECTING_ADMINS_GROUP]).exists() \
               or self.request.user.is_superuser


class DebtCollectSupervisorAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=[UserGroups.DEBT_COLLECTING_SUPERVISORS_GROUP,
                                                         UserGroups.DEBT_COLLECTING_ADMINS_GROUP]).exists() \
               or self.request.user.is_superuser


class DebtCollectingAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name=UserGroups.DEBT_COLLECTING_ADMINS_GROUP).exists() \
               or self.request.user.is_superuser