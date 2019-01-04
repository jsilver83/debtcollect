from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.DocumentMovementListingView.as_view(), name='archive_listing'),
    url(r'^new_movement/$', views.NewDocumentView.as_view(), name='new_movement'),
    url(r'^new_movement/(?P<doc_pk>\d+)/(?P<move_type>\w+)/$', views.NewMovementView.as_view(), name='new_document_movement'),
    # url(r'^project/(?P<p_type>\w+)/$', views.NewProjectView.as_view(), name='new_project'),
    # url(r'^update_project/(?P<pk>\d+)/$', views.UpdateProjectView.as_view(), name='update_project'),
]

