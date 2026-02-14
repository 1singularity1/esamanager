"""
Gestion de la version ESAdmin Marseille
"""

__version__ = "0.1.0"
__release_date__ = "2026-02-14"
__status__ = "beta"
__author__ = "ESA Marseille"

def get_version():
    """Retourne la version avec le statut"""
    return f"Beta {__version__}"

def get_version_info():
    """Retourne toutes les infos de version"""
    return {
        'version': __version__,
        'release_date': __release_date__,
        'status': __status__,
        'display': get_version(),
    }