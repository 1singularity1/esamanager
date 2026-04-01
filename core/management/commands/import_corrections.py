"""
Commande Django pour importer les corrections manuelles d'adresses

Après avoir corrigé le fichier CSV généré par --report,
cette commande réimporte les adresses corrigées et les géolocalise

Usage:
    python manage.py import_corrections corrections.csv
    python manage.py import_corrections corrections.csv --dry-run
"""

from django.core.management.base import BaseCommand
from core.models import Eleve, Benevole
import csv
import urllib.request
import urllib.parse
import json


class Command(BaseCommand):
    help = 'Importe les corrections d\'adresses et les géolocalise'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Fichier CSV des corrections')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode test : affiche ce qui serait fait sans modifier'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING('🔍 MODE TEST - Aucune modification'))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))
        
        self.stdout.write(self.style.SUCCESS(f'\n📥 Import des corrections depuis {csv_file}\n'))
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    type_obj = row.get('type', '')
                    nom = row.get('nom', '')
                    prenom = row.get('prenom', '')
                    adresse_corrigee = row.get('adresse_corrigee', '').strip()
                    
                    # Ignorer si pas de correction fournie
                    if not adresse_corrigee:
                        skipped_count += 1
                        self.stdout.write(f'⏭️  {prenom} {nom} - Pas de correction fournie')
                        continue
                    
                    # Chercher l'objet dans la base
                    obj = None
                    
                    if type_obj == 'Bénévole':
                        try:
                            obj = Benevole.objects.get(nom=nom, prenom=prenom)
                        except Benevole.DoesNotExist:
                            self.stdout.write(self.style.ERROR(
                                f'❌ Bénévole non trouvé : {prenom} {nom}'
                            ))
                            failed_count += 1
                            continue
                    
                    elif type_obj == 'Élève':
                        try:
                            obj = Eleve.objects.get(nom=nom, prenom=prenom)
                        except Eleve.DoesNotExist:
                            self.stdout.write(self.style.ERROR(
                                f'❌ Élève non trouvé : {prenom} {nom}'
                            ))
                            failed_count += 1
                            continue
                    
                    # Géolocaliser l'adresse corrigée
                    self.stdout.write(f'🔍 {prenom} {nom}')
                    self.stdout.write(f'   Nouvelle adresse : {adresse_corrigee}')
                    
                    result = self.geocode_address(adresse_corrigee)
                    
                    if result:
                        lat, lng, score = result
                        
                        if dry_run:
                            self.stdout.write(f'   ✅ Trouverait : {lat}, {lng} (score: {score:.0%})')
                        else:
                            # Mettre à jour l'adresse ET les coordonnées
                            obj.adresse = adresse_corrigee
                            obj.latitude = lat
                            obj.longitude = lng
                            obj.save(update_fields=['adresse', 'latitude', 'longitude'])
                            self.stdout.write(f'   ✅ Géolocalisé : {lat}, {lng} (score: {score:.0%})')
                        
                        success_count += 1
                    else:
                        self.stdout.write(f'   ❌ Échec de géolocalisation')
                        failed_count += 1
                    
                    self.stdout.write('')
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'\n❌ Fichier non trouvé : {csv_file}'))
            return
        
        # Résumé
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ'))
        self.stdout.write('='*60)
        self.stdout.write(f'  ✅ Corrigés avec succès : {success_count}')
        self.stdout.write(f'  ❌ Échecs : {failed_count}')
        self.stdout.write(f'  ⏭️  Ignorés (pas de correction) : {skipped_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  MODE TEST : Aucune donnée modifiée'))
        
        self.stdout.write('')

    def geocode_address(self, address):
        """
        Géocode une adresse avec l'API BAN
        
        Returns:
            tuple: (latitude, longitude, score) ou None
        """
        try:
            base_url = "https://api-adresse.data.gouv.fr/search/"
            params = urllib.parse.urlencode({
                'q': f"{address} Marseille",
                'limit': 1
            })
            
            url = f"{base_url}?{params}"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if data.get('features') and len(data['features']) > 0:
                    feature = data['features'][0]
                    coords = feature['geometry']['coordinates']
                    props = feature['properties']
                    
                    lng = coords[0]
                    lat = coords[1]
                    score = props.get('score', 0)
                    
                    if score > 0.4:
                        return (lat, lng, score)
            
            return None
            
        except Exception:
            return None
