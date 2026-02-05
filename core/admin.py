"""
🎓 ADMIN.PY - Configuration de l'interface d'administration Django

Django Admin = interface d'administration GRATUITE et AUTOMATIQUE !
Ici, on personnalise comment nos modèles apparaissent dans l'admin.

📚 Documentation : https://docs.djangoproject.com/en/stable/ref/contrib/admin/
"""

from django.contrib import admin
from .models import Eleve, Benevole, Binome


# ============================================================================
# 👨‍🎓 ADMINISTRATION DES ÉLÈVES
# ============================================================================

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    """
    Configuration de l'affichage des élèves dans l'admin.
    
    Décorateur @admin.register(Eleve) = équivalent à :
    admin.site.register(Eleve, EleveAdmin)
    """
    
    # ----------------------------------------------------------------
    # 📋 LISTE DES ÉLÈVES
    # ----------------------------------------------------------------
    
    # Colonnes affichées dans la liste
    list_display = [
        'prenom',
        'nom',
        'classe',
        'arrondissement',
        'statut',
        'est_geolocalisé',
        'date_creation',
    ]
    
    # Colonnes avec liens cliquables (vers la page de détail)
    list_display_links = ['prenom', 'nom']
    
    # Filtres latéraux (à droite)
    list_filter = [
        'statut',
        'classe',
        'arrondissement',
        'date_creation',
    ]
    
    # Barre de recherche
    search_fields = [
        'nom',
        'prenom',
        'adresse',
    ]
    
    # Champs modifiables directement dans la liste
    # list_editable = ['statut']  # Décommenter si besoin
    
    # Nombre d'éléments par page
    list_per_page = 50
    
    # ----------------------------------------------------------------
    # 📝 FORMULAIRE DE DÉTAIL
    # ----------------------------------------------------------------
    
    # Champs en lecture seule
    readonly_fields = [
        'date_creation',
        'date_modification',
        'est_geolocalisé',
    ]
    
    # Organisation des champs par sections
    fieldsets = (
        ('📝 Informations personnelles', {
            'fields': ('nom', 'prenom')
        }),
        ('🏫 Scolarité', {
            'fields': ('classe',)
        }),
        ('📍 Localisation', {
            'fields': (
                'adresse',
                'arrondissement',
                ('latitude', 'longitude'),  # Sur la même ligne
            ),
            'description': 'Les coordonnées GPS sont utilisées pour la carte interactive.',
        }),
        ('📊 Statut', {
            'fields': ('statut',)
        }),
        ('⏰ Métadonnées', {
            'fields': (
                'date_creation',
                'date_modification',
            ),
            'classes': ('collapse',),  # Section repliable
        }),
    )
    
    # ----------------------------------------------------------------
    # 🎨 APPARENCE
    # ----------------------------------------------------------------
    
    # Icône dans le menu (si vous utilisez django-admin-interface)
    # icon_name = 'school'
    
    # Actions personnalisées
    actions = ['marquer_comme_accompagne', 'marquer_comme_a_accompagner']
    
    def marquer_comme_accompagne(self, request, queryset):
        """Action : marquer les élèves sélectionnés comme accompagnés."""
        count = queryset.update(statut='accompagne')
        self.message_user(request, f'{count} élève(s) marqué(s) comme accompagné(s).')
    marquer_comme_accompagne.short_description = "✅ Marquer comme accompagné"
    
    def marquer_comme_a_accompagner(self, request, queryset):
        """Action : marquer les élèves sélectionnés comme à accompagner."""
        count = queryset.update(statut='a_accompagner')
        self.message_user(request, f'{count} élève(s) marqué(s) comme à accompagner.')
    marquer_comme_a_accompagner.short_description = "⏳ Marquer comme à accompagner"


# ============================================================================
# 🎓 ADMINISTRATION DES BÉNÉVOLES
# ============================================================================

@admin.register(Benevole)
class BenevoleAdmin(admin.ModelAdmin):
    """Configuration de l'affichage des bénévoles dans l'admin."""
    
    list_display = [
        'prenom',
        'nom',
        'email',
        'telephone',
        'arrondissement',
        'disponibilite',
        'nombre_binomes',
        'date_creation',
    ]
    
    list_display_links = ['prenom', 'nom']
    
    list_filter = [
        'disponibilite',
        'arrondissement',
        'date_creation',
    ]
    
    search_fields = [
        'nom',
        'prenom',
        'email',
        'telephone',
        'adresse',
    ]
    
    readonly_fields = [
        'date_creation',
        'date_modification',
        'nombre_binomes',
    ]
    
    fieldsets = (
        ('📝 Informations personnelles', {
            'fields': ('nom', 'prenom')
        }),
        ('📧 Contact', {
            'fields': ('email', 'telephone')
        }),
        ('📍 Localisation', {
            'fields': (
                'adresse',
                'arrondissement',
                ('latitude', 'longitude'),
            ),
        }),
        ('📊 Disponibilité', {
            'fields': ('disponibilite',)
        }),
        ('⏰ Métadonnées', {
            'fields': (
                'date_creation',
                'date_modification',
                'nombre_binomes',
            ),
            'classes': ('collapse',),
        }),
    )
    
    list_per_page = 50
    
    # Méthode personnalisée pour afficher le nombre de binômes
    def nombre_binomes(self, obj):
        """Retourne le nombre de binômes actifs du bénévole."""
        return obj.binomes.filter(actif=True).count()
    nombre_binomes.short_description = "Nombre de binômes"
    
    # Actions personnalisées
    actions = ['marquer_comme_disponible', 'marquer_comme_occupe']
    
    def marquer_comme_disponible(self, request, queryset):
        count = queryset.update(disponibilite='disponible')
        self.message_user(request, f'{count} bénévole(s) marqué(s) comme disponible(s).')
    marquer_comme_disponible.short_description = "✅ Marquer comme disponible"
    
    def marquer_comme_occupe(self, request, queryset):
        count = queryset.update(disponibilite='occupe')
        self.message_user(request, f'{count} bénévole(s) marqué(s) comme occupé(s).')
    marquer_comme_occupe.short_description = "⏳ Marquer comme occupé"


