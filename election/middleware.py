# forcing password changeon first login

'''```
Student logs in
      ↓
Middleware checks every single request
      ↓
Is the user logged in?
    NO  → let the request through normally
    YES ↓
Is the user a staff/admin?
    YES → let the request through normally
    NO  ↓
Has the student changed their password?
    YES → let the request through normally
    NO  ↓
Is the student trying to access change_password or logout?
    YES → let the request through (they need these pages)
    NO  ↓
Redirect to change_password — they cannot go anywhere else'''

from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch


class ForcePasswordChangeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ── Run this code before the view ─────────────────────
        if request.user.is_authenticated:

            # ── Skip for admin/staff users ────────────────────
            if not request.user.is_staff:

                # ── Check if password has been changed ────────
                if not request.user.password_changed:

                    try:
                        change_url = reverse('change_password')
                        logout_url = reverse('logout')
                        allowed_urls = [change_url, logout_url]

                        if request.path not in allowed_urls:
                            return redirect('change_password')

                    except NoReverseMatch:
                        # URLs not configured yet — let it pass
                        # This prevents crashes during development
                        pass

        response = self.get_response(request)
        return response
