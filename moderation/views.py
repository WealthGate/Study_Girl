from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UserReportForm


def guidelines(request):
    return render(request, "moderation/guidelines.html")


@login_required
def report_user(request):
    form = UserReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        report = form.save(commit=False)
        report.reporter = request.user
        report.save()
        messages.success(request, "Report sent to the safety team.")
        return redirect("dashboard")
    return render(request, "moderation/report.html", {"form": form})
