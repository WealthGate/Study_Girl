from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from profiles.models import Subject
from .forms import SoloStudyResourceForm
from .models import SoloStudyResource


@login_required
def resource_library(request):
    resources = SoloStudyResource.objects.filter(is_approved=True).select_related("subject")
    subjects = Subject.objects.all()
    subject_id = request.GET.get("subject")
    if subject_id:
        resources = resources.filter(subject_id=subject_id)
    quotes = [
        "Small study steps become strong exam confidence.",
        "SBS means you do not have to learn alone.",
        "Ask questions early. Confidence grows with practice.",
    ]
    return render(request, "resources/library.html", {"resources": resources, "subjects": subjects, "quotes": quotes})


@login_required
def upload_resource(request):
    if not (request.user.is_staff or hasattr(request.user, "tutor_profile")):
        messages.error(request, "Only tutors and staff can upload study resources.")
        return redirect("resource_library")
    form = SoloStudyResourceForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        resource = form.save(commit=False)
        resource.uploaded_by = request.user
        resource.is_approved = request.user.is_staff
        resource.save()
        messages.success(request, "Resource saved. Staff can approve it if needed.")
        return redirect("resource_library")
    return render(request, "resources/upload.html", {"form": form})
