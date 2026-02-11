"""
📥 Commande Django pour importer les élèves depuis le CSV

Cette commande importe ou met à jour les élèves depuis le fichier CSV harmonisé.

Usage :
    python manage.py import_eleves chemin/vers/eleves_complet.csv

Fichier à placer dans :
    core/management/commands/import_eleves.py
"""

import csv
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Eleve, Matiere
from datetime import datetime


class Command(BaseCommand):
    help = 'Importe ou met à jour les élèves depuis un fichier CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Chemin vers le fichier CSV à importer'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulation sans modification de la base de données'
        )

    def decouper_adresse(self, adresse_complete):
        """
        Découpe une adresse en numéro et nom de rue
        Ex: "217 Rue des poilus" -> ("217", "Rue des poilus")
        """
        if not adresse_complete:
            return '', ''
        
        adresse_complete = adresse_complete.strip()
        
        # Pattern pour capturer le numéro au début (peut inclure bis, ter, etc.)
        match = re.match(r'^(\d+\s*(?:bis|ter|quater|[A-Za-z])?)\s+(.+)$', adresse_complete, re.IGNORECASE)
        
        if match:
            numero = match.group(1).strip()
            rue = match.group(2).strip()
            return numero, rue
        
        # Si pas de numéro trouvé, tout va dans adresse
        return '', adresse_complete

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        
        self.stdout.write("=" * 70)
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 MODE SIMULATION (DRY-RUN)"))
        self.stdout.write(self.style.SUCCESS("📥 IMPORT DES ÉLÈVES"))
        self.stdout.write("=" * 70)
        self.stdout.write()
        
        # Compteurs
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Cache des matières pour éviter les requêtes répétées
        matieres_cache = {m.nom: m for m in Matiere.objects.all()}
        
        # Ouvrir et lire le CSV
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):
                        nom = row.get('Nom famille enfant', '').strip()
                        prenom = row.get('Prénom enfant', '').strip()
                        
                        if not nom or not prenom:
                            self.stdout.write(
                                self.style.WARNING(f"⚠️  Ligne {row_num}: Nom ou prénom manquant, ignoré")
                            )
                            skipped_count += 1
                            continue
                        
                        try:
                            # Vérifier si l'élève existe déjà (insensible à la casse)
                            eleve = Eleve.objects.filter(
                                nom__iexact=nom,
                                prenom__iexact=prenom
                            ).first()
                            
                            is_new = eleve is None
                            
                            if is_new:
                                eleve = Eleve()
                            
                            # Mapper le statut
                            statut_csv = row.get('Statut', '').strip()
                            statut_mapping = {
                                'Accompagné': 'accompagne',
                                'À accompagner': 'a_accompagner',
                                'En attente': 'en_attente',
                            }
                            statut = statut_mapping.get(statut_csv, 'a_accompagner')
                            
                            # Extraire le code postal depuis Arr.
                            arr = row.get('Arr.', '').strip()
                            code_postal = arr if arr else ''
                            
                            # Extraire l'arrondissement (format "1er", "2e", etc.)
                            arrondissement = ''
                            if code_postal and code_postal.startswith('130'):
                                num = code_postal[3:5]  # 13001 -> 01
                                try:
                                    num_int = int(num)
                                    if num_int == 1:
                                        arrondissement = '1er'
                                    else:
                                        arrondissement = f'{num_int}e'
                                except ValueError:
                                    pass
                            
                            # Découper l'adresse en numéro et nom de rue
                            adresse_complete = row.get('Adresse enfant', '').strip()
                            numero_rue, nom_rue = self.decouper_adresse(adresse_complete)
                            
                            # Remplir les données de base
                            eleve.nom = nom
                            eleve.prenom = prenom
                            eleve.statut = statut
                            eleve.statut_saisie = 'complet'
                            eleve.code_postal = code_postal
                            eleve.arrondissement = arrondissement
                            eleve.numero_rue = numero_rue
                            eleve.adresse = nom_rue
                            eleve.complement_adresse = row.get('complement d\'adresse', '').strip()
                            eleve.classe = row.get('Classe', '').strip()
                            eleve.etablissement = row.get('Etablissement scolaire', '').strip()
                            eleve.telephone_parent = row.get('Mobile', '').strip()
                            eleve.email_parent = row.get('mail', '').strip()
                            eleve.ville = 'Marseille' if code_postal.startswith('13') else ''
                            
                            # Date de dernière visite
                            date_visite = row.get('Date dernière visite chez la famille', '').strip()
                            if date_visite:
                                try:
                                    # Vérifier que c'est une date valide au format YYYY-MM-DD
                                    date_obj = datetime.strptime(date_visite, '%Y-%m-%d').date()
                                    eleve.date_derniere_visite = date_obj
                                except ValueError:
                                    pass
                            
                            # Coordonnées GPS
                            try:
                                lat = row.get('latitude', '').strip()
                                lon = row.get('longitude', '').strip()
                                if lat and lon:
                                    eleve.latitude = float(lat)
                                    eleve.longitude = float(lon)
                            except (ValueError, TypeError):
                                pass
                            
                            # Informations complémentaires (fusion commentaires + complément d'infos)
                            infos_comp = []
                            
                            # Commentaires
                            commentaires = row.get('Commentaires-observations', '').strip()
                            if commentaires:
                                infos_comp.append(f"📝 Commentaires:\n{commentaires}")
                            
                            # Complément d'informations
                            complement_info = row.get('Complément d\'informatons- Autres n°', '').strip()
                            if complement_info:
                                infos_comp.append(f"ℹ️  Autres informations:\n{complement_info}")
                            
                            eleve.informations_complementaires = '\n\n'.join(infos_comp)
                            
                            # Sauvegarder l'élève
                            if not dry_run:
                                eleve.save()
                            
                            # Gérer les matières (relation ManyToMany)
                            besoins = row.get('besoins', '').strip()
                            if besoins:
                                # Séparer les matières par virgule
                                matieres_noms = [m.strip() for m in besoins.split(',') if m.strip()]
                                matieres_objets = []
                                
                                for matiere_nom in matieres_noms:
                                    if matiere_nom in matieres_cache:
                                        matieres_objets.append(matieres_cache[matiere_nom])
                                    else:
                                        # Essayer de créer la matière si elle n'existe pas
                                        if not dry_run:
                                            matiere, created = Matiere.objects.get_or_create(
                                                nom=matiere_nom,
                                                defaults={'ordre': 99}
                                            )
                                            matieres_cache[matiere_nom] = matiere
                                            matieres_objets.append(matiere)
                                            if created:
                                                self.stdout.write(
                                                    self.style.SUCCESS(f"    ✨ Matière créée: {matiere_nom}")
                                                )
                                
                                # Assigner les matières
                                if not dry_run and matieres_objets:
                                    eleve.matieres_souhaitees.set(matieres_objets)
                            
                            # Afficher le résultat
                            if is_new:
                                created_count += 1
                                action_icon = "✅"
                                action_text = "créé"
                            else:
                                updated_count += 1
                                action_icon = "🔄"
                                action_text = "mis à jour"
                            
                            adresse_affichage = f"{numero_rue} {nom_rue}".strip() if numero_rue else nom_rue
                            matieres_str = besoins if besoins else "Aucune"
                            self.stdout.write(
                                f"{action_icon} {prenom} {nom} - {eleve.classe or '?'} - {adresse_affichage[:30]}... - {action_text}"
                            )
                            
                        except Exception as e:
                            error_count += 1
                            self.stdout.write(
                                self.style.ERROR(f"❌ Erreur ligne {row_num} ({prenom} {nom}): {str(e)}")
                            )
                    
                    # Si dry-run, annuler toutes les modifications
                    if dry_run:
                        transaction.set_rollback(True)
        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"❌ Fichier non trouvé: {csv_file}")
            )
            return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur lors de la lecture du fichier: {str(e)}")
            )
            return
        
        # Afficher le résumé
        self.stdout.write()
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("📊 RÉSUMÉ DE L'IMPORT"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"✅ Élèves créés: {created_count}")
        self.stdout.write(f"🔄 Élèves mis à jour: {updated_count}")
        self.stdout.write(f"⏭️  Élèves ignorés: {skipped_count}")
        self.stdout.write(f"❌ Erreurs: {error_count}")
        self.stdout.write(f"📊 Total traité: {created_count + updated_count + skipped_count + error_count}")
        self.stdout.write("=" * 70)
        
        if dry_run:
            self.stdout.write()
            self.stdout.write(
                self.style.WARNING("⚠️  MODE SIMULATION - Aucune modification n'a été enregistrée")
            )
            self.stdout.write(
                "💡 Relancez sans --dry-run pour effectuer l'import réel"
            )
        else:
            self.stdout.write()
            self.stdout.write(
                self.style.SUCCESS("✨ Import terminé avec succès !")
            )
