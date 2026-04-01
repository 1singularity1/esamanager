"""
Commande Django pour importer les bénévoles depuis les fichiers CSV

Usage:
    python manage.py import_benevoles benevoles.csv candidats.csv
"""

from django.core.management.base import BaseCommand
from core.models import Benevole, Matiere
import csv
from datetime import datetime


class Command(BaseCommand):
    help = 'Importe les bénévoles depuis les fichiers CSV'

    def add_arguments(self, parser):
        parser.add_argument('benevoles_csv', type=str, help='Fichier CSV des bénévoles 2025-2026')
        parser.add_argument('candidats_csv', type=str, help='Fichier CSV des candidats à recontacter')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode test : affiche ce qui serait fait sans modifier la base de données'
        )

    def handle(self, *args, **options):
        benevoles_file = options['benevoles_csv']
        candidats_file = options['candidats_csv']
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING('🔍 MODE TEST - Aucune modification en base de données'))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        # ============================================================
        # IMPORT BÉNÉVOLES 2025-2026 (statut à déterminer plus tard)
        # ============================================================
        
        self.stdout.write(self.style.SUCCESS(f'\n📥 Import des bénévoles depuis {benevoles_file}'))
        
        try:
            with open(benevoles_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Nettoyer les noms de colonnes (BOM, espaces, etc.)
                reader.fieldnames = [name.strip().lstrip('\ufeff').lstrip('\ufbff') for name in reader.fieldnames]
                
                # DEBUG: Afficher les 5 premières colonnes
                self.stdout.write(self.style.WARNING(f'\n🐛 DEBUG: Premières colonnes du CSV:'))
                for i, col in enumerate(reader.fieldnames[:5]):
                    self.stdout.write(f'   [{i}] "{col}"')
                self.stdout.write(f'   → Première colonne utilisée pour le nom: "{reader.fieldnames[0]}"')
                self.stdout.write('')
                
                for row in reader:
                    try:
                        # Ignorer les lignes vides
                        if not row.get('Prénom') or not row.get('Mail'):
                            continue
                        
                        # Extraire les données
                        # La première colonne contient le nom
                        first_col_name = reader.fieldnames[0]
                        nom = row.get(first_col_name, '').strip()
                        
                        prenom = row.get('Prénom', '').strip()
                        email = row.get('Mail', '').strip().lower()
                        
                        # DEBUG pour Léane
                        if 'léane' in prenom.lower() or 'leane' in email:
                            self.stdout.write(self.style.WARNING(f'\n🐛 DEBUG Léane:'))
                            self.stdout.write(f'   first_col_name = "{first_col_name}"')
                            self.stdout.write(f'   row.get(first_col_name) = "{row.get(first_col_name, "RIEN")}"')
                            self.stdout.write(f'   nom après strip = "{nom}"')
                            self.stdout.write(f'   Toutes les valeurs de la ligne:')
                            for k, v in list(row.items())[:5]:
                                self.stdout.write(f'      "{k}" = "{v}"')
                            self.stdout.write('')
                        
                        # Ignorer si pas de prénom ou email
                        if not prenom or not email:
                            continue
                        
                        telephone = row.get('Mobile', '').strip()
                        arrondissement = row.get('Arr.', '').strip()
                        adresse = row.get('Adresse', '').strip()
                        profession = row.get('Profession', '').strip()
                        zone_geo = row.get('Zone géographique', '').strip()
                        
                        # Niveaux
                        primaire = bool(row.get('Primaire', '').strip())
                        college = bool(row.get('Collège', '').strip())
                        lycee = bool(row.get('Lycée', '').strip())
                        
                        # Documents administratifs
                        reunion_accueil_str = row.get('Réunion d\'accueil faite', '').strip()
                        volet_3_str = row.get('Volet 3 casier judiciaire', '').strip()
                        
                        # Si "0" ou vide, considérer comme False (pas fait)
                        reunion_accueil = reunion_accueil_str not in ['', '0']
                        volet_3 = self.parse_date(volet_3_str) if volet_3_str and volet_3_str != '0' else None
                        a_donne_photo = bool(row.get('photo', '').strip())
                        
                        # Commentaires
                        commentaires = row.get('Commentaires', '').strip()
                        divers = row.get('Divers', '').strip()
                        
                        # Créer ou mettre à jour le bénévole
                        # Statut provisoire : Disponible (sera mis à jour après import binômes)
                        
                        if dry_run:
                            # Mode test : vérifier si existe sans modifier
                            benevole = Benevole.objects.filter(email=email).first()
                            if benevole:
                                updated_count += 1
                                self.stdout.write(f'  🔄 Mettrait à jour : {prenom} {nom} ({email})')
                            else:
                                created_count += 1
                                self.stdout.write(f'  ✅ Créerait : {prenom} {nom} ({email})')
                                # Afficher pour vérifier que le nom est bien lu
                                if not nom:
                                    self.stdout.write(self.style.WARNING(f'      ⚠️  NOM VIDE détecté !'))
                                else:
                                    self.stdout.write(f'      → Nom: "{nom}"')
                        else:
                            # Mode réel : créer ou mettre à jour
                            
                            # D'abord, supprimer les doublons éventuels
                            existing = Benevole.objects.filter(email=email)
                            if existing.count() > 1:
                                # Garder le premier, supprimer les autres
                                to_keep = existing.first()
                                for duplicate in existing[1:]:
                                    duplicate.delete()
                                self.stdout.write(f'  🧹 Doublons supprimés pour {email}')
                            
                            # Vérifier si existe déjà
                            try:
                                benevole = Benevole.objects.get(email=email)
                                # EXISTE DÉJÀ : Ne mettre à jour QUE le statut
                                # SAUF s'il est déjà "Mentor" (a un binôme actif)
                                old_statut = benevole.statut
                                
                                if old_statut == 'Mentor':
                                    # Garder le statut Mentor (ne pas écraser)
                                    updated_count += 1
                                    self.stdout.write(f'  ↻ Statut préservé : {prenom} {nom} (Mentor)')
                                else:
                                    # Mettre à jour vers Disponible
                                    benevole.statut = 'Disponible'
                                    benevole.save(update_fields=['statut'])
                                    updated_count += 1
                                    if old_statut != 'Disponible':
                                        self.stdout.write(f'  🔄 Mis à jour statut : {prenom} {nom} ({old_statut} → Disponible)')
                                    else:
                                        self.stdout.write(f'  ↻ Statut inchangé : {prenom} {nom}')
                                
                            except Benevole.DoesNotExist:
                                # N'EXISTE PAS : Créer avec toutes les données du CSV
                                benevole = Benevole.objects.create(
                                    email=email,
                                    nom=nom,
                                    prenom=prenom,
                                    telephone=telephone,
                                    arrondissement=arrondissement,
                                    adresse=adresse,
                                    profession=profession,
                                    primaire=primaire,
                                    college=college,
                                    lycee=lycee,
                                    statut='Disponible',  # Provisoire
                                    reunion_accueil_faite=reunion_accueil,
                                    volet_3_casier_judiciaire=volet_3,
                                    a_donne_photo=a_donne_photo,
                                    commentaires=commentaires,
                                    divers=divers,
                                )
                                
                                created_count += 1
                                self.stdout.write(f'  ✅ Créé : {prenom} {nom}')
                    
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(f'  ❌ Erreur ligne {prenom} {nom}: {str(e)}'))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé : {benevoles_file}'))
            return
        
        # ============================================================
        # IMPORT CANDIDATS À RECONTACTER (statut = Candidat)
        # ============================================================
        
        self.stdout.write(self.style.SUCCESS(f'\n📥 Import des candidats depuis {candidats_file}'))
        
        try:
            with open(candidats_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [name.strip().lstrip('\ufeff').lstrip('\ufbff') for name in reader.fieldnames]
                
                for row in reader:
                    try:
                        # Ignorer les lignes vides ou les séparateurs d'année
                        first_col_name = reader.fieldnames[0]
                        nom = row.get(first_col_name, '').strip()
                        
                        prenom = row.get('Prénom', '').strip()
                        email = row.get('Mail', '').strip().lower()
                        
                        if not nom or not prenom or not email:
                            continue
                        
                        # Si la ligne contient juste une année (ex: "2023 - 2024"), ignorer
                        if '-' in nom and len(nom) < 15:
                            continue
                        
                        # Extraire les données
                        telephone = row.get('Mobile', '').strip()
                        arrondissement = row.get('Arr.', '').strip()
                        adresse = row.get('Adresse', '').strip()
                        zone_geo = row.get('Zone géographique', '').strip()
                        
                        # Niveaux
                        primaire = bool(row.get('Prim', '').strip() or row.get('C', '').strip())
                        college = bool(row.get('Coll', '').strip())
                        lycee = bool(row.get('Lycée', '').strip())
                        
                        # Commentaires
                        commentaires = row.get('Commentaires', '').strip()
                        infos_complementaires = row.get('Informations complémentaires', '').strip()
                        disponibilites = row.get('Disponibilités et compétences', '').strip()
                        
                        # Créer ou mettre à jour le candidat
                        
                        if dry_run:
                            # Mode test : vérifier si existe sans modifier
                            benevole = Benevole.objects.filter(email=email).first()
                            if benevole:
                                updated_count += 1
                                self.stdout.write(f'  🔄 Mettrait à jour candidat : {prenom} {nom} ({email})')
                            else:
                                created_count += 1
                                self.stdout.write(f'  ✅ Créerait candidat : {prenom} {nom} ({email})')
                                # Afficher pour vérifier que le nom est bien lu
                                if not nom:
                                    self.stdout.write(self.style.WARNING(f'      ⚠️  NOM VIDE détecté !'))
                                else:
                                    self.stdout.write(f'      → Nom: "{nom}"')
                        else:
                            # Mode réel : créer ou mettre à jour
                            
                            # D'abord, supprimer les doublons éventuels
                            existing = Benevole.objects.filter(email=email)
                            if existing.count() > 1:
                                # Garder le premier, supprimer les autres
                                to_keep = existing.first()
                                for duplicate in existing[1:]:
                                    duplicate.delete()
                                self.stdout.write(f'  🧹 Doublons supprimés pour {email}')
                            
                            # Vérifier si existe déjà
                            try:
                                benevole = Benevole.objects.get(email=email)
                                # EXISTE DÉJÀ : Ne mettre à jour QUE le statut
                                old_statut = benevole.statut
                                benevole.statut = 'Candidat'
                                benevole.save(update_fields=['statut'])
                                
                                updated_count += 1
                                if old_statut != 'Candidat':
                                    self.stdout.write(f'  🔄 Mis à jour statut candidat : {prenom} {nom} ({old_statut} → Candidat)')
                                else:
                                    self.stdout.write(f'  ↻ Statut inchangé candidat : {prenom} {nom}')
                                
                            except Benevole.DoesNotExist:
                                # N'EXISTE PAS : Créer avec toutes les données du CSV
                                benevole = Benevole.objects.create(
                                    email=email,
                                    nom=nom,
                                    prenom=prenom,
                                    telephone=telephone,
                                    arrondissement=arrondissement,
                                    adresse=adresse,
                                    primaire=primaire,
                                    college=college,
                                    lycee=lycee,
                                    statut='Candidat',
                                    commentaires=commentaires,
                                    divers=f"{infos_complementaires}\n{disponibilites}".strip(),
                                )
                                
                                created_count += 1
                                self.stdout.write(f'  ✅ Créé candidat : {prenom} {nom}')
                    
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(f'  ❌ Erreur : {str(e)}'))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé : {candidats_file}'))
            return
        
        # ============================================================
        # RÉSUMÉ
        # ============================================================
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Import terminé !'))
        self.stdout.write(f'  📊 Créés : {created_count}')
        self.stdout.write(f'  🔄 Mis à jour : {updated_count}')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Erreurs : {error_count}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING('⚠️  MODE TEST : Aucune donnée n\'a été modifiée'))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n💡 Note : Les statuts "Mentor" seront attribués lors de l\'import des binômes'
            ))
    
    def parse_date(self, date_str):
        """Parse une date au format DD/MM/YYYY ou DD/MM/YY"""
        if not date_str or date_str.strip() == '0':
            return None
        
        date_str = date_str.strip()
        
        # Essayer différents formats
        formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
