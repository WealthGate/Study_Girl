from django.urls import path
from . import views

urlpatterns = [
    path("", views.tutor_list, name="tutor_list"),
    path("<int:tutor_id>/request/", views.request_session, name="request_session"),
    path("requests/", views.session_requests, name="session_requests"),
    path("requests/<int:request_id>/<str:action>/", views.respond_to_request, name="respond_to_request"),
    path("feedback/<int:session_id>/", views.feedback, name="feedback"),
    path("study-sisters/", views.study_sisters, name="study_sisters"),
    path("study-sisters/<int:connection_id>/block/", views.block_connection, name="block_connection"),
]
