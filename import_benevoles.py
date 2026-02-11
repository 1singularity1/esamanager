#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'import/mise à jour des bénévoles depuis le CSV fusionné

Utilisation:
    python manage.py shell < import_benevoles.py

Ou:
    python manage.py shell
    >>> exec(open('import_benevoles.py').read())
"""

import csv
import sys
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.contrib.auth.models import User
from core.models import Benevole

def convert_bool(value):
    """Convertit une valeur en booléen"""
    if not value or value.strip() == '':
        return False
    value_lower = str(value).strip().lower()
    return value_lower in ['oui', 'yes', 'true', '1', 'o', 'y']

def convert_decimal(value):
    """Convertit une valeur en Decimal pour latitude/longitude"""
    if not value or value.strip() == '':
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None

def import_benevoles(csv_file_path):
    """
    Importe ou met à jour les bénévoles depuis le CSV
    """
    
    stats = {
        'total': 0,
        'created': 0,
        'updated': 0,
        'errors': 0,
        'skipped': 0
    }
    
    errors = []
    
    print("=" * 80)
    print("IMPORT DES BÉNÉVOLES")
    print("=" * 80)
    print(f"\nLecture du fichier: {csv_file_path}")
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                stats['total'] += 1
                
                try:
                    nom = row.get('Nom', '').strip()
                    prenom = row.get('Prénom', '').strip()
                    
                    if not nom or not prenom:
                        stats['skipped'] += 1
                        errors.append(f"Ligne {row_num}: Nom ou prénom manquant")
                        continue
                    
                    # Chercher si le bénévole existe déjà (par nom + prénom)
                    benevole, created = Benevole.objects.get_or_create(
                        nom=nom,
                        prenom=prenom,
                        defaults={}
                    )
                    
                    # Mise à jour des champs
                    benevole.statut = row.get('Statut', '').strip() or 'Candidat'
                    benevole.adresse = row.get('Adresse', '').strip()
                    benevole.code_postal = row.get('Code postal', '').strip()
                    benevole.ville = row.get('Ville', '').strip()
                    benevole.email = row.get('Email', '').strip()
                    benevole.telephone = row.get('Téléphone', '').strip()
                    benevole.profession = row.get('Profession', '').strip()
                    benevole.matieres = row.get('Matières', '').strip()
                    benevole.zone_geographique = row.get('Zone géographique', '').strip()
                    benevole.moyen_deplacement = row.get('Moyen de déplacement', '').strip()
                    benevole.commentaires = row.get('Commentaires', '').strip()
                    benevole.divers = row.get('Divers', '').strip()
                    
                    # Coordonnées GPS
                    benevole.latitude = convert_decimal(row.get('latitude', ''))
                    benevole.longitude = convert_decimal(row.get('longitude', ''))
                    
                    # Champs booléens
                    benevole.est_responsable = convert_bool(row.get('est_responsable', ''))
                    benevole.primaire = convert_bool(row.get('Primaire', ''))
                    benevole.college = convert_bool(row.get('Collège', ''))
                    benevole.lycee = convert_bool(row.get('Lycée', ''))
                    benevole.a_donne_photo = convert_bool(row.get('a_donne_photo', ''))
                    benevole.est_ajoute_au_groupe_whatsapp = convert_bool(row.get('est_ajoute_au groupe_WhatsApp', ''))
                    benevole.fichier = convert_bool(row.get('fichier', ''))
                    benevole.outlook = convert_bool(row.get('Outlook', ''))
                    benevole.extranet = convert_bool(row.get('Extranet', ''))
                    benevole.reunion_accueil_faite = convert_bool(row.get("Réunion d'accueil faite", ''))
                    benevole.volet_3_casier_judiciaire = convert_bool(row.get('Volet 3 casier judiciaire', ''))
                    
                    # NOUVEAUX CHAMPS (spécifiques aux candidats)
                    benevole.origine_contact = row.get('Origine_contact', '').strip()
                    benevole.date_contact = row.get('Date_contact', '').strip()
                    benevole.informations_complementaires = row.get('Informations_complementaires', '').strip()
                    benevole.disponibilites_competences = row.get('Disponibilites_competences', '').strip()
                    
                    benevole.save()
                    
                    if created:
                        stats['created'] += 1
                        action = "CRÉÉ"
                    else:
                        stats['updated'] += 1
                        action = "MIS À JOUR"
                    
                    if stats['total'] % 10 == 0:
                        print(f"  Traité: {stats['total']} lignes...", end='\r')
                
                except Exception as e:
                    stats['errors'] += 1
                    error_msg = f"Ligne {row_num} ({nom} {prenom}): {str(e)}"
                    errors.append(error_msg)
                    print(f"\n⚠️  ERREUR - {error_msg}")
    
    # Affichage du rapport
    print("\n\n" + "=" * 80)
    print("RAPPORT D'IMPORT")
    print("=" * 80)
    print(f"\n📊 STATISTIQUES:")
    print(f"  • Total de lignes traitées:     {stats['total']}")
    print(f"  • Bénévoles créés:              {stats['created']}")
    print(f"  • Bénévoles mis à jour:         {stats['updated']}")
    print(f"  • Lignes ignorées (incomplètes): {stats['skipped']}")
    print(f"  • Erreurs:                       {stats['errors']}")
    
    if errors:
        print(f"\n⚠️  ERREURS DÉTAILLÉES ({len(errors)}):")
        for error in errors[:10]:  # Afficher max 10 erreurs
            print(f"  • {error}")
        if len(errors) > 10:
            print(f"  ... et {len(errors) - 10} autres erreurs")
    
    print("\n" + "=" * 80)
    if stats['errors'] == 0:
        print("✅ Import terminé avec succès!")
    else:
        print("⚠️  Import terminé avec des erreurs")
    print("=" * 80)
    
    return stats, errors


# Exécution automatique
# Détection du chemin du CSV
import os
possible_paths = [
    'benevoles_fusionnes.csv',
    '../data/benevoles_fusionnes.csv',
    '/mnt/user-data/outputs/benevoles_fusionnes.csv',
]

csv_path = None
for path in possible_paths:
    if os.path.exists(path):
        csv_path = path
        break

if csv_path:
    print(f"\n📂 Fichier trouvé: {csv_path}")
    stats, errors = import_benevoles(csv_path)
else:
    print("\n❌ ERREUR: Fichier benevoles_fusionnes.csv introuvable")
    print("Chemins testés:")
    for path in possible_paths:
        print(f"  • {path}")
    print("\nPour importer manuellement:")
    print("  stats, errors = import_benevoles('chemin/vers/benevoles_fusionnes.csv')")
