"""
🎓 COMMANDE DJANGO : import_binomes

Import des binômes élèves-bénévoles depuis eleves_benevoles.csv
Les élèves et bénévoles doivent déjà exister en base.

Usage :
    python manage.py import_binomes chemin/vers/eleves_benevoles.csv

Emplacement :
    core/management/commands/import_binomes.py
"""

from django.core.management.base import BaseCommand, CommandError
from core.models import Eleve, Benevole, Binome
from datetime import date
import csv
import os


class Command(BaseCommand):
    help = 'Importe les binômes depuis eleves_benevoles.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Chemin vers le fichier CSV'
        )
        
        parser.add_argument(
            '--date-debut',
            type=str,
            help='Date de début des binômes (format YYYY-MM-DD). Par défaut : aujourd\'hui'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler l\'import sans modifier la base de données'
        )
        
        parser.add_argument(
            '--update',
            action='store_true',
            help='Mettre à jour les binômes existants'
        )

    def normaliser_nom(self, nom):
        """Normalise un nom pour la recherche (retire espaces, met en minuscule)."""
        return nom.strip().lower()

    def trouver_eleve(self, nom, prenom):
        """
        Trouve un élève par nom et prénom (recherche souple).
        """
        nom_norm = self.normaliser_nom(nom)
        prenom_norm = self.normaliser_nom(prenom)
        
        # Recherche exacte
        eleve = Eleve.objects.filter(
            nom__iexact=nom.strip(),
            prenom__iexact=prenom.strip()
        ).first()
        
        if eleve:
            return eleve
        
        # Recherche souple (contient)
        eleve = Eleve.objects.filter(
            nom__icontains=nom.strip(),
            prenom__icontains=prenom.strip()
        ).first()
        
        return eleve

    def trouver_benevole(self, nom, prenom):
        """
        Trouve un bénévole par nom et prénom (recherche souple).
        """
        nom_norm = self.normaliser_nom(nom)
        prenom_norm = self.normaliser_nom(prenom)
        
        # Nettoyer les caractères spéciaux (*, espaces)
        nom_clean = nom.strip().replace('*', '').replace('  ', ' ')
        prenom_clean = prenom.strip().replace('*', '').replace('  ', ' ')
        
        # Recherche exacte
        benevole = Benevole.objects.filter(
            nom__iexact=nom_clean,
            prenom__iexact=prenom_clean
        ).first()
        
        if benevole:
            return benevole
        
        # Recherche souple (contient)
        benevole = Benevole.objects.filter(
            nom__icontains=nom_clean,
            prenom__icontains=prenom_clean
        ).first()
        
        return benevole

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        update_mode = options['update']
        date_debut_str = options.get('date_debut')
        
        # Date de début
        if date_debut_str:
            from datetime import datetime
            date_debut = datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        else:
            date_debut = date.today()
        
        if not os.path.exists(csv_file):
            raise CommandError(f'Le fichier {csv_file} n\'existe pas')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODE SIMULATION (dry-run)'))
        
        self.stdout.write(f'📅 Date de début des binômes : {date_debut}')
        self.stdout.write('📖 Lecture du fichier CSV...')
        self.stdout.write('')
        
        stats = {
            'total': 0,
            'créés': 0,
            'mis_à_jour': 0,
            'ignorés': 0,
            'eleve_introuvable': 0,
            'benevole_introuvable': 0,
        }
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    stats['total'] += 1
                    
                    try:
                        # Extraire les données
                        eleve_nom = row.get('Nom famille enfant', '').strip()
                        eleve_prenom = row.get('Prénom enfant', '').strip()
                        benevole_nom = row.get('Nom famille bénévole', '').strip()
                        benevole_prenom = row.get('Prénom bénévole', '').strip()
                        
                        if not all([eleve_nom, eleve_prenom, benevole_nom, benevole_prenom]):
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⚠️  Ligne {stats["total"]} : Données manquantes - IGNORÉ'
                                )
                            )
                            stats['ignorés'] += 1
                            continue
                        
                        # Chercher l'élève
                        eleve = self.trouver_eleve(eleve_nom, eleve_prenom)
                        if not eleve:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'❌ Élève introuvable : {eleve_prenom} {eleve_nom}'
                                )
                            )
                            stats['eleve_introuvable'] += 1
                            continue
                        
                        # Chercher le bénévole
                        benevole = self.trouver_benevole(benevole_nom, benevole_prenom)
                        if not benevole:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'❌ Bénévole introuvable : {benevole_prenom} {benevole_nom}'
                                )
                            )
                            stats['benevole_introuvable'] += 1
                            continue
                        
                        if not dry_run:
                            # Vérifier si le binôme existe déjà
                            binome_existant = Binome.objects.filter(
                                eleve=eleve,
                                benevole=benevole
                            ).first()
                            
                            if binome_existant:
                                if update_mode:
                                    # Réactiver le binôme s'il était inactif
                                    if not binome_existant.actif:
                                        binome_existant.actif = True
                                        binome_existant.date_debut = date_debut
                                        binome_existant.date_fin = None
                                        binome_existant.save()
                                        stats['mis_à_jour'] += 1
                                        self.stdout.write(
                                            self.style.SUCCESS(
                                                f'✓ {eleve.prenom} {eleve.nom} ↔ {benevole.prenom} {benevole.nom} - RÉACTIVÉ'
                                            )
                                        )
                                    else:
                                        stats['ignorés'] += 1
                                        self.stdout.write(
                                            self.style.WARNING(
                                                f'⊘ {eleve.prenom} {eleve.nom} ↔ {benevole.prenom} {benevole.nom} - EXISTE DÉJÀ'
                                            )
                                        )
                                else:
                                    stats['ignorés'] += 1
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f'⊘ {eleve.prenom} {eleve.nom} ↔ {benevole.prenom} {benevole.nom} - EXISTE (utilisez --update)'
                                        )
                                    )
                            else:
                                # Créer le binôme
                                binome = Binome.objects.create(
                                    eleve=eleve,
                                    benevole=benevole,
                                    date_debut=date_debut,
                                    actif=True
                                )
                                
                                # Mettre à jour les statuts
                                if eleve.statut != 'accompagne':
                                    eleve.statut = 'accompagne'
                                    eleve.save()
                                
                                if benevole.statut != 'Mentor':
                                    benevole.statut = 'Mentor'
                                    benevole.save()
                                
                                stats['créés'] += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'✓ {eleve.prenom} {eleve.nom} ↔ {benevole.prenom} {benevole.nom} - CRÉÉ'
                                    )
                                )
                        else:
                            # Mode dry-run
                            binome_existant = Binome.objects.filter(
                                eleve=eleve,
                                benevole=benevole
                            ).first()
                            
                            if binome_existant:
                                if update_mode and not binome_existant.actif:
                                    self.stdout.write(f'[DRY-RUN] Réactiverait : {eleve.prenom} {eleve.nom} ↔ {benevole.prenom} {benevole.nom}')
                                    stats['mis_à_jour'] += 1
                                else:
                                    self.stdout.write(f'[DRY-RUN] Ignorerait : {eleve.prenom} {eleve.nom} ↔ {benevole.prenom} {benevole.nom}')
                                    stats['ignorés'] += 1
                            else:
                                self.stdout.write(f'[DRY-RUN] Créerait : {eleve.prenom} {eleve.nom} ↔ {benevole.prenom} {benevole.nom}')
                                stats['créés'] += 1
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Erreur ligne {stats["total"]} : {str(e)}'
                            )
                        )
            
            # Afficher les statistiques finales
            self.stdout.write('')
            self.stdout.write('=' * 60)
            if dry_run:
                self.stdout.write(self.style.SUCCESS('✅ SIMULATION TERMINÉE'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ IMPORT TERMINÉ'))
            self.stdout.write('=' * 60)
            self.stdout.write(f'📊 Statistiques :')
            self.stdout.write(f'   • Total de lignes lues : {stats["total"]}')
            self.stdout.write(f'   • Binômes créés : {stats["créés"]}')
            self.stdout.write(f'   • Binômes mis à jour : {stats["mis_à_jour"]}')
            self.stdout.write(f'   • Binômes ignorés : {stats["ignorés"]}')
            self.stdout.write(f'   • Élèves introuvables : {stats["eleve_introuvable"]}')
            self.stdout.write(f'   • Bénévoles introuvables : {stats["benevole_introuvable"]}')
            
            if not dry_run:
                total_binomes = Binome.objects.filter(actif=True).count()
                self.stdout.write('')
                self.stdout.write(f'📈 Total de binômes actifs : {total_binomes}')
            
            # Afficher un avertissement si beaucoup d'introuvables
            if stats['eleve_introuvable'] > 0 or stats['benevole_introuvable'] > 0:
                self.stdout.write('')
                self.stdout.write(self.style.WARNING('⚠️  ATTENTION :'))
                self.stdout.write('Des élèves ou bénévoles n\'ont pas été trouvés.')
                self.stdout.write('Vérifiez les noms/prénoms dans le CSV et la base de données.')
            
        except Exception as e:
            raise CommandError(f'Erreur lors de la lecture du fichier : {str(e)}')
