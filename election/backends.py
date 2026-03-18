#  teaches Django how to log in a student using an admission number instead of a username.
# Step 1 — Find by admission number:
# Django's default login expects a username field. Our login form will send the admission number in the username field — this backend converts it to an integer and looks up the student. If the admission number doesn't exist in the database, Student.DoesNotExist is caught and None is returned — which tells Django login failed.
# Step 2 — Check is_active:
# If the admin has deactivated a student account, they cannot log in even with the correct password. This is how we block past students or students on leave.
# Step 3 — Verify password:
# check_password() handles all the hashing internally — it hashes what the student typed and compares it to the stored hash. We never compare plain text passwords anywhere.
# Step 4 — Return None:
# Returning None from any step tells Django authentication failed. Django then shows the login error automatically.
# get_user method:
# Django calls this on every request to load the currently logged-in student from the session. Without it, the student would get logged out on every page refresh.
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

Student = get_user_model()


class AdmissionNumberBackend(BaseBackend):

    def authenticate(self, request, username=None,
                     password=None, **kwargs):
        try:
            admission_number = int(username)
            student = Student.objects.get(
                admission_number=admission_number
            )
        except (ValueError, TypeError, Student.DoesNotExist):
            return None

        # ── Block deactivated accounts at login ───────────
        if not student.is_active:
            return None

        if student.check_password(password):
            return student

        return None

    def get_user(self, user_id):
        try:
            return Student.objects.get(pk=user_id)
        except Student.DoesNotExist:
            return None
