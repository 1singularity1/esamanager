# 📝 Formulaire personnalisé pour Eleve avec widget d'adresse

"""
Formulaire Django personnalisé pour le modèle Eleve
qui utilise le widget d'adresse avec autocomplétion.

Fichier à créer/modifier : core/forms.py
"""

from django import forms
from .models import Eleve
from .widgets import AdresseWidget


class EleveAdminForm(forms.ModelForm):
    """
    Formulaire personnalisé pour l'admin des élèves
    avec widget d'adresse amélioré
    """
    
    class Meta:
        model = Eleve
        fields = '__all__'  # Tous les champs
        widgets = {
            'adresse': AdresseWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les champs latitude/longitude
        if 'latitude' in self.fields:
            self.fields['latitude'].widget.attrs.update({
                'readonly': 'readonly',
                'class': 'form-control-plaintext',
            })
            self.fields['latitude'].help_text = 'Rempli automatiquement via l\'adresse'
        
        if 'longitude' in self.fields:
            self.fields['longitude'].widget.attrs.update({
                'readonly': 'readonly', 
                'class': 'form-control-plaintext',
            })
            self.fields['longitude'].help_text = 'Rempli automatiquement via l\'adresse'


# Pareil pour les bénévoles
class BenevoleAdminForm(forms.ModelForm):
    """
    Formulaire personnalisé pour l'admin des bénévoles
    avec widget d'adresse amélioré
    """
    
    class Meta:
        model = Eleve  # Remplacer par Benevole
        fields = '__all__'
        widgets = {
            'adresse': AdresseWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'latitude' in self.fields:
            self.fields['latitude'].widget.attrs.update({
                'readonly': 'readonly',
                'class': 'form-control-plaintext',
            })
            self.fields['latitude'].help_text = 'Rempli automatiquement via l\'adresse'
        
        if 'longitude' in self.fields:
            self.fields['longitude'].widget.attrs.update({
                'readonly': 'readonly',
                'class': 'form-control-plaintext',
            })
            self.fields['longitude'].help_text = 'Rempli automatiquement via l\'adresse'
