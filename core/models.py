"""
🎓 MODELS.PY - Modèles de données de l'application ESA

Un modèle = une table dans la base de données.
Chaque attribut = une colonne de la table.

📚 Documentation : https://docs.djangoproject.com/en/stable/topics/db/models/
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# ============================================================================
# 👨‍🎓 MODÈLE ÉLÈVE
# ============================================================================

"""
🎓 MODELS.PY - Modèle Eleve mis à jour

Modifications apportées :
1. Ajout des CLASSE_CHOICES pour standardiser les classes
2. Ajout des champs pour les parents (nom, prénom, téléphone)
3. Ajout du téléphone de l'élève
4. Ajout de l'établissement scolaire
5. Ajout des matières souhaitées
6. Ajout d'un champ informations complémentaires

Usage :
- Copier ce code dans core/models.py
- Exécuter : python manage.py makemigrations
- Exécuter : python manage.py migrate
"""

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
        verbose_name="Ordre d'affichage"
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
        max_length=20,
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
        max_length=200,
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
        max_length=200,
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
# 🎓 MODÈLE BÉNÉVOLE
# ============================================================================

class Benevole(models.Model):
    """
    Représente un bénévole de l'association ESA.
    
    Table en base de données : core_benevole
    """
    
    # ----------------------------------------------------------------
    # 📝 INFORMATIONS PERSONNELLES
    # ----------------------------------------------------------------
    
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de famille"
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
        verbose_name="Téléphone"
    )
    
    # ----------------------------------------------------------------
    # 📍 LOCALISATION
    # ----------------------------------------------------------------
    
    adresse = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Adresse complète"
    )
    
    arrondissement = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Arrondissement"
    )
    
    latitude = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ],
        verbose_name="Latitude"
    )
    
    longitude = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        verbose_name="Longitude"
    )
    
    # ----------------------------------------------------------------
    # 📊 DISPONIBILITÉ
    # ----------------------------------------------------------------
    
    DISPONIBILITE_CHOICES = [
        ('disponible', 'Disponible'),
        ('occupe', 'Occupé'),
        ('inactif', 'Inactif'),
    ]
    
    disponibilite = models.CharField(
        max_length=20,
        choices=DISPONIBILITE_CHOICES,
        default='disponible',
        verbose_name="Disponibilité"
    )
    
    # ----------------------------------------------------------------
    # ⏰ MÉTADONNÉES
    # ----------------------------------------------------------------
    
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'inscription"
    )
    
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière modification"
    )
    
    # ----------------------------------------------------------------
    # 🎨 MÉTADONNÉES DU MODÈLE
    # ----------------------------------------------------------------
    
    class Meta:
        verbose_name = "Bénévole"
        verbose_name_plural = "Bénévoles"
        ordering = ['nom', 'prenom']
        
        indexes = [
            models.Index(fields=['nom', 'prenom']),
            models.Index(fields=['disponibilite']),
        ]
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def get_nom_complet(self):
        return f"{self.prenom} {self.nom}"
    
    def est_disponible(self):
        """Vérifie si le bénévole est disponible."""
        return self.disponibilite == 'disponible'


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


# ============================================================================
# 🎓 NOTES D'APPRENTISSAGE
# ============================================================================

"""
📝 Concepts clés des modèles Django :

1. CHAMPS (Fields) :
   - CharField : Texte court (max_length obligatoire)
   - TextField : Texte long
   - IntegerField : Nombre entier
   - FloatField : Nombre décimal
   - BooleanField : Vrai/Faux
   - DateField : Date (YYYY-MM-DD)
   - DateTimeField : Date + heure
   - EmailField : Email (validation auto)

2. OPTIONS DES CHAMPS :
   - null=True : Peut être NULL en base de données
   - blank=True : Peut être vide dans les formulaires
   - default : Valeur par défaut
   - choices : Liste de choix prédéfinis
   - verbose_name : Label affiché
   - help_text : Texte d'aide

3. RELATIONS :
   - ForeignKey : Relation N-1 (plusieurs binômes → 1 bénévole)
   - OneToOneField : Relation 1-1 (1 élève → 1 binôme max)
   - ManyToManyField : Relation N-N (pas utilisé ici)

4. META :
   - verbose_name : Nom du modèle (singulier)
   - verbose_name_plural : Nom du modèle (pluriel)
   - ordering : Tri par défaut
   - indexes : Index pour accélérer les requêtes

5. MÉTHODES :
   - __str__() : Représentation texte (OBLIGATOIRE !)
   - Méthodes personnalisées : logique métier

📚 Après avoir créé/modifié un modèle :
1. python manage.py makemigrations  → Créer la migration
2. python manage.py migrate         → Appliquer à la BDD

🔍 Utilisation dans le code :
    # Créer
    eleve = Eleve.objects.create(nom="Dupont", prenom="Jean")
    
    # Récupérer
    eleves = Eleve.objects.all()
    eleve = Eleve.objects.get(id=1)
    
    # Filtrer
    accompagnes = Eleve.objects.filter(statut='accompagne')
    
    # Mettre à jour
    eleve.statut = 'accompagne'
    eleve.save()
    
    # Supprimer
    eleve.delete()
"""
