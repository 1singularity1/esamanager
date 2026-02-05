# 🎓 Tutoriel Django - Application ESA Manager

## 📚 Table des matières
1. [Introduction à Django](#intro)
2. [Structure du projet](#structure)
3. [Les modèles (Models)](#models)
4. [Les migrations](#migrations)
5. [Django Admin](#admin)
6. [Les vues (Views)](#views)
7. [Les templates](#templates)
8. [Les URLs](#urls)
9. [Authentification](#auth)
10. [Prochaines étapes](#next)

---

## <a name="intro"></a>1️⃣ Introduction à Django

### Qu'est-ce que Django ?
Django est un framework web Python qui suit le pattern **MVT** (Model-View-Template) :
- **Model** : Structure de vos données (base de données)
- **View** : Logique métier (traitement)
- **Template** : Interface utilisateur (HTML)

### Philosophie Django : "Batteries included"
Django inclut TOUT ce dont vous avez besoin :
- ORM (accès base de données)
- Admin (interface de gestion)
- Auth (authentification)
- Forms (formulaires)
- etc.

---

## <a name="structure"></a>2️⃣ Structure d'un projet Django

```
esa_manager/                    # Dossier racine
│
├── manage.py                   # Commandes Django (runserver, migrate, etc.)
│
├── esa_manager/                # Configuration du projet
│   ├── __init__.py
│   ├── settings.py            # ⭐ CONFIGURATION PRINCIPALE
│   ├── urls.py                # ⭐ ROUTES PRINCIPALES
│   ├── wsgi.py                # Déploiement
│   └── asgi.py                # Déploiement async
│
└── core/                       # Application principale
    ├── __init__.py
    ├── models.py              # ⭐ VOS DONNÉES (Eleve, Benevole, etc.)
    ├── admin.py               # ⭐ CONFIGURATION ADMIN
    ├── views.py               # ⭐ LOGIQUE (routes, traitement)
    ├── urls.py                # Routes de l'app
    ├── apps.py                # Config app
    │
    ├── templates/             # ⭐ VOS PAGES HTML
    │   └── core/
    │       ├── index.html
    │       └── carte.html
    │
    ├── static/                # ⭐ CSS, JS, IMAGES
    │   └── core/
    │       ├── css/
    │       ├── js/
    │       └── img/
    │
    └── migrations/            # Versions de la base de données
        └── __init__.py
```

### Concepts clés :
- **Projet** = Site web complet (esa_manager/)
- **App** = Module fonctionnel (core/)
- Un projet peut avoir plusieurs apps

---

## <a name="models"></a>3️⃣ Les Modèles (Models)

### Qu'est-ce qu'un modèle ?
Un modèle = une table dans la base de données

### Exemple : Modèle Eleve

```python
# core/models.py
from django.db import models

class Eleve(models.Model):
    """
    Représente un élève de l'association ESA
    """
    # Champs texte
    nom = models.CharField(
        max_length=100,           # Longueur max
        verbose_name="Nom"        # Label dans l'admin
    )
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    
    # Champs optionnels (blank=True)
    adresse = models.CharField(max_length=200, blank=True)
    classe = models.CharField(max_length=50, blank=True)
    
    # Champs numériques
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Choix prédéfinis
    STATUT_CHOICES = [
        ('accompagne', 'Accompagné'),
        ('a_accompagner', 'À accompagner'),
    ]
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='a_accompagner'
    )
    
    # Métadonnées automatiques
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"
        ordering = ['nom', 'prenom']  # Tri par défaut
    
    def __str__(self):
        """Représentation texte de l'objet"""
        return f"{self.prenom} {self.nom}"
```

### Types de champs courants :
- `CharField` : Texte court
- `TextField` : Texte long
- `IntegerField` : Nombre entier
- `FloatField` : Nombre décimal
- `BooleanField` : Vrai/Faux
- `DateField` : Date
- `DateTimeField` : Date + heure
- `ForeignKey` : Relation vers un autre modèle

---

## <a name="migrations"></a>4️⃣ Les Migrations

### Qu'est-ce qu'une migration ?
Une migration = un fichier Python qui décrit les changements de structure de la BDD

### Pourquoi ?
- Versionner votre base de données (comme Git pour le code)
- Synchroniser entre développeurs
- Historique des changements

### Commandes essentielles :

```bash
# 1. Créer les migrations (après modification models.py)
python manage.py makemigrations

# 2. Appliquer les migrations (créer/modifier tables)
python manage.py migrate

# 3. Voir l'état des migrations
python manage.py showmigrations

# 4. Voir le SQL généré
python manage.py sqlmigrate core 0001
```

### Workflow typique :
```
1. Modifier models.py
2. makemigrations  → Crée 0001_initial.py
3. migrate         → Applique à la BDD
4. Répéter !
```

---

## <a name="admin"></a>5️⃣ Django Admin

### C'est quoi ?
Une interface d'administration GRATUITE et AUTOMATIQUE pour gérer vos données !

### Configuration basique :

```python
# core/admin.py
from django.contrib import admin
from .models import Eleve

# Enregistrement simple
admin.site.register(Eleve)
```

### Configuration avancée :

```python
from django.contrib import admin
from .models import Eleve, Benevole, Binome

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ['prenom', 'nom', 'classe', 'statut', 'date_creation']
    
    # Filtres latéraux
    list_filter = ['statut', 'classe']
    
    # Champ de recherche
    search_fields = ['nom', 'prenom', 'adresse']
    
    # Champs en lecture seule
    readonly_fields = ['date_creation', 'date_modification']
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'classe')
        }),
        ('Localisation', {
            'fields': ('adresse', 'latitude', 'longitude'),
            'classes': ('collapse',)  # Section repliable
        }),
        ('Statut', {
            'fields': ('statut',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
```

### Accéder à l'admin :
```
http://localhost:8000/admin/
```

### Créer un super-utilisateur :
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@esa.org
# Password: ********
```

---

## <a name="views"></a>6️⃣ Les Vues (Views)

### Qu'est-ce qu'une vue ?
Une vue = une fonction Python qui traite une requête et retourne une réponse

### Types de vues :

#### 1. Function-Based Views (FBV) - Simple
```python
# core/views.py
from django.shortcuts import render
from .models import Eleve

def home(request):
    """Page d'accueil"""
    return render(request, 'core/index.html')

def liste_eleves(request):
    """Liste de tous les élèves"""
    eleves = Eleve.objects.all()  # Récupérer tous les élèves
    return render(request, 'core/eleves.html', {'eleves': eleves})
```

#### 2. Class-Based Views (CBV) - Avancé
```python
from django.views.generic import ListView, DetailView
from .models import Eleve

class EleveListView(ListView):
    model = Eleve
    template_name = 'core/eleves.html'
    context_object_name = 'eleves'
    paginate_by = 20  # Pagination automatique

class EleveDetailView(DetailView):
    model = Eleve
    template_name = 'core/eleve_detail.html'
```

### QuerySets (requêtes base de données) :
```python
# Récupérer tous
Eleve.objects.all()

# Filtrer
Eleve.objects.filter(statut='accompagne')

# Exclure
Eleve.objects.exclude(classe='')

# Récupérer un seul (erreur si 0 ou >1)
Eleve.objects.get(id=1)

# Premier / Dernier
Eleve.objects.first()
Eleve.objects.last()

# Compter
Eleve.objects.count()

# Ordonner
Eleve.objects.order_by('nom')

# Combinaisons
Eleve.objects.filter(statut='accompagne').order_by('-date_creation')[:10]
```

---

## <a name="templates"></a>7️⃣ Les Templates

### Langage de template Django (DTL)

```html
<!-- templates/core/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>ESA Manager</title>
    {% load static %}  <!-- Charger les fichiers statiques -->
    <link rel="stylesheet" href="{% static 'core/css/style.css' %}">
</head>
<body>
    <h1>Bienvenue sur ESA Manager</h1>
    
    <!-- Variables -->
    <p>Utilisateur : {{ user.username }}</p>
    
    <!-- Conditions -->
    {% if user.is_authenticated %}
        <p>Vous êtes connecté</p>
    {% else %}
        <a href="{% url 'login' %}">Se connecter</a>
    {% endif %}
    
    <!-- Boucles -->
    <ul>
    {% for eleve in eleves %}
        <li>{{ eleve.prenom }} {{ eleve.nom }} - {{ eleve.classe }}</li>
    {% empty %}
        <li>Aucun élève</li>
    {% endfor %}
    </ul>
    
    <!-- Filtres -->
    {{ eleve.nom|upper }}           <!-- DUPONT -->
    {{ date|date:"d/m/Y" }}          <!-- 28/01/2026 -->
    {{ texte|truncatewords:10 }}    <!-- Couper à 10 mots -->
    
    <!-- URLs nommées -->
    <a href="{% url 'home' %}">Accueil</a>
    <a href="{% url 'eleve_detail' eleve.id %}">Détail</a>
</body>
</html>
```

### Héritage de templates (DRY - Don't Repeat Yourself)

```html
<!-- templates/core/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}ESA Manager{% endblock %}</title>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav>
        <!-- Menu commun -->
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <!-- Footer commun -->
    </footer>
    
    {% block extra_js %}{% endblock %}
</body>
</html>

<!-- templates/core/index.html -->
{% extends 'core/base.html' %}

{% block title %}Accueil - ESA Manager{% endblock %}

{% block content %}
    <h1>Page d'accueil</h1>
    <!-- Contenu spécifique -->
{% endblock %}
```

---

## <a name="urls"></a>8️⃣ Les URLs

### Configuration des routes

```python
# esa_manager/urls.py (URLs principales)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),           # Admin Django
    path('', include('core.urls')),            # URLs de l'app core
]

# core/urls.py (URLs de l'app)
from django.urls import path
from . import views

app_name = 'core'  # Namespace

urlpatterns = [
    path('', views.home, name='home'),
    path('carte/binomes/', views.carte_binomes, name='carte_binomes'),
    path('eleves/', views.liste_eleves, name='liste_eleves'),
    path('eleves/<int:pk>/', views.eleve_detail, name='eleve_detail'),
]
```

### Paramètres dans les URLs :
```python
# URL avec paramètre
path('eleves/<int:pk>/', views.eleve_detail, name='eleve_detail')

# Vue correspondante
def eleve_detail(request, pk):
    eleve = Eleve.objects.get(pk=pk)
    return render(request, 'core/eleve_detail.html', {'eleve': eleve})
```

### Reverse URLs (dans le code Python) :
```python
from django.urls import reverse

# Obtenir l'URL
url = reverse('core:home')  # '/'
url = reverse('core:eleve_detail', args=[5])  # '/eleves/5/'
```

---

## <a name="auth"></a>9️⃣ Authentification

### Django Auth intégré

```python
# views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.shortcuts import redirect

@login_required  # Protéger une vue
def carte_binomes(request):
    return render(request, 'core/carte_binomes.html')

def login_view(request):
    if request.method == 'POST':
        # Logique de login
        pass
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')
```

### Dans les templates :
```html
{% if user.is_authenticated %}
    <p>Bonjour {{ user.username }}</p>
    <a href="{% url 'logout' %}">Déconnexion</a>
{% else %}
    <a href="{% url 'login' %}">Connexion</a>
{% endif %}
```

---

## <a name="next"></a>🔟 Prochaines étapes

1. ✅ Créer le projet
2. ✅ Définir les modèles
3. ✅ Configurer l'admin
4. ✅ Créer les vues
5. ✅ Créer les templates
6. ✅ Configurer les URLs
7. ⏭️ Ajouter l'authentification
8. ⏭️ API REST (Django REST Framework)
9. ⏭️ Déploiement

---

## 📚 Ressources pour approfondir

- Documentation officielle : https://docs.djangoproject.com/
- Django Girls Tutorial : https://tutorial.djangogirls.org/
- Real Python Django : https://realpython.com/tutorials/django/
- MDN Django Tutorial : https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django

---

**Vous êtes prêt à commencer ! 🚀**
