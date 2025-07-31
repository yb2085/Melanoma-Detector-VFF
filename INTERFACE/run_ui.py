import os
import sys
import customtkinter as ctk

# ── Ajout du dossier parent (PROJET_ROOT) dans sys.path ──
#   On récupère le chemin de INTERFACE/, puis on remonte d’un cran.
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

# Maintenant Python verra LINK/ et INTERFACE/ comme packages
from LINK.profile_manager import load_profiles
from LINK.model_handler import MelanomaDetector
from INTERFACE.app import MainApp

def main():
    """
    Point d'entrée principal de l'application graphique.

    - Configure l'apparence de l'interface avec customtkinter.
    - Charge les profils utilisateurs depuis le fichier de données.
    - Instancie le détecteur de mélanome (modèle IA).
    - Crée et lance la fenêtre principale de l'application (MainApp).

    Cette fonction ne prend aucun argument et ne retourne rien.
    Elle lance la boucle principale de l'interface graphique, qui attend les interactions de l'utilisateur.
    """
    # Apparence CTk
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    # Charge les données
    profiles = load_profiles()
    detector = MelanomaDetector()

    # Lance l’application
    app = MainApp(detector, profiles)
    app.mainloop()

if __name__ == "__main__":
    """
    Permet d'exécuter le script comme programme principal.

    Si ce fichier est lancé directement (et non importé comme module),
    cette condition exécute la fonction main(), ce qui démarre l'application graphique.
    """
    main()
