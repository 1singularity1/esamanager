"""
🎓 MODELS.PY - Modèles de données de l'application ESA

Un modèle = une table dans la base de données.
Chaque attribut = une colonne de la table.

📚 Documentation : https://docs.djangoproject.com/en/stable/topics/db/models/
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ============================================================================
# 📚 MODÈLE MATIÈRE
# ============================================================================

class Matiere(models.Model):
    """
    Représente une matière scolaire disponible pour l'accompagnement
    """
    
    nom = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la matière"
    )
    
    ordre = models.IntegerField(
        default=0,
        verbose_name="Ordre d'affichage",
        help_text="Pour trier les matières dans l'ordre souhaité"
    )
    
    actif = models.BooleanField(
        default=True,
        verbose_name="Matière active"
    )
    
    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom


# ============================================================================
# 👨‍🎓 MODÈLE ÉLÈVE
# ============================================================================

class Eleve(models.Model):
    """
    Représente un élève de l'association ESA
    """
    
    # ========================================================================
    # 📚 CHOIX PRÉDÉFINIS (Données de référence)
    # ========================================================================
    
    CLASSE_CHOICES = [
        # Primaire
        ('CP', 'CP'),
        ('CE1', 'CE1'),
        ('CE2', 'CE2'),
        ('CM1', 'CM1'),
        ('CM2', 'CM2'),
        # Collège
        ('6e', '6e'),
        ('5e', '5e'),
        ('4e', '4e'),
        ('3e', '3e'),
        # Lycée
        ('2de', '2de'),
        ('1re', '1re'),
        ('Terminale', 'Terminale'),
        # Professionnel
        ('CAP', 'CAP'),
        ('ULIS', 'ULIS'),
    ]
    
    STATUT_CHOICES = [
        ('accompagne', 'Accompagné'),
        ('a_accompagner', 'À accompagner'),
        ('en_attente', 'En attente'),
        ('archive', 'Archivé'),
    ]
    
    # Ajouter ce champ (par exemple après informations_complementaires)
    co_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eleves_geres',
        verbose_name="Co-responsable",
        help_text="Utilisateur en charge de cet élève"
    )

    # ========================================================================
    # 👤 INFORMATIONS PERSONNELLES
    # ========================================================================
    
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom"
    )
    
    prenom = models.CharField(
        max_length=100,
        verbose_name="Prénom"
    )
    
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone de l'élève",
        help_text="Numéro de téléphone personnel de l'élève"
    )
    
    # ========================================================================
    # 👨‍👩‍👧‍👦 INFORMATIONS PARENTS
    # ========================================================================
    
    nom_parent = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom du parent",
        help_text="Nom de famille du parent/tuteur légal"
    )
    
    prenom_parent = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Prénom du parent",
        help_text="Prénom du parent/tuteur légal"
    )
    
    telephone_parent = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Téléphone des parents",
        help_text="Numéro de téléphone principal des parents"
    )
    
    # ========================================================================
    # 🏫 SCOLARITÉ
    # ========================================================================
    
    classe = models.CharField(
        max_length=50,
        choices=CLASSE_CHOICES,
        blank=True,
        verbose_name="Classe"
    )
    
    etablissement = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Établissement scolaire",
        help_text="Nom de l'école, collège ou lycée"
    )
    
    # 📚 RELATION MANY-TO-MANY AVEC LES MATIÈRES
    matieres_souhaitees = models.ManyToManyField(
        Matiere,
        blank=True,
        related_name='eleves',
        verbose_name="Matières souhaitées",
        help_text="Sélectionnez une ou plusieurs matières"
    )
    
    # ========================================================================
    # 📍 LOCALISATION
    # ========================================================================
    
    code_postal = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Code postal",
        help_text="Ex: 13001, 13008"
    )

    ville = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ville",
        help_text="Ex: Marseille, Aix-en-Provence"
    )

    numero_rue = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Numéro",
        help_text="Numéro de rue (ex: 12, 12 bis, 12 ter)"
    )

    adresse = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Nom de la rue",
        help_text="Ex: Rue de la République, Avenue du Prado"
    )

    code_postal = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Code postal",
        help_text="Ex: 13001, 13008"
    )
    
    arrondissement = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Arrondissement",
        help_text="Ex: 1er, 2e, 3e, etc."
    )
    
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Latitude"
    )
    
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Longitude"
    )
    
    # ========================================================================
    # 📊 STATUT
    # ========================================================================
    
    STATUT_SAISIE_CHOICES = [
    ('brouillon', 'Brouillon (saisie en cours)'),
    ('complet', 'Complet (validé)'),
]

    statut_saisie = models.CharField(
        max_length=20,
        choices=STATUT_SAISIE_CHOICES,
        default='brouillon',
        verbose_name="Statut de saisie",
        help_text="Brouillon = saisie en cours, Complet = fiche validée"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='a_accompagner',
        verbose_name="Statut d'accompagnement"
    )
    
    # ========================================================================
    # 📝 INFORMATIONS COMPLÉMENTAIRES
    # ========================================================================
    
    informations_complementaires = models.TextField(
        blank=True,
        verbose_name="Informations complémentaires",
        help_text="Toute information utile (besoins spécifiques, disponibilités, etc.)"
    )
    
    # ========================================================================
    # ⏰ MÉTADONNÉES
    # ========================================================================
    
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    # ========================================================================
    # 👨‍👩‍👧‍👦 INFORMATIONS PARENTS - Ajouter ce champ après telephone_parent
    # ========================================================================

    email_parent = models.EmailField(
        blank=True,
        verbose_name="Email des parents",
        help_text="Adresse email de contact des parents"
    )

    # ========================================================================
    # 📍 LOCALISATION - Ajouter ce champ après adresse
    # ========================================================================

    complement_adresse = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Complément d'adresse",
        help_text="Ex: Bâtiment A, 3ème étage, appartement 12"
    )

    # ========================================================================
    # 📅 SUIVI - Ajouter cette section après informations_complementaires
    # ========================================================================

    date_derniere_visite = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de dernière visite",
        help_text="Date de la dernière visite effectuée chez la famille"
    )
    # ========================================================================
    # 🎨 MÉTADONNÉES DU MODÈLE
    # ========================================================================
    
    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def get_nom_complet(self):
        """Retourne le nom complet de l'élève"""
        return f"{self.prenom} {self.nom}"
    
    def get_nom_parent_complet(self):
        """Retourne le nom complet du parent"""
        if self.prenom_parent and self.nom_parent:
            return f"{self.prenom_parent} {self.nom_parent}"
        elif self.nom_parent:
            return self.nom_parent
        return ""
    
    def get_matieres_liste(self):
        """Retourne la liste des matières souhaitées"""
        return list(self.matieres_souhaitees.all())
    
    def get_matieres_str(self):
        """Retourne les matières sous forme de chaîne"""
        matieres = self.matieres_souhaitees.all()
        return ", ".join([m.nom for m in matieres]) if matieres else "Aucune"
    
    def est_geolocalisé(self):
        """Vérifie si l'élève a des coordonnées GPS"""
        return self.latitude is not None and self.longitude is not None
    
    est_geolocalisé.boolean = True
    est_geolocalisé.short_description = "Géolocalisé"


