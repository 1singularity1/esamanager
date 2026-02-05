"""
🎓 ASGI.PY - Configuration ASGI pour le déploiement asynchrone

ASGI = Asynchronous Server Gateway Interface
Version asynchrone de WSGI, pour WebSockets, HTTP/2, etc.

⚠️ Pour l'instant, vous n'en avez pas besoin (WSGI suffit)

📚 Documentation : https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esa_manager.settings')

application = get_asgi_application()
