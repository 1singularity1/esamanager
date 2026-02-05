<!-- 
🎓 NOTES D'APPRENTISSAGE

1. HÉRITAGE :
   {% extends 'core/base.html' %} : Hérite de base.html
   {% block content %} : Remplace le block content de base.html

2. URLS :
   {% url 'core:carte_binomes' %} : Génère l'URL vers la vue carte_binomes
   Avantage : Si vous changez l'URL dans urls.py, le lien reste valide !

3. VARIABLES :
   {{ stats.total_eleves }} : Affiche la variable passée depuis la vue
   Définie dans views.py : context = {'stats': {...}}

4. BOOTSTRAP 5 :
   - Classes CSS : card, btn, text-center, etc.
   - Icons : bi bi-map (Bootstrap Icons)
   - Grid : row, col-md-6 (responsive)

5. STYLE CSS :
   <style> dans le template : OK pour du CSS spécifique à cette page
   Pour du CSS global : créer static/core/css/style.css

6. PERSONNALISATION :
   - Changez les titres, descriptions
   - Modifiez les gradients (linear-gradient)
   - Ajoutez vos propres cartes

📚 Pour aller plus loin :
- Bootstrap 5 : https://getbootstrap.com/
- Django Templates : https://docs.djangoproject.com/en/stable/ref/templates/
-->
