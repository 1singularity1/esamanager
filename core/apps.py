"""
🎓 APPS.PY - Configuration de l'application CORE

Ce fichier contient la configuration de l'application Django.

📚 Documentation : https://docs.djangoproject.com/en/stable/ref/applications/
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuration de l'application 'core'.
    
    Cette classe est référencée dans settings.py (INSTALLED_APPS).
    """
    
    # Type de clé primaire par défaut pour les modèles
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nom de l'application (doit correspondre au nom du dossier)
    name = 'core'
    
    # Nom lisible de l'application (affiché dans l'admin)
    verbose_name = "Gestion ESA"
    
    def ready(self):
        """
        Méthode appelée quand Django démarre.
        
        Utilisée pour :
        - Enregistrer des signaux (signals)
        - Initialiser des services
        - Charger des configurations
        
        Exemple :
            import core.signals  # Charger les signaux
        """
        pass


# ============================================================================
# 🎓 NOTES D'APPRENTISSAGE
# ============================================================================

"""
📝 À quoi sert apps.py ?

1. CONFIGURATION :
   - Nom de l'application
   - Type de clé primaire
   - Nom affiché dans l'admin

2. INITIALISATION :
   - La méthode ready() s'exécute au démarrage
   - Idéale pour charger des signaux ou des services

3. RÉFÉRENCÉE DANS settings.py :
   INSTALLED_APPS = [
       'core',  # Django cherche core.apps.CoreConfig
   ]

🔧 Options disponibles :

   class MyAppConfig(AppConfig):
       name = 'myapp'                    # OBLIGATOIRE
       verbose_name = "Mon Application" # Optionnel
       default_auto_field = '...'       # Type de clé primaire
       
       def ready(self):
           import myapp.signals  # Charger les signaux

📚 Cas d'usage de ready() :

   1. SIGNAUX :
      def ready(self):
          import core.signals
   
   2. TÂCHES PÉRIODIQUES :
      def ready(self):
          from .tasks import start_scheduler
          start_scheduler()
   
   3. VÉRIFICATIONS :
      def ready(self):
          from django.core.checks import register, Error
          @register()
          def check_config(app_configs, **kwargs):
              errors = []
              # Vérifier la config...
              return errors

⚠️ ATTENTION :
   ready() peut être appelée plusieurs fois en développement !
   Ne pas y mettre de code qui ne doit s'exécuter qu'une fois.
"""
