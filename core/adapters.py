from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User

EMAILS_AUTORISES = [
    'david.delannoy@gmail.com',
    'bernadettefortain2023@gmail.com',
    'clara.jonas@hotmail.fr',
    'g.tchorbadjian@gmail.com',
    'batac.gilbert@orange.fr',
    'sylviehue1954@gmail.com',
]

class ESAAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email', '').lower()
        print(f"DEBUG email Google: {email}")
        if not User.objects.filter(email=email, is_active=True).exists():
            print(f"DEBUG non autorisé: {email}")
            raise ImmediateHttpResponse(
                HttpResponseForbidden("Accès non autorisé.")
            )
        print(f"DEBUG autorisé: {email}")
        print(f"DEBUG pre_social_login email: {sociallogin.account.extra_data.get('email')}")

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Surcharge get_client_ip pour gérer le header X-Forwarded-For
    qui peut contenir plusieurs IPs séparées par virgule (ex: "1.2.3.4, 127.0.0.1").
    """

    def get_client_ip(self, request):
        # X-Forwarded-For en priorité (set par Nginx)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Prendre uniquement la première IP (client réel)
            return x_forwarded_for.split(',')[0].strip()

        # Fallback X-Real-IP
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip.strip()

        # Dernier recours
        return request.META.get('REMOTE_ADDR', '')