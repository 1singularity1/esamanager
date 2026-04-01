"""
Commande Django pour importer les binômes depuis les fichiers CSV

Usage:
    python manage.py import_binomes binomes_david.csv binomes_clara.csv ...
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Eleve, Benevole, Binome
import csv
import unicodedata
from datetime import datetime
import os


def normaliser_nom(texte):
    """Minuscules + suppression accents pour comparaison souple."""
    texte = texte.lower().strip()
    texte = unicodedata.normalize('NFD', texte)
    return ''.join(c for c in texte if unicodedata.category(c) != 'Mn')


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

        coresponsables = {
            'david':      self.get_or_create_user('David'),
            'clara':      self.get_or_create_user('Clara'),
            'georges':    self.get_or_create_user('Georges'),
            'bernadette': self.get_or_create_user('Bernadette'),
            'sylvie':     self.get_or_create_user('Sylvie'),
        }

        # Pré-charger tous les bénévoles et élèves pour les lookups normalisés
        tous_benevoles = list(Benevole.objects.all())
        tous_eleves = list(Eleve.objects.all())

        for csv_file in csv_files:
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
                    reader.fieldnames = [
                        name.strip().lstrip('\ufeff').lstrip('\ufbff').lower()
                        for name in reader.fieldnames
                    ]

                    if dry_run:
                        self.stdout.write(self.style.WARNING(f'   📋 Colonnes : {reader.fieldnames}'))

                    for row in reader:
                        try:
                            # ================================================
                            # BÉNÉVOLE
                            # ================================================
                            nom_benevole = (row.get('nom bénévole', '') or row.get('nom benevole', '')).strip()
                            prenom_benevole = (row.get('prénom bénévole', '') or row.get('prenom benevole', '')).strip()
                            email_benevole = (row.get('mail bénévole', '') or row.get('mail benevole', '') or row.get('mail', '')).strip().lower()

                            if not nom_benevole or not prenom_benevole:
                                continue

                            # Ignorer si le nom bénévole commence par un chiffre (ex: numéro de téléphone)
                            if nom_benevole and nom_benevole[0].isdigit():
                                continue
                            
                            benevole = self.trouver_benevole(
                                tous_benevoles, nom_benevole, prenom_benevole, email_benevole
                            )

                            if not benevole:
                                self.stdout.write(self.style.WARNING(
                                    f'  ⚠️  Bénévole non trouvé : {prenom_benevole} {nom_benevole}'
                                ))
                                continue

                            # =======================================.rstrip('*')=========
                            # ÉLÈVE
                            # ================================================
                            nom_enfant = (row.get('nom enfant', '') or row.get('nom famille enfant', '')).strip().rstrip('*')
                            prenom_enfant = (row.get('prénom enfant', '') or row.get('prenom enfant', '') or row.get('prénom en fant', '')).strip()
                            tel_famille = (row.get('tél famille', '') or row.get('tel famille', '') or row.get('mobile', '')).strip()

                            if not nom_enfant or not prenom_enfant:
                                continue

                            eleve = self.trouver_eleve(tous_eleves, nom_enfant, prenom_enfant, tel_famille)

                            if not eleve:
                                self.stdout.write(self.style.WARNING(
                                    f'  ⚠️  Élève non trouvé : {prenom_enfant} {nom_enfant}'
                                ))
                                continue

                            # ================================================
                            # BINÔME
                            # ================================================
                            date_contrat = (row.get('date contrat', '') or '').strip()
                            date_debut = self.parse_date(date_contrat) or datetime.now().date()

                            commentaires = (row.get('commentaires-observations', '') or row.get('nouvelles bénévole', '') or '').strip()
                            aide_demandee = (row.get('aide demandée', '') or row.get('aide demandee', '') or row.get('besoins', '') or '').strip()
                            infos_diverses = (row.get('informations diverses', '') or '').strip()
                            notes = '\n'.join(filter(None, [commentaires, aide_demandee, infos_diverses]))

                            if dry_run:
                                try:
                                    Binome.objects.get(eleve=eleve)
                                    updated_count += 1
                                    self.stdout.write(
                                        f'  🔄 Mettrait à jour : {prenom_enfant} {nom_enfant} ↔ {prenom_benevole} {nom_benevole}')
                                except Binome.DoesNotExist:
                                    created_count += 1
                                    self.stdout.write(
                                        f'  ✅ Créerait : {prenom_enfant} {nom_enfant} ↔ {prenom_benevole} {nom_benevole}')

                                if coresponsable_user:
                                    self.stdout.write(f'      → Co-responsable : {coresponsable_user.username}')
                                self.stdout.write(f'      → Statut bénévole : Mentor')
                                self.stdout.write(f'      → Statut élève : accompagne')

                            else:
                                binome, created = Binome.objects.update_or_create(
                                    eleve=eleve,
                                    defaults={
                                        'benevole': benevole,
                                        'date_debut': date_debut,
                                        'actif': True,
                                        'notes': notes,
                                    }
                                )

                                if coresponsable_user:
                                    eleve.co_responsable = coresponsable_user
                                    eleve.save(update_fields=['co_responsable'])

                                if benevole.statut != 'Mentor':
                                    benevole.statut = 'Mentor'
                                    benevole.save(update_fields=['statut'])

                                if eleve.statut != 'accompagne':
                                    eleve.statut = 'accompagne'
                                    eleve.save(update_fields=['statut'])

                                if created:
                                    created_count += 1
                                    self.stdout.write(
                                        f'  ✅ Créé : {prenom_enfant} {nom_enfant} ↔ {prenom_benevole} {nom_benevole}')
                                else:
                                    updated_count += 1
                                    self.stdout.write(
                                        f'  🔄 Mis à jour : {prenom_enfant} {nom_enfant} ↔ {prenom_benevole} {nom_benevole}')

                        except Exception as e:
                            error_count += 1
                            self.stdout.write(self.style.ERROR(f'  ❌ Erreur : {str(e)}'))

            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé : {csv_file}'))
                continue

        # ====================================================================
        # DÉTECTER LES BINÔMES ARRÊTÉS
        # ====================================================================

        if not dry_run:
            self.stdout.write(self.style.SUCCESS('\n🔍 Détection des binômes arrêtés'))
            self.stdout.write('='*60 + '\n')

            binomes_actifs = Binome.objects.filter(actif=True)
            stopped_count = 0

            for binome in binomes_actifs:
                eleve_found = False

                for csv_file in csv_files:
                    try:
                        with open(csv_file, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            reader.fieldnames = [
                                name.strip().lstrip('\ufeff').lstrip('\ufbff').lower()
                                for name in reader.fieldnames
                            ]

                            for row in reader:
                                nom_enfant = (row.get('nom enfant', '') or row.get('nom famille enfant', '')).strip().rstrip('*')
                                prenom_enfant = (row.get('prénom enfant', '') or row.get('prenom enfant', '') or row.get('prénom en fant', '')).strip()
                                tel_famille = (row.get('tél famille', '') or row.get('tel famille', '') or row.get('mobile', '')).strip()

                                if (normaliser_nom(binome.eleve.nom) == normaliser_nom(nom_enfant) and
                                        normaliser_nom(binome.eleve.prenom) == normaliser_nom(prenom_enfant)):
                                    eleve_found = True
                                    break

                        if eleve_found:
                            break

                    except FileNotFoundError:
                        continue

                if not eleve_found:
                    binome.actif = False
                    binome.date_fin = datetime.now().date()
                    binome.save(update_fields=['actif', 'date_fin'])

                    stopped_count += 1
                    self.stdout.write(
                        f'  ⏹️  Binôme arrêté : {binome.eleve.prenom} {binome.eleve.nom} '
                        f'↔ {binome.benevole.prenom if binome.benevole else "?"} '
                        f'{binome.benevole.nom if binome.benevole else ""}'
                    )

                    if binome.eleve.statut == 'accompagne':
                        binome.eleve.statut = 'archive'
                        binome.eleve.save(update_fields=['statut'])

            if stopped_count > 0:
                self.stdout.write(f'\n📊 Binômes arrêtés détectés : {stopped_count}')
            else:
                self.stdout.write('✅ Aucun binôme arrêté détecté')

        # ====================================================================
        # RÉSUMÉ
        # ====================================================================

        self.stdout.write(self.style.SUCCESS(f'\n✅ Import terminé !'))
        self.stdout.write(f'  📊 Créés : {created_count}')
        self.stdout.write(f'  🔄 Mis à jour : {updated_count}')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Erreurs : {error_count}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING("⚠️  MODE TEST : Aucune donnée n'a été modifiée"))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))

    # ========================================================================
    # MÉTHODES UTILITAIRES
    # ========================================================================

    def trouver_benevole(self, tous_benevoles, nom, prenom, email):
        """Recherche un bénévole par email, puis nom+prénom normalisés."""
        # 1. Par email (exact)
        if email and '@' in email:
            for b in tous_benevoles:
                if b.email and b.email.lower() == email:
                    return b

        # 2. Par nom + prénom normalisés (insensible casse + accents)
        nom_norm = normaliser_nom(nom)
        prenom_norm = normaliser_nom(prenom)
        for b in tous_benevoles:
            if (normaliser_nom(b.nom) == nom_norm and
                    normaliser_nom(b.prenom) == prenom_norm):
                return b

        return None

    def trouver_eleve(self, tous_eleves, nom, prenom, tel):
        """Recherche un élève par nom+prénom+tel normalisés, puis sans tel."""
        nom_norm = normaliser_nom(nom)
        prenom_norm = normaliser_nom(prenom)

        # 1. Avec téléphone
        if tel:
            for e in tous_eleves:
                if (normaliser_nom(e.nom) == nom_norm and
                        normaliser_nom(e.prenom) == prenom_norm and
                        e.telephone_parent == tel):
                    return e

        # 2. Sans téléphone (fallback)
        matches = [
            e for e in tous_eleves
            if normaliser_nom(e.nom) == nom_norm and normaliser_nom(e.prenom) == prenom_norm
        ]
        if len(matches) == 1:
            return matches[0]

        return None

    def get_or_create_user(self, name):
        username = name.lower()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'first_name': name, 'is_staff': False, 'is_active': True}
        )
        if created:
            user.set_password(f'{username}123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'  👤 Utilisateur créé : {name}'))
        return user

    def parse_date(self, date_str):
        if not date_str or date_str.strip() == '0':
            return None
        date_str = date_str.strip()
        for fmt in ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
