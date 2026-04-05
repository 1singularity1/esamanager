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