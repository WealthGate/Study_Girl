from django.urls import path
from . import views

urlpatterns = [
    path("student/", views.edit_student_profile, name="edit_student_profile"),
    path("tutor/", views.edit_tutor_profile, name="edit_tutor_profile"),
    path("tutor/<int:pk>/", views.tutor_profile_detail, name="tutor_profile_detail"),
]
