# 📥 Import des données Google Sheet vers ESAdmin Marseille

Ce guide explique comment synchroniser les données de votre Google Sheet vers la base de données PostgreSQL d'ESAdmin Marseille.

---

## 📋 Vue d'ensemble

**Flux de données :**
```
Google Sheet (source de vérité)
    ↓ Export manuel CSV
PostgreSQL ESAdmin
    ↓
Cartes Leaflet à jour
```

**Fichiers importés :**
- ✅ Bénévoles 2025-2026
- ✅ Candidats à recontacter
- ✅ Enfants aidés (élèves)
- ✅ Binômes (David, Clara, Georges, Bernadette, Sylvie)

---

## 🚀 Installation (à faire UNE SEULE FOIS)

### 1. Copier les commandes Django sur le VPS

```bash
# Sur votre machine locale
scp import_benevoles.py ubuntu@213.32.23.36:/home/ubuntu/esa_manager/core/management/commands/
scp import_eleves.py ubuntu@213.32.23.36:/home/ubuntu/esa_manager/core/management/commands/
scp import_binomes.py ubuntu@213.32.23.36:/home/ubuntu/esa_manager/core/management/commands/
```

### 2. Copier le script de synchronisation

```bash
# Rendre le script exécutable
chmod +x sync_google_sheet.sh
```

---

## 📤 Utilisation régulière (hebdomadaire ou selon besoin)

### Étape 1 : Exporter les CSV depuis Google Sheet

**Pour CHAQUE onglet :**

1. Cliquez sur l'onglet
2. **Fichier → Télécharger → Valeurs séparées par des virgules (.csv)**
3. Le fichier est téléchargé dans votre dossier "Téléchargements"

**Onglets à exporter (8 fichiers) :**
- ✅ Bénévoles 2025-2026
- ✅ Candidats à recontacter
- ✅ Enfants aidés
- ✅ Binômes David
- ✅ Binômes Clara
- ✅ Binômes Georges
- ✅ Binômes Bernadette
- ✅ Bînomes Sylvie

---

### Étape 2 : Placer les CSV dans un dossier

```bash
# Créer un dossier dédié
mkdir ~/esa_import
cd ~/esa_import

# Copier le script de synchro
cp /chemin/vers/sync_google_sheet.sh .

# Déplacer tous les CSV téléchargés dans ce dossier
mv ~/Téléchargements/2025-2026_Fichier_Antenne_*.csv .
```

---

### Étape 3 : Lancer la synchronisation

```bash
cd ~/esa_import
./sync_google_sheet.sh
```

**Le script va automatiquement :**
1. ✅ Vérifier que tous les fichiers CSV sont présents
2. ✅ Les envoyer vers le VPS
3. ✅ Importer les bénévoles et candidats
4. ✅ Importer les élèves
5. ✅ Créer/mettre à jour les binômes
6. ✅ Mettre à jour les statuts (Mentor, Disponible, Candidat)
7. ✅ Nettoyer les fichiers temporaires

**Durée totale : 1-2 minutes**

---

## 🎯 Ce qui est importé automatiquement

