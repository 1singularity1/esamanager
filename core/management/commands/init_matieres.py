"""
🎓 Commande Django pour initialiser les matières

Cette commande crée les matières par défaut dans la base de données.

Usage :
    python manage.py init_matieres

Fichier à placer dans :
    core/management/commands/init_matieres.py
"""

from django.core.management.base import BaseCommand
from core.models import Matiere


class Command(BaseCommand):
    help = 'Initialise les matières disponibles pour l\'accompagnement'

    def handle(self, *args, **options):
        
        matieres_data = [
            {'nom': 'Français', 'ordre': 1},
            {'nom': 'Mathématiques', 'ordre': 2},
            {'nom': 'Anglais', 'ordre': 3},
            {'nom': 'Espagnol', 'ordre': 4},
            {'nom': 'Allemand', 'ordre': 5},
            {'nom': 'Histoire-Géographie', 'ordre': 6},
            {'nom': 'Sciences (SVT)', 'ordre': 7},
            {'nom': 'Physique-Chimie', 'ordre': 8},
            {'nom': 'Philosophie', 'ordre': 9},
            {'nom': 'Économie', 'ordre': 10},
            {'nom': 'Aide aux devoirs (toutes matières)', 'ordre': 11},
            {'nom': 'Méthodologie', 'ordre': 12},
            {'nom': 'Autre', 'ordre': 99},
        ]
        
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("📚 INITIALISATION DES MATIÈRES"))
        self.stdout.write("=" * 70)
        self.stdout.write()
        
        created_count = 0
        existing_count = 0
        
        for data in matieres_data:
            matiere, created = Matiere.objects.get_or_create(
                nom=data['nom'],
                defaults={'ordre': data['ordre']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Créée : {matiere.nom}")
                )
            else:
                existing_count += 1
                self.stdout.write(
                    f"⏭️  Existe déjà : {matiere.nom}"
                )
        
        self.stdout.write()
        self.stdout.write("=" * 70)
        self.stdout.write(f"✅ Matières créées : {created_count}")
        self.stdout.write(f"⏭️  Matières existantes : {existing_count}")
        self.stdout.write(f"📊 Total : {created_count + existing_count}")
        self.stdout.write("=" * 70)
        self.stdout.write()
        self.stdout.write(
            self.style.SUCCESS("✨ Initialisation terminée !")
        )
