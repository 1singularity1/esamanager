# 🚀 QUICKSTART - ESA Manager Django

## 📦 Démarrage ultra-rapide (5 minutes)

### 1️⃣ Extraire le projet
```bash
tar -xzf esa_manager.tar.gz
cd esa_manager
```

### 2️⃣ Installer
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

pip install django
```

### 3️⃣ Initialiser
```bash
python manage.py migrate
python manage.py createsuperuser
# Username: admin
# Password: admin123
```

### 4️⃣ Lancer
```bash
python manage.py runserver
```

### 5️⃣ Ouvrir
- **Page d'accueil :** http://localhost:8000/
- **Admin Django :** http://localhost:8000/admin/

---

## 📚 Fichiers importants

| Fichier | Description |
|---------|-------------|
| `README.md` | Vue d'ensemble complète |
| `INSTALLATION.md` | Guide d'installation détaillé |
| `DJANGO_TUTORIAL.md` | Tutoriel Django complet |
| `requirements.txt` | Dépendances Python |
| `manage.py` | Commandes Django |

---

## 🎯 Structure du projet

```
esa_manager/
├── manage.py              # Commandes Django
├── esa_manager/           # Configuration
│   └── settings.py        # ⭐ Configuration principale
├── core/                  # Application principale
│   ├── models.py          # ⭐ Modèles (Eleve, Benevole, Binome)
│   ├── views.py           # ⭐ Logique
│   ├── urls.py            # ⭐ Routes
│   ├── admin.py           # ⭐ Configuration admin
│   └── templates/         # ⭐ Pages HTML
└── db.sqlite3             # Base de données (après migrate)
```

---

## 💡 Commandes essentielles

```bash
# Lancer le serveur
python manage.py runserver

# Créer/Appliquer migrations
python manage.py makemigrations
python manage.py migrate

# Créer admin
python manage.py createsuperuser

# Shell interactif
python manage.py shell
```

---

## 🎓 Apprendre Django

**Ordre recommandé :**
1. Lire `DJANGO_TUTORIAL.md` (sections 1-4)
2. Explorer l'admin Django
3. Modifier `views.py` et `templates/`
4. Créer vos propres modèles

---

## ✨ Fonctionnalités actuelles

✅ Page d'accueil avec 2 boutons
✅ Modèles (Eleve, Benevole, Binome)
✅ Django Admin configuré
✅ Cartes Leaflet intégrées
✅ API JSON
✅ Templates Bootstrap 5

---

## 🆘 Problèmes ?

**"No module named 'django'"**
```bash
source venv/bin/activate
pip install django
```

**"Table doesn't exist"**
```bash
python manage.py migrate
```

**"Port already in use"**
```bash
python manage.py runserver 8080
```

---

## 🎉 Bon apprentissage !

**Tous les fichiers sont commentés ligne par ligne pour votre apprentissage.**

**N'hésitez pas à :**
- Modifier le code
- Casser des choses (c'est comme ça qu'on apprend !)
- Lire les commentaires
- Expérimenter

**Chaque erreur est une opportunité d'apprentissage ! 🚀**
