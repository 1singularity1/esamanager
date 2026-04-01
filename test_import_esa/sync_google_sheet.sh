#!/bin/bash
#
# Script d'import complet des données Google Sheet vers ESAdmin Marseille
#
# Usage:
#   1. Exportez tous les onglets de la Google Sheet en CSV
#   2. Placez les CSV dans le même dossier que ce script
#   3. Lancez : ./sync_google_sheet.sh
#

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ESAdmin Marseille - Synchronisation Google Sheet${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# VÉRIFICATION DES FICHIERS
# ============================================================================

echo -e "${YELLOW}📋 Vérification des fichiers CSV...${NC}"

REQUIRED_FILES=(
    "2025-2026_Fichier_Antenne_-_Bénévoles_2025-2026.csv"
    "2025-2026_Fichier_Antenne_-_Candidats_à_recontacter.csv"
    "2025-2026_Fichier_Antenne_-_Enfants_aidés.csv"
    "2025-2026_Fichier_Antenne_-_Binômes_David.csv"
    "2025-2026_Fichier_Antenne_-_Binômes_Clara.csv"
    "2025-2026_Fichier_Antenne_-_Binômes_Georges.csv"
    "2025-2026_Fichier_Antenne_-_Binômes_Bernadette.csv"
    "2025-2026_Fichier_Antenne_-_Bînomes_Sylvie.csv"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Fichier manquant : $file${NC}"
        MISSING_FILES=$((MISSING_FILES + 1))
    else
        echo -e "${GREEN}✓${NC} $file"
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ $MISSING_FILES fichier(s) manquant(s)${NC}"
    echo ""
    echo "Pour exporter les CSV depuis Google Sheet :"
    echo "  1. Ouvrez chaque onglet"
    echo "  2. Fichier → Télécharger → Valeurs séparées par des virgules (.csv)"
    echo "  3. Placez tous les CSV dans ce dossier"
    exit 1
fi

echo -e "${GREEN}✅ Tous les fichiers sont présents${NC}"
echo ""

# ============================================================================
# UPLOAD VERS LE VPS
# ============================================================================

echo -e "${YELLOW}📤 Envoi des fichiers vers le VPS...${NC}"

VPS_HOST="ubuntu@213.32.23.36"
VPS_TMP="/tmp/csv_import"

# Créer le dossier temporaire sur le VPS
ssh $VPS_HOST "mkdir -p $VPS_TMP"

# Envoyer tous les CSV
for file in "${REQUIRED_FILES[@]}"; do
    echo "  → $file"
    scp "$file" $VPS_HOST:$VPS_TMP/
done

echo -e "${GREEN}✅ Fichiers envoyés${NC}"
echo ""

# ============================================================================
# IMPORT DANS LA BASE DE DONNÉES
# ============================================================================

echo -e "${YELLOW}🔄 Import dans la base de données...${NC}"
echo ""

ssh $VPS_HOST << 'ENDSSH'
cd /home/ubuntu/esa_manager
source venv/bin/activate

TMP="/tmp/csv_import"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1/3 📥 Import des bénévoles et candidats..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py import_benevoles \
    "$TMP/2025-2026_Fichier_Antenne_-_Bénévoles_2025-2026.csv" \
    "$TMP/2025-2026_Fichier_Antenne_-_Candidats_à_recontacter.csv"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2/3 📥 Import des élèves..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py import_eleves \
    "$TMP/2025-2026_Fichier_Antenne_-_Enfants_aidés.csv"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3/3 📥 Import des binômes..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py import_binomes \
    "$TMP/2025-2026_Fichier_Antenne_-_Enfants_aidés.csv" \
    "$TMP/2025-2026_Fichier_Antenne_-_Binômes_David.csv" \
    "$TMP/2025-2026_Fichier_Antenne_-_Binômes_Clara.csv" \
    "$TMP/2025-2026_Fichier_Antenne_-_Binômes_Georges.csv" \
    "$TMP/2025-2026_Fichier_Antenne_-_Binômes_Bernadette.csv" \
    "$TMP/2025-2026_Fichier_Antenne_-_Bînomes_Sylvie.csv"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧹 Nettoyage..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
rm -rf $TMP
echo "✅ Fichiers temporaires supprimés"

ENDSSH

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Synchronisation terminée !${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "🗺️  Les cartes sont maintenant à jour :"
echo "   https://esa.unsoutienpourapprendre.org/carte/binomes/"
echo ""
