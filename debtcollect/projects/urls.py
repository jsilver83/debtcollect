from django.conf.urls import url

from . import popup_views
from . import auto_complete_views
from . import views
urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),

    url(r'^listing/(?P<p_type>\w+)/$', views.ProjectListing.as_view(), name='case_listing'),
    url(r'^new-project/(?P<p_type>\w+)/$', views.NewProjectView.as_view(), name='new_project'),
    url(r'^update_project/(?P<pk>\d+)/$', views.UpdateProjectView.as_view(), name='update_project'),
    url(r'^project/(?P<pk>\d+)/new-update/$', views.NewUpdateView.as_view(), name='new_update'),
    url(r'^project/(?P<pk>\d+)/request_fund/$', views.NewFundRequestView.as_view(), name='new_request_fund'),
    url(r'^project/(?P<pk>\d+)/reminder/$', views.NewReminderView.as_view(), name='new_project_reminder'),

    url(r'^clients/$', views.ClientListingView.as_view(), name='clients'),
    url(r'^new-client/$', views.NewClientView.as_view(), name='new_client'),
    url(r'^new-client-popup/$', popup_views.NewClientPopupView.as_view(), name='new-client-popup'),
    url(r'^client/(?P<pk>\d+)/$', views.ClientView.as_view(), name='update_client'),

    url(r'^organizations/$', views.OrganizationListingView.as_view(), name='organizations'),
    url(r'^courts/$', views.CourtsListing.as_view(), name='courts'),
    url(r'^new-organization/$', views.NewOrganizationView.as_view(), name='new_organization'),
    url(r'^new-organization-popup/$', popup_views.NewOrganizationPopupView.as_view(), name='new_organization_popup'),
    url(r'^new-court/$', views.NewCourtView.as_view(), name='new_court'),
    url(r'^new-court-popup/$', popup_views.NewCourtPopupView.as_view(), name='new-court-popup'),
    url(r'^organization/(?P<pk>\d+)/$', views.OrganizationView.as_view(), name='update_organization'),
    # url(r'^organization/(?P<pk>\d+)/$', views.OrganizationView.as_view(), name='update_organization'),

    url(r'^employees/$', views.EmployeesListingView.as_view(), name='employees'),
    url(r'^new-employee/$', views.NewEmployeeView.as_view(), name='new_employee'),
    url(r'^employee/(?P<pk>\d+)/$', views.EmployeeView.as_view(), name='update_employee'),


    url(r'^users/$', views.UsersListingView.as_view(), name='users'),
    url(r'^user/(?P<pk>\d+)/$', views.UpdateUserView.as_view(), name='update-user'),
    url(r'^new-user/$', views.NewUserView.as_view(), name='new-user'),
    url(r'^new-user-popup/$', popup_views.NewUserView.as_view(), name='new-user-popup'),

    url(r'^lookups/$', views.LookupsListingView.as_view(), name='lookups'),
    url(r'^new-lookup/$', views.NewLookupView.as_view(), name='new-lookup'),
    url(r'^lookup/(?P<pk>\d+)/$', views.UpdateLookupView.as_view(), name='update-lookup'),

    url(r'^project-autocomplete/$', auto_complete_views.ProjectAutocomplete.as_view(), name='project-autocomplete', ),
    url(r'^client-autocomplete/$', auto_complete_views.ClientAutocomplete.as_view(), name='client-autocomplete', ),
    url(r'^person-autocomplete/$', auto_complete_views.PersonAutocomplete.as_view(), name='person-autocomplete', ),
    url(r'^org-autocomplete/$', auto_complete_views.OrganizationAutocomplete.as_view(), name='org-autocomplete', ),
    url(r'^court-autocomplete/$', auto_complete_views.CourtAutocomplete.as_view(), name='court-autocomplete', ),
]


