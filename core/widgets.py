# 📍 Widget d'adresse amélioré avec numéro de rue

"""
Widget pour l'autocomplétion de l'adresse complète
avec remplissage automatique de tous les champs.

Fichier : core/widgets.py
"""

from django import forms
from django.utils.safestring import mark_safe


class VilleWidget(forms.TextInput):
    """Widget pour le champ ville avec autocomplétion"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control ville-autocomplete',
            'placeholder': 'Tapez une ville...',
            'autocomplete': 'off',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        field_id = attrs.get('id', 'id_' + name)
        
        extra = """
        <div id="{fid}_autocomplete" class="autocomplete-results"></div>
        <small id="{fid}_message" class="form-text text-muted"></small>
        
        <style>
            .autocomplete-results {{
                position: absolute;
                z-index: 1000;
                background: white;
                border: 1px solid #ddd;
                max-height: 300px;
                overflow-y: auto;
                width: 100%;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                display: none;
            }}
            .autocomplete-item {{
                padding: 10px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
            }}
            .autocomplete-item:hover {{
                background-color: #f8f9fa;
            }}
            .autocomplete-item strong {{
                color: #0066cc;
            }}
        </style>
        
        <script>
        (function() {{
            const input = document.getElementById('{fid}');
            const autocompleteDiv = document.getElementById('{fid}_autocomplete');
            const messageDiv = document.getElementById('{fid}_message');
            let debounceTimer = null;
            
            async function searchVille(query) {{
                if (query.length < 2) {{
                    autocompleteDiv.style.display = 'none';
                    return;
                }}
                
                try {{
                    const response = await fetch(
                        `https://geo.api.gouv.fr/communes?nom=${{encodeURIComponent(query)}}&fields=nom,code,codesPostaux,centre&limit=10`
                    );
                    const data = await response.json();
                    
                    if (data && data.length > 0) {{
                        displayVilles(data);
                    }} else {{
                        autocompleteDiv.innerHTML = '<div class="autocomplete-item">Aucune ville trouvée</div>';
                        autocompleteDiv.style.display = 'block';
                    }}
                }} catch (error) {{
                    console.error('Erreur:', error);
                    messageDiv.textContent = 'Erreur lors de la recherche';
                    messageDiv.className = 'form-text text-danger';
                }}
            }}
            
            function displayVilles(villes) {{
                autocompleteDiv.innerHTML = '';
                
                villes.forEach(ville => {{
                    const item = document.createElement('div');
                    item.className = 'autocomplete-item';
                    
                    const codesPostaux = ville.codesPostaux ? ville.codesPostaux.join(', ') : '';
                    item.innerHTML = `
                        <strong>${{ville.nom}}</strong><br>
                        <small>${{codesPostaux}}</small>
                    `;
                    
                    item.onclick = () => selectVille(ville);
                    autocompleteDiv.appendChild(item);
                }});
                
                autocompleteDiv.style.display = 'block';
            }}
            
            function selectVille(ville) {{
                input.value = ville.nom;
                autocompleteDiv.style.display = 'none';
                
                // Remplir le code postal
                const cpField = document.getElementById('id_code_postal');
                if (cpField && ville.codesPostaux && ville.codesPostaux.length > 0) {{
                    cpField.value = ville.codesPostaux[0];
                }}
                
                // Remplir les coordonnées GPS du centre de la ville (temporaire)
                const latField = document.getElementById('id_latitude');
                const lonField = document.getElementById('id_longitude');
                if (latField && lonField && ville.centre) {{
                    latField.value = ville.centre.coordinates[1];
                    lonField.value = ville.centre.coordinates[0];
                }}
                
                messageDiv.textContent = '✓ Ville sélectionnée : ' + ville.nom;
                messageDiv.className = 'form-text text-success';
            }}
            
            input.addEventListener('input', (e) => {{
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {{
                    searchVille(e.target.value);
                }}, 300);
            }});
            
            document.addEventListener('click', (e) => {{
                if (e.target !== input && !autocompleteDiv.contains(e.target)) {{
                    autocompleteDiv.style.display = 'none';
                }}
            }});
        }})();
        </script>
        """.format(fid=field_id)
        
        return mark_safe(html + extra)


class AdresseWidget(forms.TextInput):
    """
    Widget pour l'autocomplétion de l'adresse.
    Utilise le numéro de rue + nom de rue + ville pour chercher.
    """
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control adresse-autocomplete',
            'placeholder': 'Nom de la rue...',
            'autocomplete': 'off',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        field_id = attrs.get('id', 'id_' + name)
        
        extra = """
        <div id="{fid}_autocomplete" class="autocomplete-results"></div>
        <small id="{fid}_message" class="form-text text-muted"></small>
        
        <style>
            .autocomplete-results {{
                position: absolute;
                z-index: 1000;
                background: white;
                border: 1px solid #ddd;
                max-height: 300px;
                overflow-y: auto;
                width: 100%;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                display: none;
            }}
            .autocomplete-item {{
                padding: 10px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
            }}
            .autocomplete-item:hover {{
                background-color: #f8f9fa;
            }}
            .autocomplete-item strong {{
                color: #0066cc;
            }}
        </style>
        
        <script>
        (function() {{
            const input = document.getElementById('{fid}');
            const autocompleteDiv = document.getElementById('{fid}_autocomplete');
            const messageDiv = document.getElementById('{fid}_message');
            let debounceTimer = null;
            
            async function searchAdresse(query) {{
                if (query.length < 3) {{
                    autocompleteDiv.style.display = 'none';
                    return;
                }}
                
                try {{
                    // Récupérer ville, code postal et numéro
                    const villeField = document.getElementById('id_ville');
                    const codePostalField = document.getElementById('id_code_postal');
                    const numeroField = document.getElementById('id_numero_rue');
                    
                    let searchQuery = '';
                    
                    // Ajouter le numéro s'il existe
                    if (numeroField && numeroField.value) {{
                        searchQuery = numeroField.value + ' ';
                    }}
                    
                    // Ajouter le nom de rue
                    searchQuery += query;
                    
                    // Ajouter le code postal (prioritaire) ou la ville
                    if (codePostalField && codePostalField.value) {{
                        searchQuery += ' ' + codePostalField.value;
                    }} else if (villeField && villeField.value) {{
                        searchQuery += ' ' + villeField.value;
                    }}
                    
                    console.log('Recherche:', searchQuery);
                    
                    const response = await fetch(
                        `https://api-adresse.data.gouv.fr/search/?q=${{encodeURIComponent(searchQuery)}}&limit=10`
                    );
                    const data = await response.json();
                    
                    if (data.features && data.features.length > 0) {{
                        displayAdresses(data.features);
                    }} else {{
                        autocompleteDiv.innerHTML = '<div class="autocomplete-item">Aucune adresse trouvée</div>';
                        autocompleteDiv.style.display = 'block';
                    }}
                }} catch (error) {{
                    console.error('Erreur:', error);
                    messageDiv.textContent = 'Erreur lors de la recherche d\\'adresse';
                    messageDiv.className = 'form-text text-danger';
                }}
            }}
            
            function displayAdresses(features) {{
                autocompleteDiv.innerHTML = '';
                
                features.forEach(feature => {{
                    const item = document.createElement('div');
                    item.className = 'autocomplete-item';
                    
                    const props = feature.properties;
                    item.innerHTML = `
                        <strong>${{props.name}}</strong><br>
                        <small>${{props.postcode}} ${{props.city}}</small>
                    `;
                    
                    item.onclick = () => selectAdresse(feature);
                    autocompleteDiv.appendChild(item);
                }});
                
                autocompleteDiv.style.display = 'block';
            }}
            
            function selectAdresse(feature) {{
                const props = feature.properties;
                const coords = feature.geometry.coordinates;
                
                // Extraire le numéro et le nom de rue
                const adresseComplete = props.name;
                const parts = adresseComplete.match(/^(\\d+\\s*(?:bis|ter|quater)?)?\\s*(.+)$/i);
                
                let numero = '';
                let nomRue = adresseComplete;
                
                if (parts) {{
                    numero = parts[1] ? parts[1].trim() : '';
                    nomRue = parts[2] ? parts[2].trim() : adresseComplete;
                }}
                
                // Remplir les champs
                const numeroField = document.getElementById('id_numero_rue');
                const cpField = document.getElementById('id_code_postal');
                const villeField = document.getElementById('id_ville');
                const latField = document.getElementById('id_latitude');
                const lonField = document.getElementById('id_longitude');
                const arrField = document.getElementById('id_arrondissement');
                
                // Numéro et nom de rue
                if (numeroField && numero) numeroField.value = numero;
                input.value = nomRue;
                
                // Code postal et ville
                if (cpField) cpField.value = props.postcode;
                if (villeField) villeField.value = props.city;
                
                // GPS
                if (latField) latField.value = coords[1];
                if (lonField) lonField.value = coords[0];
                
                // Arrondissement (pour Marseille, Lyon, Paris)
                if (arrField && props.postcode) {{
                    const postcode = props.postcode;
                    
                    // Marseille : 13001-13016
                    if (postcode.startsWith('130') && postcode.length === 5) {{
                        const num = postcode.substring(3);
                        const numInt = parseInt(num);
                        if (numInt >= 1 && numInt <= 16) {{
                            if (num === '01') {{
                                arrField.value = '1er';
                            }} else {{
                                arrField.value = numInt + 'e';
                            }}
                        }}
                    }}
                    // Lyon : 69001-69009
                    else if (postcode.startsWith('690') && postcode.length === 5) {{
                        const num = postcode.substring(3);
                        const numInt = parseInt(num);
                        if (numInt >= 1 && numInt <= 9) {{
                            if (num === '01') {{
                                arrField.value = '1er';
                            }} else {{
                                arrField.value = numInt + 'e';
                            }}
                        }}
                    }}
                    // Paris : 75001-75020
                    else if (postcode.startsWith('750') && postcode.length === 5) {{
                        const num = postcode.substring(3);
                        const numInt = parseInt(num);
                        if (numInt >= 1 && numInt <= 20) {{
                            if (num === '01') {{
                                arrField.value = '1er';
                            }} else {{
                                arrField.value = numInt + 'e';
                            }}
                        }}
                    }}
                }}
                
                autocompleteDiv.style.display = 'none';
                messageDiv.textContent = '✓ Adresse complète : ' + props.label;
                messageDiv.className = 'form-text text-success';
            }}
            
            // Trigger search on input
            input.addEventListener('input', (e) => {{
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {{
                    searchAdresse(e.target.value);
                }}, 300);
            }});
            
            // Trigger search when numero_rue changes
            const numeroField = document.getElementById('id_numero_rue');
            if (numeroField) {{
                numeroField.addEventListener('input', () => {{
                    if (input.value) {{
                        clearTimeout(debounceTimer);
                        debounceTimer = setTimeout(() => {{
                            searchAdresse(input.value);
                        }}, 300);
                    }}
                }});
            }}
            
            document.addEventListener('click', (e) => {{
                if (e.target !== input && !autocompleteDiv.contains(e.target)) {{
                    autocompleteDiv.style.display = 'none';
                }}
            }});
        }})();
        </script>
        """.format(fid=field_id)
        
        return mark_safe(html + extra)
