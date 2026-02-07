"""
🎓 VIEWS.PY - Vues (contrôleurs) de l'application

Une vue = une fonction Python qui :
1. Reçoit une requête HTTP (request)
2. Traite la logique (récupère des données, etc.)
3. Retourne une réponse HTTP (page HTML, JSON, etc.)

📚 Documentation : https://docs.djangoproject.com/en/stable/topics/http/views/
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Eleve, Benevole, Binome


# ============================================================================
# 🏠 PAGE D'ACCUEIL
# ============================================================================

def home(request):
    """
    Vue de la page d'accueil avec 2 boutons vers les cartes.
    
    Args:
        request : Objet HttpRequest contenant les infos de la requête
    
    Returns:
        HttpResponse : Page HTML rendue
    """
    
    # Récupérer quelques statistiques pour l'affichage
    stats = {
        'total_eleves': Eleve.objects.count(),
        'eleves_accompagnes': Eleve.objects.filter(statut='accompagne').count(),
        'total_benevoles': Benevole.objects.count(),
        'benevoles_disponibles': Benevole.objects.filter(disponibilite='disponible').count(),
        'total_binomes': Binome.objects.filter(actif=True).count(),
    }
    
    # Contexte = dictionnaire de variables passées au template
    context = {
        'stats': stats,
        'page_title': 'ESA Manager - Accueil',
    }
    
    # Rendre le template avec le contexte
    # Django cherche dans : core/templates/core/index.html
    return render(request, 'core/index.html', context)


# ============================================================================
# 🗺️ CARTE DES BINÔMES
# ============================================================================

# @login_required  # Décommenter pour protéger par authentification
def carte_binomes(request):
    """
    Vue de la carte interactive des binômes élèves-bénévoles.
    
    Charge tous les binômes actifs avec leurs coordonnées GPS
    et les affiche sur une carte Leaflet.
    """
    
    # Récupérer tous les binômes actifs avec leurs relations
    # select_related() : Optimisation pour éviter les requêtes multiples
    binomes = Binome.objects.filter(
        actif=True
    ).select_related(
        'eleve',      # Charge l'élève en même temps
        'benevole'    # Charge le bénévole en même temps
    )
    
    # Filtrer uniquement les binômes avec coordonnées GPS
    binomes_geolocalisés = []
    for binome in binomes:
        if (binome.eleve.latitude and binome.eleve.longitude and
            binome.benevole and binome.benevole.latitude and binome.benevole.longitude):
            binomes_geolocalisés.append(binome)
    
    context = {
        'binomes': binomes_geolocalisés,
        'page_title': 'Carte des binômes',
        'total_binomes': len(binomes_geolocalisés),
    }
    
    return render(request, 'core/carte_binomes.html', context)


# ============================================================================
# 🗺️ CARTE des elèves et bénévoles en attente
# ============================================================================

def carte_enattente(request):
    """
    - Carte des élèves non accompagnés et des bénévoles disponibles
    """
    
    # Exemple : carte des élèves à accompagner
    eleves_a_accompagner = Eleve.objects.filter(
        statut='a_accompagner',
        latitude__isnull=False,    # Seulement ceux géolocalisés
        longitude__isnull=False
    )
    
    context = {
        'eleves': eleves_a_accompagner,
        'page_title': 'Élèves à accompagner',
        'total_eleves': eleves_a_accompagner.count(),
    }
    
    return render(request, 'core/carte_enattente.html', context)


# ============================================================================
# 📊 API - DONNÉES POUR LES CARTES (Format JSON)
# ============================================================================

def api_binomes_json(request):
    """
    API REST : Retourne les binômes au format JSON.
    
    Utile pour alimenter les cartes JavaScript dynamiquement.
    
    URL : /api/binomes/
    Returns : JSON
    """
    
    binomes = Binome.objects.filter(
        actif=True
    ).select_related('eleve', 'benevole')
    
    # Construire la liste de données
    data = []
    for binome in binomes:
        if (binome.eleve.latitude and binome.eleve.longitude and
            binome.benevole and binome.benevole.latitude and binome.benevole.longitude):
            
            data.append({
                'id': binome.id,
                'eleve': {
                    'nom': binome.eleve.nom,
                    'prenom': binome.eleve.prenom,
                    'classe': binome.eleve.classe,
                    'statut': binome.eleve.statut,
                    'latitude': binome.eleve.latitude,
                    'longitude': binome.eleve.longitude,
                    'arrondissement': binome.eleve.arrondissement,
                },
                'benevole': {
                    'nom': binome.benevole.nom,
                    'prenom': binome.benevole.prenom,
                    'latitude': binome.benevole.latitude,
                    'longitude': binome.benevole.longitude,
                    'arrondissement': binome.benevole.arrondissement,
                },
                'date_debut': binome.date_debut.isoformat(),
            })
    
    return JsonResponse({'binomes': data, 'count': len(data)})


def api_eleves_json(request):
    """
    API REST : Retourne tous les élèves au format JSON.
    
    URL : /api/eleves/
    """
    
    eleves = Eleve.objects.all()
    
    data = []
    for eleve in eleves:
        data.append({
            'id': eleve.id,
            'nom': eleve.nom,
            'prenom': eleve.prenom,
            'classe': eleve.classe,
            'statut': eleve.statut,
            'arrondissement': eleve.arrondissement,
            'latitude': eleve.latitude,
            'longitude': eleve.longitude,
        })
    
    return JsonResponse({'eleves': data, 'count': len(data)})


def api_benevoles_json(request):
    """
    API REST : Retourne tous les bénévoles au format JSON.
    
    URL : /api/benevoles/
    """
    
    benevoles = Benevole.objects.all()
    
    data = []
    for benevole in benevoles:
        data.append({
            'id': benevole.id,
            'nom': benevole.nom,
            'prenom': benevole.prenom,
            'email': benevole.email,
            'disponibilite': benevole.disponibilite,
            'arrondissement': benevole.arrondissement,
            'latitude': benevole.latitude,
            'longitude': benevole.longitude,
        })
    
    return JsonResponse({'benevoles': data, 'count': len(data)})


# ============================================================================
# 📋 LISTES (Optionnel - Pour afficher des listes HTML simples)
# ============================================================================

def liste_eleves(request):
    """Liste de tous les élèves (page HTML simple)."""
    
    eleves = Eleve.objects.all().order_by('nom', 'prenom')
    
    context = {
        'eleves': eleves,
        'page_title': 'Liste des élèves',
    }
    
    return render(request, 'core/liste_eleves.html', context)


def liste_benevoles(request):
    """Liste de tous les bénévoles (page HTML simple)."""
    
    benevoles = Benevole.objects.all().order_by('nom', 'prenom')
    
    context = {
        'benevoles': benevoles,
        'page_title': 'Liste des bénévoles',
    }
    
    return render(request, 'core/liste_benevoles.html', context)


# ============================================================================
# 🔍 DÉTAILS (Optionnel - Pages de détail individuelles)
# ============================================================================

def eleve_detail(request, pk):
    """
    Page de détail d'un élève.
    
    Args:
        pk (int) : Primary Key (ID) de l'élève
    """
    
    # get_object_or_404 : Récupère l'objet ou retourne une erreur 404
    eleve = get_object_or_404(Eleve, pk=pk)
    
    # Récupérer le binôme s'il existe
    try:
        binome = eleve.binome
    except Binome.DoesNotExist:
        binome = None
    
    context = {
        'eleve': eleve,
        'binome': binome,
        'page_title': f'{eleve.get_nom_complet()} - Détail',
    }
    
    return render(request, 'core/eleve_detail.html', context)


def benevole_detail(request, pk):
    """Page de détail d'un bénévole."""
    
    benevole = get_object_or_404(Benevole, pk=pk)
    
    # Récupérer tous les binômes du bénévole
    binomes = benevole.binomes.filter(actif=True)
    
    context = {
        'benevole': benevole,
        'binomes': binomes,
        'page_title': f'{benevole.get_nom_complet()} - Détail',
    }
    
    return render(request, 'core/benevole_detail.html', context)


