from django.shortcuts import redirect
from django.conf import settings
from allauth.mfa.models import Authenticator
from urllib3 import request
from datetime import datetime

URLS_PUBLIQUES = [
    '/accounts/',
    '/favicon.ico',
    '/static/',
]
from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if '2fa' in request.path:
                    print(f"DEBUG [{request.method}] session mfa secret: {request.session.get('mfa.totp.secret', 'ABSENT')}")
        if not request.user.is_authenticated:
            if not any(request.path.startswith(url) for url in URLS_PUBLIQUES):
                return redirect('/accounts/login/')
        elif request.user.is_authenticated:
            # Vérifier si le 2FA est configuré
            if not any(request.path.startswith(url) for url in URLS_PUBLIQUES):
                has_mfa = Authenticator.objects.filter(
                    user=request.user,
                    type=Authenticator.Type.TOTP
                ).exists()
                if not has_mfa:
                    return redirect('/accounts/2fa/totp/activate/')
        print(f"DEBUG path: {request.path}")
        print(f"DEBUG user: {request.user}")
        print(f"DEBUG authenticated: {request.user.is_authenticated}")
        if request.method == 'POST' and '2fa' in request.path:
            print(f"DEBUG POST data: {request.POST}")
        print(f"DEBUG heure serveur: {datetime.now()}")

        if request.user.is_authenticated:
            auths = Authenticator.objects.filter(user=request.user)
            print(f"DEBUG authenticators: {list(auths.values())}")

        if request.method == 'POST' and '2fa' in request.path:
            print(f"DEBUG session keys: {list(request.session.keys())}")
            print(f"DEBUG session data: {dict(request.session)}")
        return self.get_response(request)