"""
Commande Django pour importer les élèves depuis le fichier "Enfants aidés"

Usage:
    python manage.py import_eleves enfants_aides.csv
"""

from django.core.management.base import BaseCommand
from core.models import Eleve, Matiere
import csv
from datetime import datetime


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
                # Nettoyer les noms de colonnes
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
                
                for row in reader:
                    try:
                        # Extraire les données de l'enfant
                        nom_famille = row.get('Nom famille enfant', '').strip()
                        prenom_enfant = row.get('Prénom enfant', '').strip()
                        telephone_famille = row.get('Mobile', '').strip()
                        
                        # Si pas de données essentielles, ignorer
                        if not nom_famille or not prenom_enfant:
                            continue
                        
                        # Autres données
                        arrondissement = row.get('Arr.', '').strip()
                        adresse = row.get('Adresse enfant', '').strip()
                        complement_adresse = row.get('complement d\'adresse', '').strip()
                        
                        classe = row.get('yion', '').strip()  # Semble être la colonne classe
                        etablissement = row.get('Etablissement scolaire', '').strip()
                        
                        email_parent = row.get('mail', '').strip().lower()
                        
                        # Besoins = matières souhaitées
                        besoins = row.get('besoins', '').strip()
                        
                        # Commentaires
                        commentaires = row.get('Commentaires-observations', '').strip()
                        complement_infos = row.get('Complément d\'informatons- Autres n°', '').strip()
                        
                        # Date dernière visite
                        date_visite = self.parse_date(row.get('Date dernière visite chez la famille', ''))
                        
                        # Créer ou mettre à jour l'élève
                        # Clé unique : nom + prenom + telephone_parent
                        
                        if dry_run:
                            # Mode test : vérifier si existe sans modifier
                            try:
                                eleve = Eleve.objects.get(
                                    nom=nom_famille,
                                    prenom=prenom_enfant,
                                    telephone_parent=telephone_famille
                                )
                                updated_count += 1
                                self.stdout.write(f'  🔄 Mettrait à jour : {prenom_enfant} {nom_famille}')
                            except Eleve.DoesNotExist:
                                created_count += 1
                                self.stdout.write(f'  ✅ Créerait : {prenom_enfant} {nom_famille}')
                            
                            # Simuler l'ajout de matières
                            if besoins:
                                self.stdout.write(f'      → Matières : {besoins}')
                        else:
                            # Mode réel : créer ou mettre à jour
                            eleve, created = Eleve.objects.update_or_create(
                                nom=nom_famille,
                                prenom=prenom_enfant,
                                telephone_parent=telephone_famille,
                                defaults={
                                    'arrondissement': arrondissement,
                                    'adresse': adresse,
                                    'complement_adresse': complement_adresse,
                                    'classe': classe,
                                    'etablissement': etablissement,
                                    'email_parent': email_parent,
                                    'statut': 'accompagne',  # Ils sont dans "enfants aidés" donc accompagnés
                                    'statut_saisie': 'complet',
                                    'informations_complementaires': f"{commentaires}\n{complement_infos}\nBesoins: {besoins}".strip(),
                                    'date_derniere_visite': date_visite,
                                }
                            )
                            
                            # Ajouter les matières souhaitées si renseignées
                            if besoins:
                                self.add_matieres(eleve, besoins)
                            
                            if created:
                                created_count += 1
                                self.stdout.write(f'  ✅ Créé : {prenom_enfant} {nom_famille}')
                            else:
                                updated_count += 1
                                self.stdout.write(f'  🔄 Mis à jour : {prenom_enfant} {nom_famille}')
                    
                    except Exception as e:
                        error_count += 1
                        prenom = row.get('Prénom enfant', 'inconnu')
                        nom = row.get('Nom famille enfant', 'inconnu')
                        self.stdout.write(self.style.ERROR(f'  ❌ Erreur {prenom} {nom}: {str(e)}'))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé : {csv_file}'))
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
    
    def parse_date(self, date_str):
        """Parse une date au format DD/MM/YYYY ou DD/MM/YY"""
        if not date_str or date_str.strip() == '0':
            return None
        
        date_str = date_str.strip()
        
        # Essayer différents formats
        formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d', '%d/%m/%y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    def add_matieres(self, eleve, besoins_str):
        """
        Ajoute les matières souhaitées à l'élève
        Format attendu: "Maths, Français" ou "Maths / SVT"
        """
        if not besoins_str:
            return
        
        # Séparer par virgule ou slash
        separateurs = [',', '/', ';']
        matieres_list = [besoins_str]
        
        for sep in separateurs:
            if sep in besoins_str:
                matieres_list = [m.strip() for m in besoins_str.split(sep)]
                break
        
        # Mapper les noms de matières aux objets Matiere
        for matiere_nom in matieres_list:
            matiere_nom = matiere_nom.strip()
            if not matiere_nom:
                continue
            
            # Chercher ou créer la matière
            matiere, _ = Matiere.objects.get_or_create(
                nom__iexact=matiere_nom,
                defaults={'nom': matiere_nom, 'actif': True}
            )
            
            # Ajouter à l'élève (ManyToMany)
            eleve.matieres_souhaitees.add(matiere)
