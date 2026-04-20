from django.urls import path
from . import views

urlpatterns = [
    path("guidelines/", views.guidelines, name="guidelines"),
    path("report/", views.report_user, name="report_user"),
]
