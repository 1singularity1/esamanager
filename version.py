"""
Gestion de la version ESAdmin Marseille
"""

__version__ = "0.3.0"
__release_date__ = "2026-04-05"
__status__ = "beta"
__author__ = "ESA Marseille"
__changelog__ = "CHANGELOG.md"

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
        'changelog': __changelog__,
    }