"""
core/matching.py

Logique de scoring pour l'appariement élève ↔ bénévole.
Aucune écriture en base — fonctions pures, testables indépendamment.
"""

import math


# ---------------------------------------------------------------------------
# Mapping classe → niveau(x)
# ---------------------------------------------------------------------------

CLASSE_VERS_NIVEAU = {
    "CP":        {"primaire"},
    "CE1":       {"primaire"},
    "CE2":       {"primaire"},
    "CM1":       {"primaire"},
    "CM2":       {"primaire"},
    "6e":        {"college"},
    "5e":        {"college"},
    "4e":        {"college"},
    "3e":        {"college"},
    "2de":       {"lycee"},
    "1re":       {"lycee"},
    "Terminale": {"lycee"},
    "CAP":       {"lycee"},
    "ULIS":      {"primaire", "college", "lycee"},  # compatible tous niveaux
}


# ---------------------------------------------------------------------------
# Poids du scoring (total = 100)
# ---------------------------------------------------------------------------

POIDS_NIVEAU    = 35
POIDS_PROXIMITE = 35
POIDS_MATIERES  = 30

# Distance en km au-delà de laquelle le score de proximité tombe à 0
DISTANCE_MAX_KM = 5.0


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------

def distance_haversine(lat1, lon1, lat2, lon2):
    """
    Distance à vol d'oiseau en kilomètres entre deux points GPS.
    Retourne None si l'une des coordonnées est manquante.
    """
    if None in (lat1, lon1, lat2, lon2):
        return None

    R = 6371.0
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlam = math.radians(float(lon2) - float(lon1))

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def niveaux_eleve(classe):
    """
    Retourne l'ensemble des niveaux correspondant à la classe de l'élève.
    Retourne un ensemble vide si la classe est inconnue.
    """
    return CLASSE_VERS_NIVEAU.get(classe, set())


# ---------------------------------------------------------------------------
# Fonctions de scoring
# ---------------------------------------------------------------------------

def score_niveau(eleve, benevole):
    """
    35 pts si le bénévole couvre le niveau de l'élève, 0 sinon.
    """
    niveaux = niveaux_eleve(eleve.classe)
    if not niveaux:
        return 0.0

    couvre = (
        ("primaire" in niveaux and benevole.primaire) or
        ("college"  in niveaux and benevole.college)  or
        ("lycee"    in niveaux and benevole.lycee)
    )
    return float(POIDS_NIVEAU) if couvre else 0.0


def score_proximite(eleve, benevole):
    """
    35 pts à 0 km, décroissance linéaire jusqu'à 0 pt à DISTANCE_MAX_KM.
    Retourne 0 si l'une des coordonnées est absente.
    """
    dist = distance_haversine(
        eleve.latitude, eleve.longitude,
        benevole.latitude, benevole.longitude,
    )
    if dist is None:
        return 0.0

    ratio = max(0.0, 1.0 - dist / DISTANCE_MAX_KM)
    return round(POIDS_PROXIMITE * ratio, 2)


def score_matieres(eleve, benevole):
    """
    30 pts × (nb matières en commun / nb matières souhaitées par l'élève).
    Retourne 0 si l'élève n'a aucune matière renseignée.
    """
    matieres_eleve = set(
        m.nom.lower() for m in eleve.matieres_souhaitees.all()
    )
    if not matieres_eleve:
        return 0.0

    matieres_benevole = set(
        m.nom.lower() for m in benevole.matieres.all()
    )

    if not matieres_benevole:
        return 0.0

    commun = matieres_eleve & matieres_benevole
    ratio = len(commun) / len(matieres_eleve)
    return round(POIDS_MATIERES * ratio, 2)


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def calculer_score(eleve, benevole):
    """
    Retourne un dict avec le score total et le détail par critère.
    Le bénévole doit avoir statut == "Disponible" (filtre appliqué en amont).
    """
    s_niveau    = score_niveau(eleve, benevole)
    s_proximite = score_proximite(eleve, benevole)
    s_matieres  = score_matieres(eleve, benevole)
    total       = s_niveau + s_proximite + s_matieres

    dist = distance_haversine(
        eleve.latitude, eleve.longitude,
        benevole.latitude, benevole.longitude,
    )

    return {
        "benevole":        benevole,
        "score_total":     round(total, 2),
        "score_niveau":    s_niveau,
        "score_proximite": s_proximite,
        "score_matieres":  s_matieres,
        "distance_km":     round(dist, 2) if dist is not None else None,
    }


def suggestions_pour_eleve(eleve, benevoles_qs=None):
    """
    Retourne la liste des bénévoles Disponibles triés par score décroissant.
    """
    from .models import Benevole

    if benevoles_qs is None:
        benevoles_qs = Benevole.objects.filter(statut="Disponible").prefetch_related('matieres')

    resultats = [calculer_score(eleve, b) for b in benevoles_qs]
    return sorted(resultats, key=lambda r: r["score_total"], reverse=True)


def suggestions_pour_benevole(benevole, eleves_qs=None):
    """
    Retourne la liste des élèves à_accompagner triés par score décroissant.
    """
    from .models import Eleve

    if eleves_qs is None:
        eleves_qs = Eleve.objects.filter(statut="a_accompagner").prefetch_related('matieres_souhaitees')

    resultats = []
    for eleve in eleves_qs:
        s = calculer_score(eleve, benevole)
        resultats.append({
            "eleve":           eleve,
            "score_total":     s["score_total"],
            "score_niveau":    s["score_niveau"],
            "score_proximite": s["score_proximite"],
            "score_matieres":  s["score_matieres"],
            "distance_km":     s["distance_km"],
        })

    return sorted(resultats, key=lambda r: r["score_total"], reverse=True)
