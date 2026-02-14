from django.urls import path, include
from django.conf import settings

# Import conditionnel de l'admin
if settings.ADMIN_ENABLED:
    from django.contrib import admin

urlpatterns = [
    path('', include('core.urls')),
]

# Ajouter l'admin seulement si activé
if settings.ADMIN_ENABLED:
    urlpatterns.insert(0, path('admin/', admin.site.urls))