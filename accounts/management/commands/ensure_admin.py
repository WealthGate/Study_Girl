import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a superadmin from ADMIN_USERNAME, ADMIN_PASSWORD, and optional ADMIN_EMAIL."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME", "").strip()
        password = os.getenv("ADMIN_PASSWORD", "")
        email = os.getenv("ADMIN_EMAIL", "admin@studygirl.local").strip()

        if not username or not password:
            self.stdout.write("ADMIN_USERNAME or ADMIN_PASSWORD not set. Skipping superadmin setup.")
            return

        user, created = User.objects.get_or_create(username=username, defaults={"email": email})
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} superadmin account: {username}"))
