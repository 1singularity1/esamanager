"""
Commande Django pour géolocaliser tous les bénévoles et élèves

Utilise l'API BAN (Base Adresse Nationale) - gratuite et officielle
Plus précise que Nominatim pour les adresses françaises

Usage:
    python manage.py geolocalize_all
    python manage.py geolocalize_all --dry-run
    python manage.py geolocalize_all --force
    python manage.py geolocalize_all --report echecs.csv
"""

from django.core.management.base import BaseCommand
from core.models import Eleve, Benevole
import urllib.request
import urllib.parse
import json
import time
import csv


class Command(BaseCommand):
    help = 'Géolocalise tous les bénévoles et élèves'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode test : affiche ce qui serait fait sans modifier la base'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la re-géolocalisation même si déjà géolocalisé'
        )
        parser.add_argument(
            '--report',
            type=str,
            help='Génère un rapport CSV des échecs'
        )
        parser.add_argument(
            '--benevoles-only',
            action='store_true',
            help='Géolocalise uniquement les bénévoles'
        )
        parser.add_argument(
            '--eleves-only',
            action='store_true',
            help='Géolocalise uniquement les élèves'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        report_file = options.get('report')
        benevoles_only = options.get('benevoles_only', False)
        eleves_only = options.get('eleves_only', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING('🔍 MODE TEST - Aucune modification en base'))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))
        
        self.stats = {
            'total': 0,
            'success': 0,
            'already_geocoded': 0,
            'failed': 0,
            'skipped': 0
        }
        
        self.failures = []  # Pour le rapport
        
        # ============================================================
        # GÉOLOCALISER LES BÉNÉVOLES
        # ============================================================
        
        if not eleves_only:
            self.stdout.write(self.style.SUCCESS('\n📍 Géolocalisation des bénévoles'))
            self.stdout.write('='*60 + '\n')
            
            benevoles = Benevole.objects.all()
            
            if not force:
                benevoles = benevoles.filter(latitude__isnull=True) | benevoles.filter(longitude__isnull=True)
            
            count = benevoles.count()
            self.stdout.write(f'🔍 {count} bénévole(s) à géolocaliser\n')
            
            for i, benevole in enumerate(benevoles, 1):
                self.geolocalize_benevole(benevole, i, count, dry_run)
                
                # Petite pause pour ne pas surcharger l'API
                if not dry_run:
                    time.sleep(0.2)
        
        # ============================================================
        # GÉOLOCALISER LES ÉLÈVES
        # ============================================================
        
        if not benevoles_only:
            self.stdout.write(self.style.SUCCESS('\n📍 Géolocalisation des élèves'))
            self.stdout.write('='*60 + '\n')
            
            eleves = Eleve.objects.all()
            
            if not force:
                eleves = eleves.filter(latitude__isnull=True) | eleves.filter(longitude__isnull=True)
            
            count = eleves.count()
            self.stdout.write(f'🔍 {count} élève(s) à géolocaliser\n')
            
            for i, eleve in enumerate(eleves, 1):
                self.geolocalize_eleve(eleve, i, count, dry_run)
                
                # Petite pause pour ne pas surcharger l'API
                if not dry_run:
                    time.sleep(0.2)
        
        # ============================================================
        # RÉSUMÉ
        # ============================================================
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ'))
        self.stdout.write('='*60)
        self.stdout.write(f'  📍 Total traité : {self.stats["total"]}')
        self.stdout.write(f'  ✅ Géolocalisés avec succès : {self.stats["success"]}')
        self.stdout.write(f'  ↻ Déjà géolocalisés : {self.stats["already_geocoded"]}')
        self.stdout.write(f'  ⏭️  Ignorés (pas d\'adresse) : {self.stats["skipped"]}')
        self.stdout.write(f'  ❌ Échecs : {self.stats["failed"]}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  MODE TEST : Aucune donnée modifiée'))
        
        # ============================================================
        # RAPPORT DES ÉCHECS
        # ============================================================
        
        if report_file and self.failures:
            self.generate_report(report_file)
        elif self.stats['failed'] > 0 and not report_file:
            self.stdout.write(self.style.WARNING(
                f'\n💡 {self.stats["failed"]} échec(s). '
                f'Utilisez --report fichier.csv pour générer un rapport détaillé'
            ))
        
        self.stdout.write('')

    def geolocalize_benevole(self, benevole, index, total, dry_run):
        """Géolocalise un bénévole"""
        self.stats['total'] += 1
        
        nom_complet = f"{benevole.prenom} {benevole.nom}"
        
        # Vérifier si déjà géolocalisé
        if benevole.latitude and benevole.longitude:
            self.stats['already_geocoded'] += 1
            self.stdout.write(f'[{index}/{total}] ↻ {nom_complet} - Déjà géolocalisé')
            return
        
        # Vérifier si adresse présente
        if not benevole.adresse:
            self.stats['skipped'] += 1
            self.stdout.write(f'[{index}/{total}] ⏭️  {nom_complet} - Pas d\'adresse')
            return
        
        self.stdout.write(f'[{index}/{total}] 🔍 {nom_complet}')
        self.stdout.write(f'       {benevole.adresse}, {benevole.code_postal or benevole.arrondissement}')
        
        # Géolocaliser
        result = self.geocode_address(
            address=benevole.adresse,
            postal_code=benevole.code_postal or benevole.arrondissement,
            city='Marseille'
        )
        
        if result:
            lat, lng, score = result
            
            if dry_run:
                self.stdout.write(f'       ✅ Trouverait : {lat}, {lng} (score: {score:.0%})')
            else:
                benevole.latitude = lat
                benevole.longitude = lng
                benevole.save(update_fields=['latitude', 'longitude'])
                self.stdout.write(f'       ✅ Géolocalisé : {lat}, {lng} (score: {score:.0%})')
            
            self.stats['success'] += 1
        else:
            self.stdout.write(f'       ❌ Échec')
            self.stats['failed'] += 1
            self.failures.append({
                'type': 'Bénévole',
                'nom': benevole.nom,
                'prenom': benevole.prenom,
                'adresse': benevole.adresse,
                'code_postal': benevole.code_postal or benevole.arrondissement,
                'arrondissement': benevole.arrondissement,
                'suggestion': self.suggest_correction(benevole.adresse)
            })

    def geolocalize_eleve(self, eleve, index, total, dry_run):
        """Géolocalise un élève"""
        self.stats['total'] += 1
        
        nom_complet = f"{eleve.prenom} {eleve.nom}"
        
        # Vérifier si déjà géolocalisé
        if eleve.latitude and eleve.longitude:
            self.stats['already_geocoded'] += 1
            self.stdout.write(f'[{index}/{total}] ↻ {nom_complet} - Déjà géolocalisé')
            return
        
        # Vérifier si adresse présente
        if not eleve.adresse:
            self.stats['skipped'] += 1
            self.stdout.write(f'[{index}/{total}] ⏭️  {nom_complet} - Pas d\'adresse')
            return
        
        self.stdout.write(f'[{index}/{total}] 🔍 {nom_complet}')
        self.stdout.write(f'       {eleve.adresse}, {eleve.code_postal or eleve.arrondissement}')
        
        # Géolocaliser
        result = self.geocode_address(
            address=eleve.adresse,
            postal_code=eleve.code_postal or eleve.arrondissement,
            city='Marseille'
        )
        
        if result:
            lat, lng, score = result
            
            if dry_run:
                self.stdout.write(f'       ✅ Trouverait : {lat}, {lng} (score: {score:.0%})')
            else:
                eleve.latitude = lat
                eleve.longitude = lng
                eleve.save(update_fields=['latitude', 'longitude'])
                self.stdout.write(f'       ✅ Géolocalisé : {lat}, {lng} (score: {score:.0%})')
            
            self.stats['success'] += 1
        else:
            self.stdout.write(f'       ❌ Échec')
            self.stats['failed'] += 1
            self.failures.append({
                'type': 'Élève',
                'nom': eleve.nom,
                'prenom': eleve.prenom,
                'adresse': eleve.adresse,
                'code_postal': eleve.code_postal or eleve.arrondissement,
                'arrondissement': eleve.arrondissement,
                'suggestion': self.suggest_correction(eleve.adresse)
            })

    def geocode_address(self, address, postal_code, city='Marseille'):
        """
        Géocode une adresse avec l'API BAN (Base Adresse Nationale)
        
        Returns:
            tuple: (latitude, longitude, score) ou None si échec
        """
        # Normaliser l'adresse
        normalized_address = self.normalize_address(address)
        
        # Stratégie en cascade : plusieurs tentatives
        attempts = [
            # Tentative 1 : Adresse complète avec numéro
            f"{normalized_address} {postal_code} {city}",
            
            # Tentative 2 : Sans le numéro de rue
            f"{self.remove_street_number(normalized_address)} {postal_code} {city}",
            
            # Tentative 3 : Juste le code postal
            f"{postal_code} {city}",
        ]
        
        for attempt in attempts:
            result = self._call_ban_api(attempt)
            
            if result:
                # Vérifier que c'est bien Marseille
                lat, lng, score, city_found = result
                
                if 'marseille' in city_found.lower():
                    return (lat, lng, score)
        
        return None

    def _call_ban_api(self, query):
        """
        Appelle l'API BAN
        
        Returns:
            tuple: (lat, lng, score, city) ou None
        """
        try:
            # URL de l'API BAN
            base_url = "https://api-adresse.data.gouv.fr/search/"
            params = urllib.parse.urlencode({
                'q': query,
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
                    city = props.get('city', '')
                    
                    # Accepter seulement si score > 0.4 (40%)
                    if score > 0.4:
                        return (lat, lng, score, city)
            
            return None
            
        except Exception as e:
            return None

    def normalize_address(self, address):
        """Normalise une adresse (corrections automatiques)"""
        if not address:
            return ""
        
        # Dictionnaire des abréviations courantes
        replacements = {
            ' r ': ' rue ',
            ' r. ': ' rue ',
            ' av ': ' avenue ',
            ' av. ': ' avenue ',
            ' bd ': ' boulevard ',
            ' bd. ': ' boulevard ',
            ' imp ': ' impasse ',
            ' imp. ': ' impasse ',
            ' ch ': ' chemin ',
            ' ch. ': ' chemin ',
            ' all ': ' allée ',
            ' all. ': ' allée ',
            ' pl ': ' place ',
            ' pl. ': ' place ',
            ' crs ': ' cours ',
            ' crs. ': ' cours ',
            'st ': 'saint ',
            'st. ': 'saint ',
            'ste ': 'sainte ',
            'ste. ': 'sainte ',
        }
        
        normalized = address.lower()
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Nettoyer les espaces multiples
        normalized = ' '.join(normalized.split())
        
        return normalized

    def remove_street_number(self, address):
        """Retire le numéro de rue d'une adresse"""
        if not address:
            return ""
        
        parts = address.split()
        
        # Si le premier mot est un nombre (ou nombre + bis/ter), le retirer
        if parts and (parts[0].isdigit() or 
                     (len(parts[0]) > 1 and parts[0][:-3].isdigit() and parts[0][-3:] in ['bis', 'ter'])):
            return ' '.join(parts[1:])
        
        return address

    def suggest_correction(self, address):
        """Suggère une correction pour une adresse qui a échoué"""
        if not address:
            return "Ajouter une adresse valide"
        
        suggestions = []
        
        # Détecter les adresses trop vagues
        vague_words = ['chez', 'près', 'face', 'à côté', 'devant']
        if any(word in address.lower() for word in vague_words):
            suggestions.append("Adresse trop vague - Ajouter une adresse précise")
        
        # Détecter l'absence de numéro
        if not any(char.isdigit() for char in address):
            suggestions.append("Ajouter le numéro de rue")
        
        # Vérifier longueur
        if len(address) < 10:
            suggestions.append("Adresse trop courte - Vérifier")
        
        return ' | '.join(suggestions) if suggestions else "Vérifier orthographe et format"

    def generate_report(self, filename):
        """Génère un rapport CSV des échecs"""
        self.stdout.write(f'\n📄 Génération du rapport : {filename}')
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['type', 'nom', 'prenom', 'adresse', 'code_postal', 
                         'arrondissement', 'suggestion', 'adresse_corrigee']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for failure in self.failures:
                failure['adresse_corrigee'] = ''  # À remplir manuellement
                writer.writerow(failure)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Rapport généré : {filename}'))
        self.stdout.write(f'\n💡 Vous pouvez maintenant :')
        self.stdout.write(f'   1. Ouvrir {filename}')
        self.stdout.write(f'   2. Corriger les adresses dans la colonne "adresse_corrigee"')
        self.stdout.write(f'   3. Réimporter avec : python manage.py import_corrections {filename}')
