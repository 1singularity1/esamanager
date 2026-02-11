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
            # Matières principales
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
            
            # Compétences de base (primaire surtout)
            {'nom': 'Lecture', 'ordre': 20},
            {'nom': 'Écriture', 'ordre': 21},
            {'nom': 'Compréhension', 'ordre': 22},
            {'nom': 'Orthographe', 'ordre': 23},
            {'nom': 'Calcul', 'ordre': 24},
            {'nom': 'Conjugaison', 'ordre': 25},
            {'nom': 'Grammaire', 'ordre': 26},
            
            # Compétences transversales
            {'nom': 'Méthodologie', 'ordre': 30},
            {'nom': 'Concentration', 'ordre': 31},
            {'nom': 'Organisation', 'ordre': 32},
            {'nom': 'Compréhension des consignes', 'ordre': 33},
            {'nom': 'Mémoire', 'ordre': 34},
            {'nom': 'Orientation', 'ordre': 35},
            
            # Général
            {'nom': 'Aide aux devoirs (toutes matières)', 'ordre': 90},
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
