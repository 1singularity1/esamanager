# 🚀 Installation du projet ESA Manager

Guide d'installation complet pour démarrer avec Django.

---

## ✅ Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (optionnel)

**Vérifier les versions :**
```bash
python --version   # Doit afficher Python 3.8+
pip --version      # Doit afficher pip
```

---

## 📥 Installation (10 minutes)

### 1️⃣ Créer un environnement virtuel

**Linux / Mac :**
```bash
cd esa_manager
python3 -m venv venv
source venv/bin/activate
```

**Windows :**
```bash
cd esa_manager
python -m venv venv
venv\Scripts\activate
```

**Vérification :**
Votre terminal doit afficher `(venv)` au début de la ligne.

---

### 2️⃣ Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Temps estimé :** 2-3 minutes

**Vérification :**
```bash
python -m django --version
# Doit afficher : 5.x.x
```

---

### 3️⃣ Créer la base de données

```bash
# Créer les migrations (transformer models.py en SQL)
python manage.py makemigrations

# Appliquer les migrations (créer les tables)
python manage.py migrate
```

**Résultat :**
- Fichier `db.sqlite3` créé
- Tables créées : core_eleve, core_benevole, core_binome, etc.

---

### 4️⃣ Créer un super-utilisateur (admin)

```bash
python manage.py createsuperuser
```

**Répondre aux questions :**
```
Username: admin
Email address: admin@esa.org
Password: ******** (votre mot de passe)
Password (again): ********
```

✅ **Super-utilisateur créé !**

---

### 5️⃣ Lancer le serveur

```bash
python manage.py runserver
```

**Résultat :**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## 🎉 Tester l'installation

### Ouvrir dans le navigateur :

**1. Page d'accueil :**
```
http://localhost:8000/
```
→ Doit afficher la page avec 2 boutons

**2. Interface admin :**
```
http://localhost:8000/admin/
```
→ Se connecter avec admin / votre_mot_de_passe
→ Interface d'administration Django

**3. API JSON :**
```
http://localhost:8000/api/eleves/
```
→ Doit afficher : `{"eleves": [], "count": 0}`

---

## 📊 Ajouter des données de test

### Via l'admin Django :

1. Aller sur http://localhost:8000/admin/
2. Cliquer sur "Élèves" → "Ajouter élève"
3. Remplir le formulaire :
   - Nom : Dupont
   - Prénom : Jean
   - Classe : CE2
   - Statut : À accompagner
4. Sauvegarder

**Répéter pour bénévoles et binômes !**

### Via le shell Django :

```bash
python manage.py shell
```

```python
from core.models import Eleve, Benevole, Binome
from datetime import date

# Créer un élève
eleve = Eleve.objects.create(
    nom="Dupont",
    prenom="Jean",
    classe="CE2",
    adresse="10 rue de la République, 13001 Marseille",
    arrondissement="13001",
    statut="a_accompagner",
    latitude=43.2965,
    longitude=5.3698
)

# Créer un bénévole
benevole = Benevole.objects.create(
    nom="Martin",
    prenom="Sophie",
    email="sophie.martin@example.com",
    adresse="25 avenue Prado, 13008 Marseille",
    arrondissement="13008",
    disponibilite="disponible",
    latitude=43.2617,
    longitude=5.3792
)

# Créer un binôme
binome = Binome.objects.create(
    eleve=eleve,
    benevole=benevole,
    date_debut=date.today(),
    actif=True
)

print("✅ Données de test créées !")

# Quitter
exit()
```

---

## 🔧 Commandes utiles

### Développement

```bash
# Lancer le serveur
python manage.py runserver

# Lancer sur un autre port
python manage.py runserver 8080

# Accessible depuis le réseau local
python manage.py runserver 0.0.0.0:8000
```

### Base de données

```bash
# Créer les migrations (après modification models.py)
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Voir l'état des migrations
python manage.py showmigrations

# Réinitialiser la BDD (⚠️ SUPPRIME TOUTES LES DONNÉES)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Shell interactif

```bash
# Shell Django (avec accès aux modèles)
python manage.py shell

# Dans le shell :
from core.models import Eleve
eleves = Eleve.objects.all()
print(eleves.count())
```

---

## 🐛 Problèmes courants

### "No module named 'django'"

**Cause :** Environnement virtuel pas activé

**Solution :**
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

---

### "CSRF verification failed"

**Cause :** Formulaire sans {% csrf_token %}

**Solution :** Vérifier que les formulaires contiennent :
```html
<form method="POST">
    {% csrf_token %}
    ...
</form>
```

---

### "Port already in use"

**Cause :** Le port 8000 est déjà utilisé

**Solution :**
```bash
# Utiliser un autre port
python manage.py runserver 8080

# Ou tuer le processus
# Linux/Mac :
lsof -ti:8000 | xargs kill -9
# Windows :
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

### "Table doesn't exist"

**Cause :** Migrations pas appliquées

**Solution :**
```bash
python manage.py migrate
```

---

## 📚 Prochaines étapes

**Maintenant que l'installation fonctionne :**

1. ✅ Lire `DJANGO_TUTORIAL.md`
2. ✅ Explorer l'interface admin
3. ✅ Ajouter des données de test
4. ✅ Personnaliser les templates
5. ✅ Créer vos propres vues

---

## 🆘 Besoin d'aide ?

**Documentation :**
- Django officiel : https://docs.djangoproject.com/
- README.md du projet
- DJANGO_TUTORIAL.md

**Communautés :**
- r/django (Reddit)
- Django Forum : https://forum.djangoproject.com/
- Stack Overflow (tag : django)

---

## ✅ Checklist d'installation

- [ ] Python 3.8+ installé
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Migrations appliquées (`python manage.py migrate`)
- [ ] Super-utilisateur créé
- [ ] Serveur lancé (`python manage.py runserver`)
- [ ] Page d'accueil accessible (http://localhost:8000/)
- [ ] Admin accessible (http://localhost:8000/admin/)
- [ ] Données de test ajoutées

**Si toutes les cases sont cochées, vous êtes prêt ! 🎉**
