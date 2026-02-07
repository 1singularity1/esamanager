# 🎓 ESA Manager - Projet Django

## 🚀 **Installation rapide (5 minutes)**

### **1. Installer Django**
```bash
# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# Installer Django
pip install django

# Vérifier l'installation
python -m django --version
# Doit afficher : 5.x
```

### **2. Initialiser la base de données**
```bash
cd esa_manager

# Créer les tables
python manage.py migrate

# Créer un super-utilisateur (admin)
python manage.py createsuperuser
# Username: admin
# Email: admin@esa.org
# Password: admin123  (changez en production !)
```

### **3. Lancer le serveur**
```bash
python manage.py runserver

# Ouvrir dans le navigateur :
# http://localhost:8000/        → Page d'accueil
# http://localhost:8000/admin/  → Interface admin
```

---

## 📁 **Structure du projet**

```
esa_manager/
│
├── README.md                      ← VOUS ÊTES ICI
├── DJANGO_TUTORIAL.md             ← Tutoriel complet Django
├── requirements.txt               ← Dépendances Python
├── manage.py                      ← Commandes Django
│
├── esa_manager/                   ← Configuration du projet
│   ├── __init__.py
│   ├── settings.py               ← ⭐ Configuration principale
│   ├── urls.py                   ← ⭐ Routes principales
│   ├── wsgi.py
│   └── asgi.py
│
└── core/                          ← Application principale
    ├── models.py                 ← ⭐ VOS DONNÉES (Eleve, Benevole, Binome)
    ├── admin.py                  ← ⭐ Configuration Admin Django
    ├── views.py                  ← ⭐ Logique métier (routes)
    ├── urls.py                   ← Routes de l'app
    ├── apps.py
    │
    ├── templates/core/           ← ⭐ Pages HTML
    │   ├── base.html
    │   ├── index.html           ← Page d'accueil (2 boutons)
    │   └── carte_binomes.html   ← Carte interactive
    │
    ├── static/core/              ← ⭐ CSS, JS, Images
    │   ├── css/style.css
    │   ├── js/main.js
    │   └── img/
    │
    └── migrations/               ← Versions de la base de données
```

---

## 🎯 **Commandes Django essentielles**

### **Développement**
```bash
# Lancer le serveur de développement
python manage.py runserver

# Lancer sur un port spécifique
python manage.py runserver 8080

# Accessible depuis le réseau
python manage.py runserver 0.0.0.0:8000
```

### **Base de données**
```bash
# Créer les migrations (après modification models.py)
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Voir l'état des migrations
python manage.py showmigrations

# Réinitialiser la BDD (⚠️ efface les données)
rm db.sqlite3
python manage.py migrate
```

### **Admin**
```bash
# Créer un super-utilisateur
python manage.py createsuperuser

# Changer le mot de passe d'un utilisateur
python manage.py changepassword admin
```

### **Utilitaires**
```bash
# Shell interactif Django
python manage.py shell

# Collecter les fichiers statiques (production)
python manage.py collectstatic

# Vérifier le projet
python manage.py check
```

---

## 📚 **Parcours d'apprentissage recommandé**

### **Jour 1 : Les bases**
1. ✅ Lire `DJANGO_TUTORIAL.md` (sections 1-4)
2. ✅ Comprendre `models.py` (structure des données)
3. ✅ Créer les migrations : `python manage.py makemigrations`
4. ✅ Appliquer les migrations : `python manage.py migrate`
5. ✅ Créer un super-user et accéder à `/admin/`

### **Jour 2 : Admin Django**
1. ✅ Lire section 5 du tutoriel (Django Admin)
2. ✅ Comprendre `admin.py`
3. ✅ Ajouter des élèves via l'admin
4. ✅ Tester les filtres et la recherche

### **Jour 3 : Views & Templates**
1. ✅ Lire sections 6-7 du tutoriel
2. ✅ Comprendre `views.py` et `urls.py`
3. ✅ Modifier `index.html` (page d'accueil)
4. ✅ Créer une nouvelle page

### **Jour 4 : Authentification**
1. ✅ Lire section 9 du tutoriel
2. ✅ Protéger la carte avec `@login_required`
3. ✅ Créer page login/logout

### **Jour 5+ : Fonctionnalités avancées**
1. ✅ API REST (Django REST Framework)
2. ✅ Formulaires personnalisés
3. ✅ Import CSV des élèves
4. ✅ Export PDF des rapports

---

## 🎨 **Fonctionnalités actuelles**

### ✅ **Déjà implémenté :**
- Page d'accueil avec 2 boutons
- Modèles (Eleve, Benevole, Binome)
- Django Admin configuré
- Routes de base
- Templates avec Bootstrap 5

### 🔜 **À développer :**
- Authentification complète
- Import CSV
- API REST pour les cartes
- Statistiques
- Export de données

---

## 🐛 **Problèmes courants & Solutions**

### **Erreur : "No module named 'django'"**
```bash
# Solution : activer l'environnement virtuel
source venv/bin/activate
```

### **Erreur : "CSRF verification failed"**
```python
# Dans templates : ajouter {% csrf_token %} dans les formulaires
<form method="POST">
    {% csrf_token %}
    ...
</form>
```

### **Page admin moche (sans CSS)****
```bash
# Solution : Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

### **Migrations non appliquées**
```bash
# Toujours après modification models.py :
python manage.py makemigrations
python manage.py migrate
```

---

## 📖 **Ressources d'apprentissage**

### **Documentation officielle**
- https://docs.djangoproject.com/
- https://docs.djangoproject.com/en/stable/intro/tutorial01/

### **Tutoriels recommandés**
- Django Girls : https://tutorial.djangogirls.org/
- Real Python : https://realpython.com/tutorials/django/
- MDN Django : https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django

### **Communautés**
- r/django (Reddit)
- Django Forum : https://forum.djangoproject.com/
- Discord Django

---

## 🚀 **Déploiement (plus tard)**

### **Options d'hébergement**
1. **Railway** (recommandé débutant) - Gratuit
2. **PythonAnywhere** - Gratuit
3. **Heroku** - Payant
4. **VPS** (votre serveur actuel)

### **Pour déployer sur votre serveur**
```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Variables d'environnement
export DEBUG=False
export SECRET_KEY="votre-clé-secrète-longue"
export ALLOWED_HOSTS="esa.unsoutienpourapprendre.org"

# 3. Collecter les statiques
python manage.py collectstatic

# 4. Migrations
python manage.py migrate

# 5. Utiliser gunicorn
pip install gunicorn
gunicorn esa_manager.wsgi:application
```

---

## ✅ **Checklist avant de commencer**

- [ ] Python 3.8+ installé
- [ ] Environnement virtuel créé
- [ ] Django installé
- [ ] `DJANGO_TUTORIAL.md` lu (au moins sections 1-3)
- [ ] Base de données initialisée (`migrate`)
- [ ] Super-utilisateur créé
- [ ] Serveur lancé et page accessible

