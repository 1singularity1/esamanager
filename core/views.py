"""
🎓 VIEWS.PY - Vues de l'application CORE
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from .models import Eleve, Benevole, Binome
import json


# ============================================================================
# 🏠 PAGE D'ACCUEIL
# ============================================================================

def home(request):
    """Page d'accueil de l'application"""
    # Récupérer quelques statistiques pour l'affichage
    stats = {
        'total_eleves': Eleve.objects.count(),
        'eleves_accompagnes': Eleve.objects.filter(statut='accompagne').count(),
        'total_benevoles': Benevole.objects.count(),
        'benevoles_disponibles': Benevole.objects.filter(statut='Mentor').count(),  # ← MAJUSCULE !
        'total_binomes': Binome.objects.filter(actif=True).count(),
    }
    
    context = {
        'stats': stats,
        'page_title': 'ESA Manager - Accueil',
    }
    return render(request, 'core/index.html', context)


# ============================================================================
# 🗺️ CARTES INTERACTIVES
# ============================================================================

def carte_binomes(request):
    """
    Vue de la carte interactive des binômes élèves-bénévoles.
    
    Charge tous les binômes actifs avec leurs coordonnées GPS
    et les affiche sur une carte Leaflet.
    """
    
    # Récupérer tous les binômes actifs
    binomes = Binome.objects.filter(actif=True).select_related('eleve', 'benevole')
    
    # Compter pour les stats
    total_binomes = binomes.count()
    
    context = {
        'total_binomes': total_binomes,
        'page_title': 'Carte des Binômes',
    }
    
    return render(request, 'core/carte_binomes.html', context)


def carte_enattente(request):
    """Carte des élèves en attente"""
    return render(request, 'core/carte_enattente.html')


# ============================================================================
# 📊 API JSON
# ============================================================================

def api_binomes_json(request):
    """
    API JSON qui retourne tous les binômes actifs pour la carte.
    
    Format de retour :
    {
        "binomes": [
            {
                "id": 1,
                "eleve": {
                    "id": 5,
                    "nom": "Dupont",
                    "prenom": "Jean",
                    "classe": "CE2",
                    "latitude": 43.2965,
                    "longitude": 5.3698
                },
                "benevole": {
                    "id": 12,
                    "nom": "Martin",
                    "prenom": "Sophie",
                    "latitude": 43.2617,
                    "longitude": 5.3792
                },
                "date_debut": "2024-09-01",
                "actif": true
            },
            ...
        ],
        "count": 75
    }
    """
    
    # Récupérer les binômes actifs avec les relations
    binomes = Binome.objects.filter(actif=True).select_related('eleve', 'benevole')
    
    data = []
    for binome in binomes:
        # Vérifier que l'élève et le bénévole ont des coordonnées
        if binome.eleve.latitude and binome.eleve.longitude and \
           binome.benevole.latitude and binome.benevole.longitude:
            
            data.append({
                'id': binome.id,
                'eleve': {
                    'id': binome.eleve.id,
                    'nom': binome.eleve.nom,
                    'prenom': binome.eleve.prenom,
                    'arrondissement': binome.eleve.arrondissement,
                    'classe': binome.eleve.classe,
                    'latitude': binome.eleve.latitude,
                    'longitude': binome.eleve.longitude,
                },
                'benevole': {
                    'id': binome.benevole.id,
                    'nom': binome.benevole.nom,
                    'prenom': binome.benevole.prenom,
                    'arrondissement': binome.benevole.code_postal,
                    'ville' : binome.benevole.ville,
                    'latitude': binome.benevole.latitude,
                    'longitude': binome.benevole.longitude,
                },
                'date_debut': binome.date_debut.isoformat() if binome.date_debut else None,
                'actif': binome.actif,
            })
    
    return JsonResponse({'binomes': data, 'count': len(data)})


def api_eleves_json(request):
    """API JSON pour les élèves"""
    eleves = Eleve.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    data = []
    for eleve in eleves:
        data.append({
            'id': eleve.id,
            'nom': eleve.nom,
            'prenom': eleve.prenom,
            'classe': eleve.classe,
            'latitude': eleve.latitude,
            'longitude': eleve.longitude,
            'arrondissement': eleve.arrondissement,
            'statut': eleve.get_statut_display(),
        })
    
    return JsonResponse(data, safe=False)


def api_benevoles_json(request):
    """API JSON pour les bénévoles"""
    benevoles = Benevole.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    data = []
    for benevole in benevoles:
        data.append({
            'id': benevole.id,
            'nom': benevole.nom,
            'prenom': benevole.prenom,
            'latitude': benevole.latitude,
            'longitude': benevole.longitude,
            'arrondissement': benevole.arrondissement,
            'disponibilite': benevole.get_disponibilite_display(),
        })
    
    return JsonResponse(data, safe=False)


# ============================================================================
# 📋 LISTES
# ============================================================================

def liste_eleves(request):
    """Liste de tous les élèves"""
    eleves = Eleve.objects.all().order_by('nom', 'prenom')
    context = {
        'eleves': eleves,
    }
    return render(request, 'core/liste_eleves.html', context)


def liste_benevoles(request):
    """Liste de tous les bénévoles"""
    benevoles = Benevole.objects.all().order_by('nom', 'prenom')
    context = {
        'benevoles': benevoles,
    }
    return render(request, 'core/liste_benevoles.html', context)


# ============================================================================
# 🔍 DÉTAILS
# ============================================================================

def eleve_detail(request, pk):
    """Page de détail d'un élève"""
    eleve = get_object_or_404(Eleve, pk=pk)
    context = {
        'eleve': eleve,
    }
    return render(request, 'core/eleve_detail.html', context)