# ============================================================================
# 🎓 MODÈLE BÉNÉVOLE - VERSION COMPLÈTE
# ============================================================================

class Benevole(models.Model):
    """
    Représente un bénévole de l'association ESA.
    
    Ce modèle contient toutes les informations nécessaires pour gérer
    les bénévoles : coordonnées, disponibilités, compétences, documents, etc.
    """
    
    # Ajouter ce champ (par exemple après les informations complémentaires)
    co_responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='benevoles_geres',
        verbose_name="Co-responsable",
        help_text="Utilisateur en charge de ce bénévole"
    )

    # ================================================================
    # 📝 INFORMATIONS PERSONNELLES
    # ================================================================
    
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de famille",
        help_text="Nom de famille du bénévole"
    )
    
    prenom = models.CharField(
        max_length=100,
        verbose_name="Prénom"
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name="Email",
        help_text="Adresse email du bénévole"
    )
    
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone",
        help_text="Numéro de téléphone"
    )
    
    profession = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Profession",
        help_text="Profession actuelle ou passée"
    )
    
    # ================================================================
    # 📍 LOCALISATION
    # ================================================================
    
    adresse = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Adresse complète"
    )
    
    code_postal = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Code postal",
        help_text="Exemple : 13001, 13190"
    )
    
    arrondissement = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Arrondissement",
        help_text="Ex: 1er, 2e, 3e, etc."
    )
    
    ville = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ville",
        help_text="Exemple : Marseille, Allauch"
    )
    
    numero_rue = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Numéro",
        help_text="Numéro de rue (ex: 12, 12 bis, 12 ter)"
    )
    
    zone_geographique = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Zone géographique",
        help_text="Zone d'intervention préférée"
    )
    
    latitude = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ],
        verbose_name="Latitude",
        help_text="Coordonnée GPS pour la carte"
    )
    
    longitude = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        verbose_name="Longitude",
        help_text="Coordonnée GPS pour la carte"
    )
    
    moyen_deplacement = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Moyen de déplacement",
        help_text="Exemple : Véhicule personnel, Transport en commun"
    )
    
    # ================================================================
    # 📊 STATUT
    # ================================================================
    
    STATUT_CHOICES = [
        ('Mentor', 'Mentor'),
        ('Disponible', 'Disponible'),
        ('Indisponible', 'Indisponible'),
    ]
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='Disponible',
        verbose_name="Statut",
        help_text="Statut actuel du bénévole"
    )
    
    est_responsable = models.BooleanField(
        default=False,
        verbose_name="Est responsable",
        help_text="Indique si la personne est responsable dans l'association"
    )
    
    # ================================================================
    # 🎓 COMPÉTENCES ET NIVEAUX D'INTERVENTION
    # ================================================================
    
    # Relation ManyToMany vers le modèle Matiere
    matieres = models.ManyToManyField(
        Matiere,
        blank=True,
        verbose_name="Matières enseignées",
        help_text="Matières que le bénévole peut enseigner (choix multiples)",
        related_name='benevoles'
    )
    
    # Niveaux d'intervention (BooleanField)
    primaire = models.BooleanField(
        default=False,
        verbose_name="Primaire",
        help_text="Peut accompagner niveau primaire"
    )
    
    college = models.BooleanField(
        default=False,
        verbose_name="Collège",
        help_text="Peut accompagner niveau collège"
    )
    
    lycee = models.BooleanField(
        default=False,
        verbose_name="Lycée",
        help_text="Peut accompagner niveau lycée"
    )
    
    # ================================================================
    # 📋 DOCUMENTS ET FORMALITÉS (tous en BooleanField)
    # ================================================================
    
    a_donne_photo = models.BooleanField(
        default=False,
        verbose_name="A donné photo",
        help_text="Photo fournie"
    )
    
    est_ajoute_au_groupe_whatsapp = models.BooleanField(
        default=False,
        verbose_name="Groupe WhatsApp",
        help_text="Ajouté au groupe WhatsApp"
    )
    
    fichier = models.BooleanField(
        default=False,
        verbose_name="Fichier",
        help_text="Dossier administratif complet"
    )
    
    outlook = models.BooleanField(
        default=False,
        verbose_name="Outlook",
        help_text="Ajouté dans Outlook"
    )
    
    extranet = models.BooleanField(
        default=False,
        verbose_name="Extranet",
        help_text="Accès extranet créé"
    )
    
    reunion_accueil_faite = models.BooleanField(
        default=False,
        verbose_name="Réunion d'accueil faite",
        help_text="A participé à la réunion d'accueil"
    )
    
    volet_3_casier_judiciaire = models.CharField(
        null=True,
        max_length=50,
        blank=True,
        verbose_name="Volet 3 casier judiciaire",
        help_text="Date de réception du volet 3 (ou laissez vide)"
    )
    
    # ============================================================================
    # NOUVEAUX CHAMPS À AJOUTER (spécifiques aux candidats à recontacter)
    # ============================================================================
    
    origine_contact = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Origine du contact",
        help_text="Source du contact (JVA, site ESA, Maison des associations, etc.)"
    )
    
    date_contact = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Date du contact",
        help_text="Date du premier contact (format libre)"
    )
    
    informations_complementaires = models.TextField(
        blank=True,
        null=True,
        verbose_name="Informations complémentaires",
        help_text="Informations supplémentaires sur le candidat"
    )
    
    disponibilites_competences = models.TextField(
        blank=True,
        null=True,
        verbose_name="Disponibilités et compétences",
        help_text="Détails sur les disponibilités et compétences du candidat"
    )
    
    # ================================================================
    # 💬 NOTES ET INFORMATIONS COMPLÉMENTAIRES
    # ================================================================
    
    commentaires = models.TextField(
        blank=True,
        verbose_name="Commentaires",
        help_text="Remarques et informations diverses"
    )
    
    divers = models.TextField(
        blank=True,
        verbose_name="Divers",
        help_text="Autres informations"
    )
    
    # ================================================================
    # ⏰ MÉTADONNÉES AUTOMATIQUES
    # ================================================================
    
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date d'ajout dans le système"
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification",
        help_text="Dernière mise à jour de la fiche"
    )
    
    # ================================================================
    # 🎨 MÉTADONNÉES DU MODÈLE
    # ================================================================
    
    class Meta:
        verbose_name = "Bénévole"
        verbose_name_plural = "Bénévoles"
        ordering = ['nom', 'prenom']
        
        indexes = [
            models.Index(fields=['nom', 'prenom']),
            models.Index(fields=['statut']),
            models.Index(fields=['code_postal']),
        ]
    
    # ================================================================
    # 🔤 REPRÉSENTATION ET MÉTHODES
    # ================================================================
    
    def __str__(self):
        """Représentation textuelle du bénévole."""
        return f"{self.prenom} {self.nom}"
    
    def get_nom_complet(self):
        """Retourne le nom complet du bénévole."""
        return f"{self.prenom} {self.nom}"
    
    def get_prenom(self):
        """Retourne le prénom du bénévole."""
        return self.prenom
    
    def est_disponible(self):
        """Vérifie si le bénévole est disponible."""
        return self.statut == 'Disponible'
    
    def est_mentor(self):
        """Vérifie si le bénévole est actuellement mentor."""
        return self.statut == 'Mentor'
    
    def est_geolocalisé(self):
        """Vérifie si le bénévole a des coordonnées GPS."""
        return self.latitude is not None and self.longitude is not None
    
    def get_adresse_complete(self):
        """Retourne l'adresse complète formatée."""
        parts = [self.adresse, self.code_postal, self.ville]
        return ', '.join([p for p in parts if p])
    
    def peut_accompagner_niveau(self, niveau):
        """
        Vérifie si le bénévole peut accompagner un niveau donné.
        
        Args:
            niveau (str): 'primaire', 'college' ou 'lycee'
        
        Returns:
            bool: True si le bénévole peut accompagner ce niveau
        """
        niveau_map = {
            'primaire': self.primaire,
            'college': self.college,
            'lycee': self.lycee
        }
        return niveau_map.get(niveau.lower(), False)
    
    def get_niveaux_accompagnement(self):
        """Retourne la liste des niveaux que le bénévole peut accompagner."""
        niveaux = []
        if self.primaire:
            niveaux.append('Primaire')
        if self.college:
            niveaux.append('Collège')
        if self.lycee:
            niveaux.append('Lycée')
        return niveaux
    
    def get_matieres_list(self):
        """Retourne la liste des noms de matières enseignées."""
        return list(self.matieres.values_list('nom', flat=True))
    
    def documents_complets(self):
        """Vérifie si tous les documents administratifs sont OK."""
        return all([
            self.fichier,
            self.volet_3_casier_judiciaire,
            self.reunion_accueil_faite
        ])
    
    def get_documents_manquants(self):
        """Retourne la liste des documents manquants."""
        manquants = []
        if not self.fichier:
            manquants.append('Dossier administratif')
        if not self.volet_3_casier_judiciaire:
            manquants.append('Volet 3 casier judiciaire')
        if not self.reunion_accueil_faite:
            manquants.append('Réunion d\'accueil')
        if not self.a_donne_photo:
            manquants.append('Photo')
        return manquants


