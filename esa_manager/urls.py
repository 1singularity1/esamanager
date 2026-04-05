"""
🎓 URLS.PY - Routes principales du projet
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import conditionnel de l'admin
if settings.ADMIN_ENABLED:
    from django.contrib import admin

# ============================================================================
# 🛣️ CONFIGURATION DES ROUTES
# ============================================================================

urlpatterns = [
    # Routes de l'application CORE
    path('', include('core.urls')),
]

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
]

# Ajouter l'admin seulement si activé
if settings.ADMIN_ENABLED:
    urlpatterns.insert(0, path('admin/', admin.site.urls))

# ============================================================================
# 📂 FICHIERS MÉDIA EN DÉVELOPPEMENT
# ============================================================================

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