def benevole_detail(request, pk):
    """Page de détail d'un bénévole"""
    benevole = get_object_or_404(Benevole, pk=pk)
    context = {
        'benevole': benevole,
    }
    return render(request, 'core/benevole_detail.html', context)


# ============================================================================
# 💾 AUTOSAVE (Sauvegarde automatique)
# ============================================================================

@staff_member_required
@require_POST
def autosave_eleve(request):
    """
    Sauvegarde automatique d'un élève en mode brouillon.
    Appelée par AJAX toutes les 30 secondes.
    """
    try:
        data = json.loads(request.body)
        eleve_id = data.get('id')
        
        # Si pas d'ID, créer un nouvel élève
        if eleve_id:
            eleve = Eleve.objects.get(id=eleve_id)
        else:
            eleve = Eleve()
        
        # Mettre à jour les champs (sans validation stricte)
        eleve.nom = data.get('nom', '')
        eleve.prenom = data.get('prenom', '')
        eleve.telephone = data.get('telephone', '')
        eleve.nom_parent = data.get('nom_parent', '')
        eleve.prenom_parent = data.get('prenom_parent', '')
        eleve.telephone_parent = data.get('telephone_parent', '')
        eleve.classe = data.get('classe', '')
        eleve.etablissement = data.get('etablissement', '')
        eleve.ville = data.get('ville', '')
        eleve.code_postal = data.get('code_postal', '')
        eleve.numero_rue = data.get('numero_rue', '')
        eleve.adresse = data.get('adresse', '')
        eleve.arrondissement = data.get('arrondissement', '')
        eleve.statut = data.get('statut', 'a_accompagner')
        eleve.informations_complementaires = data.get('informations_complementaires', '')
        
        # Coordonnées GPS
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude:
            try:
                eleve.latitude = float(latitude)
            except (ValueError, TypeError):
                pass
        if longitude:
            try:
                eleve.longitude = float(longitude)
            except (ValueError, TypeError):
                pass
        
        # IMPORTANT : Marquer comme brouillon
        eleve.statut_saisie = 'brouillon'
        
        # Sauvegarder sans validation stricte
        eleve.save()
        
        return JsonResponse({
            'success': True,
            'id': eleve.id,
            'message': 'Brouillon sauvegardé automatiquement'
        })
        
    except Eleve.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Élève introuvable'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
@require_POST
def validate_eleve(request):
    """
    Marque un élève comme complet (validé).
    Appelée quand l'utilisateur clique sur "Enregistrer".
    """
    try:
        data = json.loads(request.body)
        eleve_id = data.get('id')
        
        if not eleve_id:
            return JsonResponse({
                'success': False,
                'error': 'ID manquant'
            }, status=400)
        
        eleve = Eleve.objects.get(id=eleve_id)
        eleve.statut_saisie = 'complet'
        eleve.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Fiche validée'
        })
        
    except Eleve.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Élève introuvable'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