# ============================================================================
# 🔗 ADMINISTRATION DES BINÔMES
# ============================================================================

@admin.register(Binome)
class BinomeAdmin(admin.ModelAdmin):
    """Configuration de l'affichage des binômes dans l'admin."""
    
    list_display = [
        'eleve',
        'benevole',
        'date_debut',
        'date_fin',
        'actif',
        'duree',
    ]
    
    list_display_links = ['eleve']
    
    list_filter = [
        'actif',
        'date_debut',
        'date_fin',
    ]
    
    search_fields = [
        'eleve__nom',      # Recherche dans le nom de l'élève
        'eleve__prenom',
        'benevole__nom',   # Recherche dans le nom du bénévole
        'benevole__prenom',
    ]
    
    # Filtres automatiques sur les clés étrangères
    autocomplete_fields = ['eleve', 'benevole']
    
    readonly_fields = [
        'date_creation',
        'date_modification',
        'duree',
    ]
    
    fieldsets = (
        ('🔗 Association', {
            'fields': ('eleve', 'benevole')
        }),
        ('📅 Dates', {
            'fields': (
                ('date_debut', 'date_fin'),
                'duree',
            ),
        }),
        ('📝 Informations', {
            'fields': ('actif', 'notes')
        }),
        ('⏰ Métadonnées', {
            'fields': (
                'date_creation',
                'date_modification',
            ),
            'classes': ('collapse',),
        }),
    )
    
    list_per_page = 50
    
    # Méthode personnalisée pour calculer la durée
    def duree(self, obj):
        """Calcule la durée de l'accompagnement."""
        if obj.date_fin:
            delta = obj.date_fin - obj.date_debut
            return f"{delta.days} jours"
        else:
            from datetime import date
            delta = date.today() - obj.date_debut
            return f"{delta.days} jours (en cours)"
    duree.short_description = "Durée"
    
    # Actions personnalisées
    actions = ['activer_binomes', 'desactiver_binomes']
    
    def activer_binomes(self, request, queryset):
        count = queryset.update(actif=True)
        self.message_user(request, f'{count} binôme(s) activé(s).')
    activer_binomes.short_description = "✅ Activer les binômes"
    
    def desactiver_binomes(self, request, queryset):
        from datetime import date
        count = queryset.update(actif=False, date_fin=date.today())
        self.message_user(request, f'{count} binôme(s) désactivé(s).')
    desactiver_binomes.short_description = "❌ Désactiver les binômes"


# ============================================================================
# 🎨 PERSONNALISATION DU SITE ADMIN
# ============================================================================

# Titre du site
admin.site.site_header = "ESA Manager - Administration"

# Titre de la page
admin.site.site_title = "ESA Admin"

# Texte de l'en-tête
admin.site.index_title = "Gestion de l'association ESA"


# ============================================================================
# 🎓 NOTES D'APPRENTISSAGE
# ============================================================================

"""
📝 Options de l'Admin Django :

1. LISTE (list_display, list_filter, etc.) :
   - list_display : Colonnes affichées
   - list_filter : Filtres latéraux
   - search_fields : Champs recherchables
   - list_editable : Champs modifiables dans la liste
   - list_per_page : Pagination

2. FORMULAIRE (fieldsets, readonly_fields, etc.) :
   - fieldsets : Organisation en sections
   - readonly_fields : Champs non modifiables
   - autocomplete_fields : Autocomplétion pour ForeignKey
   - raw_id_fields : Sélection par ID

3. ACTIONS :
   - Fonctions appelées sur les objets sélectionnés
   - Utile pour modifications en masse

4. MÉTHODES PERSONNALISÉES :
   - def ma_methode(self, obj) : Calcul ou affichage personnalisé
   - Utiliser .short_description pour le label

🎨 Personnalisation avancée :
   - Inline : Éditer les relations dans la même page
   - Filters : Filtres personnalisés
   - Forms : Formulaires personnalisés
   - Templates : Changer l'apparence

📚 Pour aller plus loin :
   https://docs.djangoproject.com/en/stable/ref/contrib/admin/
"""
