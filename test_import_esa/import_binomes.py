"""
Commande Django pour importer les binômes depuis les fichiers CSV

Usage:
    python manage.py import_binomes enfants_aides.csv binomes_david.csv binomes_clara.csv binomes_georges.csv binomes_bernadette.csv binomes_sylvie.csv
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Eleve, Benevole, Binome
import csv
from datetime import datetime
import os


class Command(BaseCommand):
    help = 'Importe les binômes depuis les fichiers CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_files', nargs='+', type=str, help='Fichiers CSV des binômes')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode test : affiche ce qui serait fait sans modifier la base de données'
        )

    def handle(self, *args, **options):
        csv_files = options['csv_files']
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING('🔍 MODE TEST - Aucune modification en base de données'))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        # Créer les utilisateurs co-responsables si nécessaire
        coresponsables = {
            'david': self.get_or_create_user('David'),
            'clara': self.get_or_create_user('Clara'),
            'georges': self.get_or_create_user('Georges'),
            'bernadette': self.get_or_create_user('Bernadette'),
            'sylvie': self.get_or_create_user('Sylvie'),
        }
        
        # ============================================================
        # IMPORT DE CHAQUE FICHIER BINÔME
        # ============================================================
        
        for csv_file in csv_files:
            # Déterminer le co-responsable depuis le nom du fichier
            filename = os.path.basename(csv_file).lower()
            coresponsable_user = None
            
            for name, user in coresponsables.items():
                if name in filename:
                    coresponsable_user = user
                    break
            
            self.stdout.write(self.style.SUCCESS(f'\n📥 Import des binômes depuis {csv_file}'))
            if coresponsable_user:
                self.stdout.write(f'   👤 Co-responsable : {coresponsable_user.username}')
            
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    reader.fieldnames = [name.strip() for name in reader.fieldnames]
                    
                    for row in reader:
                        try:
                            # ====================================================
                            # IDENTIFIER LE BÉNÉVOLE
                            # ====================================================
                            
                            nom_benevole = row.get('Nom bénévole', '') or row.get('Nom', '')
                            prenom_benevole = row.get('Prénom bénévole', '') or row.get('Prénom', '')
                            email_benevole = row.get('Mail Bénévole', '') or row.get('Mail', '')
                            
                            nom_benevole = nom_benevole.strip()
                            prenom_benevole = prenom_benevole.strip()
                            email_benevole = email_benevole.strip().lower()
                            
                            if not nom_benevole or not prenom_benevole:
                                continue
                            
                            # Chercher le bénévole (priorité email, sinon nom+prénom)
                            benevole = None
                            if email_benevole:
                                try:
                                    benevole = Benevole.objects.get(email=email_benevole)
                                except Benevole.DoesNotExist:
                                    pass
                            
                            if not benevole:
                                try:
                                    benevole = Benevole.objects.get(
                                        nom__iexact=nom_benevole,
                                        prenom__iexact=prenom_benevole
                                    )
                                except Benevole.DoesNotExist:
                                    self.stdout.write(self.style.WARNING(
                                        f'  ⚠️  Bénévole non trouvé : {prenom_benevole} {nom_benevole}'
                                    ))
                                    continue
                                except Benevole.MultipleObjectsReturned:
                                    self.stdout.write(self.style.WARNING(
                                        f'  ⚠️  Plusieurs bénévoles trouvés : {prenom_benevole} {nom_benevole}'
                                    ))
                                    benevole = Benevole.objects.filter(
                                        nom__iexact=nom_benevole,
                                        prenom__iexact=prenom_benevole
                                    ).first()
                            
                            # ====================================================
                            # IDENTIFIER L'ÉLÈVE
                            # ====================================================
                            
                            nom_enfant = row.get('Nom enfant', '') or row.get('Nom famille enfant', '')
                            prenom_enfant = row.get('Prénom enfant', '')
                            tel_famille = row.get('Tél famille', '') or row.get('Mobile', '')
                            
                            nom_enfant = nom_enfant.strip()
                            prenom_enfant = prenom_enfant.strip()
                            tel_famille = tel_famille.strip()
                            
                            if not nom_enfant or not prenom_enfant:
                                continue
                            
                            # Chercher l'élève (clé: nom + prenom + telephone_parent)
                            eleve = None
                            try:
                                eleve = Eleve.objects.get(
                                    nom=nom_enfant,
                                    prenom=prenom_enfant,
                                    telephone_parent=tel_famille
                                )
                            except Eleve.DoesNotExist:
                                # Si pas trouvé avec le tel, essayer sans
                                try:
                                    eleve = Eleve.objects.get(
                                        nom=nom_enfant,
                                        prenom=prenom_enfant
                                    )
                                except (Eleve.DoesNotExist, Eleve.MultipleObjectsReturned):
                                    self.stdout.write(self.style.WARNING(
                                        f'  ⚠️  Élève non trouvé : {prenom_enfant} {nom_enfant}'
                                    ))
                                    continue
                            
                            # ====================================================
                            # CRÉER/METTRE À JOUR LE BINÔME
                            # ====================================================
                            
                            # Date de début
                            date_contrat = row.get('Date contrat', '') or row.get('date contrat', '')
                            date_debut = self.parse_date(date_contrat)
                            if not date_debut:
                                date_debut = datetime.now().date()
                            
                            # Notes
                            commentaires = row.get('Commentaires-observations', '') or row.get('Nouvelles bénévole', '') or ''
                            aide_demandee = row.get('Aide demandée', '') or row.get('besoins', '') or ''
                            infos_diverses = row.get('Informations diverses', '') or ''
                            
                            notes = f"{commentaires}\n{aide_demandee}\n{infos_diverses}".strip()
                            
                            # Créer ou mettre à jour le binôme
                            
                            if dry_run:
                                # Mode test : vérifier si existe sans modifier
                                try:
                                    binome = Binome.objects.get(eleve=eleve)
                                    updated_count += 1
                                    self.stdout.write(f'  🔄 Mettrait à jour : {prenom_enfant} {nom_enfant} ↔ {prenom_benevole} {nom_benevole}')
                                    if coresponsable_user:
                                        self.stdout.write(f'      → Co-responsable : {coresponsable_user.username}')
                                    self.stdout.write(f'      → Statut bénévole : Mentor')
                                    self.stdout.write(f'      → Statut élève : accompagne')
                                except Binome.DoesNotExist:
                                    created_count += 1
                                    self.stdout.write(f'  ✅ Créerait : {prenom_enfant} {nom_enfant} ↔ {prenom_benevole} {nom_benevole}')
                                    if coresponsable_user:
                                        self.stdout.write(f'      → Co-responsable : {coresponsable_user.username}')
                                    self.stdout.write(f'      → Statut bénévole : Mentor')
                                    self.stdout.write(f'      → Statut élève : accompagne')
                            else:
                                # Mode réel : créer ou mettre à jour
                                binome, created = Binome.objects.update_or_create(
                                    eleve=eleve,
                                    defaults={
                                        'benevole': benevole,
                                        'date_debut': date_debut,
                                        'actif': True,
                                        'notes': notes,
                                    }
                                )
                                
                                # Mettre à jour le co-responsable de l'élève
                                if coresponsable_user:
                                    eleve.co_responsable = coresponsable_user
                                    eleve.save(update_fields=['co_responsable'])
                                
                                # Mettre à jour le statut du bénévole en "Mentor"
                                if benevole.statut != 'Mentor':
                                    benevole.statut = 'Mentor'
                                    benevole.save(update_fields=['statut'])
                                
                                # Mettre à jour le statut de l'élève en "accompagne"
                                if eleve.statut != 'accompagne':
                                    eleve.statut = 'accompagne'
                                    eleve.save(update_fields=['statut'])
                                
                                if created:
                                    created_count += 1
                                    self.stdout.write(f'  ✅ Créé : {prenom_enfant} {nom_enfant} ↔ {prenom_benevole} {nom_benevole}')
                                else:
                                    updated_count += 1
                                    self.stdout.write(f'  🔄 Mis à jour : {prenom_enfant} {nom_enfant} ↔ {prenom_benevole} {nom_benevole}')
                        
                        except Exception as e:
                            error_count += 1
                            self.stdout.write(self.style.ERROR(f'  ❌ Erreur : {str(e)}'))
            
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé : {csv_file}'))
                continue
        
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
    
    def get_or_create_user(self, name):
        """Créer ou récupérer un utilisateur Django pour le co-responsable"""
        username = name.lower()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': name,
                'is_staff': False,
                'is_active': True,
            }
        )
        if created:
            # Définir un mot de passe temporaire
            user.set_password(f'{username}123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'  👤 Utilisateur créé : {name}'))
        return user
    
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
