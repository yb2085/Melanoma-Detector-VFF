import customtkinter as ctk
import LINK.profile_manager as pm

from header      import HeaderFrame
from sidebar     import SidebarFrame
from main_area   import MainAreaFrame
from traductions import translations 

class MainApp(ctk.CTk):
    """
    Fenêtre principale de l'application de détection de mélanome.

    Cette classe hérite de CTk (customtkinter) et orchestre l'ensemble de l'interface graphique :
    - gestion du changement de langue,
    - gestion des profils utilisateurs,
    - affichage de la sidebar, du header et de la zone principale,
    - communication entre les différentes parties de l'interface.

    Attributs :
        detector : Instance de MelanomaDetector pour l'analyse d'images.
        profiles (list) : Liste des profils utilisateurs.
        current_lang (str) : Langue courante de l'interface ('fr' ou 'en').
        current_profile (dict) : Profil utilisateur actuellement sélectionné.
        btn_font : Police utilisée pour les boutons.
        title_font : Police utilisée pour les titres.
        header : Widget HeaderFrame affichant le titre et le sélecteur de langue.
        sidebar : Widget SidebarFrame pour la gestion des profils et de l'historique.
        main_area : Widget MainAreaFrame pour l'import, l'analyse et l'affichage des résultats.
        container : Cadre principal contenant la sidebar et la zone principale.
    """

    def __init__(self, detector, profiles):
        """
        Initialise la fenêtre principale et tous ses composants graphiques.

        Args:
            detector : Instance de MelanomaDetector pour l'analyse d'images.
            profiles (list) : Liste des profils utilisateurs chargés au démarrage.
        Effets :
            Crée et place tous les widgets de l'interface graphique.
            Configure l'apparence et la langue par défaut.
        """
        super().__init__()
        self.detector        = detector
        self.profiles        = profiles
        self.current_lang    = 'fr'
        self.current_profile = None

        # Configuration de la fenêtre principale
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        self.title(translations[self.current_lang]['app_title'])
        self.geometry("900x700")
        self.configure(fg_color="#F0F0F0")

        # Polices partagées
        self.btn_font   = ctk.CTkFont(family="Helvetica", size=14, weight="bold")
        self.title_font = ctk.CTkFont(family="Helvetica", size=20, weight="bold")

        # Création du header (titre + sélecteur de langue)
        self.header = HeaderFrame(
            master=self,
            current_lang=self.current_lang,
            change_language_callback=self.change_language,
            translations=translations,
            title_font=self.title_font,
            btn_font=self.btn_font
        )
        self.header.pack(fill="x", pady=(10,0))

        # Container pour sidebar + main_area
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=20, pady=10)

        # Sidebar (gestion profils/historique)
        self.sidebar = SidebarFrame(
            master=self,
            profiles=self.profiles,
            translations=translations,
            btn_font=self.btn_font,
            title_font=self.title_font
        )
        self.sidebar.pack(in_=self.container, side="left", fill="y")

        # Zone principale (import, analyse, résultats)
        self.main_area = MainAreaFrame(
            master=self,
            detector=self.detector,
            translations=translations,
            btn_font=self.btn_font
        )
        self.main_area.pack(in_=self.container, side="right", expand=True, fill="both")

        # Sélection initiale du profil et de la langue
        self.header.lang_option.set("Français")
        if self.profiles:
            self.current_profile = self.profiles[0]
            names = [self.sidebar._format_profile_name(p) for p in self.profiles]
            self.sidebar.profile_option.configure(values=names)
            self.sidebar.profile_option.set(names[0])
            self.sidebar._refresh_history()
        else:
            self.sidebar.profile_option.set(translations[self.current_lang]['add_profile'])

    def change_language(self, choice):
        """
        Change la langue de l'interface graphique.

        Args:
            choice (str) : Libellé de la langue choisie ("Français" ou "English").
        Effets :
            Détruit puis reconstruit tous les widgets pour refléter la nouvelle langue.
            Met à jour le titre de la fenêtre et les textes affichés.
        """
        self.current_lang = 'fr' if choice.startswith("Fr") else 'en'
        self.title(translations[self.current_lang]['app_title'])

        # Détruit et reconstruit tous les widgets dépendant de la langue
        self.header.destroy()
        self.sidebar.destroy()
        self.main_area.destroy()
        self.container.destroy()

        # Reconstruction du header
        self.header = HeaderFrame(
            master=self,
            current_lang=self.current_lang,
            change_language_callback=self.change_language,
            translations=translations,
            title_font=self.title_font,
            btn_font=self.btn_font
        )
        self.header.pack(fill="x", pady=(10,0))

        # Reconstruction du container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=20, pady=10)

        # Reconstruction de la sidebar et de la zone principale
        self.sidebar = SidebarFrame(
            master=self,
            profiles=self.profiles,
            translations=translations,
            btn_font=self.btn_font,
            title_font=self.title_font
        )
        self.sidebar.pack(in_=self.container, side="left", fill="y")

        self.main_area = MainAreaFrame(
            master=self,
            detector=self.detector,
            translations=translations,
            btn_font=self.btn_font
        )
        self.main_area.pack(in_=self.container, side="right", expand=True, fill="both")

        # Réinitialisation de la sélection
        self.header.lang_option.set("Français" if self.current_lang=='fr' else "English")
        if self.current_profile:
            name = self.sidebar._format_profile_name(self.current_profile)
            self.sidebar.profile_option.set(name)
            self.sidebar._refresh_history()

    def load_history_entry(self, entry):
        """
        Charge une entrée d'historique dans la zone principale.

        Args:
            entry (dict) : Dictionnaire contenant les informations de l'historique sélectionné.
        Effets :
            Appelle la méthode de MainAreaFrame pour afficher l'entrée d'historique.
        """
        self.main_area._load_history_entry(entry)

    def add_history(self, label, pred, conf, image_path):
        """
        Ajoute une nouvelle entrée à l'historique du profil courant.

        Args:
            label (str) : Libellé de la photo (zone du corps).
            pred (int) : Prédiction (0 = mélanome, 1 = bénin).
            conf (float) : Confiance de la prédiction (en %).
            image_path (str) : Chemin de l'image analysée.
        Effets :
            Enregistre l'analyse dans l'historique du profil courant.
        """
        pm.add_history(self.current_profile['id'], label, pred, conf, image_path)

    def refresh_history(self):
        """
        Rafraîchit l'affichage de l'historique dans la sidebar.

        Effets :
            Met à jour la liste des analyses précédentes pour le profil courant.
        """
        self.sidebar._refresh_history()
