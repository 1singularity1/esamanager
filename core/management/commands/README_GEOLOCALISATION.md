# 📍 Géolocalisation des adresses - Guide complet

Ce guide explique comment géolocaliser automatiquement les bénévoles et élèves d'ESAdmin Marseille.

---

## 🎯 Vue d'ensemble

**API utilisée :** Base Adresse Nationale (BAN) - Officielle et gratuite  
**Précision :** Optimale pour les adresses françaises  
**Taux de succès attendu :** 85-95%

---

## 🚀 Utilisation de base

### **Géolocaliser tout**

```bash
cd /chemin/vers/esa_manager
source venv/bin/activate

python manage.py geolocalize_all
```

**Résultat :**
- ✅ Calcule latitude/longitude pour chaque adresse
- ✅ Sauvegarde dans la base de données
- ✅ Les cartes affichent immédiatement les positions

---

## 🧪 Mode test (dry-run)

**Testez SANS modifier la base :**

```bash
python manage.py geolocalize_all --dry-run
```

**Affiche :**
```
[1/150] 🔍 Jean Dupont
       12 rue de la République, 13001
       ✅ Trouverait : 43.2965, 5.3698 (score: 87%)

[2/150] 🔍 Marie Martin
       217 rue des Poilus, 13011
       ✅ Trouverait : 43.3015, 5.4821 (score: 92%)
```

**→ Aucune donnée modifiée, vous voyez juste ce qui serait fait**

---

## 📊 Options avancées

### **Forcer la re-géolocalisation**

```bash
# Re-géolocalise même les adresses déjà géolocalisées
python manage.py geolocalize_all --force
```

### **Géolocaliser seulement les bénévoles**

```bash
python manage.py geolocalize_all --benevoles-only
```

### **Géolocaliser seulement les élèves**

```bash
python manage.py geolocalize_all --eleves-only
```

### **Générer un rapport des échecs**

```bash
python manage.py geolocalize_all --report echecs.csv
```

**Crée un fichier CSV avec les adresses qui ont échoué**

---

## 🔄 Workflow complet (recommandé)

### **Étape 1 : Test en dry-run**

```bash
python manage.py geolocalize_all --dry-run
```

**Vérifiez :**
- Combien d'adresses seront géolocalisées ?
- Taux de succès attendu ?

---

### **Étape 2 : Géolocalisation réelle avec rapport**

```bash
python manage.py geolocalize_all --report echecs.csv
```

**Résultat typique :**
```
📊 RÉSUMÉ
  📍 Total traité : 150
  ✅ Géolocalisés avec succès : 138
  ↻ Déjà géolocalisés : 0
  ⏭️  Ignorés (pas d'adresse) : 5
  ❌ Échecs : 7

📄 Rapport généré : echecs.csv
```

---

### **Étape 3 : Corriger les échecs manuellement**

**Ouvrez `echecs.csv` :**

| type | nom | prenom | adresse | code_postal | suggestion | adresse_corrigee |
|------|-----|--------|---------|-------------|------------|------------------|
| Bénévole | Dupont | Jean | chez marie | 13001 | Adresse trop vague | 12 rue Paradis |
| Élève | Martin | Paul | r paradix | 13006 | Vérifier orthographe | 15 rue Paradis |

**Remplissez la colonne `adresse_corrigee`**

---

### **Étape 4 : Réimporter les corrections**

```bash
python manage.py import_corrections echecs.csv
```

**Résultat :**
```
🔍 Jean Dupont
   Nouvelle adresse : 12 rue Paradis
   ✅ Géolocalisé : 43.2896, 5.3782 (score: 95%)

📊 RÉSUMÉ
  ✅ Corrigés avec succès : 7
  ❌ Échecs : 0
```

---

### **Étape 5 : Vérifier les cartes**

```
https://esa.unsoutienpourapprendre.org/carte/binomes/
https://esa.unsoutienpourapprendre.org/carte/enattente/
```

**Tous les markers doivent s'afficher !** 🗺️

---

## 🔧 Comment ça fonctionne

### **Stratégie en cascade**

Pour chaque adresse, le script essaie dans l'ordre :

**1. Adresse complète normalisée**
```
"12 rue de la République 13001 Marseille"
```

**2. Sans le numéro de rue**
```
"rue de la République 13001 Marseille"
```

**3. Juste le code postal**
```
"13001 Marseille"
```

**→ S'arrête dès qu'une tentative réussit**

---

### **Normalisations automatiques**

Le script corrige automatiquement :

| Original | Normalisé |
|----------|-----------|
| `12 r. République` | `12 rue République` |
| `5 av Prado` | `5 avenue Prado` |
| `bd Michelet` | `boulevard Michelet` |
| `imp. Paradis` | `impasse Paradis` |
| `St Charles` | `Saint Charles` |

---

### **Score de confiance**

