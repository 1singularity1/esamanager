"""
Commande Django pour importer les élèves en attente depuis le fichier CSV.

Usage:
    python manage.py import_eleves_attente eleves_en_attente.csv
    python manage.py import_eleves_attente eleves_en_attente.csv --dry-run
"""

import csv
import re
import unicodedata
from datetime import datetime

from django.core.management.base import BaseCommand

from core.models import Eleve, Matiere


# Matières canoniques et leurs mots-clés associés (identique à import_eleves.py)
MATIERES_CANONIQUES = {
    'Mathématiques': ['math', 'maths', 'mathématiques', 'calcul', 'géométrie', 'nombres'],
    'Français':      ['français', 'francais', 'lecture', 'écriture', 'ecriture', 'orthographe',
                      'grammaire', 'conjugaison', 'rédaction', 'redaction', 'compréhension',
                      'comprehension', 'consignes', 'conjuguaison', 'fraçais'],
    'Anglais':       ['anglais'],
    'Espagnol':      ['espagnol'],
    'Histoire-Géographie': ['histoire', 'géographie', 'geographie', 'hg', 'hist', 'his-geo'],
    'SVT':           ['svt'],
    'Physique-Chimie': ['physique', 'chimie', 'phys'],
    'Toutes matières': ['toutes', 'toutes matières', 'toutes matieres', 'primaire',
                        'matières primaires', 'bases du primaire', 'tout-'],
    'Méthodologie':  ['méthodo', 'methodologie', 'méthodologie', 'organisation', 'méthode',
                      'apprendre à apprendre'],
    'Sciences':      ['sciences', 'matières scientifiques'],
}

# Mapping pour normaliser les classes du CSV vers les choix du modèle.
# Toutes les clés sont en MAJUSCULES — la fonction fait un .upper() avant lookup.
CLASSE_MAPPING = {
    # Collège — variantes orthographiques
    '6°': '6e',  '6ÈME': '6e', '6EME': '6e',
    '5°': '5e',  '5ÈME': '5e', '5EME': '5e',
    '4°': '4e',  '4ÈME': '4e', '4EME': '4e',
    '3°': '3e',  '3ÈME': '3e', '3EME': '3e',
    # Collège — sections (6A … 6E, etc.)
    '6A': '6e', '6B': '6e', '6C': '6e', '6D': '6e', '6E': '6e',
    '5A': '5e', '5B': '5e', '5C': '5e', '5D': '5e', '5E': '5e',
    '4A': '4e', '4B': '4e', '4C': '4e', '4D': '4e', '4E': '4e',
    '3A': '3e', '3B': '3e', '3C': '3e', '3D': '3e', '3E': '3e',
    # Lycée général
    '2NDE': '2de', '2DE': '2de', '2°': '2de', 'SECONDE': '2de',
    '1ÈRE': '1re', '1ERE': '1re', '1RE': '1re', '1°': '1re', 'PREMIERE': '1re',
    # Terminale
    'T': 'Terminale', 'TLE': 'Terminale', 'TERM': 'Terminale', 'TERMINALE': 'Terminale',
    'TS': 'Terminale', 'TES': 'Terminale', 'TL': 'Terminale',
    # CAP
    'CAP 1': 'CAP 1e', 'CAP1': 'CAP 1e',
    'CAP 2': 'CAP 2e', 'CAP2': 'CAP 2e',
    # Bac Pro
    '2DE BAC PRO': 'Bac Pro 2e', '2NDE BAC PRO': 'Bac Pro 2e',
    'SECONDE BAC PRO': 'Bac Pro 2e', '2DE BACPRO': 'Bac Pro 2e',
    'BAC PRO 2E': 'Bac Pro 2e', 'BAC PRO 2': 'Bac Pro 2e',
}

CLASSES_VALIDES = {c for c, _ in Eleve.CLASSE_CHOICES}


def normaliser(texte):
    """Minuscules + suppression accents pour comparaison."""
    texte = texte.lower().strip()
    texte = unicodedata.normalize('NFD', texte)
    return ''.join(c for c in texte if unicodedata.category(c) != 'Mn')


