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
from django.core.cache import cache
from django.utils import timezone
import time


class ForcePasswordChangeMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ── Auto-close expired elections ──────────────────
        # Check at most once every 60 seconds to avoid
        # hitting the DB on every single request
        last_check = cache.get('election_autoclose_check')
        if not last_check:
            try:
                from .models import Election
                expired = Election.objects.filter(
                    status=Election.STATUS_ACTIVE,
                    end_date__lte=timezone.now()
                )
                for election in expired:
                    election.status = Election.STATUS_CLOSED
                    election.save()
            except Exception:
                pass
            # Only check again after 60 seconds
            cache.set('election_autoclose_check', True, timeout=60)

        # ── Track active users ────────────────────────────
        if request.user.is_authenticated \
                and not request.user.is_staff:
            cache_key = f'active_user_{request.user.id}'
            cache.set(cache_key, {
                'user_id':   request.user.id,
                'name':      request.user.get_full_name(),
                'admission': request.user.admission_number,
                'last_seen': time.time(),
            }, timeout=300)

            active_ids = cache.get('active_user_ids', set())
            active_ids.add(request.user.id)
            cache.set('active_user_ids', active_ids, timeout=300)

        # ── Force password change ─────────────────────────
        if request.user.is_authenticated:
            if not request.user.is_staff:
                if not request.user.password_changed:
                    try:
                        change_url = reverse('change_password')
                        logout_url = reverse('logout')
                        allowed_urls = [change_url, logout_url]
                        if request.path not in allowed_urls:
                            return redirect('change_password')
                    except NoReverseMatch:
                        pass

        response = self.get_response(request)
        return response
