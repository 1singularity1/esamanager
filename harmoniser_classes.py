"""
🧹 Script pour harmoniser la colonne "Classe" dans le fichier CSV

Ce script nettoie et standardise les valeurs de la colonne Classe.

Usage:
    python harmoniser_classes.py eleves_geocoded.csv eleves_harmonise.csv
"""

import csv
import sys
import re

def harmoniser_classe(classe):
    """
    Harmonise la valeur d'une classe selon des règles de standardisation
    
    Règles :
    - CE1, CE2, CM1, CM2, CP → Restent tels quels
    - 6°, 6e, 6E, 6ème, "6° Pasteur" → "6e"
    - 5°, 5e, 5ème → "5e"
    - 4°, 4e, 4è → "4e"
    - 3°, 3e, 3ème → "3e"
    - 2°, 2de, 2e → "2de"
    - 1°, 1ere, 1e → "1re"
    - T, T°, Terminale → "Terminale"
    - CAP → "CAP"
    """
    
    if not classe or classe.strip() == '':
        return ''
    
    classe = classe.strip()
    
    # Primaire - garder tel quel
    primaire = ['CP', 'CE1', 'CE2', 'CM1', 'CM2']
    for p in primaire:
        if p in classe.upper():
            return p
    
    # Collège
    # 6e
    if re.search(r'6[°eèE]?', classe, re.IGNORECASE):
        return '6e'
    
    # 5e
    if re.search(r'5[°eèE]?', classe, re.IGNORECASE):
        return '5e'
    
    # 4e
    if re.search(r'4[°eèE]?', classe, re.IGNORECASE):
        return '4e'
    
    # 3e
    if re.search(r'3[°eèE]?', classe, re.IGNORECASE):
        return '3e'
    
    # Lycée
    # 2de
    if re.search(r'2[°de]*', classe, re.IGNORECASE):
        return '2de'
    
    # 1re
    if re.search(r'1[°ere]*', classe, re.IGNORECASE):
        return '1re'
    
    # Terminale
    if re.search(r'T[°erminale]*', classe, re.IGNORECASE):
        return 'Terminale'
    
    # CAP
    if 'CAP' in classe.upper():
        return 'CAP'
    
    # ULIS (Unité Localisée pour l'Inclusion Scolaire)
    if 'ULIS' in classe.upper():
        return 'ULIS'
    
    # Si rien ne correspond, retourner la valeur originale
    return classe


def harmoniser_csv(fichier_entree, fichier_sortie):
    """Harmonise le fichier CSV"""
    
    print("=" * 70)
    print("🧹 HARMONISATION DES CLASSES")
    print("=" * 70)
    print(f"📥 Fichier d'entrée : {fichier_entree}")
    print(f"📤 Fichier de sortie : {fichier_sortie}")
    print()
    
    stats = {}
    lignes_traitees = 0
    
    with open(fichier_entree, 'r', encoding='utf-8') as f_in:
        with open(fichier_sortie, 'w', encoding='utf-8', newline='') as f_out:
            reader = csv.DictReader(f_in)
            
            # Écrire le header
            writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for ligne in reader:
                classe_originale = ligne.get('Classe', '')
                classe_harmonisee = harmoniser_classe(classe_originale)
                
                # Statistiques
                if classe_originale and classe_originale != classe_harmonisee:
                    if classe_originale not in stats:
                        stats[classe_originale] = classe_harmonisee
                
                # Mettre à jour la ligne
                ligne['Classe'] = classe_harmonisee
                writer.writerow(ligne)
                
                lignes_traitees += 1
    
    # Afficher les transformations
    print("📊 TRANSFORMATIONS EFFECTUÉES :")
    print("-" * 70)
    if stats:
        for original, harmonise in sorted(stats.items()):
            print(f"   {original:30} → {harmonise}")
    else:
        print("   Aucune transformation nécessaire")
    
    print()
    print("=" * 70)
    print(f"✅ {lignes_traitees} lignes traitées")
    print(f"📤 Fichier créé : {fichier_sortie}")
    print("=" * 70)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python harmoniser_classes.py fichier_entree.csv fichier_sortie.csv")
        sys.exit(1)
    
    fichier_entree = sys.argv[1]
    fichier_sortie = sys.argv[2]
    
    harmoniser_csv(fichier_entree, fichier_sortie)
