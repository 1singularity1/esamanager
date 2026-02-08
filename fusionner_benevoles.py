"""
🔄 Script pour fusionner les fichiers de bénévoles

Ce script fusionne :
- benevoles_a_recontacter.csv (avec toutes les infos)
- benevoles_a_recontacter_geocoded.csv (avec coordonnées GPS)

Usage:
    python fusionner_benevoles.py
"""

import csv
import sys

def nettoyer_texte(texte):
    """Nettoie un texte"""
    if texte is None or texte == '':
        return ''
    return str(texte).strip()

def fusionner_benevoles():
    """Fusionne les deux fichiers CSV de bénévoles"""
    
    print("=" * 70)
    print("🔄 FUSION DES FICHIERS BÉNÉVOLES")
    print("=" * 70)
    print()
    
    # Fichiers
    fichier_original = 'benevoles_a_recontacter.csv'
    fichier_geocoded = 'benevoles_a_recontacter_geocoded.csv'
    fichier_sortie = 'benevoles_complet.csv'
    
    # Lire le fichier geocoded (avec coordonnées GPS)
    benevoles_geo = {}
    print("📍 Lecture du fichier avec coordonnées GPS...")
    
    with open(fichier_geocoded, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for ligne in reader:
            nom = nettoyer_texte(ligne.get('Nom', '')).upper()
            prenom = nettoyer_texte(ligne.get('Prénom', ''))
            
            if nom and prenom:
                cle = f"{nom}_{prenom}".upper()
                benevoles_geo[cle] = {
                    'latitude': nettoyer_texte(ligne.get('latitude', '')),
                    'longitude': nettoyer_texte(ligne.get('longitude', '')),
                    'telephone': nettoyer_texte(ligne.get('N° de téléphone', '')),
                    'specialites': nettoyer_texte(ligne.get('Spécialités', '')),
                    'date_dernier_contact': nettoyer_texte(ligne.get('Date du dernier contact', '')),
                }
    
    print(f"✅ {len(benevoles_geo)} bénévoles avec coordonnées GPS chargés")
    print()
    
    # Lire le fichier original et fusionner
    print("📋 Fusion des données...")
    print()
    
    lignes_fusionnees = []
    compteur_fusion = 0
    compteur_sans_geo = 0
    
    with open(fichier_original, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for ligne in reader:
            nom = nettoyer_texte(ligne.get('Nom', '')).upper()
            prenom = nettoyer_texte(ligne.get('Prénom', ''))
            
            # Ignorer les lignes vides ou d'en-tête
            if not nom or not prenom or '2023' in nom or '2024' in nom:
                continue
            
            # Créer la clé de recherche
            cle = f"{nom}_{prenom}".upper()
            
            # Fusionner avec les données GPS si disponibles
            donnees_fusionnees = {
                'Nom': nom.title(),
                'Prénom': prenom,
                'Adresse': nettoyer_texte(ligne.get('Adresse', '')),
                'Arrondissement': nettoyer_texte(ligne.get('Arr.', '')),
                'Mobile': nettoyer_texte(ligne.get('Mobile', '')),
                'Email': nettoyer_texte(ligne.get('Mail', '')),
                'Zone_geographique': nettoyer_texte(ligne.get('Zone géographique', '')),
                'Commentaires': nettoyer_texte(ligne.get('Commentaires', '')),
                'Informations_complementaires': nettoyer_texte(ligne.get('Informations complémentaires', '')),
                'Disponibilites_competences': nettoyer_texte(ligne.get('Disponibilités et compétences', '')),
                'Date_contact': nettoyer_texte(ligne.get('Date Contact', '')),
                'Origine_contact': nettoyer_texte(ligne.get('Origine du contact', '')),
            }
            
            # Ajouter les coordonnées GPS si disponibles
            if cle in benevoles_geo:
                geo = benevoles_geo[cle]
                donnees_fusionnees['latitude'] = geo['latitude']
                donnees_fusionnees['longitude'] = geo['longitude']
                
                # Compléter le téléphone si manquant
                if not donnees_fusionnees['Mobile'] and geo['telephone']:
                    donnees_fusionnees['Mobile'] = geo['telephone']
                
                # Ajouter les spécialités si disponibles
                if geo['specialites']:
                    if donnees_fusionnees['Disponibilites_competences']:
                        donnees_fusionnees['Disponibilites_competences'] += f" | {geo['specialites']}"
                    else:
                        donnees_fusionnees['Disponibilites_competences'] = geo['specialites']
                
                compteur_fusion += 1
                print(f"✅ {prenom} {nom} - Coordonnées GPS ajoutées")
            else:
                donnees_fusionnees['latitude'] = ''
                donnees_fusionnees['longitude'] = ''
                compteur_sans_geo += 1
                print(f"⚠️  {prenom} {nom} - Pas de coordonnées GPS")
            
            lignes_fusionnees.append(donnees_fusionnees)
    
    # Écrire le fichier de sortie
    print()
    print("💾 Écriture du fichier fusionné...")
    
    with open(fichier_sortie, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'Nom', 'Prénom', 'Adresse', 'Arrondissement', 'latitude', 'longitude',
            'Mobile', 'Email', 'Zone_geographique',
            'Commentaires', 'Informations_complementaires', 'Disponibilites_competences',
            'Date_contact', 'Origine_contact'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lignes_fusionnees)
    
    # Rapport final
    print()
    print("=" * 70)
    print("📊 RAPPORT DE FUSION")
    print("=" * 70)
    print(f"✅ Bénévoles avec coordonnées GPS : {compteur_fusion}")
    print(f"⚠️  Bénévoles sans coordonnées GPS : {compteur_sans_geo}")
    print(f"📋 Total de bénévoles : {len(lignes_fusionnees)}")
    print()
    print(f"📤 Fichier créé : {fichier_sortie}")
    print("=" * 70)
    print()
    print("✨ Fusion terminée !")
    print()
    print("🔜 Prochaine étape :")
    print("   python manage.py import_benevoles benevoles_complet.csv")


if __name__ == '__main__':
    try:
        fusionner_benevoles()
    except FileNotFoundError as e:
        print(f"❌ Erreur : Fichier introuvable - {e}")
        print()
        print("💡 Assurez-vous que les fichiers suivants sont présents :")
        print("   - benevoles_a_recontacter.csv")
        print("   - benevoles_a_recontacter_geocoded.csv")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        sys.exit(1)
