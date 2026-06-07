# core/utils_matieres.py
#
# Module partagé entre import_eleves et import_benevoles.
# Contient la logique de normalisation et d'extraction des matières.

import re
import unicodedata


MATIERES_CANONIQUES = {
    'Mathématiques':       ['math', 'maths', 'mathématiques', 'calcul', 'géométrie', 'nombres','matières scientifiques'],
    'Français':            ['français', 'francais', 'lecture', 'écriture', 'ecriture', 'orthographe',
                            'grammaire', 'conjugaison', 'rédaction', 'redaction', 'compréhension',
                            'comprehension', 'consignes', 'conjuguaison', 'fraçais','lettres'],
    'Anglais':             ['anglais'],
    'Espagnol':            ['espagnol'],
    'Histoire-Géographie': ['histoire', 'géographie', 'geographie', 'hg', 'hist', 'his-geo'],
    'SVT':                 ['svt', 'sciences','matières scientifiques'],
    'Physique-Chimie':     ['physique', 'chimie', 'phys','matières scientifiques'],
    'Toutes matières':     ['toutes', 'toutes matières', 'toutes matieres', 'primaire',
                            'matières primaires', 'bases du primaire'],
    'Méthodologie':        ['méthodo', 'methodologie', 'méthodologie', 'organisation', 'méthode',
                            'apprendre à apprendre'],
    'Informatiques':        ['informatique', 'informatiques', 'informat', 'info', 'programmation','scratch','python'],
    'Orientation':          ['orientation', 'conseil en orientation', 'aide à l\'orientation', 'conseil d\'orientation'],
    'Concentration':         ['concentration', 'gestion du stress', 'gestion du temps', 'motivation', 'conseils pour se concentrer'],
    'Compréhension':         ['compréhension', 'comprehension', 'ne comprend pas', 'comprendre les énoncés',],
    'Mémorisation':         ['mémorisation', 'memorisation', 'mémoriser', 'mémoire', 'aide à la mémorisation', 'aide à la memorisation'],
}


def normaliser(texte):
    """Minuscules + suppression accents pour comparaison."""
    texte = texte.lower().strip()
    texte = unicodedata.normalize('NFD', texte)
    return ''.join(c for c in texte if unicodedata.category(c) != 'Mn')


def extraire_matieres(besoins_str):
    """
    Retourne (matieres_reconnues: list[str], texte_non_reconnu: str)

    Découpe la chaîne en tokens, les compare aux mots-clés canoniques.
    Ce qui n'est pas reconnu est renvoyé en texte libre (→ commentaires).
    """
    if not besoins_str:
        return [], ''

    tokens = re.split(r'[,;/\n]+', besoins_str)
    tokens = [t.strip() for t in tokens if t.strip()]

    matieres_trouvees = set()
    tokens_non_reconnus = []

    for token in tokens:
        token_norm = normaliser(token)
        reconnu = False

        for matiere_canon, mots_cles in MATIERES_CANONIQUES.items():
            for mot in mots_cles:
                if normaliser(mot) in token_norm:
                    matieres_trouvees.add(matiere_canon)
                    reconnu = True
                    break
            if reconnu:
                break

        if not reconnu:
            tokens_non_reconnus.append(token)

    texte_non_reconnu = ', '.join(tokens_non_reconnus)
    return list(matieres_trouvees), texte_non_reconnu
