from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from dashboard import views as dashboard_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard_views.home, name="home"),
    path("about/", dashboard_views.about, name="about"),
    path("dashboard/", dashboard_views.dashboard, name="dashboard"),
    path("staff-dashboard/", dashboard_views.staff_dashboard, name="staff_dashboard"),
    path("staff-dashboard/applications/<int:application_id>/<str:action>/", dashboard_views.review_tutor_application, name="review_tutor_application"),
    path("accounts/", include("accounts.urls")),
    path("profiles/", include("profiles.urls")),
    path("tutors/", include("tutoring.urls")),
    path("sessions/", include("sessions.urls")),
    path("solo-study/", include("resources.urls")),
    path("safety/", include("moderation.urls")),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), name="password_reset"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
