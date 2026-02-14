"""
🎓 SETTINGS.PY - Configuration principale de Django

Ce fichier contient TOUTE la configuration de votre projet Django.
Chaque section est commentée pour que vous compreniez son rôle.

📚 Documentation : https://docs.djangoproject.com/en/stable/ref/settings/
"""

from pathlib import Path

# ============================================================================
# 📁 CHEMINS DE BASE
# ============================================================================

# Dossier racine du projet : /chemin/vers/esa_manager/
BASE_DIR = Path(__file__).resolve().parent.parent

# Exemple d'utilisation : BASE_DIR / 'templates' / 'index.html'


# ============================================================================
# 🔐 SÉCURITÉ
# ============================================================================

# Clé secrète utilisée pour le chiffrement
# ⚠️ EN PRODUCTION : Générer une nouvelle clé et la mettre dans une variable d'environnement !
# Générer une clé : python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = 'django-insecure-votre-cle-secrete-a-changer-en-production-123456789'

# Mode DEBUG : affiche les erreurs détaillées
# ⚠️ EN PRODUCTION : Toujours mettre à False !
DEBUG = True

# Hôtes autorisés à accéder au site
# En développement : ['localhost', '127.0.0.1']
# En production : ['esa.unsoutienpourapprendre.org', 'www.unsoutienpourapprendre.org']
ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# ============================================================================
# 📦 APPLICATIONS INSTALLÉES
# ============================================================================

INSTALLED_APPS = [
    # Applications Django intégrées (ne pas toucher)
    'django.contrib.admin',          # Interface d'administration
    'django.contrib.auth',           # Système d'authentification
    'django.contrib.contenttypes',   # Système de types de contenu
    'django.contrib.sessions',       # Gestion des sessions
    'django.contrib.messages',       # Framework de messages
    'django.contrib.staticfiles',    # Gestion des fichiers statiques (CSS, JS, images)
    'bootstrap5',               # Intégration de Bootstrap 5
    'django_bootstrap_icons',  # Intégration des icônes Bootstrap Icons
    # Vos applications personnalisées
    'core',  # ← Application principale ESA Manager
]


# ============================================================================
# 🔌 MIDDLEWARE
# ============================================================================
# Middleware = couche intermédiaire entre la requête HTTP et votre code
# Ils traitent les requêtes/réponses dans l'ordre de la liste

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',       # Sécurité
    'django.contrib.sessions.middleware.SessionMiddleware', # Sessions utilisateur
    'django.middleware.common.CommonMiddleware',           # Fonctionnalités communes
    'django.middleware.csrf.CsrfViewMiddleware',          # Protection CSRF (attaques)
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Authentification
    'django.contrib.messages.middleware.MessageMiddleware',    # Messages flash
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Protection clickjacking
]

# ============================================================================
# 🌐 CONFIGURATION URLs
# ============================================================================

# Fichier principal des routes
ROOT_URLCONF = 'esa_manager.urls'


# ============================================================================
# 🎨 TEMPLATES (Pages HTML)
# ============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        
        # Dossiers où Django cherche les templates
        # Ordre : d'abord core/templates/, puis ici
        'DIRS': [
            BASE_DIR / 'templates',  # Templates globaux (si besoin)
        ],
        
        # Chercher templates dans les dossiers des apps
        'APP_DIRS': True,
        
        # Processeurs de contexte : variables disponibles dans TOUS les templates
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # {{ request }} disponible
                'django.contrib.auth.context_processors.auth', # {{ user }} disponible
                'django.contrib.messages.context_processors.messages', # Messages flash
                'core.context_processors.version_info',
            ],
        },
    },
]


# ============================================================================
# 🚀 WSGI (Déploiement)
# ============================================================================

WSGI_APPLICATION = 'esa_manager.wsgi.application'


# ============================================================================
# 🗄️ BASE DE DONNÉES
# ============================================================================

# Configuration SQLite (développement)
# Simple, un seul fichier : db.sqlite3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Pour PostgreSQL en production (commenté pour l'instant) :
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'esa_manager_db',
#         'USER': 'esa_user',
#         'PASSWORD': 'votre_mot_de_passe',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


# ============================================================================
# 🔑 VALIDATION DES MOTS DE PASSE
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        # Empêche les mots de passe trop similaires aux infos utilisateur
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Impose une longueur minimale (8 caractères par défaut)
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # Empêche les mots de passe trop communs (password123, etc.)
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Empêche les mots de passe uniquement numériques
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================================================
# 🌍 INTERNATIONALISATION
# ============================================================================

# Langue par défaut
LANGUAGE_CODE = 'fr-fr'  # Français

# Fuseau horaire
TIME_ZONE = 'Europe/Paris'  # Heure de Paris

# Activer l'internationalisation
USE_I18N = True

# Activer la localisation (formats de dates, nombres)
USE_L10N = True

# Utiliser les fuseaux horaires (recommandé)
USE_TZ = True


# ============================================================================
# 📂 FICHIERS STATIQUES (CSS, JS, Images)
# ============================================================================

# URL pour accéder aux fichiers statiques
# Exemple : http://localhost:8000/static/core/css/style.css
STATIC_URL = '/static/'

# Dossiers supplémentaires pour les fichiers statiques globaux
STATICFILES_DIRS = [
    # BASE_DIR / 'static',  # Si vous avez des fichiers statiques globaux
]

# Dossier où collecter tous les fichiers statiques en production
# Commande : python manage.py collectstatic
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ============================================================================
# 📤 FICHIERS MÉDIA (Uploads utilisateurs)
# ============================================================================

# URL pour accéder aux fichiers média
MEDIA_URL = '/media/'

# Dossier où stocker les uploads
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================================================
# 🔐 AUTHENTIFICATION
# ============================================================================

# URL de redirection après login
LOGIN_REDIRECT_URL = '/'

# URL de redirection après logout
LOGOUT_REDIRECT_URL = '/'

# URL de la page de login
LOGIN_URL = '/login/'


# ============================================================================
# 🔑 TYPE DE CLÉ PRIMAIRE PAR DÉFAUT
# ============================================================================

# Type de clé primaire pour les nouveaux modèles
# BigAutoField = entiers de -9223372036854775808 à 9223372036854775807
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================================
# 📧 EMAIL (Configuration pour plus tard)
# ============================================================================

# En développement : afficher les emails dans la console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# En production (Gmail par exemple) :
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'votre.email@gmail.com'
# EMAIL_HOST_PASSWORD = 'votre_mot_de_passe_application'


# ============================================================================
# 📊 LOGGING (Journalisation des erreurs)
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


# ============================================================================
# 🎓 NOTES D'APPRENTISSAGE
# ============================================================================

"""
📝 Ce que vous devez savoir :

1. SECRET_KEY : Ne JAMAIS la partager ou la commiter sur Git !
2. DEBUG = True : Seulement en développement
3. ALLOWED_HOSTS : Mettre votre domaine en production
4. INSTALLED_APPS : Liste vos applications (core, etc.)
5. DATABASES : SQLite en dev, PostgreSQL en prod
6. STATIC_URL : Pour accéder à vos CSS/JS
7. MEDIA_URL : Pour les uploads utilisateurs

🔧 Modifications courantes :
- Ajouter une app : INSTALLED_APPS
- Changer la langue : LANGUAGE_CODE
- Configurer la BDD : DATABASES
- Ajouter un middleware : MIDDLEWARE

📚 Pour approfondir :
https://docs.djangoproject.com/en/stable/ref/settings/
"""
