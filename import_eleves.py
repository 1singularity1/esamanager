"""
🎓 Script d'import des élèves depuis un fichier CSV

Ce script lit le fichier eleves_geocoded.csv et importe les élèves dans la base de données.

Usage :
    python manage.py shell < import_eleves.py
    
Ou :
    python manage.py shell
    >>> exec(open('import_eleves.py').read())
"""

import csv
import os
from core.models import Eleve

# ============================================================================
# 📁 CONFIGURATION
# ============================================================================

CSV_FILE = 'eleves_geocoded.csv'  # Nom du fichier CSV

# Mapping des statuts
STATUT_MAPPING = {
    'Accompagné': 'accompagne',
    'À accompagner': 'a_accompagner',
    'Accompagne': 'accompagne',
    'A accompagner': 'a_accompagner',
}

# ============================================================================
# 🔧 FONCTIONS UTILITAIRES
# ============================================================================

def nettoyer_texte(texte):
    """Nettoie un texte (supprime espaces superflus, None, etc.)"""
    if texte is None or texte == '':
        return ''
    return str(texte).strip()

def obtenir_statut(statut_csv):
    """Convertit le statut du CSV au format de la base de données"""
    statut_clean = nettoyer_texte(statut_csv)
    return STATUT_MAPPING.get(statut_clean, 'a_accompagner')

def obtenir_arrondissement(arr_csv):
    """Nettoie l'arrondissement (13001 → 1er, 13008 → 8e, etc.)"""
    arr = nettoyer_texte(arr_csv)
    
    # Si c'est un code postal (13001, 13008, etc.)
    if arr.startswith('13') and len(arr) == 5:
        numero = arr[3:]  # Récupère les 2 derniers chiffres
        if numero == '01':
            return '1er'
        else:
            return f"{int(numero)}e"
    
    return arr

def obtenir_float(valeur):
    """Convertit une valeur en float, retourne None si impossible"""
    try:
        val = nettoyer_texte(valeur)
        if val == '':
            return None
        return float(val)
    except (ValueError, TypeError):
        return None

# ============================================================================
# 📊 FONCTION D'IMPORT
# ============================================================================

def importer_eleves():
    """Import les élèves depuis le fichier CSV"""
    
    print("=" * 70)
    print("🎓 IMPORT DES ÉLÈVES DEPUIS CSV")
    print("=" * 70)
    print()
    
    # Vérifier que le fichier existe
    if not os.path.exists(CSV_FILE):
        print(f"❌ ERREUR : Le fichier '{CSV_FILE}' n'existe pas !")
        print(f"📂 Assurez-vous que le fichier est dans le dossier : {os.getcwd()}")
        return
    
    # Compteurs
    compteur_succes = 0
    compteur_erreurs = 0
    compteur_ignores = 0
    erreurs = []
    
    # Ouvrir et lire le fichier CSV
    with open(CSV_FILE, 'r', encoding='utf-8') as fichier:
        lecteur = csv.DictReader(fichier)
        
        print(f"📋 Colonnes détectées : {lecteur.fieldnames}\n")
        
        for numero_ligne, ligne in enumerate(lecteur, start=2):  # Start=2 car ligne 1 = header
            try:
                # Extraire les données
                nom = nettoyer_texte(ligne.get('Nom famille enfant', ''))
                prenom = nettoyer_texte(ligne.get('Prénom enfant', ''))
                classe = nettoyer_texte(ligne.get('Classe', ''))
                adresse = nettoyer_texte(ligne.get('Adresse enfant', ''))
                arrondissement = obtenir_arrondissement(ligne.get('Arr.', ''))
                statut = obtenir_statut(ligne.get('Statut', ''))
                latitude = obtenir_float(ligne.get('latitude'))
                longitude = obtenir_float(ligne.get('longitude'))
                
                # Validation : nom et prénom obligatoires
                if not nom or not prenom:
                    compteur_ignores += 1
                    erreurs.append(f"Ligne {numero_ligne} : Nom ou prénom manquant - ignoré")
                    continue
                
                # Vérifier si l'élève existe déjà (même nom + prénom)
                eleve_existe = Eleve.objects.filter(
                    nom__iexact=nom,
                    prenom__iexact=prenom
                ).exists()
                
                if eleve_existe:
                    compteur_ignores += 1
                    print(f"⏭️  Ligne {numero_ligne} : {prenom} {nom} existe déjà - ignoré")
                    continue
                
                # Créer l'élève
                eleve = Eleve.objects.create(
                    nom=nom,
                    prenom=prenom,
                    classe=classe,
                    adresse=adresse,
                    arrondissement=arrondissement,
                    statut=statut,
                    latitude=latitude,
                    longitude=longitude,
                )
                
                compteur_succes += 1
                print(f"✅ Ligne {numero_ligne} : {prenom} {nom} ({classe}) - importé")
                
            except Exception as e:
                compteur_erreurs += 1
                erreur_msg = f"Ligne {numero_ligne} : Erreur - {str(e)}"
                erreurs.append(erreur_msg)
                print(f"❌ {erreur_msg}")
    
    # ========================================================================
    # 📊 RAPPORT FINAL
    # ========================================================================
    
    print()
    print("=" * 70)
    print("📊 RAPPORT D'IMPORT")
    print("=" * 70)
    print(f"✅ Élèves importés avec succès : {compteur_succes}")
    print(f"⏭️  Élèves ignorés (doublons/invalides) : {compteur_ignores}")
    print(f"❌ Erreurs : {compteur_erreurs}")
    print(f"📋 Total de lignes traitées : {compteur_succes + compteur_erreurs + compteur_ignores}")
    print()
    
    # Afficher les erreurs détaillées
    if erreurs:
        print("⚠️  DÉTAILS DES ERREURS :")
        print("-" * 70)
        for erreur in erreurs[:10]:  # Afficher max 10 erreurs
            print(f"   {erreur}")
        if len(erreurs) > 10:
            print(f"   ... et {len(erreurs) - 10} autre(s) erreur(s)")
        print()
    
    # Statistiques finales
    print("📈 STATISTIQUES DE LA BASE DE DONNÉES :")
    print("-" * 70)
    print(f"   Total élèves : {Eleve.objects.count()}")
    print(f"   Élèves accompagnés : {Eleve.objects.filter(statut='accompagne').count()}")
    print(f"   Élèves à accompagner : {Eleve.objects.filter(statut='a_accompagner').count()}")
    print(f"   Élèves géolocalisés : {Eleve.objects.filter(latitude__isnull=False, longitude__isnull=False).count()}")
    print()
    print("=" * 70)
    print("✨ IMPORT TERMINÉ !")
    print("=" * 70)

# ============================================================================
# 🚀 EXÉCUTION
# ============================================================================

if __name__ == '__main__':
    importer_eleves()

# Si exécuté depuis le shell Django
try:
    importer_eleves()
except NameError:
    # Le script sera exécuté manuellement
    pass