L'API BAN retourne un score de 0 à 1 :
- **> 0.9** : Excellent (adresse exacte)
- **0.7 - 0.9** : Bon (adresse trouvée avec petite approximation)
- **0.4 - 0.7** : Acceptable (peut être imprécis)
- **< 0.4** : Rejeté (trop incertain)

---

## ⚠️ Cas d'échec courants

### **1. Adresses trop vagues**

❌ **Mauvais :**
```
"chez Marie"
"près du bar"
"face à la mairie"
```

✅ **Bon :**
```
"12 rue de la République"
"15 avenue Paradis"
```

---

### **2. Fautes d'orthographe**

❌ **Mauvais :**
```
"rue Paradix" (Paradis)
"rue du Prao" (Prado)
```

✅ **Solution :** Corriger dans `echecs.csv`

---

### **3. Adresses incomplètes**

❌ **Mauvais :**
```
"Rue Paradis" (pas de numéro, rue longue)
```

✅ **Mieux :**
```
"12 rue Paradis"
```

---

### **4. Adresses hors Marseille**

❌ **Problème :**
```
"15 rue Victor Hugo" (existe partout en France)
```

✅ **Solution :** Le script ajoute automatiquement "Marseille"

---

## 📋 Checklist avant géolocalisation

**Avant de lancer le script, vérifiez dans la Google Sheet :**

- [ ] Les adresses ont un numéro de rue
- [ ] Les codes postaux/arrondissements sont renseignés
- [ ] Pas d'adresses type "chez X", "près de Y"
- [ ] Orthographe correcte des noms de rues

**→ Ça réduit drastiquement les échecs**

---

## 🐛 Dépannage

### **Erreur : "No module named 'urllib'"**

**Solution :** C'est un module standard Python, vérifiez votre environnement virtuel

```bash
source venv/bin/activate
python --version  # Doit être 3.8+
```

---

### **Erreur : "timeout" ou "ConnectionError"**

**Cause :** Problème réseau ou API BAN temporairement indisponible

**Solution :**
```bash
# Réessayer plus tard
python manage.py geolocalize_all
```

---

### **Beaucoup d'échecs (> 20%)**

**Causes possibles :**
1. Adresses mal formatées dans la Google Sheet
2. Beaucoup d'adresses hors Marseille
3. Adresses trop vagues

**Solution :**
1. Générer le rapport : `--report echecs.csv`
2. Analyser les échecs
3. Corriger à la source (Google Sheet) si nécessaire
4. Réimporter les données
5. Re-géolocaliser

---

## 📊 Statistiques typiques

**Pour ~150 adresses :**

| Métrique | Valeur attendue |
|----------|-----------------|
| Succès du premier coup | 85-90% |
| Nécessitant fallback | 5-10% |
| Échecs (correction manuelle) | 3-5% |
| Ignorées (pas d'adresse) | 2-3% |

---

## 🔄 Maintenance régulière

### **Après chaque import CSV**

```bash
# Importer les nouvelles données
python manage.py import_benevoles benevoles.csv candidats.csv
python manage.py import_eleves eleves.csv
python manage.py import_binomes binomes*.csv

# Géolocaliser les nouveaux
python manage.py geolocalize_all
```

**→ Seules les nouvelles adresses (sans lat/lng) seront géolocalisées**

---

### **Tous les 6 mois (optionnel)**

```bash
# Re-géolocaliser tout pour améliorer la précision
# (l'API BAN s'améliore avec le temps)
python manage.py geolocalize_all --force
```

---

## 💡 Astuces

### **Géolocalisation plus rapide**

Le script fait une pause de 0.2 secondes entre chaque requête.

**Pour aller plus vite (à vos risques) :**

Éditez `geolocalize_all.py`, ligne ~70 et ~95 :
```python
# Avant
time.sleep(0.2)

# Après
time.sleep(0.1)  # ou même 0.05
```

**⚠️ Attention : Trop rapide = risque de ban temporaire de l'API**

---

### **Vérifier une adresse manuellement**

**Testez une adresse sur le site officiel :**
https://adresse.data.gouv.fr/

**Entrez l'adresse, vérifiez le résultat**

---

### **Géolocalisation manuelle via l'admin**

**Si vraiment une adresse ne passe pas :**

1. Allez sur https://esa.unsoutienpourapprendre.org/admin/core/eleve/
2. Cliquez sur l'élève/bénévole
3. Cherchez l'adresse sur Google Maps
4. Copiez les coordonnées GPS
5. Collez dans les champs `latitude` / `longitude`

---

## 📞 Support

**En cas de problème :**

1. Vérifiez les logs du script
2. Générez un rapport avec `--report`
3. Testez en `--dry-run` d'abord
4. Contactez David Delannoy : david.delannoy@gmail.com

---

**Version :** 1.0  
**Dernière mise à jour :** 9 mars 2026  
**API utilisée :** https://api-adresse.data.gouv.fr (BAN)
