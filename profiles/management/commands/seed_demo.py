from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from profiles.models import PersonalityTrait, StudentProfile, Subject, TutorProfile
from resources.models import SoloStudyResource
from tutoring.models import SessionFeedback, StudySession, StudySisterConnection


class Command(BaseCommand):
    help = "Create realistic demo data for a Study_girl presentation."

    def handle(self, *args, **options):
        subjects = [
            "Mathematics", "English A", "English B", "Biology", "Chemistry", "Physics",
            "Information Technology", "Social Studies", "Principles of Accounts",
            "Principles of Business", "Spanish", "French",
        ]
        traits = ["Patient", "Encouraging", "Calm", "Organized", "Funny", "Direct", "Creative"]

        subject_objects = {name: Subject.objects.get_or_create(name=name)[0] for name in subjects}
        trait_objects = {name: PersonalityTrait.objects.get_or_create(name=name)[0] for name in traits}

        tutor_names = [
            ("Aaliyah Joseph", ["Mathematics", "Physics"], ["Patient", "Direct"]),
            ("Mia Charles", ["English A", "English B"], ["Creative", "Encouraging"]),
            ("Zara Fontaine", ["Biology", "Chemistry"], ["Calm", "Organized"]),
            ("Kayla Henderson", ["Information Technology", "Mathematics"], ["Funny", "Patient"]),
            ("Nia Douglas", ["Social Studies", "Spanish"], ["Encouraging", "Calm"]),
            ("Leah Thomas", ["Principles of Accounts", "Principles of Business"], ["Organized", "Direct"]),
        ]
        student_names = ["Amara", "Janelle", "Renee", "Tiana", "Skye", "Elise", "Mikayla"]

        tutors = []
        for index, (full_name, strong_subjects, strong_traits) in enumerate(tutor_names, start=1):
            user, _ = User.objects.get_or_create(username=f"tutor{index}", defaults={"email": f"tutor{index}@example.com"})
            user.set_password("demo12345")
            user.save()
            profile, _ = TutorProfile.objects.get_or_create(user=user, defaults={"full_name": full_name})
            profile.full_name = full_name
            profile.school = "Wesley High School"
            profile.form_year = "Form 5"
            profile.short_bio = f"I enjoy helping sisters build confidence in {', '.join(strong_subjects)}."
            profile.tutoring_style = "Step-by-step explanations with practice questions."
            profile.availability = "After school and Saturday mornings"
            profile.approval_status = "approved"
            profile.completed_sessions = index + 2
            profile.average_rating = 4.3 + (index % 3) * 0.2
            profile.save()
            profile.subjects.set([subject_objects[name] for name in strong_subjects])
            profile.personality_traits.set([trait_objects[name] for name in strong_traits])
            tutors.append(profile)

        students = []
        for index, first_name in enumerate(student_names, start=1):
            user, _ = User.objects.get_or_create(username=f"student{index}", defaults={"email": f"student{index}@example.com"})
            user.set_password("demo12345")
            user.save()
            profile, _ = StudentProfile.objects.get_or_create(user=user, defaults={"full_name": f"{first_name} Demo"})
            profile.full_name = f"{first_name} Demo"
            profile.school = "Wesley High School"
            profile.form_year = f"Form {3 + (index % 3)}"
            profile.learning_style = "Visual practice and short explanations"
            profile.short_intro = "I want to feel more prepared for CSEC."
            profile.favorite_study_times = "Evenings"
            profile.save()
            profile.subjects_needing_help.set([subject_objects["Mathematics"], subject_objects["English A"]])
            profile.preferred_traits.set([trait_objects["Patient"], trait_objects["Encouraging"]])
            students.append(profile)

        for index in range(3):
            session, _ = StudySession.objects.get_or_create(
                student=students[index].user,
                tutor=tutors[index].user,
                subject=subject_objects["Mathematics"],
                defaults={"status": "completed"},
            )
            session.status = "completed"
            session.save()
            for reviewer in [session.student, session.tutor]:
                SessionFeedback.objects.get_or_create(session=session, reviewer=reviewer, defaults={"rating": 5, "was_helpful": True, "wants_to_continue": True})
            connection, _ = StudySisterConnection.objects.get_or_create(student=session.student, tutor=session.tutor)
            connection.status = "active"
            connection.session_count = 5 if index == 0 else 2
            connection.vibe_unlocked = index == 0
            connection.save()

        for subject_name in subjects[:8]:
            SoloStudyResource.objects.get_or_create(
                title=f"{subject_name} CSEC practice starter",
                subject=subject_objects[subject_name],
                defaults={
                    "resource_type": "video",
                    "description": f"A demo resource for reviewing {subject_name} skills before exams.",
                    "external_link": "https://www.youtube.com/results?search_query=royalty+free+study+skills",
                    "is_approved": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Study_girl demo data created. Demo password: demo12345"))
