# INTERFACE/ui/header.py

import customtkinter as ctk

class HeaderFrame(ctk.CTkFrame):
    """
    En-tête de l'application contenant le titre et le sélecteur de langue.

    Ce widget affiche en haut de l'interface le titre de l'application et un menu déroulant
    permettant de changer la langue de l'interface.

    Attributs :
        master : Widget parent (généralement la fenêtre principale).
        current_lang (str) : Langue courante ('fr' ou 'en').
        change_language_callback (function) : Fonction appelée lors du changement de langue.
        translations (dict) : Dictionnaire des traductions pour chaque langue.
        title_font (CTkFont) : Police utilisée pour le titre.
        btn_font (CTkFont) : Police utilisée pour le menu déroulant.
        title_label (CTkLabel) : Label affichant le titre de l'application.
        lang_option (CTkOptionMenu) : Menu déroulant pour sélectionner la langue.
    """
    def __init__(self,
                 master,
                 current_lang: str,
                 change_language_callback,
                 translations: dict,
                 title_font: ctk.CTkFont,
                 btn_font: ctk.CTkFont,
                 **kwargs):
        """
        Initialise le header avec le titre et le sélecteur de langue.

        Args:
            master : Widget parent.
            current_lang (str) : Langue courante ('fr' ou 'en').
            change_language_callback (function) : Fonction appelée lors du changement de langue.
            translations (dict) : Dictionnaire des traductions.
            title_font (CTkFont) : Police pour le titre.
            btn_font (CTkFont) : Police pour le menu déroulant.
            **kwargs : Arguments supplémentaires pour le CTkFrame.
        """
        super().__init__(master, fg_color="#F0F0F0", corner_radius=0, **kwargs)

        # 3 colonnes, avec la 1ère et la 3ème extensibles
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        # Label titre centré
        self.title_label = ctk.CTkLabel(
        self,
        text=translations[current_lang]['app_title'],
        font=title_font
        )
        self.title_label.place(relx=0.5, y=5, anchor="n")


        # Sélecteur de langue à droite
        self.lang_option = ctk.CTkOptionMenu(
            self,
            values=["Français", "English"],
            command=change_language_callback,
            width=120,
            font=btn_font
        )
        self.lang_option.grid(row=0, column=2, padx=20, sticky="e")
