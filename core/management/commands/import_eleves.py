"""
🎓 Commande Django pour importer des élèves depuis un fichier CSV

Cette commande permet d'importer des élèves depuis un fichier CSV dans la base de données.

Usage :
    python manage.py import_eleves chemin/vers/fichier.csv
    
Exemples :
    python manage.py import_eleves eleves_geocoded.csv
    python manage.py import_eleves /chemin/complet/vers/fichier.csv
"""

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from core.models import Eleve


class Command(BaseCommand):
    help = 'Importe des élèves depuis un fichier CSV'

    def add_arguments(self, parser):
        """Ajoute les arguments de la commande"""
        parser.add_argument(
            'csv_file',
            type=str,
            help='Chemin vers le fichier CSV à importer'
        )

    def handle(self, *args, **options):
        """Exécute la commande d'import"""
        csv_file = options['csv_file']
        
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("🎓 IMPORT DES ÉLÈVES DEPUIS CSV"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"📁 Fichier : {csv_file}\n")
        
        # Vérifier que le fichier existe
        if not os.path.exists(csv_file):
            raise CommandError(f"❌ Le fichier '{csv_file}' n'existe pas !")
        
        # Compteurs
        compteur_succes = 0
        compteur_erreurs = 0
        compteur_ignores = 0
        erreurs = []
        
        # Mapping des statuts
        STATUT_MAPPING = {
            'Accompagné': 'accompagne',
            'À accompagner': 'a_accompagner',
            'Accompagne': 'accompagne',
            'A accompagner': 'a_accompagner',
        }
        
        # Ouvrir et lire le fichier CSV
        with open(csv_file, 'r', encoding='utf-8') as fichier:
            lecteur = csv.DictReader(fichier)
            
            self.stdout.write(f"📋 Colonnes détectées : {lecteur.fieldnames}\n")
            
            for numero_ligne, ligne in enumerate(lecteur, start=2):
                try:
                    # Extraire les données
                    nom = self.nettoyer_texte(ligne.get('Nom famille enfant', ''))
                    prenom = self.nettoyer_texte(ligne.get('Prénom enfant', ''))
                    classe = self.nettoyer_texte(ligne.get('Classe', ''))
                    adresse = self.nettoyer_texte(ligne.get('Adresse enfant', ''))
                    arrondissement = self.obtenir_arrondissement(ligne.get('Arr.', ''))
                    statut = self.obtenir_statut(ligne.get('Statut', ''), STATUT_MAPPING)
                    latitude = self.obtenir_float(ligne.get('latitude'))
                    longitude = self.obtenir_float(ligne.get('longitude'))
                    
                    # Validation : nom et prénom obligatoires
                    if not nom or not prenom:
                        compteur_ignores += 1
                        erreurs.append(f"Ligne {numero_ligne} : Nom ou prénom manquant - ignoré")
                        continue
                    
                    # Vérifier si l'élève existe déjà
                    eleve_existe = Eleve.objects.filter(
                        nom__iexact=nom,
                        prenom__iexact=prenom
                    ).exists()
                    
                    if eleve_existe:
                        compteur_ignores += 1
                        self.stdout.write(f"⏭️  Ligne {numero_ligne} : {prenom} {nom} existe déjà - ignoré")
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
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Ligne {numero_ligne} : {prenom} {nom} ({classe}) - importé")
                    )
                    
                except Exception as e:
                    compteur_erreurs += 1
                    erreur_msg = f"Ligne {numero_ligne} : Erreur - {str(e)}"
                    erreurs.append(erreur_msg)
                    self.stdout.write(self.style.ERROR(f"❌ {erreur_msg}"))
        
        # ====================================================================
        # 📊 RAPPORT FINAL
        # ====================================================================
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("📊 RAPPORT D'IMPORT"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"✅ Élèves importés avec succès : {compteur_succes}")
        self.stdout.write(f"⏭️  Élèves ignorés (doublons/invalides) : {compteur_ignores}")
        self.stdout.write(f"❌ Erreurs : {compteur_erreurs}")
        self.stdout.write(f"📋 Total de lignes traitées : {compteur_succes + compteur_erreurs + compteur_ignores}\n")
        
        # Afficher les erreurs détaillées
        if erreurs:
            self.stdout.write(self.style.WARNING("⚠️  DÉTAILS DES ERREURS :"))
            self.stdout.write("-" * 70)
            for erreur in erreurs[:10]:
                self.stdout.write(f"   {erreur}")
            if len(erreurs) > 10:
                self.stdout.write(f"   ... et {len(erreurs) - 10} autre(s) erreur(s)\n")
        
        # Statistiques finales
        self.stdout.write("📈 STATISTIQUES DE LA BASE DE DONNÉES :")
        self.stdout.write("-" * 70)
        self.stdout.write(f"   Total élèves : {Eleve.objects.count()}")
        self.stdout.write(f"   Élèves accompagnés : {Eleve.objects.filter(statut='accompagne').count()}")
        self.stdout.write(f"   Élèves à accompagner : {Eleve.objects.filter(statut='a_accompagner').count()}")
        self.stdout.write(f"   Élèves géolocalisés : {Eleve.objects.filter(latitude__isnull=False, longitude__isnull=False).count()}\n")
        
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("✨ IMPORT TERMINÉ !"))
        self.stdout.write("=" * 70)
    
    # ========================================================================
    # 🔧 MÉTHODES UTILITAIRES
    # ========================================================================
    
    def nettoyer_texte(self, texte):
        """Nettoie un texte (supprime espaces superflus, None, etc.)"""
        if texte is None or texte == '':
            return ''
        return str(texte).strip()
    
    def obtenir_statut(self, statut_csv, mapping):
        """Convertit le statut du CSV au format de la base de données"""
        statut_clean = self.nettoyer_texte(statut_csv)
        return mapping.get(statut_clean, 'a_accompagner')
    
    def obtenir_arrondissement(self, arr_csv):
        """Nettoie l'arrondissement (13001 → 1er, 13008 → 8e, etc.)"""
        arr = self.nettoyer_texte(arr_csv)
        
        # Si c'est un code postal (13001, 13008, etc.)
        if arr.startswith('13') and len(arr) == 5:
            numero = arr[3:]  # Récupère les 2 derniers chiffres
            if numero == '01':
                return '1er'
            else:
                return f"{int(numero)}e"
        
        return arr
    
    def obtenir_float(self, valeur):
        """Convertit une valeur en float, retourne None si impossible"""
        try:
            val = self.nettoyer_texte(valeur)
            if val == '':
                return None
            return float(val)
        except (ValueError, TypeError):
            return None
