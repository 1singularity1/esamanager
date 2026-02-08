"""
🎓 ADMIN.PY - Configuration de l'interface d'administration Django

Django Admin = interface d'administration GRATUITE et AUTOMATIQUE !
Ici, on personnalise comment nos modèles apparaissent dans l'admin.

📚 Documentation : https://docs.djangoproject.com/en/stable/ref/contrib/admin/
"""

from django.contrib import admin
from .models import Matiere, Eleve, Benevole, Binome
from .forms import EleveAdminForm, BenevoleAdminForm


# ============================================================================
# 👨‍🎓 ADMINISTRATION DES ÉLÈVES
# ============================================================================

# ============================================================================
# 📚 ADMIN MATIÈRES
# ============================================================================

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    """Configuration de l'affichage des matières dans l'admin"""
    
    list_display = ['nom', 'ordre', 'actif']
    list_editable = ['ordre', 'actif']
    list_filter = ['actif']
    search_fields = ['nom']
    ordering = ['ordre', 'nom']


# ============================================================================
# 👨‍🎓 ADMIN ÉLÈVES
# ============================================================================

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    form = EleveAdminForm
    """Configuration de l'affichage des élèves dans l'admin"""
    
    # ========================================================================
    # 📋 LISTE DES ÉLÈVES
    # ========================================================================
    
    list_display = [
        'prenom',
        'nom',
        'classe',
        'etablissement',
        'statut',
        'statut_saisie',
        'afficher_matieres',
        'telephone_parent',
        'arrondissement',
        'est_geolocalisé',
        'date_creation',
    ]
    
    list_display_links = ['prenom', 'nom']
    
    list_filter = [
        'statut',
        'statut_saisie',
        'classe',
        'arrondissement',
        'matieres_souhaitees',  # Filtre par matière
        'date_creation',
    ]
    
    search_fields = [
        'nom',
        'prenom',
        'nom_parent',
        'prenom_parent',
        'adresse',
        'etablissement',
        'telephone',
        'telephone_parent',
    ]
    
    # Widget pour sélection multiple des matières
    filter_horizontal = ('matieres_souhaitees',)
    
    list_per_page = 50
    
    # ========================================================================
    # 📝 FORMULAIRE D'ÉDITION
    # ========================================================================
    
    readonly_fields = ['date_creation', 'date_modification', 'est_geolocalisé','statut_saisie']
    
    fieldsets = (
        ('👤 Elève', {
            'fields': (
                ('nom', 'prenom'),
                'telephone',
            )
        }),
        
        ('👨‍👩‍👧‍👦 Parents', {
            'fields': (
                ('nom_parent', 'prenom_parent'),
                'telephone_parent',
            ),
            'description': 'Coordonnées des parents ou tuteurs légaux',
        }),
        
        ('📍 Localisation', {
            'fields': (
                'ville',
                'adresse',
                'code_postal',
                'numero_rue',
                'arrondissement',
                ('latitude', 'longitude'),
            ),
            'description': 'L\'arrondissement et les coordonnées GPS sont remplis automatiquement',
        }),

        ('🏫 Scolarité', {
            'fields': (
                'classe',
                'etablissement',
                'matieres_souhaitees',  # Widget de sélection multiple
            ),
        }),
        
        ('📊 Statut', {
            'fields': (
                'statut_saisie','statut',
            ),
        }),
        
        ('📝 Remarques', {
            'fields': (
                'informations_complementaires',
            ),
            'classes': ('collapse',),
        }),
        
        ('⏰ Métadonnées', {
            'fields': (
                'date_creation',
                'date_modification',
                'est_geolocalisé',
            ),
            'classes': ('collapse',),
        }),
    )
    
    # ========================================================================
    # 🎨 MÉTHODES PERSONNALISÉES
    # ========================================================================
    
    def afficher_matieres(self, obj):
        """Affiche les matières dans la liste"""
        matieres = obj.matieres_souhaitees.all()
        if matieres:
            return ", ".join([m.nom for m in matieres[:3]])  # Max 3 pour ne pas surcharger
        return "-"
    afficher_matieres.short_description = "Matières"
    
    # ========================================================================
    # ⚡ ACTIONS RAPIDES
    # ========================================================================
    
    actions = ['marquer_accompagne', 'marquer_a_accompagner', 'marquer_complet','exporter_csv']
    
    def marquer_accompagne(self, request, queryset):
        """Marque les élèves sélectionnés comme accompagnés"""
        updated = queryset.update(statut='accompagne')
        self.message_user(request, f'{updated} élève(s) marqué(s) comme accompagné(s).')
    marquer_accompagne.short_description = "✅ Marquer comme accompagné"
    
    def marquer_a_accompagner(self, request, queryset):
        """Marque les élèves sélectionnés comme à accompagner"""
        updated = queryset.update(statut='a_accompagner')
        self.message_user(request, f'{updated} élève(s) marqué(s) comme à accompagner.')
    marquer_a_accompagner.short_description = "⏳ Marquer comme à accompagner"
    
    def marquer_complet(self, request, queryset):
        updated = queryset.update(statut_saisie='complet')
        self.message_user(request, f'{updated} fiche(s) marquée(s) comme complète(s).')
    marquer_complet.short_description = "✅ Marquer comme fiche complète"
    
    def exporter_csv(self, request, queryset):
        """Exporte les élèves sélectionnés en CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="eleves_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Nom', 'Prénom', 'Téléphone élève',
            'Nom parent', 'Prénom parent', 'Téléphone parent',
            'Classe', 'Établissement', 'Matières souhaitées',
            'Adresse', 'Arrondissement', 'Statut',
            'Informations complémentaires'
        ])
        
        for eleve in queryset:
            writer.writerow([
                eleve.nom,
                eleve.prenom,
                eleve.telephone,
                eleve.nom_parent,
                eleve.prenom_parent,
                eleve.telephone_parent,
                eleve.classe,
                eleve.etablissement,
                eleve.get_matieres_str(),  # Convertit les matières en chaîne
                eleve.adresse,
                eleve.arrondissement,
                eleve.get_statut_display(),
                eleve.informations_complementaires,
            ])
        
        return response
    exporter_csv.short_description = "📥 Exporter en CSV"
    
# ============================================================================
# 🎓 ADMINISTRATION DES BÉNÉVOLES
# ============================================================================
"""
Configuration de l'admin Django pour le modèle Benevole mis à jour.

