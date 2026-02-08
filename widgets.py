# 📍 Widget personnalisé pour l'adresse avec autocomplétion et carte

"""
Ce fichier contient un widget Django personnalisé pour le champ adresse
avec autocomplétion via l'API Adresse Gouv et mini-carte de visualisation.

Fichier à créer : core/widgets.py
"""

from django import forms
from django.utils.safestring import mark_safe


class AdresseWidget(forms.TextInput):
    """
    Widget personnalisé pour le champ adresse avec :
    - Autocomplétion via l'API Adresse du gouvernement français
    - Mini-carte Leaflet pour visualiser l'adresse
    - Mise à jour automatique des coordonnées GPS
    """
    
    class Media:
        css = {
            'all': (
                'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            )
        }
        js = (
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
        )
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control adresse-autocomplete',
            'placeholder': 'Commencez à taper une adresse...',
            'autocomplete': 'off',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        """Rendu du widget avec HTML + JavaScript"""
        
        # Rendu du champ de base
        html = super().render(name, value, attrs, renderer)
        
        # ID unique pour ce widget
        field_id = attrs.get('id', 'id_' + name)
        
        # L'URL du tile server avec les placeholders Leaflet
        tile_url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        
        # HTML supplémentaire - Utiliser .format() pour éviter les problèmes d'accolades
        extra_html = """
        <!-- Container pour l'autocomplétion -->
        <div id="{fid}_autocomplete" class="autocomplete-results" style="display: none;"></div>
        
        <!-- Mini-carte -->
        <div id="{fid}_map" style="height: 200px; margin-top: 10px; display: none; border-radius: 8px;"></div>
        
        <!-- Messages -->
        <small id="{fid}_message" class="form-text text-muted"></small>
        
        <style>
            .autocomplete-results {{
                position: absolute;
                z-index: 1000;
                background: white;
                border: 1px solid #ddd;
                border-top: none;
                max-height: 300px;
                overflow-y: auto;
                width: 100%;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
            const mapDiv = document.getElementById('{fid}_map');
            const messageDiv = document.getElementById('{fid}_message');
            
            let map = null;
            let marker = null;
            let debounceTimer = null;
            
            // Initialiser la carte Leaflet
            function initMap(lat, lon) {{
                if (!map) {{
                    mapDiv.style.display = 'block';
                    map = L.map('{fid}_map').setView([lat, lon], 15);
                    
                    L.tileLayer('{tile_url}', {{
                        attribution: '© OpenStreetMap'
                    }}).addTo(map);
                }} else {{
                    map.setView([lat, lon], 15);
                }}
                
                // Ajouter/déplacer le marqueur
                if (marker) {{
                    marker.setLatLng([lat, lon]);
                }} else {{
                    marker = L.marker([lat, lon]).addTo(map);
                }}
                
                // Force un refresh de la carte
                setTimeout(() => map.invalidateSize(), 100);
            }}
            
            // Recherche d'adresse via l'API
            async function searchAddress(query) {{
                if (query.length < 3) {{
                    autocompleteDiv.style.display = 'none';
                    return;
                }}
                
                try {{
                    // Ajouter "Marseille" à la recherche si pas déjà présent
                    let searchQuery = query;
                    if (!query.toLowerCase().includes('marseille')) {{
                        searchQuery = query + ' Marseille';
                    }}
                    
                    // API Adresse du gouvernement français
                    // &lat=43.2965&lon=5.3698 pour privilégier Marseille
                    const response = await fetch(
                        `https://api-adresse.data.gouv.fr/search/?q=${{encodeURIComponent(searchQuery)}}&limit=10&lat=43.2965&lon=5.3698`
                    );
                    const data = await response.json();
                    
                    if (data.features && data.features.length > 0) {{
                        // Filtrer pour ne garder que Marseille (codes postaux 13001-13016)
                        const marseillResults = data.features.filter(f => {{
                            const postcode = f.properties.postcode;
                            return postcode && postcode.startsWith('130') && 
                                   parseInt(postcode.substring(3, 5)) <= 16;
                        }});
                        
                        if (marseillResults.length > 0) {{
                            displaySuggestions(marseillResults);
                        }} else {{
                            // Si aucun résultat à Marseille, afficher tous les résultats
                            displaySuggestions(data.features);
                        }}
                    }} else {{
                        autocompleteDiv.innerHTML = '<div class="autocomplete-item">Aucune adresse trouvée</div>';
                        autocompleteDiv.style.display = 'block';
                    }}
                }} catch (error) {{
                    console.error('Erreur lors de la recherche d\\'adresse:', error);
                    messageDiv.textContent = 'Erreur lors de la recherche d\\'adresse';
                    messageDiv.className = 'form-text text-danger';
                }}
            }}
            
            // Afficher les suggestions
            function displaySuggestions(features) {{
                autocompleteDiv.innerHTML = '';
                
                features.forEach(feature => {{
                    const item = document.createElement('div');
                    item.className = 'autocomplete-item';
                    
                    const props = feature.properties;
                    item.innerHTML = `
                        <strong>${{props.name}}</strong><br>
                        <small>${{props.postcode}} ${{props.city}}</small>
                    `;
                    
                    item.onclick = () => selectAddress(feature);
                    autocompleteDiv.appendChild(item);
                }});
                
                autocompleteDiv.style.display = 'block';
            }}
            
            // Sélectionner une adresse
            function selectAddress(feature) {{
                const props = feature.properties;
                const coords = feature.geometry.coordinates; // [lon, lat]
                
                // Remplir le champ adresse
                input.value = props.label;
                
                // Remplir les champs cachés de latitude/longitude
                const latField = document.getElementById('id_latitude');
                const lonField = document.getElementById('id_longitude');
                const arrField = document.getElementById('id_arrondissement');
                
                if (latField) latField.value = coords[1];
                if (lonField) lonField.value = coords[0];
                
                // Essayer de déterminer l'arrondissement depuis le code postal
                if (arrField && props.postcode) {{
                    const postcode = props.postcode;
                    if (postcode.startsWith('130')) {{
                        const num = postcode.substring(3);
                        if (num === '01') {{
                            arrField.value = '1er';
                        }} else {{
                            arrField.value = parseInt(num) + 'e';
                        }}
                    }}
                }}
                
                // Afficher la carte
                initMap(coords[1], coords[0]);
                
                // Masquer les suggestions
                autocompleteDiv.style.display = 'none';
                
                // Message de confirmation
                messageDiv.textContent = '✓ Adresse géolocalisée : ' + coords[1].toFixed(6) + ', ' + coords[0].toFixed(6);
                messageDiv.className = 'form-text text-success';
            }}
            
            // Événement sur la saisie
            input.addEventListener('input', (e) => {{
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {{
                    searchAddress(e.target.value);
                }}, 300); // Attendre 300ms après la dernière frappe
            }});
            
            // Fermer les suggestions si on clique ailleurs
            document.addEventListener('click', (e) => {{
                if (e.target !== input && !autocompleteDiv.contains(e.target)) {{
                    autocompleteDiv.style.display = 'none';
                }}
            }});
            
            // Si une adresse existe déjà, afficher la carte
            if (input.value) {{
                const latField = document.getElementById('id_latitude');
                const lonField = document.getElementById('id_longitude');
                
                if (latField && lonField && latField.value && lonField.value) {{
                    initMap(parseFloat(latField.value), parseFloat(lonField.value));
                    messageDiv.textContent = '✓ Adresse déjà géolocalisée';
                    messageDiv.className = 'form-text text-success';
                }}
            }}
        }})();
        </script>
        """.format(fid=field_id, tile_url=tile_url)
        
        return mark_safe(html + extra_html)
