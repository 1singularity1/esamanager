# Changelog ESAdmin Marseille

## [0.2.0] - 2026-04-02

### Backend
- Pipeline d'import CSV complet (`import_benevoles`, `import_eleves`, `import_eleves_attente`, `import_binomes`)
- Nouveau script `import_eleves_attente` pour les élèves en statut `en_attente`
- Géolocalisation via l'API BAN (Base Adresse Nationale) avec rapport d'échecs et commande `import_corrections`
- Correction modèle : `volet_3_casier_judiciaire` rendu nullable
- Préservation du statut `Mentor` lors de l'import candidats
- Priorité statut bénévole sur statut candidat
- Détection et ignorage de la section `Responsables` dans le CSV bénévoles
- Normalisation des classes dans `import_eleves_attente` avec fallback CAP/Bac Pro
- Script de mise à jour `update_esadmin.sh`

### Frontend
- Correction du décalage des filtres par arrondissement sur la carte des binômes
- Ajout d'un filtre "Autre" pour les codes postaux hors Marseille
- Affichage d'un binôme dès qu'un de ses éléments appartient à l'arrondissement filtré
- Refactoring de la carte en attente : remplacement de `binomeLayers` par deux layers distincts `eleveLayers` et `benevoleLayers`

---

## [0.1.0] - 2026-02-14

- Version initiale
