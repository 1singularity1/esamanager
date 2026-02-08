"""
Script Django pour vérifier les tables dans la base de données

Usage :
    python check_tables.py
    
À placer dans le dossier racine du projet (à côté de manage.py)
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Vérifie les tables dans la base de données'

    def handle(self, *args, **options):
        
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("📊 TABLES DANS LA BASE DE DONNÉES"))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        
        tables = cursor.fetchall()
        
        self.stdout.write(f"Total de tables : {len(tables)}")
        self.stdout.write("")
        
        # Afficher toutes les tables
        for table in tables:
            table_name = table[0]
            self.stdout.write(f"  • {table_name}")
        
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("🔍 TABLES LIÉES AUX MATIÈRES ET BÉNÉVOLES"))
        self.stdout.write("=" * 70)
        self.stdout.write("")
        
        # Chercher les tables importantes
        tables_importantes = [
            'core_matiere',
            'core_benevole',
            'core_benevole_matieres',
            'core_eleve'
        ]
        
        for table_name in tables_importantes:
            existe = any(table_name == t[0] for t in tables)
            if existe:
                self.stdout.write(self.style.SUCCESS(f"✅ EXISTE : {table_name}"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ MANQUANTE : {table_name}"))
        
        self.stdout.write("")
        
        # Si core_benevole existe, afficher sa structure
        if any('core_benevole' == t[0] for t in tables):
            self.stdout.write("=" * 70)
            self.stdout.write(self.style.SUCCESS("📋 STRUCTURE DE core_benevole"))
            self.stdout.write("=" * 70)
            self.stdout.write("")
            
            cursor.execute("PRAGMA table_info(core_benevole);")
            colonnes = cursor.fetchall()
            
            self.stdout.write(f"Nombre de colonnes : {len(colonnes)}")
            self.stdout.write("")
            self.stdout.write("Colonnes :")
            for col in colonnes:
                col_name = col[1]
                col_type = col[2]
                self.stdout.write(f"  • {col_name} ({col_type})")
        
        self.stdout.write("")
        
        # Vérifier si core_benevole_matieres existe et afficher sa structure
        if any('core_benevole_matieres' == t[0] for t in tables):
            self.stdout.write("=" * 70)
            self.stdout.write(self.style.SUCCESS("📋 STRUCTURE DE core_benevole_matieres"))
            self.stdout.write("=" * 70)
            self.stdout.write("")
            
            cursor.execute("PRAGMA table_info(core_benevole_matieres);")
            colonnes = cursor.fetchall()
            
            self.stdout.write(f"Nombre de colonnes : {len(colonnes)}")
            self.stdout.write("")
            self.stdout.write("Colonnes :")
            for col in colonnes:
                col_name = col[1]
                col_type = col[2]
                self.stdout.write(f"  • {col_name} ({col_type})")
            
            self.stdout.write("")
            
            # Compter les relations
            cursor.execute("SELECT COUNT(*) FROM core_benevole_matieres;")
            count = cursor.fetchone()[0]
            self.stdout.write(f"Nombre de relations bénévole-matière : {count}")
        
        self.stdout.write("")
