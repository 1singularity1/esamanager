"""
Commande Django pour importer les élèves depuis le fichier "Enfants aidés"

Usage:
    python manage.py import_eleves enfants_aides.csv
"""

from django.core.management.base import BaseCommand
from core.models import Eleve, Matiere
import csv
from datetime import datetime


# Matières canoniques et leurs mots-clés associés
MATIERES_CANONIQUES = {
    'Mathématiques': ['math', 'maths', 'mathématiques', 'calcul', 'géométrie', 'nombres'],
    'Français':      ['français', 'francais', 'lecture', 'écriture', 'ecriture', 'orthographe',
                      'grammaire', 'conjugaison', 'rédaction', 'redaction', 'compréhension',
                      'comprehension', 'consignes','conjugaison', 'conjuguaison', 'fraçais'],
    'Anglais':       ['anglais'],
    'Espagnol':      ['espagnol'],
    'Histoire-Géographie': ['histoire', 'géographie', 'geographie', 'hg', 'hist', 'his-geo'],
    'SVT':           ['svt', 'sciences'],
    'Physique-Chimie': ['physique', 'chimie', 'phys'],
    'Toutes matières': ['toutes', 'toutes matières', 'toutes matieres', 'primaire',
                        'matières primaires', 'bases du primaire'],
    'Méthodologie':  ['méthodo', 'methodologie', 'méthodologie', 'organisation', 'méthode',
                      'apprendre à apprendre'],
}


def normaliser(texte):
    """Minuscules + suppression accents pour comparaison."""
    import unicodedata
    texte = texte.lower().strip()
    texte = unicodedata.normalize('NFD', texte)
    texte = ''.join(c for c in texte if unicodedata.category(c) != 'Mn')
    return texte


def extraire_matieres(besoins_str):
    """
    Retourne (matieres_reconnues: list[str], texte_non_reconnu: str)
    """
    if not besoins_str:
        return [], ''

    # Découper par séparateurs courants
    import re
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
    help = 'Importe les élèves depuis le fichier CSV Enfants aidés'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Fichier CSV des enfants aidés')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode test : affiche ce qui serait fait sans modifier la base de données'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING('🔍 MODE TEST - Aucune modification en base de données'))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))

        created_count = 0
        updated_count = 0
        error_count = 0

        self.stdout.write(self.style.SUCCESS(f'\n📥 Import des élèves depuis {csv_file}'))

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [name.strip().lstrip('\ufeff').lstrip('\ufbff')
                                     for name in reader.fieldnames]

                for row in reader:
                    try:
                        nom_famille = row.get('Nom famille enfant', '').strip().rstrip('*')
                        prenom_enfant = row.get('Prénom enfant', '').strip()
                        telephone_famille = row.get('Mobile', '').strip()

                        if not nom_famille or not prenom_enfant:
                            continue

                        arrondissement = row.get('Arr.', '').strip()
                        adresse = row.get('Adresse enfant', '').strip()
                        complement_adresse = row.get("complement d'adresse", '').strip()
                        classe = row.get('yion', '').strip()
                        etablissement = row.get('Etablissement scolaire', '').strip()
                        email_parent = row.get('mail', '').strip().lower()
                        besoins = row.get('besoins', '').strip()
                        commentaires = row.get('Commentaires-observations', '').strip()
                        complement_infos = row.get("Complément d'informatons- Autres n°", '').strip()
                        date_visite = self.parse_date(
                            row.get('Date dernière visite chez la famille', ''))

                        # Normalisation des matières
                        matieres_reconnues, texte_non_reconnu = extraire_matieres(besoins)

                        if dry_run:
                            try:
                                eleve = Eleve.objects.get(
                                    nom=nom_famille,
                                    prenom=prenom_enfant,
                                    telephone_parent=telephone_famille
                                )
                                updated_count += 1
                                self.stdout.write(
                                    f'  🔄 Mettrait à jour statut : {prenom_enfant} {nom_famille}')
                            except Eleve.DoesNotExist:
                                created_count += 1
                                self.stdout.write(
                                    f'  ✅ Créerait : {prenom_enfant} {nom_famille}')

                            if matieres_reconnues:
                                self.stdout.write(
                                    f'      → Matières : {", ".join(sorted(matieres_reconnues))}')
                            if texte_non_reconnu:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'      ⚠️  Non reconnu → commentaires : "{texte_non_reconnu}"'))

                        else:
                            # Construire le texte des commentaires enrichi
                            commentaire_final_parts = []
                            if commentaires:
                                commentaire_final_parts.append(commentaires)
                            if complement_infos:
                                commentaire_final_parts.append(complement_infos)
                            if texte_non_reconnu:
                                commentaire_final_parts.append(f'Besoins (non classifié) : {texte_non_reconnu}')
                            commentaire_final = '\n'.join(commentaire_final_parts).strip()

                            try:
                                eleve = Eleve.objects.get(
                                    nom=nom_famille,
                                    prenom=prenom_enfant,
                                    telephone_parent=telephone_famille
                                )
                                # EXISTE : mettre à jour uniquement le statut
                                old_statut = eleve.statut
                                eleve.statut = 'accompagne'
                                eleve.save(update_fields=['statut'])

                                updated_count += 1
                                if old_statut != 'accompagne':
                                    self.stdout.write(
                                        f'  🔄 Mis à jour statut : {prenom_enfant} {nom_famille} '
                                        f'({old_statut} → accompagne)')
                                else:
                                    self.stdout.write(
                                        f'  ↻ Statut inchangé : {prenom_enfant} {nom_famille}')

                            except Eleve.DoesNotExist:
                                eleve = Eleve.objects.create(
                                    nom=nom_famille,
                                    prenom=prenom_enfant,
                                    telephone_parent=telephone_famille,
                                    arrondissement=arrondissement,
                                    adresse=adresse,
                                    complement_adresse=complement_adresse,
                                    classe=classe,
                                    etablissement=etablissement,
                                    email_parent=email_parent,
                                    statut='accompagne',
                                    statut_saisie='complet',
                                    informations_complementaires=commentaire_final,
                                    date_derniere_visite=date_visite,
                                )

                                created_count += 1
                                self.stdout.write(f'  ✅ Créé : {prenom_enfant} {nom_famille}')

                            # Ajouter les matières reconnues (M2M)
                            if matieres_reconnues:
                                self.add_matieres(eleve, matieres_reconnues)

                    except Exception as e:
                        error_count += 1
                        prenom = row.get('Prénom enfant', 'inconnu')
                        nom = row.get('Nom famille enfant', 'inconnu')
                        self.stdout.write(self.style.ERROR(f'  ❌ Erreur {prenom} {nom}: {str(e)}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé : {csv_file}'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n✅ Import terminé !'))
        self.stdout.write(f'  📊 Créés : {created_count}')
        self.stdout.write(f'  🔄 Mis à jour : {updated_count}')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Erreurs : {error_count}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING("⚠️  MODE TEST : Aucune donnée n'a été modifiée"))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))

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
