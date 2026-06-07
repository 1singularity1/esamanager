"""
Commande Django pour importer les bénévoles depuis les fichiers CSV

Usage:
    python manage.py import_benevoles benevoles.csv candidats.csv
"""

from django.core.management.base import BaseCommand
from core.models import Benevole, Matiere
from core.utils_matieres import extraire_matieres
import csv
from datetime import datetime
import unicodedata

ZONE_GEO_CHOICES = [
    ('1', '1er'),
    ('2', '2e'),
    ('3', '3e'),
    ('4', '4e'),
    ('5', '5e'),
    ('6', '6e'),
    ('7', '7e'),
    ('8', '8e'),
    ('9', '9e'),
    ('10', '10e'),
    ('11', '11e'),
    ('12', '12e'),
    ('13', '13e'),
    ('14', '14e'),
    ('15', '15e'),
    ('16', '16e'),
    ('hors', 'Hors Marseille'),
]

def normaliser_nom(texte):
    """Minuscules + suppression accents pour comparaison souple."""
    texte = texte.lower().strip()
    texte = unicodedata.normalize('NFD', texte)
    return ''.join(c for c in texte if unicodedata.category(c) != 'Mn')


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
        tous_benevoles = list(Benevole.objects.all())

        # ============================================================
        # IMPORT BÉNÉVOLES 2025-2026
        # ============================================================

        self.stdout.write(self.style.SUCCESS(f'\n📥 Import des bénévoles depuis {benevoles_file}'))

        try:
            with open(benevoles_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [name.strip().lstrip('\ufeff').lstrip('\ufbff') for name in reader.fieldnames]

                for row in reader:
                    try:
                        first_col_name = reader.fieldnames[0]
                        nom = row.get(first_col_name, '').strip().rstrip('*')

                        # Arrêter à la section Responsables
                        if nom.lower() == 'responsables':
                            break

                        # Ignorer les lignes sans prénom ou email valide
                        if not row.get('Prénom') or not row.get('Mail') or '@' not in row.get('Mail') or len(row.get('Mail')) < 5:
                            continue

                        prenom = row.get('Prénom', '').strip()
                        email = row.get('Mail', '').strip().lower()

                        if not prenom or not email:
                            continue

                        telephone = row.get('Mobile', '').strip()
                        code_postal = row.get('Arr.', '').strip()
                        adresse = row.get('Adresse', '').strip()
                        profession = row.get('Profession', '').strip()

                        # Niveaux
                        primaire = bool(row.get('Primaire', '').strip())
                        college = bool(row.get('Collège', '').strip())
                        lycee = bool(row.get('Lycée', '').strip())

                        # Documents administratifs
                        reunion_accueil_str = row.get("Réunion d'accueil faite", '').strip()
                        volet_3_str = row.get('Volet 3 casier judiciaire', '').strip()
                        reunion_accueil = reunion_accueil_str not in ['', '0']
                        volet_3 = self.parse_date(volet_3_str) if volet_3_str and volet_3_str != '0' else None
                        a_donne_photo = bool(row.get('photo', '').strip())

                        # Commentaires
                        commentaires = row.get('Commentaires', '').strip()
                        divers = row.get('Divers', '').strip()

                        # Matières (extraction uniquement pour la création)
                        matieres_str = row.get('Matières', '').strip()
                        matieres_reconnues, texte_non_reconnu = extraire_matieres(matieres_str)
                        zone_geo_str = row.get('Zone géographique', '').strip()
                        arrondissements, zone_commentaire = self.extraire_arrondissements(zone_geo_str)
                        ville = row.get('Ville', '').strip() or self.get_ville_from_cp(code_postal)

                        if dry_run:
                            benevole = Benevole.objects.filter(email=email).first()
                            if benevole:
                                updated_count += 1
                                self.stdout.write(f'  🔄 Mettrait à jour : {prenom} {nom} ({email})')
                            else:
                                created_count += 1
                                self.stdout.write(f'  ✅ Créerait : {prenom} {nom} ({email})')
                                if not nom:
                                    self.stdout.write(self.style.WARNING(f'      ⚠️  NOM VIDE détecté !'))
                                if matieres_reconnues:
                                    self.stdout.write(f'      → Matières : {", ".join(sorted(matieres_reconnues))}')
                                if zone_geo_str:
                                    self.stdout.write(f'      → Zone géographique : {zone_geo_str}')
                                if texte_non_reconnu:
                                    self.stdout.write(self.style.WARNING(
                                        f'      ⚠️  Non reconnu → commentaires : "{texte_non_reconnu}"'))
                        else:
                            # Supprimer les doublons éventuels
                            existing = Benevole.objects.filter(email=email)
                            if existing.count() > 1:
                                for duplicate in existing[1:]:
                                    duplicate.delete()
                                self.stdout.write(f'  🧹 Doublons supprimés pour {email}')

                            try:
                                benevole = Benevole.objects.get(email=email)
                                # EXISTE : mettre à jour uniquement le statut
                                old_statut = benevole.statut
                                if old_statut == 'Mentor':
                                    updated_count += 1
                                    self.stdout.write(f'  ↻ Statut préservé : {prenom} {nom} (Mentor)')
                                else:
                                    benevole.statut = 'Disponible'
                                    benevole.save(update_fields=['statut'])
                                    updated_count += 1
                                    if old_statut != 'Disponible':
                                        self.stdout.write(f'  🔄 Mis à jour statut : {prenom} {nom} ({old_statut} → Disponible)')
                                    else:
                                        self.stdout.write(f'  ↻ Statut inchangé : {prenom} {nom}')

                            except Benevole.DoesNotExist:
                                # NOUVEAU : créer avec toutes les données
                                commentaire_final_parts = [commentaires] if commentaires else []
                                if texte_non_reconnu:
                                    commentaire_final_parts.append(f'Matières (non classifié) : {texte_non_reconnu}')
                                commentaire_final = '\n'.join(commentaire_final_parts).strip()

                                benevole = Benevole.objects.create(
                                    email=email,
                                    nom=nom,
                                    prenom=prenom,
                                    telephone=telephone,
                                    code_postal=code_postal,
                                    adresse=adresse,
                                    profession=profession,
                                    primaire=primaire,
                                    college=college,
                                    lycee=lycee,
                                    statut='Disponible',
                                    reunion_accueil_faite=reunion_accueil,
                                    volet_3_casier_judiciaire=volet_3,
                                    a_donne_photo=a_donne_photo,
                                    divers=divers,
                                    zone_geographique=','.join(arrondissements),  # ex: "1,5,6"
                                    commentaires='\n'.join(filter(None, [commentaire_final, zone_commentaire])),
                                    ville=ville,
                                )

                                if matieres_reconnues:
                                    self.add_matieres(benevole, matieres_reconnues)

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

        tous_benevoles = list(Benevole.objects.all())
        self.stdout.write(self.style.SUCCESS(f'\n📥 Import des candidats depuis {candidats_file}'))

        try:
            with open(candidats_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [name.strip().lstrip('\ufeff').lstrip('\ufbff') for name in reader.fieldnames]

                for row in reader:
                    try:
                        first_col_name = reader.fieldnames[0]
                        nom = row.get(first_col_name, '').strip().rstrip('*')
                        prenom = row.get('Prénom', '').strip()
                        email = row.get('Mail', '').strip().lower()

                        # Arrêter à la section "Demandes retirées"
                        if 'demande' in nom.lower() and 'retir' in nom.lower():
                            break

                        if not nom or not prenom:
                            continue

                        # Ignorer les séparateurs d'année (ex: "2023 - 2024")
                        if '-' in nom and len(nom) < 15:
                            continue

                        # Email invalide → vider plutôt que rejeter la ligne
                        if email and '@' not in email and len(email) < 5:
                            email = ''

                        telephone = row.get('Mobile', '').strip()
                        code_postal = row.get('Arr.', '').strip()
                        adresse = row.get('Adresse', '').strip()
                        primaire = bool(row.get('Prim', '').strip() or row.get('C', '').strip())
                        college = bool(row.get('Coll', '').strip())
                        lycee = bool(row.get('Lycée', '').strip())
                        commentaires = row.get('Commentaires', '').strip()
                        infos_complementaires = row.get('Informations complémentaires', '').strip()
                        disponibilites = row.get('Disponibilités et compétences', '').strip()
                        zone_geo_str = row.get('Zone géographique', '').strip()
                        arrondissements, zone_commentaire = self.extraire_arrondissements(zone_geo_str)
                        ville = row.get('Ville', '').strip() or self.get_ville_from_cp(code_postal)

                        # Lookup : email en priorité, sinon nom+prénom normalisés
                        if email:
                            benevole = next(
                                (b for b in tous_benevoles if b.email and b.email.lower() == email),
                                None
                            )
                        else:
                            nom_norm = normaliser_nom(nom)
                            prenom_norm = normaliser_nom(prenom)
                            benevole = next(
                                (b for b in tous_benevoles
                                 if normaliser_nom(b.nom) == nom_norm
                                 and normaliser_nom(b.prenom) == prenom_norm),
                                None
                            )

                        if dry_run:
                            if benevole:
                                updated_count += 1
                                if benevole.statut in ('Mentor', 'Disponible'):
                                    self.stdout.write(f'  ↻ Statut préservé candidat : {prenom} {nom} ({benevole.statut})')
                                else:
                                    self.stdout.write(f'  🔄 Mettrait à jour candidat : {prenom} {nom} ({email})')
                            else:
                                created_count += 1
                                self.stdout.write(f'  ✅ Créerait candidat : {prenom} {nom} ({email or "sans email"})')
                        else:
                            if benevole:
                                old_statut = benevole.statut
                                if old_statut in ('Mentor', 'Disponible'):
                                    updated_count += 1
                                    self.stdout.write(f'  ↻ Statut préservé candidat : {prenom} {nom} ({old_statut})')
                                else:
                                    benevole.statut = 'Candidat'
                                    benevole.save(update_fields=['statut'])
                                    updated_count += 1
                                    if old_statut != 'Candidat':
                                        self.stdout.write(f'  🔄 Mis à jour statut candidat : {prenom} {nom} ({old_statut} → Candidat)')
                                    else:
                                        self.stdout.write(f'  ↻ Statut inchangé candidat : {prenom} {nom}')
                            else:
                                benevole = Benevole.objects.create(
                                    email=email,
                                    nom=nom,
                                    prenom=prenom,
                                    telephone=telephone,
                                    code_postal=code_postal,
                                    adresse=adresse,
                                    primaire=primaire,
                                    college=college,
                                    lycee=lycee,
                                    statut='Candidat',
                                    divers=f"{infos_complementaires}\n{disponibilites}".strip(),
                                    zone_geographique=','.join(arrondissements),  # ex: "1,5,6"
                                    commentaires='\n'.join(filter(None, [commentaires, zone_commentaire])),
                                    ville=ville,
                                )
                                tous_benevoles.append(benevole)
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
            self.stdout.write(self.style.WARNING("⚠️  MODE TEST : Aucune donnée n'a été modifiée"))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))
        else:
            self.stdout.write(self.style.SUCCESS(
                '\n💡 Note : Les statuts "Mentor" seront attribués lors de l\'import des binômes'
            ))

    def parse_date(self, date_str):
        """Parse une date au format DD/MM/YYYY ou DD/MM/YY"""
        if not date_str or date_str.strip() == '0':
            return None
        date_str = date_str.strip()
        for fmt in ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def add_matieres(self, benevole, matieres_list):
        """Ajoute les matières canoniques reconnues au bénévole (ManyToMany)."""
        for nom_matiere in matieres_list:
            matiere, _ = Matiere.objects.get_or_create(
                nom__iexact=nom_matiere,
                defaults={'nom': nom_matiere, 'actif': True}
            )
            benevole.matieres.add(matiere)

    def get_ville_from_cp(self, code_postal):
        """Résout la ville depuis le code postal via geo.api.gouv.fr"""
        if not code_postal:
            return ''
        # Marseille : 13001 à 13016
        if code_postal.startswith('130') and len(code_postal) == 5:
            return 'Marseille'
        try:
            import urllib.request, json
            url = f'https://geo.api.gouv.fr/communes?codePostal={code_postal}&fields=nom&format=json'
            with urllib.request.urlopen(url, timeout=3) as r:
                data = json.loads(r.read())
                if data:
                    return data[0]['nom']
        except Exception:
            pass
        return ''
    
    def extraire_arrondissements(self, zone_geo_str):
        """
        Extrait les arrondissements marseillais depuis le texte libre.
        Retourne (liste_arrondissements, texte_original_si_non_reconnu)
        """
        if not zone_geo_str:
            return [], ''
        
        import re
        arrondissements = set()
        
        # Chercher patterns : 13001-13016, 1er, 2e, 2ème, 15°...
        patterns = [
            r'130(\d{2})',                          # 13001 → 13016
            r'(?<!\d)(\d{1,2})\s*°',               # 6°, 8°, 13°
            r'(?<!\d)(\d{1,2})\s*[eè][èéme]*(?!\w)', # 6e, 8ème, 3ème, 1er
            r'(?<!\d)(\d{1,2})\s*(?:arr|ardt)\b',  # 12 arr, 5 ardt
        ]       
        
        for pattern in patterns:
            for match in re.finditer(pattern, zone_geo_str, re.IGNORECASE):
                n = int(match.group(1))
                if 1 <= n <= 16:
                    arrondissements.add(str(n))
        
        if arrondissements:
            return sorted(arrondissements, key=int), ''
        else:
            return [], zone_geo_str
