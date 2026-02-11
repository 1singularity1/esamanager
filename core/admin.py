"""
🎓 ADMIN.PY - Configuration de l'interface d'administration Django

Django Admin = interface d'administration GRATUITE et AUTOMATIQUE !
Ici, on personnalise comment nos modèles apparaissent dans l'admin.

📚 Documentation : https://docs.djangoproject.com/en/stable/ref/contrib/admin/
"""

from django.contrib import admin
from .models import Matiere, Eleve, Benevole, Binome, ProfilUtilisateur
from .forms import EleveAdminForm, BenevoleAdminForm
from django.utils.html import format_html
from django.contrib.auth.models import User


# ============================================================================
# Admin pour le profil utilisateur
# ============================================================================
@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ['user', 'benevole']
    list_filter = ['benevole']
    search_fields = ['user__username', 'benevole__nom', 'benevole__prenom']
    
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
        'coresponsable_vignette',
        'statut_colore',
        'classe',
        'statut_saisie',
        'telephone_parent',
        'code_postal',
        'date_creation',
    ]
    
    list_display_links = ['prenom', 'nom']
    
    list_filter = [
        'statut',
        'classe',
        'code_postal',
        'matieres_souhaitees',  # Filtre par matière
        'date_creation',
        'co_responsable',
    ]
    
    search_fields = [
        'nom',
        'prenom',
        'adresse',
        'etablissement',
        'telephone',
        'telephone_parent',
        'code_postal',
    ]
    
    # Widget pour sélection multiple des matières
    filter_horizontal = ('matieres_souhaitees',)
    
    list_per_page = 50
    
    # ========================================================================
    # 📝 FORMULAIRE D'ÉDITION
    # ========================================================================
    
    readonly_fields = ['date_creation', 'date_modification', 'est_geolocalisé','statut_saisie','code_postal','arrondissement','latitude','longitude']
    
    fieldsets = (
        ('👤 Elève', {
            'fields': (
                ('nom', 'prenom'),
                'telephone',
            )
        }),
        
        ('👤 Gestion', {
            'fields': ('co_responsable',)
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
    
    # Préserver les filtres lors de la navigation
    preserve_filters = True
    
    # Sauvegarder en bas ET en haut du formulaire
    save_on_top = True


    # ========================================================================
    # 🎨 STATUTS COLORES
    # ========================================================================
    def statut_colore(self, obj):
        """Affiche le statut avec une couleur."""
        couleurs = {
            'accompagne': '#28a745',      # Vert
            'a_accompagner': '#dc3545',   # Rouge
            'en_attente': '#ffc107',      # Jaune/Orange
            'archive': '#6c757d',         # Gris
        }
        
        couleur = couleurs.get(obj.statut, '#6c757d')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            couleur,
            obj.get_statut_display()
        )
    
    statut_colore.short_description = 'Statut'
    statut_colore.admin_order_field = 'statut'  # Permet de trier par statut

    @admin.display(description='Co-responsable', ordering='co_responsable')
    def coresponsable_vignette(self, obj):
        # 1. Définir les couleurs de fond pour chaque statut
        # 2. Utiliser format_html() pour générer une <span> avec style
        # 3. Le style doit inclure : background, padding, border-radius, color (texte blanc)
        if not obj.co_responsable:
            return '-'
    
        colors = {
            'Georges': '#007bff',
            'David': '#6c757d',
            'Bernadette': '#dc3545',
            'Sylvie': '#28a745',
            'Clara': '#8B5CF6',
            'Martine': "#a1a728",
            'Gilbert': "#123f0c",
        }
        color = colors.get(obj.co_responsable.profil.benevole.get_prenom(), '#6c757d')
        return format_html(
            '<span style="background-color: {}; padding: 4px 8px; border-radius: 4px; color: white;">{}</span>',
            color,
            obj.co_responsable.profil.benevole.get_prenom()
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
    
     # Méthode pour afficher le bénévole associé
    def co_responsable_nom(self, obj):
        if obj.co_responsable and hasattr(obj.co_responsable, 'profil'):
            return obj.co_responsable.profil.benevole.get_nom_complet()
        return '-'
    
    co_responsable_nom.short_description = 'Co-responsable'

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
        'coresponsable_vignette',
        'statut_colore',
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
        'co_responsable__profil__benevole__nom',
        'co_responsable__profil__benevole__prenom',
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
        ('👤 Gestion', {
            'fields': ('co_responsable',)
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
        ('Candidature (nouveaux candidats)', {
            'fields': (
                'origine_contact',
                'date_contact',
                'disponibilites_competences',
                'informations_complementaires',
            ),
            'classes': ('collapse',),
            'description': 'Informations spécifiques aux candidats à recontacter'
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
    
    # ========================================================================
    # 5. ACTIONS PERSONNALISÉES UTILES
    # ========================================================================
    actions = [
        'convertir_en_mentor',
        'marquer_comme_disponible',
        'marquer_comme_indisponible',
    ]
    
    @admin.action(description="Convertir en Mentor")
    def convertir_en_mentor(self, request, queryset):
        updated = queryset.update(statut='Mentor')
        self.message_user(request, f"{updated} bénévole(s) converti(s) en Mentor.")
    
    @admin.action(description="Marquer comme Disponible")
    def marquer_comme_disponible(self, request, queryset):
        updated = queryset.update(statut='Disponible')
        self.message_user(request, f"{updated} bénévole(s) marqué(s) comme Disponible.")
    
    @admin.action(description="Marquer comme Indisponible")
    def marquer_comme_indisponible(self, request, queryset):
        updated = queryset.update(statut='Indisponible')
        self.message_user(request, f"{updated} bénévole(s) marqué(s) comme Indisponible.")

    # ================================================================
    # 🎨 MÉTHODES PERSONNALISÉES POUR L'AFFICHAGE
    # ================================================================
    
    # ========================================================================
    # 🎨 STATUTS COLORES
    # ========================================================================
    def statut_colore(self, obj):
        """Affiche le statut avec une couleur."""
        couleurs = {
            'Mentor': '#28a745',      # Vert
            'Indisponible': '#dc3545',   # Rouge
            'Disponible': '#ffc107',      # Jaune/Orange
            'Archive': '#6c757d',         # Gris
            'Candidat': '#17a2b8',         # Bleu
        }
        
        couleur = couleurs.get(obj.statut, '#6c757d')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            couleur,
            obj.get_statut_display()
        )
    
    statut_colore.short_description = 'Statut'
    statut_colore.admin_order_field = 'statut'  # Permet de trier par statut

    @admin.display(description='Co-responsable', ordering='co_responsable')
    def coresponsable_vignette(self, obj):
        # 1. Définir les couleurs de fond pour chaque statut
        # 2. Utiliser format_html() pour générer une <span> avec style
        # 3. Le style doit inclure : background, padding, border-radius, color (texte blanc)
        if not obj.co_responsable:
            return '-'
    
        colors = {
            'Georges': '#007bff',
            'David': '#6c757d',
            'Bernadette': '#dc3545',
            'Sylvie': '#28a745',
            'Clara': '#8B5CF6',
            'Martine': "#a1a728",
            'Gilbert': "#123f0c",
        }
        color = colors.get(obj.co_responsable.profil.benevole.get_prenom(), '#6c757d')
        return format_html(
            '<span style="background-color: {}; padding: 4px 8px; border-radius: 4px; color: white;">{}</span>',
            color,
            obj.co_responsable.profil.benevole.get_prenom()
        )

    # Méthode pour afficher le bénévole associé au co-responsable
    @admin.display(description='Co-responsable', ordering='co_responsable__username')
    def co_responsable_nom(self, obj):
        if obj.co_responsable and hasattr(obj.co_responsable, 'profil'):
            return obj.co_responsable.profil.benevole.get_nom_complet()
        return '-'
    
    co_responsable_nom.short_description = 'Co-responsable'

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
        'exporter_csv_complet',
        'assigner_co_responsable'
    ]
    
    @admin.display(description='Statut', ordering='statut')
    def statut_vignette(self, obj):
        # 1. Définir les couleurs de fond pour chaque statut
        # 2. Utiliser format_html() pour générer une <span> avec style
        # 3. Le style doit inclure : background, padding, border-radius, color (texte blanc)
        colors = {
            'Mentor': '#007bff',
            'Disponible': '#28a745',
            'Indisponible': '#dc3545'
        }
        color = colors.get(obj.statut, '#6c757d')
        return format_html(
            '<span style="background-color: {}; padding: 4px 8px; border-radius: 4px; color: white;">{}</span>',
            color,
            obj.statut
        )

    @admin.action(description='Assigner un co-responsable aux bénévoles sélectionnés')
    def assigner_co_responsable(self, request, queryset):
        from django import forms
        from django.shortcuts import render, redirect
        from django.contrib.auth.models import User
        
        class CoResponsableForm(forms.Form):
            co_responsable = forms.ModelChoiceField(
                queryset=User.objects.filter(profil__isnull=False),
                label="Co-responsable",
                help_text="Sélectionnez l'utilisateur à assigner"
            )
        
        # Si le formulaire est soumis
        if 'apply' in request.POST:
            print("🔍 FORMULAIRE SOUMIS")
            form = CoResponsableForm(request.POST)
            
            if form.is_valid():
                print("✅ FORMULAIRE VALIDE")
                co_responsable = form.cleaned_data['co_responsable']
                
                # IMPORTANT : Récupérer les IDs depuis le POST
                selected = request.POST.getlist('_selected_action')
                print(f"IDs sélectionnés: {selected}")
                
                # Mettre à jour les bénévoles sélectionnés
                count = Benevole.objects.filter(pk__in=selected).update(co_responsable=co_responsable)
                print(f"✅ {count} bénévole(s) mis à jour")
                
                self.message_user(
                    request,
                    f'{count} bénévole(s) assigné(s) à {co_responsable.username}'
                )
                return redirect('admin:core_benevole_changelist')
            else:
                print("❌ FORMULAIRE INVALIDE:", form.errors)
        
        print("📝 AFFICHAGE DU FORMULAIRE")
        form = CoResponsableForm()
        
        return render(
            request,
            'admin/assigner_co_responsable.html',
            {
                'form': form,
                'benevoles': queryset,
                'selected_ids': queryset.values_list('pk', flat=True),
                'title': 'Assigner un co-responsable'
            }
        )
    
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
