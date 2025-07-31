import json
import os
import uuid
from datetime import datetime

DATA_DIR     = os.path.abspath(os.path.join(__file__, os.pardir, "../data"))
PROFILE_FILE = os.path.join(DATA_DIR, "profiles.json")

def _ensure_data_dir():
    """
    Vérifie si le dossier de stockage des données existe, sinon le crée.
    Cette fonction est utilisée en interne pour garantir la présence du dossier avant toute opération de lecture/écriture.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_profiles():
    """
    Charge la liste des profils depuis le fichier profiles.json.

    Si le fichier n'existe pas, il est créé avec une structure vide.
    En cas de fichier vide ou invalide, il est réinitialisé avec une liste vide.

    Returns:
        list: La liste des profils (dictionnaires).
    """
    _ensure_data_dir()
    # Si le fichier n'existe pas, on le crée avec la structure vide
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump({"profiles": []}, f, indent=2)
    # On tente de charger le JSON
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # Fichier vide ou invalide : on réinitialise
        data = {"profiles": []}
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    return data["profiles"]

def save_profiles(profiles):
    """
    Sauvegarde la liste des profils dans le fichier profiles.json.

    Args:
        profiles (list): Liste des profils (dictionnaires) à sauvegarder.
    """
    _ensure_data_dir()
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump({"profiles": profiles}, f, indent=2, ensure_ascii=False)

def add_profile(nom, prenom, age, taille, poids):
    """
    Ajoute un nouveau profil à la liste et le sauvegarde.

    Args:
        nom (str): Nom du profil.
        prenom (str): Prénom du profil.
        age (int): Âge du profil.
        taille (float): Taille du profil.
        poids (float): Poids du profil.

    Returns:
        dict: Le profil créé (dictionnaire).
    """
    profiles = load_profiles()
    new = {
        "id":       str(uuid.uuid4()),
        "nom":      nom,
        "prenom":   prenom,
        "age":      age,
        "taille":   taille,
        "poids":    poids,
        "history":  []
    }
    profiles.append(new)
    save_profiles(profiles)
    return new

def get_profile(profile_id):
    """
    Recherche un profil par son identifiant.

    Args:
        profile_id (str): Identifiant unique du profil.

    Returns:
        dict or None: Le profil trouvé, ou None si non trouvé.
    """
    for p in load_profiles():
        if p["id"] == profile_id:
            return p
    return None

def update_profile(profile_id, **fields):
    """
    Met à jour les champs d'un profil existant.

    Args:
        profile_id (str): Identifiant unique du profil à mettre à jour.
        **fields: Champs à modifier (nom, prenom, age, taille, poids, etc.).
    """
    profiles = load_profiles()
    for p in profiles:
        if p["id"] == profile_id:
            p.update(fields)
            break
    save_profiles(profiles)

def add_history(profile_id, label, pred, conf, image_path):
    """
    Ajoute une entrée d'historique à un profil.

    Args:
        profile_id (str): Identifiant unique du profil.
        label (str): Libellé de l'historique.
        pred (str): Prédiction associée.
        conf (float): Confiance de la prédiction.
        image_path (str): Chemin vers l'image associée.

    Returns:
        dict: L'entrée d'historique ajoutée.
    """
    profiles = load_profiles()
    for p in profiles:
        if p["id"] == profile_id:
            entry = {
                "timestamp":  datetime.now().isoformat(timespec="seconds"),
                "label":      label,
                "pred":       pred,
                "conf":       conf,
                "image_path": image_path
            }
            p.setdefault("history", []).append(entry)
            break
    save_profiles(profiles)
    return entry

def get_history(profile_id):
    """
    Récupère l'historique d'un profil.

    Args:
        profile_id (str): Identifiant unique du profil.

    Returns:
        list: Liste des entrées d'historique, ou liste vide si le profil n'existe pas.
    """
    p = get_profile(profile_id)
    return p.get("history", []) if p else []

def delete_profile(profile_id):
    """
    Supprime un profil par son identifiant.

    Args:
        profile_id (str): Identifiant unique du profil à supprimer.

    Returns:
        list: Liste des profils mise à jour.
    """
    profiles = load_profiles()
    profiles = [p for p in profiles if p["id"] != profile_id]
    save_profiles(profiles)
    return profiles