### Bénévoles
- ✅ Nom, prénom, email, téléphone
- ✅ Arrondissement, adresse
- ✅ Niveaux (Primaire, Collège, Lycée)
- ✅ Documents administratifs (réunion d'accueil, casier judiciaire, photo)
- ✅ Statut automatique :
  - **"Mentor"** si présent dans un binôme
  - **"Disponible"** sinon
  - **"Candidat"** si dans "Candidats à recontacter"

### Élèves
- ✅ Nom, prénom de l'enfant
- ✅ Nom, téléphone, email des parents
- ✅ Arrondissement, adresse
- ✅ Classe, établissement
- ✅ Matières souhaitées
- ✅ Commentaires et observations
- ✅ Co-responsable (David, Clara, Georges, etc.)

### Binômes
- ✅ Association élève ↔ bénévole
- ✅ Date de début (date contrat)
- ✅ Statut actif
- ✅ Notes et commentaires
- ✅ Co-responsable identifié automatiquement depuis le nom du fichier

---

## 🔄 Logique de mise à jour (update_or_create)

**Bénévoles :**
- Clé unique : **Email**
- Si email existe → mise à jour des données
- Si email n'existe pas → création

**Élèves :**
- Clé unique : **Nom + Prénom + Téléphone parent**
- Si combinaison existe → mise à jour
- Si n'existe pas → création

**Binômes :**
- Clé unique : **Élève** (un élève = un seul binôme actif)
- Si élève a déjà un binôme → mise à jour du bénévole
- Si élève n'a pas de binôme → création

**→ Pas de doublons, les données sont écrasées par les plus récentes**

---

## 🛠️ Commandes individuelles (avancé)

Si vous voulez importer manuellement sur le VPS :

### Import bénévoles uniquement

```bash
ssh ubuntu@213.32.23.36
cd /home/ubuntu/esa_manager
source venv/bin/activate
python manage.py import_benevoles \
    /tmp/benevoles.csv \
    /tmp/candidats.csv
```

### Import élèves uniquement

```bash
python manage.py import_eleves /tmp/enfants_aides.csv
```

### Import binômes uniquement

```bash
python manage.py import_binomes \
    /tmp/enfants_aides.csv \
    /tmp/binomes_david.csv \
    /tmp/binomes_clara.csv \
    /tmp/binomes_georges.csv \
    /tmp/binomes_bernadette.csv \
    /tmp/binomes_sylvie.csv
```

---

## ⚠️ Points d'attention

### Données obligatoires

**Pour qu'un bénévole soit importé :**
- ✅ Prénom
- ✅ Email (clé unique)

**Pour qu'un élève soit importé :**
- ✅ Nom famille
- ✅ Prénom enfant
- ⚠️ Téléphone parent (recommandé pour éviter doublons)

**Pour qu'un binôme soit créé :**
- ✅ Bénévole doit exister dans la base
- ✅ Élève doit exister dans la base

### Ordre d'import recommandé

**TOUJOURS dans cet ordre :**
1. **Bénévoles** (d'abord)
2. **Élèves** (ensuite)
3. **Binômes** (en dernier)

**→ Le script `sync_google_sheet.sh` respecte automatiquement cet ordre**

---

## 🐛 En cas d'erreur

### Erreur : "Bénévole non trouvé"

**Cause :** Le bénévole n'existe pas encore dans la base

**Solution :**
1. Vérifiez que le fichier "Bénévoles 2025-2026.csv" contient ce bénévole
2. Relancez l'import des bénévoles en premier

### Erreur : "Élève non trouvé"

**Cause :** L'élève n'existe pas encore dans la base

**Solution :**
1. Vérifiez que le fichier "Enfants aidés.csv" contient cet élève
2. Vérifiez que Nom + Prénom + Téléphone correspondent exactement

### Erreur : "Plusieurs bénévoles trouvés"

**Cause :** Homonymes dans la base

**Solution :**
- Utilisez l'email comme clé unique (prioritaire)
- Ou vérifiez manuellement dans l'admin Django

---

## 📊 Vérifier que tout est à jour

### 1. Vérifier les stats sur la page d'accueil

```
https://esa.unsoutienpourapprendre.org/
```

**Vous devez voir :**
- Nombre d'élèves à jour
- Nombre de bénévoles à jour
- Nombre de binômes actifs

### 2. Vérifier les cartes

```
https://esa.unsoutienpourapprendre.org/carte/binomes/
https://esa.unsoutienpourapprendre.org/carte/enattente/
```

**Les marqueurs doivent correspondre aux données de la Google Sheet**

---

## 🔐 Sécurité

### Fichiers CSV en local

**Après l'import :**
```bash
# Supprimer les CSV locaux
rm ~/esa_import/*.csv
```

**Ou les stocker dans un dossier chiffré (VeraCrypt, 7-Zip avec mot de passe)**

### Fichiers CSV sur le VPS

**Automatiquement supprimés** par le script après import

**Vérification manuelle :**
```bash
ssh ubuntu@213.32.23.36
ls /tmp/csv_import/  # Doit être vide
```

---

## 📅 Fréquence recommandée

| Fréquence | Cas d'usage |
|-----------|-------------|
| **Hebdomadaire** | Phase de test, peu de changements |
| **2-3x par semaine** | Utilisation active, nouveaux binômes réguliers |
| **Quotidienne** | Période de rentrée, forte activité |

**Après chaque import → Les cartes sont à jour immédiatement**

---

## 📝 Logs et debugging

### Voir les logs Django

```bash
ssh ubuntu@213.32.23.36
cd /home/ubuntu/esa_manager
source venv/bin/activate
python manage.py import_benevoles benevoles.csv candidats.csv 2>&1 | tee import_log.txt
```

### Voir les logs système

```bash
ssh ubuntu@213.32.23.36
sudo journalctl -u esa_manager -n 100 --no-pager
```

---

## 🎯 Résumé - Checklist rapide

**Tous les vendredis (ou selon besoin) :**

- [ ] Exporter les 8 CSV depuis Google Sheet
- [ ] Les placer dans `~/esa_import/`
- [ ] Lancer `./sync_google_sheet.sh`
- [ ] Vérifier les stats sur https://esa.unsoutienpourapprendre.org/
- [ ] Supprimer les CSV locaux

**Durée totale : 5 minutes**

---

## 📞 Support

**En cas de problème :**
1. Vérifier les logs d'import (affichés par le script)
2. Vérifier que tous les CSV sont à jour
3. Contacter David Delannoy : david.delannoy@gmail.com

---

**Version du document :** 1.0  
**Dernière mise à jour :** 9 mars 2026
