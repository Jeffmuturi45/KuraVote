# election/admin_2fa.py

from django.shortcuts import redirect, render
from django.contrib import messages
from django_otp import user_has_device, verify_token
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import qrcode.image.svg
import io
import base64


class AdminOTPMiddleware:
    """
    Every request to /admin-panel/* from a staff user that has
    an OTP device registered must have passed OTP verification
    this session. If not, redirect to the OTP verify page.
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
            # Has a device registered?
            if user_has_device(request.user):
                # Has verified this session?
                if not request.user.is_verified():
                    return redirect('/admin-panel/verify-otp/')
            else:
                # No device — force setup
                return redirect('/admin-panel/setup-otp/')

        return self.get_response(request)