# ============================================================================
# 🔗 MODÈLE BINÔME
# ============================================================================

class Binome(models.Model):
    """
    Représente l'association entre un élève et un bénévole.
    
    Table en base de données : core_binome
    """
    
    # ----------------------------------------------------------------
    # 🔗 RELATIONS (Clés étrangères)
    # ----------------------------------------------------------------
    
    eleve = models.OneToOneField(
        Eleve,
        on_delete=models.CASCADE,  # Si l'élève est supprimé, supprimer le binôme
        related_name='binome',     # Accès inverse : eleve.binome
        verbose_name="Élève"
    )
    
    benevole = models.ForeignKey(
        Benevole,
        on_delete=models.SET_NULL,  # Si bénévole supprimé, garder le binôme mais mettre NULL
        null=True,
        related_name='binomes',     # Accès inverse : benevole.binomes.all()
        verbose_name="Bénévole"
    )
    
    # ----------------------------------------------------------------
    # 📅 DATES
    # ----------------------------------------------------------------
    
    date_debut = models.DateField(
        verbose_name="Date de début",
        help_text="Date de début de l'accompagnement"
    )
    
    date_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin",
        help_text="Date de fin de l'accompagnement (si terminé)"
    )
    
    # ----------------------------------------------------------------
    # 📝 INFORMATIONS SUPPLÉMENTAIRES
    # ----------------------------------------------------------------
    
    notes = models.TextField(
        blank=True,
        verbose_name="Notes",
        help_text="Remarques sur l'accompagnement"
    )
    
    actif = models.BooleanField(
        default=True,
        verbose_name="Binôme actif"
    )
    
    # ----------------------------------------------------------------
    # ⏰ MÉTADONNÉES
    # ----------------------------------------------------------------
    
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    # ----------------------------------------------------------------
    # 🎨 MÉTADONNÉES DU MODÈLE
    # ----------------------------------------------------------------
    
    class Meta:
        verbose_name = "Binôme"
        verbose_name_plural = "Binômes"
        ordering = ['-date_debut']  # Tri par date décroissante
        
        # Contrainte : un élève ne peut avoir qu'un seul binôme actif
        constraints = [
            models.UniqueConstraint(
                fields=['eleve'],
                condition=models.Q(actif=True),
                name='unique_active_binome_per_eleve'
            )
        ]
    
    def __str__(self):
        if self.benevole:
            return f"{self.eleve.get_nom_complet()} ↔ {self.benevole.get_nom_complet()}"
        return f"{self.eleve.get_nom_complet()} (sans bénévole)"
    
    def est_actif(self):
        """Vérifie si le binôme est actif."""
        return self.actif and self.date_fin is None

# Profil utilisateur lié à un bénévole
class ProfilUtilisateur(models.Model):
    """
    Profil pour lier un utilisateur Django à un bénévole.
    Chaque utilisateur EST un bénévole.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profil',
        verbose_name="Utilisateur"
    )
    
    benevole = models.OneToOneField(
        Benevole,
        on_delete=models.CASCADE,
        related_name='utilisateur',
        verbose_name="Bénévole associé",
        help_text="Bénévole correspondant à cet utilisateur"
    )
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        return f"{self.user.username} → {self.benevole.get_nom_complet()}"

