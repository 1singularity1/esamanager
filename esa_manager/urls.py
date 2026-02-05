"""
🎓 URLS.PY - Routes principales du projet

Ce fichier définit les URLs (routes) de TOUT le projet.
Il fait le lien entre une URL et une vue (fonction Python).

📚 Documentation : https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ============================================================================
# 🛣️ CONFIGURATION DES ROUTES
# ============================================================================

urlpatterns = [
    # ----------------------------------------------------------------
    # 🔐 ADMIN DJANGO
    # ----------------------------------------------------------------
    # URL : http://localhost:8000/admin/
    # Interface d'administration automatique de Django
    path('admin/', admin.site.urls),
    
    # ----------------------------------------------------------------
    # 📱 ROUTES DE L'APPLICATION "CORE"
    # ----------------------------------------------------------------
    # Toutes les URLs de core/ sont incluses ici
    # '' signifie : à la racine (pas de préfixe)
    # Exemple : '' + 'carte/binomes/' = '/carte/binomes/'
    path('', include('core.urls')),
    
    # ----------------------------------------------------------------
    # 🔐 AUTHENTIFICATION (optionnel, à décommenter si besoin)
    # ----------------------------------------------------------------
    # Django fournit des vues d'authentification prêtes à l'emploi
    # path('accounts/', include('django.contrib.auth.urls')),
    # Cela crée automatiquement :
    # - /accounts/login/
    # - /accounts/logout/
    # - /accounts/password_change/
    # - etc.
]

# ============================================================================
# 📂 SERVIR LES FICHIERS STATIQUES ET MÉDIA EN DÉVELOPPEMENT
# ============================================================================

# ⚠️ Cette configuration est SEULEMENT pour le développement !
# En production, les fichiers statiques sont servis par Nginx/Apache

if settings.DEBUG:
    # Ajouter les routes pour servir les fichiers média (uploads)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Les fichiers statiques (CSS/JS) sont déjà servis automatiquement en DEBUG


# ============================================================================
# 🎓 NOTES D'APPRENTISSAGE
# ============================================================================

"""
📝 Comprendre les URLs :

1. path('admin/', admin.site.urls)
   └─ URL : /admin/
   └─ Vue : Interface admin Django

2. path('', include('core.urls'))
   └─ Inclut TOUTES les URLs définies dans core/urls.py
   └─ Permet de organiser les routes par application

3. path('api/', include('api.urls'))  # Exemple
   └─ Préfixe toutes les URLs de api/urls.py avec '/api/'
   └─ Si api/urls.py contient path('users/', ...)
   └─ L'URL finale sera : /api/users/

🔍 Comment Django trouve la bonne vue :
1. Requête : GET /carte/binomes/
2. Django cherche dans urlpatterns
3. Trouve path('', include('core.urls'))
4. Regarde dans core/urls.py
5. Trouve path('carte/binomes/', views.carte_binomes)
6. Exécute la fonction views.carte_binomes()
7. Retourne la réponse HTTP

📚 Patterns d'URL courants :
- path('', views.home)                    → /
- path('about/', views.about)             → /about/
- path('user/<int:id>/', views.user)      → /user/5/
- path('user/<str:username>/', views.user)→ /user/john/
- path('<slug:slug>/', views.page)        → /mon-article/

🎯 Organisation recommandée :
- URLs principales (admin, etc.) → esa_manager/urls.py
- URLs de l'app core → core/urls.py
- URLs de l'app api → api/urls.py
"""
