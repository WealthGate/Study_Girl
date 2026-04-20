from django.urls import path
from . import views

urlpatterns = [
    path("<int:session_id>/room/", views.study_room, name="study_room"),
    path("<int:session_id>/leave/", views.leave_session, name="leave_session"),
]