Cette configuration organise les champs en sections logiques et ajoute
des filtres, recherches et actions personnalisées.
"""

@admin.register(Benevole)
class BenevoleAdmin(admin.ModelAdmin):
    """
    Configuration avancée de l'interface d'administration pour les bénévoles.
    """
    
    # ================================================================
    # 📋 AFFICHAGE DE LA LISTE
    # ================================================================
    
    list_display = [
        'nom',
        'prenom',
        'statut',
        'ville',
        'telephone',
        'email',
        'est_responsable',
        'est_geolocalisé',
        'date_creation'
    ]
    
    # ================================================================
    # 🔍 RECHERCHE ET FILTRES
    # ================================================================
    
    search_fields = [
        'nom',
        'prenom',
        'email',
        'telephone',
        'adresse',
        'ville',
        'code_postal',
        'profession',
        'matieres__nom',  # Recherche dans les matières
    ]
    
    list_filter = [
        'statut',
        'est_responsable',
        'ville',
        'primaire',
        'college',
        'lycee',
        'fichier',
        'outlook',
        'extranet',
        'date_creation'
    ]
    
    # ================================================================
    # 📝 ORGANISATION DU FORMULAIRE
    # ================================================================
    
    fieldsets = (
        ('👤 Informations personnelles', {
            'fields': (
                ('nom', 'prenom'),
                'profession',
                ('email', 'telephone'),
                'est_responsable'
            )
        }),
        
        ('📍 Localisation', {
            'fields': (
                'adresse',
                ('code_postal', 'ville'),
                'zone_geographique',
                'moyen_deplacement',
                ('latitude', 'longitude'),
            ),
            'classes': ('collapse',)  # Section repliable
        }),
        
        ('📊 Statut', {
            'fields': (
                'statut',
            )
        }),
        
        ('🎓 Compétences et niveaux', {
            'fields': (
                'matieres',
                ('primaire', 'college', 'lycee'),
            )
        }),
        
        ('📋 Documents et formalités', {
            'fields': (
                ('a_donne_photo', 'est_ajoute_au_groupe_whatsapp'),
                ('fichier', 'outlook', 'extranet'),
                'reunion_accueil_faite',
                'volet_3_casier_judiciaire',
            ),
            'classes': ('collapse',)
        }),
        
        ('💬 Notes', {
            'fields': (
                'commentaires',
                'divers',
            ),
            'classes': ('collapse',)
        }),
        
        ('⏰ Métadonnées', {
            'fields': (
                'date_creation',
                'date_modification',
            ),
            'classes': ('collapse',)
        }),
    )
    
    # ================================================================
    # 🔒 CHAMPS EN LECTURE SEULE
    # ================================================================
    
    readonly_fields = [
        'date_creation',
        'date_modification'
    ]
    
    # ================================================================
    # ⚙️ OPTIONS DIVERSES
    # ================================================================
    
    # Nombre de bénévoles par page
    list_per_page = 50
    
    # Sélection par page
    list_max_show_all = 200
    
    # Préserver les filtres lors de la navigation
    preserve_filters = True
    
    # Sauvegarder en bas ET en haut du formulaire
    save_on_top = True
    
    # ================================================================
    # 🎨 MÉTHODES PERSONNALISÉES POUR L'AFFICHAGE
    # ================================================================
    
    @admin.display(description='Nom complet', ordering='nom')
    def get_nom_complet_display(self, obj):
        """Affiche le nom complet avec icône selon le statut."""
        icons = {
            'Mentor': '👨‍🏫',
            'Disponible': '✅',
            'Indisponible': '❌'
        }
        icon = icons.get(obj.statut, '👤')
        return f"{icon} {obj.get_nom_complet()}"
    
    @admin.display(description='Géolocalisé', boolean=True)
    def est_geolocalisé(self, obj):
        """Affiche si le bénévole est géolocalisé."""
        return obj.est_geolocalisé()
    
    # ================================================================
    # 🔧 ACTIONS PERSONNALISÉES
    # ================================================================
    
    actions = [
        'marquer_comme_mentor',
        'marquer_comme_disponible',
        'marquer_comme_indisponible',
        'exporter_csv_complet'
    ]
    
    @admin.action(description='✅ Marquer comme Mentor')
    def marquer_comme_mentor(self, request, queryset):
        """Action pour marquer des bénévoles comme Mentor."""
        updated = queryset.update(statut='Mentor')
        self.message_user(
            request,
            f'{updated} bénévole(s) marqué(s) comme Mentor.'
        )
    
    @admin.action(description='🟢 Marquer comme Disponible')
    def marquer_comme_disponible(self, request, queryset):
        """Action pour marquer des bénévoles comme Disponible."""
        updated = queryset.update(statut='Disponible')
        self.message_user(
            request,
            f'{updated} bénévole(s) marqué(s) comme Disponible.'
        )
    
    @admin.action(description='🔴 Marquer comme Indisponible')
    def marquer_comme_indisponible(self, request, queryset):
        """Action pour marquer des bénévoles comme Indisponible."""
        updated = queryset.update(statut='Indisponible')
        self.message_user(
            request,
            f'{updated} bénévole(s) marqué(s) comme Indisponible.'
        )
    
    @admin.action(description='📥 Exporter en CSV complet')
    def exporter_csv_complet(self, request, queryset):
        """Exporte les bénévoles sélectionnés en CSV complet."""
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        # Créer la réponse HTTP
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        filename = f'benevoles_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Créer le writer CSV
        writer = csv.writer(response)
        
        # En-têtes
        writer.writerow([
            'Nom', 'Prénom', 'Statut', 'Adresse', 'Code postal', 'Ville',
            'Email', 'Téléphone', 'Est responsable',
            'Profession', 'Matières', 'Zone géographique', 'Moyen de déplacement',
            'Primaire', 'Collège', 'Lycée',
            'A donné photo', 'Groupe WhatsApp',
            'Fichier', 'Outlook', 'Extranet',
            'Réunion accueil', 'Volet 3',
            'Commentaires', 'Divers',
            'Latitude', 'Longitude'
        ])
        
        # Données
        for benevole in queryset:
            writer.writerow([
                benevole.nom,
                benevole.prenom,
                benevole.statut,
                benevole.adresse,
                benevole.code_postal,
                benevole.ville,
                benevole.email,
                benevole.telephone,
                benevole.est_responsable,
                benevole.profession,
                benevole.matieres,
                benevole.zone_geographique,
                benevole.moyen_deplacement,
                benevole.primaire,
                benevole.college,
                benevole.lycee,
                benevole.a_donne_photo,
                benevole.est_ajoute_au_groupe_whatsapp,
                benevole.fichier,
                benevole.outlook,
                benevole.extranet,
                benevole.reunion_accueil_faite,
                benevole.volet_3_casier_judiciaire,
                benevole.commentaires,
                benevole.divers,
                benevole.latitude,
                benevole.longitude,
            ])
        
        self.message_user(
            request,
            f'{queryset.count()} bénévole(s) exporté(s) en CSV.'
        )
        
        return response

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
