from django.urls import path
from . import views

urlpatterns = [
    path("", views.resource_library, name="resource_library"),
    path("upload/", views.upload_resource, name="upload_resource"),
]
