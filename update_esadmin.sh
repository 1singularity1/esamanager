#!/bin/bash
# ============================================================
# Script de mise à jour ESAdmin
# Usage: ./update_esadmin.sh [--skip-import] [--skip-geo]
# ============================================================

set -e  # Arrêter en cas d'erreur

PROJECT_DIR="/home/ubuntu/esa_manager"
VENV="$PROJECT_DIR/venv/bin/activate"
CSV_DIR="$PROJECT_DIR/test_import_esa"
LOG_FILE="$PROJECT_DIR/update_$(date +%Y%m%d_%H%M%S).log"

SKIP_IMPORT=false
SKIP_GEO=false

for arg in "$@"; do
    case $arg in
        --skip-import) SKIP_IMPORT=true ;;
        --skip-geo)    SKIP_GEO=true ;;
    esac
done

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "============================================================"
log "Début de la mise à jour ESAdmin"
log "============================================================"

# ------------------------------------------------------------
# 1. DÉPLOIEMENT GIT
# ------------------------------------------------------------
log ""
log ">>> Étape 1 : Mise à jour du code (git pull)"
cd "$PROJECT_DIR"
git pull
log "Code mis à jour."

# ------------------------------------------------------------
# 2. MIGRATIONS DJANGO
# ------------------------------------------------------------
log ""
log ">>> Étape 2 : Migrations Django"
source "$VENV"
python manage.py migrate
log "Migrations appliquées."

# ------------------------------------------------------------
# 3. COLLECTSTATIC
# ------------------------------------------------------------
log ""
log ">>> Étape 3 : Collecte des fichiers statiques"
python manage.py collectstatic --noinput
log "Fichiers statiques collectés."

# ------------------------------------------------------------
# 4. IMPORT DES DONNÉES
# ------------------------------------------------------------
if [ "$SKIP_IMPORT" = false ]; then
    log ""
    log ">>> Étape 4 : Import des données CSV"

    log "  Vidage de la base..."
    python manage.py dbshell << 'SQL'
DELETE FROM core_profilutilisateur;
DELETE FROM core_binome;
DELETE FROM core_eleve_matieres_souhaitees;
DELETE FROM core_benevole_matieres;
DELETE FROM core_eleve;
DELETE FROM core_benevole;
SQL
    log "  Base vidée."

    log "  Import bénévoles..."
    python manage.py import_benevoles \
        "$CSV_DIR/benevoles.csv" \
        "$CSV_DIR/candidats.csv" \
        | tee -a "$LOG_FILE"

    log "  Import élèves accompagnés..."
    python manage.py import_eleves \
        "$CSV_DIR/eleves.csv" \
        | tee -a "$LOG_FILE"

    log "  Import élèves en attente..."
    python manage.py import_eleves_attente \
        "$CSV_DIR/eleves_en_attente.csv" \
        | tee -a "$LOG_FILE"

    log "  Import binômes..."
    python manage.py import_binomes \
        "$CSV_DIR"/binomes_*.csv \
        | tee -a "$LOG_FILE"

    log "  Reconstruction des profils co-responsables..."
    python manage.py dbshell << 'SQL'
UPDATE core_profilutilisateur p
SET benevole_id = b.id
FROM core_benevole b
JOIN auth_user u ON u.id = p.user_id
WHERE b.email = u.email;
SQL
    log "  Profils co-responsables reconstruits."

else
    log ""
    log ">>> Étape 4 : Import ignoré (--skip-import)"
fi

# ------------------------------------------------------------
# 5. GÉOLOCALISATION
# ------------------------------------------------------------
if [ "$SKIP_GEO" = false ] && [ "$SKIP_IMPORT" = false ]; then
    log ""
    log ">>> Étape 5 : Géolocalisation"
    python manage.py geolocalize_all \
        --report "$PROJECT_DIR/echecs_geo_$(date +%Y%m%d).csv" \
        | tee -a "$LOG_FILE"
    log "Géolocalisation terminée."
else
    log ""
    log ">>> Étape 5 : Géolocalisation ignorée"
fi

# ------------------------------------------------------------
# 6. REDÉMARRAGE DU SERVICE
# ------------------------------------------------------------
log ""
log ">>> Étape 6 : Redémarrage du service"
sudo systemctl restart esa_manager
sleep 2
sudo systemctl status esa_manager --no-pager | tee -a "$LOG_FILE"

log ""
log "============================================================"
log "Mise à jour terminée. Log : $LOG_FILE"
log "============================================================"
