import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esa_manager.settings')
django.setup()

from core.models import Benevole, Eleve
from django.contrib.auth.models import User

def random_string(n=8):
    return ''.join(random.choices(string.ascii_lowercase, k=n))

def random_phone():
    return f"06{''.join(random.choices(string.digits, k=8))}"

def random_lat():
    return float(f"{random.uniform(43.25, 43.35):.6f}")

def random_lon():
    return float(f"{random.uniform(5.33, 5.45):.6f}")

# Anonymiser les bénévoles
for b in Benevole.objects.all():
    b.nom = f"Nom_{b.id}"
    b.prenom = f"Prenom_{b.id}"
    b.email = f"benevole_{b.id}@test.fr"
    b.telephone = random_phone()
    b.adresse = f"{b.id} rue de la Paix"
    b.numero_rue = str(b.id)
    b.ville = "Marseille"
    b.commentaires = ""
    b.divers = ""
    b.profession = "Profession test"
    b.disponibilites_competences = ""
    b.informations_complementaires = ""
    # b.latitude = random_lat()
    # b.longitude = random_lon()
    b.save()

# Anonymiser les élèves
for e in Eleve.objects.all():
    e.nom = f"Eleve_{e.id}"
    e.prenom = f"Prenom_{e.id}"
    e.nom_parent = f"Parent_{e.id}"
    e.prenom_parent = f"ParentPrenom_{e.id}"
    e.telephone = random_phone()
    e.telephone_parent = random_phone()
    e.email_parent = f"parent_{e.id}@test.fr"
    e.adresse = f"{e.id} rue de la Paix"
    e.numero_rue = str(e.id)
    e.ville = "Marseille"
    e.complement_adresse = ""
    # e.latitude = random_lat()
    # e.longitude = random_lon()
    e.save()

# Anonymiser les utilisateurs
for u in User.objects.all():
    if not u.is_superuser:
        u.first_name = f"User_{u.id}"
        u.last_name = f"Test_{u.id}"
        u.email = f"user_{u.id}@test.fr"
        u.username = f"user_{u.id}"
        u.save()

print("Anonymisation terminée.")