# ============================================================================
# 🎓 NOTES D'APPRENTISSAGE
# ============================================================================

"""
📝 Anatomie d'une vue Django :

1. FONCTION DE BASE :
   def ma_vue(request):
       return render(request, 'template.html')

2. AVEC CONTEXTE :
   def ma_vue(request):
       data = Model.objects.all()
       context = {'data': data}
       return render(request, 'template.html', context)

3. AVEC PARAMÈTRES (depuis l'URL) :
   def ma_vue(request, id):
       obj = Model.objects.get(pk=id)
       return render(request, 'template.html', {'obj': obj})

4. API JSON :
   def ma_vue(request):
       data = {'key': 'value'}
       return JsonResponse(data)

🔧 Requêtes ORM courantes :

   # Tous les objets
   Model.objects.all()
   
   # Filtrer
   Model.objects.filter(field=value)
   
   # Exclure
   Model.objects.exclude(field=value)
   
   # Un seul objet
   Model.objects.get(pk=1)
   get_object_or_404(Model, pk=1)  # Avec gestion 404
   
   # Compter
   Model.objects.count()
   
   # Optimisation (éviter requêtes multiples)
   Model.objects.select_related('foreign_key_field')
   Model.objects.prefetch_related('many_to_many_field')

🎯 Décorateurs utiles :

   @login_required              # Protéger par authentification
   @require_http_methods(["GET", "POST"])  # Limiter les méthodes HTTP
   @cache_page(60 * 15)         # Cache la vue pendant 15 min

📚 Class-Based Views (alternative) :

   from django.views.generic import ListView
   
   class EleveListView(ListView):
       model = Eleve
       template_name = 'core/eleves.html'
       context_object_name = 'eleves'

🔗 Liens avec les URLs :
   views.py définit la LOGIQUE
   urls.py fait le LIEN entre URL et vue
   templates/ affiche le RÉSULTAT
"""
