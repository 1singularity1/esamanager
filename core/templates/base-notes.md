
<!-- 
🎓 NOTES D'APPRENTISSAGE - TEMPLATES DJANGO

1. HÉRITAGE :
   base.html = Template parent (structure commune)
   Autres templates = Templates enfants (contenu spécifique)
   
   Utilisation :
   {% extends 'core/base.html' %}
   {% block content %}Mon contenu{% endblock %}

2. BLOCKS :
   {% block nom %}contenu par défaut{% endblock %}
   
   Blocks communs :
   - title : Titre de la page
   - content : Contenu principal
   - extra_css : CSS supplémentaire
   - extra_js : JavaScript supplémentaire

3. TAGS DJANGO :
   {% load static %} : Charger les fichiers statiques
   {% url 'core:home' %} : Générer une URL
   {% if condition %} : Condition
   {% for item in liste %} : Boucle

4. VARIABLES :
   {{ variable }} : Afficher une variable
   {{ user.username }} : Accéder à un attribut
   {{ liste|length }} : Appliquer un filtre

5. FICHIERS STATIQUES :
   {% load static %}
   <img src="{% static 'core/img/logo.png' %}">
   <link href="{% static 'core/css/style.css' %}">

6. MESSAGES FLASH :
   from django.contrib import messages
   messages.success(request, "Succès !")
   → Affichés automatiquement dans ce template

📚 Documentation complète :
https://docs.djangoproject.com/en/stable/ref/templates/
-->