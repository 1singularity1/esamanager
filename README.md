# ESAdmin — Système de gestion des binômes ESA Marseille

Application web Django de gestion des binômes de tutorat/mentorat pour l'antenne marseillaise de l'association ESA (Étudiants et Salarié(es)/Retraité(es) Accompagnant(es)).

**Version :** Beta 0.2.0 — voir [CHANGELOG.md](CHANGELOG.md)

---

## Architecture technique

- **Backend :** Django 5.2, Python 3.12, PostgreSQL 16, Gunicorn
- **Frontend :** Bootstrap 5, Leaflet.js, Vanilla JavaScript ES6+
- **Infrastructure :** Nginx 1.24, Ubuntu 24.04 LTS, VPS OVH France
- **Géolocalisation :** API BAN (Base Adresse Nationale)
- **Sécurité :** HTTPS Let's Encrypt, HTTP Basic Auth

---

## Fonctionnalités

### Gestion des données
- **Bénévoles** : statuts Disponible / Mentor / Candidat / Indisponible
- **Élèves** : statuts accompagné / à_accompagner / en_attente / archive
- **Binômes** : suivi date_début, date_fin, actif/inactif

### Cartographie interactive
- Carte des binômes actifs avec lignes de liaison élève ↔ bénévole
- Carte des élèves en attente et bénévoles disponibles
- Filtrage par arrondissement (13001–13016) et hors Marseille
- Calcul d'itinéraire à pied (OSRM)
- Recherche de bénévoles à proximité (Haversine)

### Pipeline d'import CSV
Import depuis Google Sheets (8 onglets) via commandes Django :

```bash
python manage.py import_benevoles benevoles.csv candidats.csv
python manage.py import_eleves eleves.csv
python manage.py import_eleves_attente eleves_en_attente.csv
python manage.py import_binomes binomes_*.csv
```

Toutes les commandes supportent `--dry-run`.

### Géolocalisation
```bash
python manage.py geolocalize_all --report echecs.csv
python manage.py import_corrections echecs.csv
```

---

## Modèles de données

### Benevole
Clé unique : `email`
Statuts : `Disponible`, `Mentor`, `Candidat`, `Indisponible`

### Eleve
Clé unique : `nom + prenom + telephone_parent`
Statuts : `accompagne`, `a_accompagner`, `en_attente`, `archive`

### Binome
- `eleve` : OneToOneField(Eleve)
- `benevole` : ForeignKey(Benevole)
- `actif` : Boolean
- `date_debut`, `date_fin`, `notes`

Le co-responsable est stocké dans `eleve.co_responsable` (FK User).

---

## Déploiement

### Prérequis
- Python 3.12, PostgreSQL 16
- Nginx, Gunicorn
- VPS Ubuntu 24.04

### Installation
```bash
git clone <repo>
cd esa_manager
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

### Mise à jour
```bash
bash update_esadmin.sh
```

Options : `--skip-import` (code seul), `--skip-geo` (sans géolocalisation).

### Configuration VPS
- `/home/ubuntu/esa_manager/esa_manager/settings.py`
- `/home/ubuntu/esa_manager/.env`
- `/etc/nginx/sites-available/esa_manager`
- `/etc/systemd/system/esa_manager.service`

### Commandes utiles
```bash
sudo systemctl status esa_manager
sudo journalctl -u esa_manager -n 50 --no-pager
sudo tail -f /var/log/nginx/error.log
```

---

## Co-responsables

| Nom | Onglet binômes |
|---|---|
| David Delannoy | binomes_david.csv |
| Clara Jonas | binomes_clara.csv |
| Georges Tchorbadjian | binomes_georges.csv |
| Bernadette Fortain | binomes_bernadette.csv |
| Gilbert Batac | binomes_gilbert.csv |
| Sylvie Hue | binomes_sylvie.csv |

---

## Auteur

David Delannoy — Co-responsable technique ESA Marseille
