"""
🎓 WSGI.PY - Configuration WSGI pour le déploiement

WSGI = Web Server Gateway Interface
C'est l'interface standard entre les serveurs web (Gunicorn, uWSGI) et Django.

⚠️ NE PAS MODIFIER sauf configuration avancée de déploiement

📚 Documentation : https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Indique à Django où se trouve settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esa_manager.settings')

# Créer l'application WSGI
application = get_wsgi_application()

# En production avec Gunicorn :
# gunicorn esa_manager.wsgi:application
