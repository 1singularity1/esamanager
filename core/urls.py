"""
🎓 URLS.PY - Configuration des routes de l'application CORE

Ce fichier mappe les URLs aux vues (fonctions Python).

📚 Documentation : https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.urls import path
from . import views

# ============================================================================
# 🏷️ NAMESPACE
# ============================================================================

# Nom de l'application (pour les références inversées)
# Utilisation dans les templates : {% url 'core:home' %}
app_name = 'core'


# ============================================================================
# 🛣️ PATTERNS D'URL
# ============================================================================

urlpatterns = [
    # ----------------------------------------------------------------
    # 🏠 PAGE D'ACCUEIL
    # ----------------------------------------------------------------
    # URL : /
    # Vue : views.home
    # Nom : 'home' (pour {% url 'core:home' %})
    path('', views.home, name='home'),
    
    # ----------------------------------------------------------------
    # 🗺️ CARTES INTERACTIVES
    # ----------------------------------------------------------------
    # URL : /carte/binomes/
    # Vue : views.carte_binomes
    path('carte/binomes/', views.carte_binomes, name='carte_binomes'),
    
    # URL : /carte/autre/
    # Vue : views.carte_autre
    path('carte/enattente/', views.carte_enattente, name='carte_enattente'),
    
    # ----------------------------------------------------------------
    # 📊 API JSON (pour alimenter les cartes JavaScript)
    # ----------------------------------------------------------------
    # URL : /api/binomes/
    # Retourne : JSON
    path('api/binomes/', views.api_binomes_json, name='api_binomes'),
    
    # URL : /api/eleves/
    path('api/eleves/', views.api_eleves_json, name='api_eleves'),
    
    # URL : /api/benevoles/
    path('api/benevoles/', views.api_benevoles_json, name='api_benevoles'),
    
    # ----------------------------------------------------------------
    # 📋 LISTES (Optionnel)
    # ----------------------------------------------------------------
    # URL : /eleves/
    path('eleves/', views.liste_eleves, name='liste_eleves'),
    
    # URL : /benevoles/
    path('benevoles/', views.liste_benevoles, name='liste_benevoles'),
    
    # ----------------------------------------------------------------
    # 🔍 DÉTAILS (Optionnel)
    # ----------------------------------------------------------------
    # URL : /eleves/5/
    # <int:pk> : Paramètre entier nommé 'pk'
    path('eleves/<int:pk>/', views.eleve_detail, name='eleve_detail'),
    
    # URL : /benevoles/3/
    path('benevoles/<int:pk>/', views.benevole_detail, name='benevole_detail'),
    
# ----------------------------------------------------------------
    # 💾 AUTOSAVE (ROUTES CORRIGÉES)
    # ----------------------------------------------------------------
    # ⚠️ IMPORTANT : Ne pas mettre "admin/" au début !
    # Ces routes doivent être en dehors du namespace admin de Django
    path('autosave/eleve/', views.autosave_eleve, name='autosave_eleve'),
    path('validate/eleve/', views.validate_eleve, name='validate_eleve'),
]


# ============================================================================
# 🎓 NOTES D'APPRENTISSAGE
# ============================================================================

"""
📝 Syntaxe des patterns d'URL :

1. PATH SIMPLE :
   path('about/', views.about, name='about')
   └─ URL : /about/
   └─ Vue : views.about()
   └─ Nom : 'about'

2. AVEC PARAMÈTRES :
   path('user/<int:id>/', views.user_detail, name='user_detail')
   └─ URL : /user/5/
   └─ Paramètre : id=5 (entier)
   └─ Vue : views.user_detail(request, id=5)

3. TYPES DE PARAMÈTRES :
   - <int:name> : Nombre entier
   - <str:name> : Chaîne de caractères (défaut)
   - <slug:name> : Slug (lettres, chiffres, tirets)
   - <uuid:name> : UUID
   - <path:name> : Chemin complet (avec /)

4. NOMS D'URL :
   name='home' permet :
   - Dans templates : {% url 'core:home' %}
   - Dans code Python : reverse('core:home')
   - Avantage : Changer l'URL sans toucher au code !

📚 Exemples d'utilisation :

DANS LES TEMPLATES :
   <a href="{% url 'core:home' %}">Accueil</a>
   <a href="{% url 'core:eleve_detail' eleve.pk %}">Voir élève</a>

DANS LE CODE PYTHON :
   from django.urls import reverse
   url = reverse('core:home')  # '/'
   url = reverse('core:eleve_detail', args=[5])  # '/eleves/5/'

REDIRECTIONS :
   from django.shortcuts import redirect
   return redirect('core:home')

🔗 Organisation multi-apps :

esa_manager/urls.py :
   path('', include('core.urls'))        → Pas de préfixe
   path('blog/', include('blog.urls'))   → Préfixe /blog/

core/urls.py :
   path('carte/', views.carte)           → URL finale : /carte/

blog/urls.py :
   path('articles/', views.list)         → URL finale : /blog/articles/

🎯 Bonnes pratiques :
   1. Toujours nommer vos URLs (name='...')
   2. Utiliser des namespaces (app_name = 'core')
   3. Organiser par fonctionnalité
   4. Préférer path() à re_path() (sauf regex complexes)
"""
