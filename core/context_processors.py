"""
Context processors pour ajouter des variables globales aux templates
"""

import sys
import os
from django.conf import settings

# Ajouter le répertoire parent au path
sys.path.insert(0, str(settings.BASE_DIR))

def version_info(request):
    """Ajoute les infos de version et nom de l'app au contexte"""
    try:
        import version
        app_version = version.get_version()
    except ImportError:
        app_version = 'Beta 0.1'
    
    return {
        'APP_VERSION': app_version,
        'APP_NAME': 'ESAdmin Marseille',
    }