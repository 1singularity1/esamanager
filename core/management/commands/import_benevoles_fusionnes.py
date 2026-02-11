"""
🎓 COMMANDE DJANGO : import_benevoles_fusionnes

Import des bénévoles depuis le fichier benevoles_fusionnes.csv
avec gestion des candidats et des nouveaux champs.
"""

from django.core.management.base import BaseCommand, CommandError
from core.models import Benevole, Matiere
import csv
import os
from decimal import Decimal, InvalidOperation


class Command(BaseCommand):
    help = 'Importe les bénévoles depuis benevoles_fusionnes.csv avec gestion des candidats'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Chemin vers le fichier CSV'
        )
        
        parser.add_argument(
            '--update',
            action='store_true',
            help='Mettre à jour les bénévoles existants (par nom+prénom)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler l\'import sans modifier la base de données'
        )

    def convert_to_boolean(self, value):
        """
        Convertit une valeur texte en Boolean.
        "oui" → True
        "" ou "non" ou autre → False
        """
        if not value:
            return False
        return value.strip().lower() == 'oui'

    def convert_to_decimal(self, value):
        """
        Convertit une valeur en Decimal pour latitude/longitude
        """
        if not value or str(value).strip() == '':
            return None
        try:
            return Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            return None

    def parse_matieres(self, matieres_str):
        """
        Parse la chaîne de matières et retourne une liste d'objets Matiere.
        """
        if not matieres_str or matieres_str.strip() == '':
            return []
        
        # Séparer par virgule
        matieres_list = [m.strip() for m in matieres_str.split(',') if m.strip()]
        matieres_objets = []
        
        for matiere_nom in matieres_list:
            try:
                matiere = Matiere.objects.get(nom__iexact=matiere_nom)
                matieres_objets.append(matiere)
            except Matiere.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"      ⚠️  Matière non trouvée : '{matiere_nom}'"
                    )
                )
        
        return matieres_objets

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        update_mode = options['update']
        dry_run = options['dry_run']
        
        if not os.path.exists(csv_file):
            raise CommandError(f'Le fichier {csv_file} n\'existe pas')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODE SIMULATION (dry-run)'))
        
        self.stdout.write('📖 Lecture du fichier CSV...')
        
        stats = {
            'total': 0,
            'créés': 0,
            'mis_à_jour': 0,
            'erreurs': 0,
            'ignorés': 0
        }
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                lecteur = csv.DictReader(f)
                
                for row in lecteur:
                    stats['total'] += 1
                    nom = row.get('Nom', '').strip()
                    prenom = row.get('Prénom', '').strip()
                    
                    try:
                        if not nom or not prenom:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⚠️  Ligne {stats["total"]} : Nom ou prénom manquant - IGNORÉ'
                                )
                            )
                            stats['ignorés'] += 1
                            continue
                        
                        # Convertir latitude/longitude
                        latitude = self.convert_to_decimal(row.get('latitude', ''))
                        longitude = self.convert_to_decimal(row.get('longitude', ''))
                        
                        # CONVERSION DES CHAMPS BOOLEAN
                        est_responsable = self.convert_to_boolean(row.get('est_responsable', ''))
                        primaire = self.convert_to_boolean(row.get('Primaire', ''))
                        college = self.convert_to_boolean(row.get('Collège', ''))
                        lycee = self.convert_to_boolean(row.get('Lycée', ''))
                        a_donne_photo = self.convert_to_boolean(row.get('a_donne_photo', ''))
                        est_ajoute_au_groupe_whatsapp = self.convert_to_boolean(row.get('est_ajoute_au groupe_WhatsApp', ''))
                        fichier = self.convert_to_boolean(row.get('fichier', ''))
                        outlook = self.convert_to_boolean(row.get('Outlook', ''))
                        extranet = self.convert_to_boolean(row.get('Extranet', ''))
                        reunion_accueil_faite = self.convert_to_boolean(row.get('Réunion d\'accueil faite', ''))
                        volet_3_casier_judiciaire = self.convert_to_boolean(row.get('Volet 3 casier judiciaire', ''))
                        
                        # Parser les matières
                        matieres_str = row.get('Matières', '')
                        matieres_objets = self.parse_matieres(matieres_str) if not dry_run else []
                        
                        # Préparer les données du bénévole (SANS matieres - c'est un ManyToMany)
                        benevole_data = {
                            'nom': nom,
                            'prenom': prenom,
                            'statut': row.get('Statut', '').strip() or 'Candidat',
                            'adresse': row.get('Adresse', '').strip(),
                            'code_postal': row.get('Code postal', '').strip(),
                            'ville': row.get('Ville', '').strip(),
                            'email': row.get('Email', '').strip(),
                            'telephone': row.get('Téléphone', '').strip(),
                            'est_responsable': est_responsable,
                            'profession': row.get('Profession', '').strip(),
                            'zone_geographique': row.get('Zone géographique', '').strip(),
                            'moyen_deplacement': row.get('Moyen de déplacement', '').strip(),
                            'primaire': primaire,
                            'college': college,
                            'lycee': lycee,
                            'a_donne_photo': a_donne_photo,
                            'est_ajoute_au_groupe_whatsapp': est_ajoute_au_groupe_whatsapp,
                            'fichier': fichier,
                            'outlook': outlook,
                            'extranet': extranet,
                            'reunion_accueil_faite': reunion_accueil_faite,
                            'volet_3_casier_judiciaire': volet_3_casier_judiciaire,
                            'commentaires': row.get('Commentaires', '').strip(),
                            'divers': row.get('Divers', '').strip(),
                            'latitude': latitude,
                            'longitude': longitude,
                            # NOUVEAUX CHAMPS (candidats)
                            'origine_contact': row.get('Origine_contact', '').strip(),
                            'date_contact': row.get('Date_contact', '').strip(),
                            'informations_complementaires': row.get('Informations_complementaires', '').strip(),
                            'disponibilites_competences': row.get('Disponibilites_competences', '').strip(),
                        }
                        
                        if not dry_run:
                            benevole_existant = Benevole.objects.filter(
                                nom=nom,
                                prenom=prenom
                            ).first()
                            
                            if benevole_existant:
                                if update_mode:
                                    # Mise à jour
                                    for key, value in benevole_data.items():
                                        setattr(benevole_existant, key, value)
                                    benevole_existant.save()
                                    
                                    # IMPORTANT : Mettre à jour les matières APRÈS save()
                                    benevole_existant.matieres.set(matieres_objets)
                                    
                                    stats['mis_à_jour'] += 1
                                    matieres_names = [m.nom for m in matieres_objets]
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f'✔ {nom} {prenom} ({benevole_data["statut"]}) - MIS À JOUR ({len(matieres_names)} matière(s))'
                                        )
                                    )
                                else:
                                    stats['ignorés'] += 1
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f'⊘ {nom} {prenom} - EXISTE DÉJÀ (utilisez --update)'
                                        )
                                    )
                            else:
                                # Création en 2 étapes
                                # 1. Créer le bénévole SANS les matières
                                benevole = Benevole.objects.create(**benevole_data)
                                
                                # 2. Associer les matières APRÈS création
                                benevole.matieres.set(matieres_objets)
                                
                                stats['créés'] += 1
                                matieres_names = [m.nom for m in matieres_objets]
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'✔ {nom} {prenom} ({benevole_data["statut"]}) - CRÉÉ ({len(matieres_names)} matière(s))'
                                    )
                                )
                        else:
                            # Mode dry-run
                            benevole_existant = Benevole.objects.filter(
                                nom=nom,
                                prenom=prenom
                            ).first()
                            
                            if benevole_existant:
                                if update_mode:
                                    self.stdout.write(f'[DRY-RUN] Mettrait à jour : {nom} {prenom} ({benevole_data["statut"]})')
                                    stats['mis_à_jour'] += 1
                                else:
                                    self.stdout.write(f'[DRY-RUN] Ignorerait : {nom} {prenom}')
                                    stats['ignorés'] += 1
                            else:
                                self.stdout.write(f'[DRY-RUN] Créerait : {nom} {prenom} ({benevole_data["statut"]})')
                                stats['créés'] += 1
                    
                    except Exception as e:
                        stats['erreurs'] += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'✗ Erreur ligne {stats["total"]} ({nom} {prenom}) : {str(e)}'
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
            self.stdout.write(f'   • Bénévoles créés : {stats["créés"]}')
            self.stdout.write(f'   • Bénévoles mis à jour : {stats["mis_à_jour"]}')
            self.stdout.write(f'   • Bénévoles ignorés : {stats["ignorés"]}')
            self.stdout.write(f'   • Erreurs : {stats["erreurs"]}')
            
            if not dry_run:
                total_benevoles = Benevole.objects.count()
                
                # Statistiques par statut
                self.stdout.write('')
                self.stdout.write('👥 Répartition par statut :')
                from django.db.models import Count
                statuts = Benevole.objects.values('statut').annotate(count=Count('id')).order_by('-count')
                for s in statuts:
                    self.stdout.write(f'   • {s["statut"]}: {s["count"]} bénévole(s)')
                
                self.stdout.write('')
                self.stdout.write(f'📈 Total de bénévoles en base : {total_benevoles}')
            
        except Exception as e:
            raise CommandError(f'Erreur lors de la lecture du fichier : {str(e)}')
