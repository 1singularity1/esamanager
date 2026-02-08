# 💾 Vue Django pour la sauvegarde automatique AJAX

"""
Ajouter cette vue dans core/views.py
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from .models import Eleve
import json

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
