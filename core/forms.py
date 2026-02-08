# 📝 Formulaire mis à jour avec les nouveaux widgets

"""
Fichier : core/forms.py (remplacer le contenu)
"""

from django import forms
from .models import Eleve, Benevole
from .widgets import VilleWidget, AdresseWidget


class EleveAdminForm(forms.ModelForm):
    """Formulaire personnalisé pour l'admin des élèves"""
    
    class Meta:
        model = Eleve
        fields = '__all__'
        widgets = {
            'ville': VilleWidget(),
            'adresse': AdresseWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Champs en lecture seule (remplis automatiquement)
        readonly_fields = ['latitude', 'longitude']
        
        for field_name in readonly_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'readonly': 'readonly',
                    'class': 'form-control-plaintext',
                })
                self.fields[field_name].help_text = 'Rempli automatiquement'


class BenevoleAdminForm(forms.ModelForm):
    """Formulaire personnalisé pour l'admin des bénévoles"""
    
    class Meta:
        model = Benevole
        fields = '__all__'
        widgets = {
            'ville': VilleWidget(),
            'adresse': AdresseWidget(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        readonly_fields = ['latitude', 'longitude']
        
        for field_name in readonly_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'readonly': 'readonly',
                    'class': 'form-control-plaintext',
                })
                self.fields[field_name].help_text = 'Rempli automatiquement'
