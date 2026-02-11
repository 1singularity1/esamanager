from django.core.management.base import BaseCommand
from core.models import Binome

class Command(BaseCommand):
    help = 'Affecte le co-responsable du bénévole à son élève'
    
    def handle(self, *args, **options):
        # Compter les affectations
        count = 0
        
        # Parcourir tous les binômes actifs
        binomes = Binome.objects.filter(actif=True).select_related('eleve', 'benevole')
        
        for binome in binomes:
            # Si le bénévole a un co-responsable
            if binome.benevole and binome.benevole.co_responsable:
                # L'affecter à l'élève
                binome.eleve.co_responsable = binome.benevole.co_responsable
                binome.eleve.save()
                count += 1
                
                self.stdout.write(
                    f"✓ {binome.eleve.get_nom_complet()} → {binome.benevole.co_responsable.username}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ {count} élève(s) mis à jour')
        )