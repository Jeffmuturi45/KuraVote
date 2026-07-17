
from django.shortcuts import redirect
from django_otp import user_has_device


class AdminOTPMiddleware:
    """
    Every request to /admin-panel/* from a staff user that has
    an OTP device registered must have passed OTP verification
    this session. If not, redirect to the OTP verify page.

    Respects the SystemSettings.two_fa_enabled toggle — when 2FA
    is disabled globally, the middleware is effectively bypassed.
    """
    EXEMPT_PATHS = [
        '/admin-panel/verify-otp/',
        '/admin-panel/setup-otp/',
        '/logout/',
        '/login/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path.startswith('/admin-panel/')
            and request.user.is_authenticated
            and request.user.is_staff
            and request.path not in self.EXEMPT_PATHS
        ):
            # Check if 2FA is globally enabled
            from .models import SystemSettings
            settings_obj = SystemSettings.get()

            if settings_obj.two_fa_enabled:
                if user_has_device(request.user):
                    if not request.user.is_verified():
                        return redirect('/admin-panel/verify-otp/')
                else:
                    # No device yet — force setup
                    return redirect('/admin-panel/setup-otp/')
            # If 2FA is disabled, skip all OTP checks

        return self.get_response(request)
