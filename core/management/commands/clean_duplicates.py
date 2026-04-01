"""
Commande Django pour nettoyer les doublons de bénévoles

Supprime les doublons basés sur l'email, garde le plus récent

Usage:
    python manage.py clean_duplicates
    python manage.py clean_duplicates --dry-run
"""

from django.core.management.base import BaseCommand
from core.models import Benevole, Eleve
from collections import Counter


class Command(BaseCommand):
    help = 'Nettoie les doublons de bénévoles et élèves'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode test : affiche ce qui serait fait sans supprimer'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING('🔍 MODE TEST - Aucune suppression'))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))
        
        # ============================================================
        # NETTOYER LES DOUBLONS BÉNÉVOLES (par email)
        # ============================================================
        
        self.stdout.write(self.style.SUCCESS('\n🧹 Nettoyage des doublons bénévoles\n'))
        
        # Récupérer tous les emails valides
        emails = Benevole.objects.values_list('email', flat=True)
        
        # Filtrer les emails invalides
        valid_emails = [
            email for email in emails 
            if email and '@' in email and len(email) > 5
        ]
        
        email_counts = Counter(valid_emails)
        duplicates = [email for email, count in email_counts.items() if count > 1]
        
        if not duplicates:
            self.stdout.write('✅ Aucun doublon trouvé\n')
        else:
            self.stdout.write(f'⚠️  {len(duplicates)} email(s) en double trouvé(s)\n')
            
            total_deleted = 0
            
            for email in duplicates:
                benevoles = Benevole.objects.filter(email=email).order_by('id')
                count = benevoles.count()
                
                self.stdout.write(f'\n📧 {email} ({count} occurrences)')
                
                # Vérifier si c'est vraiment la même personne
                # (même nom + prénom en normalisant)
                first = benevoles.first()
                
                for b in benevoles:
                    nom_normalized = self.normalize_name(b.nom)
                    prenom_normalized = self.normalize_name(b.prenom)
                    first_nom = self.normalize_name(first.nom)
                    first_prenom = self.normalize_name(first.prenom)
                    
                    if b.id == first.id:
                        self.stdout.write(f'   ✅ Garder : {b.prenom} {b.nom} (id={b.id})')
                    elif nom_normalized == first_nom and prenom_normalized == first_prenom:
                        # Même personne → doublon
                        if dry_run:
                            self.stdout.write(f'   ❌ Supprimerait : {b.prenom} {b.nom} (id={b.id})')
                        else:
                            self.stdout.write(f'   ❌ Supprimé : {b.prenom} {b.nom} (id={b.id})')
                            b.delete()
                        total_deleted += 1
                    else:
                        # Personnes différentes avec même email
                        self.stdout.write(f'   ⚠️  Personne différente : {b.prenom} {b.nom} (id={b.id}) - Email partagé ?')
            
            self.stdout.write(f'\n📊 Total doublons supprimés : {total_deleted}')
        
        # ============================================================
        # NETTOYER LES DOUBLONS ÉLÈVES (par nom+prenom+telephone)
        # ============================================================
        
        self.stdout.write(self.style.SUCCESS('\n🧹 Nettoyage des doublons élèves\n'))
        
        # Grouper par nom + prenom + telephone_parent
        from django.db.models import Count
        
        duplicates_eleves = Eleve.objects.values(
            'nom', 'prenom', 'telephone_parent'
        ).annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if not duplicates_eleves:
            self.stdout.write('✅ Aucun doublon trouvé\n')
        else:
            self.stdout.write(f'⚠️  {len(duplicates_eleves)} élève(s) en double trouvé(s)\n')
            
            total_deleted = 0
            
            for dup in duplicates_eleves:
                nom = dup['nom']
                prenom = dup['prenom']
                tel = dup['telephone_parent']
                
                eleves = Eleve.objects.filter(
                    nom=nom,
                    prenom=prenom,
                    telephone_parent=tel
                ).order_by('id')
                
                count = eleves.count()
                
                self.stdout.write(f'\n👤 {prenom} {nom} - {tel} ({count} occurrences)')
                
                # Garder le premier, supprimer les autres
                to_keep = eleves.first()
                to_delete = eleves[1:]
                
                self.stdout.write(f'   ✅ Garder : id={to_keep.id}')
                
                for e in to_delete:
                    if dry_run:
                        self.stdout.write(f'   ❌ Supprimerait : id={e.id}')
                    else:
                        self.stdout.write(f'   ❌ Supprimé : id={e.id}')
                        e.delete()
                    total_deleted += 1
            
            self.stdout.write(f'\n📊 Total doublons supprimés : {total_deleted}')
        
        # ============================================================
        # RÉSUMÉ
        # ============================================================
        
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODE TEST : Aucune donnée supprimée'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Nettoyage terminé !'))
        self.stdout.write('='*60 + '\n')

    def normalize_name(self, name):
        """Normalise un nom pour comparaison (enlève accents, casse, et caractères spéciaux)"""
        if not name:
            return ""
        
        import unicodedata
        import re
        
        # Enlever les accents
        normalized = unicodedata.normalize('NFD', name)
        normalized = ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')
        
        # Mettre en minuscules
        normalized = normalized.lower()
        
        # Retirer les caractères spéciaux (*, espaces multiples, etc.)
        normalized = re.sub(r'[*\s]+', '', normalized)
        
        return normalized
