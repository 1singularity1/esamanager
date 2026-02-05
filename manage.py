#!/usr/bin/env python
"""
🎓 MANAGE.PY - Point d'entrée de Django

Ce fichier est créé automatiquement par Django.
Il permet d'exécuter des commandes administratives.

Commandes principales :
- python manage.py runserver      → Lancer le serveur
- python manage.py migrate         → Appliquer migrations
- python manage.py makemigrations  → Créer migrations
- python manage.py createsuperuser → Créer admin
- python manage.py shell           → Console Python interactive

⚠️ NE PAS MODIFIER CE FICHIER (sauf cas très rare)
"""
import os
import sys


def main():
    """Lance les commandes administratives Django."""
    # Indique à Django où se trouve le fichier settings.py
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esa_manager.settings')
    
    try:
        # Importer la fonction d'exécution des commandes
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Exécuter la commande
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