def normaliser_classe(classe_str):
    """Normalise la valeur de classe CSV vers un choix du modèle, ou '' si inconnu."""
    if not classe_str:
        return ''
    classe_str = classe_str.strip()
    if classe_str in CLASSES_VALIDES:
        return classe_str
    return CLASSE_MAPPING.get(classe_str.upper(), '')


def extraire_matieres(besoins_str):
    """
    Retourne (matieres_reconnues: list[str], texte_non_reconnu: str)
    """
    if not besoins_str:
        return [], ''

    tokens = re.split(r'[,;/\n]+', besoins_str)
    tokens = [t.strip() for t in tokens if t.strip()]

    matieres_trouvees = set()
    tokens_non_reconnus = []

    for token in tokens:
        token_norm = normaliser(token)
        reconnu = False

        for matiere_canon, mots_cles in MATIERES_CANONIQUES.items():
            for mot in mots_cles:
                if normaliser(mot) in token_norm:
                    matieres_trouvees.add(matiere_canon)
                    reconnu = True
                    break
            if reconnu:
                break

        if not reconnu:
            tokens_non_reconnus.append(token)

    texte_non_reconnu = ', '.join(tokens_non_reconnus)
    return list(matieres_trouvees), texte_non_reconnu


class Command(BaseCommand):
    help = 'Importe les élèves en attente depuis le fichier CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Fichier CSV des élèves en attente')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode test : affiche ce qui serait fait sans modifier la base de données'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '=' * 60))
            self.stdout.write(self.style.WARNING('MODE TEST - Aucune modification en base de données'))
            self.stdout.write(self.style.WARNING('=' * 60 + '\n'))

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        self.stdout.write(self.style.SUCCESS(f'\nImport des élèves en attente depuis {csv_file}'))

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [
                    name.strip().lstrip('\ufeff').lstrip('\ufbff')
                    for name in reader.fieldnames
                ]

                for row in reader:
                    try:
                        nom = row.get('Nom enfant', '').strip().rstrip('*')
                        prenom = row.get('Prénom enfant', '').strip()
                        telephone_parent = row.get('Mobile parents', '').strip()

                        if not nom or not prenom:
                            skipped_count += 1
                            continue

                        # La 4e colonne (header vide après strip) contient l'arrondissement
                        arrondissement = row.get('', '').strip()
                        adresse = row.get('Adresse', '').strip()
                        complement_adresse = row.get("complement d'adresse", '').strip()
                        classe_raw = row.get('Classe', '').strip()
                        classe = normaliser_classe(classe_raw)
                        classe_note = None  # valeur brute à conserver en commentaire si fallback
                        if not classe and classe_raw:
                            raw_up = classe_raw.upper()
                            if 'CAP' in raw_up:
                                classe = 'CAP'
                                classe_note = f'Classe brute : {classe_raw}'
                            elif 'BAC PRO' in raw_up or 'BACPRO' in raw_up:
                                classe = '2de'
                                classe_note = f'Classe brute : {classe_raw}'
                        etablissement = row.get('Etab.  scolaire', '').strip()
                        email_parent = row.get('Mail parents', '').strip().lower()
                        besoins = row.get('Besoins', '').strip()
                        commentaires = row.get('Commentaires', '').strip()
                        complement_infos = row.get('complements infos autre n°de tel contact)', '').strip()
                        benevole_pressenti = row.get('Bénévole pressenti', '').strip()
                        date_demande = row.get('date de demande', '').strip()
                        date_visite = self.parse_date(row.get('Famille visitée le :', ''))

                        matieres_reconnues, texte_non_reconnu = extraire_matieres(besoins)

                        if dry_run:
                            try:
                                Eleve.objects.get(
                                    nom=nom,
                                    prenom=prenom,
                                    telephone_parent=telephone_parent,
                                )
                                updated_count += 1
                                self.stdout.write(f'  Mettrait à jour statut : {prenom} {nom}')
                            except Eleve.DoesNotExist:
                                created_count += 1
                                self.stdout.write(f'  Creerait : {prenom} {nom}')

                            if classe_note:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'      Classe partielle : "{classe_raw}" -> "{classe}" + note dans commentaires'))
                            elif classe_raw and not classe:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'      Classe non reconnue : "{classe_raw}" (sera ignoree)'))
                            if matieres_reconnues:
                                self.stdout.write(
                                    f'      Matieres : {", ".join(sorted(matieres_reconnues))}')
                            if texte_non_reconnu:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'      Non reconnu -> commentaires : "{texte_non_reconnu}"'))

                        else:
                            # Construire les informations complémentaires
                            commentaire_parts = []
                            if commentaires:
                                commentaire_parts.append(commentaires)
                            if complement_infos:
                                commentaire_parts.append(complement_infos)
                            if benevole_pressenti:
                                commentaire_parts.append(f'Bénévole pressenti : {benevole_pressenti}')
                            if date_demande:
                                commentaire_parts.append(f'Date de demande : {date_demande}')
                            if texte_non_reconnu:
                                commentaire_parts.append(f'Besoins (non classifié) : {texte_non_reconnu}')
                            if classe_note:
                                commentaire_parts.append(classe_note)
                            commentaire_final = '\n'.join(commentaire_parts).strip()

                            try:
                                eleve = Eleve.objects.get(
                                    nom=nom,
                                    prenom=prenom,
                                    telephone_parent=telephone_parent,
                                )
                                old_statut = eleve.statut
                                eleve.statut = 'en_attente'
                                eleve.save(update_fields=['statut'])

                                updated_count += 1
                                if old_statut != 'en_attente':
                                    self.stdout.write(
                                        f'  Mis a jour statut : {prenom} {nom} '
                                        f'({old_statut} -> en_attente)')
                                else:
                                    self.stdout.write(f'  Statut inchange : {prenom} {nom}')

                            except Eleve.DoesNotExist:
                                eleve = Eleve.objects.create(
                                    nom=nom,
                                    prenom=prenom,
                                    telephone_parent=telephone_parent,
                                    arrondissement=arrondissement,
                                    adresse=adresse,
                                    complement_adresse=complement_adresse,
                                    classe=classe,
                                    etablissement=etablissement,
                                    email_parent=email_parent,
                                    statut='en_attente',
                                    statut_saisie='complet',
                                    informations_complementaires=commentaire_final,
                                    date_derniere_visite=date_visite,
                                )
                                created_count += 1
                                self.stdout.write(f'  Cree : {prenom} {nom}')

                            if matieres_reconnues:
                                self.add_matieres(eleve, matieres_reconnues)

                    except Exception as e:
                        error_count += 1
                        prenom = row.get('Prénom enfant', 'inconnu')
                        nom = row.get('Nom enfant', 'inconnu')
                        self.stdout.write(self.style.ERROR(f'  Erreur {prenom} {nom}: {str(e)}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Fichier non trouve : {csv_file}'))
            return

        self.stdout.write(self.style.SUCCESS('\nImport termine !'))
        self.stdout.write(f'  Crees    : {created_count}')
        self.stdout.write(f'  Mis a jour : {updated_count}')
        if skipped_count:
            self.stdout.write(f'  Ignores  : {skipped_count} (lignes sans nom/prenom)')
        if error_count:
            self.stdout.write(self.style.WARNING(f'  Erreurs  : {error_count}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '=' * 60))
            self.stdout.write(self.style.WARNING("MODE TEST : Aucune donnee n'a ete modifiee"))
            self.stdout.write(self.style.WARNING('=' * 60 + '\n'))

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

    def add_matieres(self, eleve, matieres_list):
        """Ajoute les matières canoniques reconnues à l'élève (ManyToMany)."""
        for nom_matiere in matieres_list:
            matiere, _ = Matiere.objects.get_or_create(
                nom__iexact=nom_matiere,
                defaults={'nom': nom_matiere, 'actif': True}
            )
            eleve.matieres_souhaitees.add(matiere)
