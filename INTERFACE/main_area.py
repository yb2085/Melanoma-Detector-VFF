# INTERFACE/ui/main_area.py

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageFilter
from customtkinter import CTkImage
import webbrowser

class MainAreaFrame(ctk.CTkFrame):
    """
    Cadre principal de l'application pour la gestion de l'import, l'affichage,
    l'analyse et la visualisation des résultats sur une image médicale.

    Attributs :
        master : Fenêtre principale (MainApp) qui contient ce cadre.
        detector : Instance de MelanomaDetector pour l'analyse d'image.
        translations : Dictionnaire de traductions multilingues.
        btnfont : Police utilisée pour les boutons et labels.
        currentlang : Langue courante de l'application.
        currentpath : Chemin de l'image actuellement chargée.
        originalimg : Image originale chargée (format CTkImage).
        blurredimg : Version floutée de l'image (CTkImage).
        showclear : Booléen indiquant si l'image affichée est floutée ou non.
        lastpred : Dernière prédiction effectuée (0 ou 1).
        lastconf : Dernière confiance de prédiction (en %).
        prog : Avancement de la barre de progression (0-100).
"""

    def __init__(self, master, detector, translations, btn_font):
        """
        Initialise la zone principale avec tous les widgets nécessaires.

        Args:
            master : Référence à la fenêtre principale (MainApp).
            detector : Objet MelanomaDetector pour la prédiction.
            translations : Dictionnaire des traductions de l'interface.
            btnfont : Police utilisée pour les boutons et labels.
        """
        super().__init__(master, corner_radius=0)
        self.master       = master
        self.detector     = detector
        self.translations = translations
        self.btn_font     = btn_font
        self.current_lang = master.current_lang
        self.current_path = None
        self.original_img = None
        self.blurred_img  = None
        self.show_clear   = False
        self.last_pred    = None
        self.last_conf    = None
        self._prog        = 0

        tr = self.translations[self.current_lang]

        # — Choisir image —
        self.import_btn = ctk.CTkButton(
            self,
            text=tr['import'],
            font=self.btn_font,
            width=200,
            command=self.import_image
        )
        self.import_btn.pack(pady=(0,5))

        # — Label photo (zone du corps) —
        self.label_entry = ctk.CTkEntry(
        self,
        placeholder_text=tr['label'],
        font=self.btn_font,
        width=225,    # Largeur augmentée (ajuste si besoin)
        height=30     # Hauteur augmentée pour plus de confort
        )
        self.label_entry.pack(pady=(0,10))


        # — Aperçu image —
        self.preview_lbl = ctk.CTkLabel(
            self,
            text=tr['no_image'],
            width=400, height=240,
            fg_color="#d0d0d0", corner_radius=10,
            font=self.btn_font
        )
        self.preview_lbl.pack()

        # — Toggle flou/nette —
        self.toggle_btn = ctk.CTkButton(
            self,
            text=tr['show_clear'],
            font=self.btn_font,
            width=150,
            command=self.toggle_blur
        )
        self.toggle_btn.pack(pady=(5,20))

        # — Bouton Analyser —
        self.analyse_btn = ctk.CTkButton(
            self,
            text=tr['analyse'],
            font=self.btn_font,
            width=200,
            command=self.start_analysis
        )
        self.analyse_btn.pack(pady=5)

        # — Barre de progression (cachée) —
        self.progress = ctk.CTkProgressBar(self, width=400, height=15)
        self.progress.configure(progress_color="#5DADE2")
        self.progress.pack(pady=10)
        self.progress.pack_forget()

        # — Cadre Résultat —
        self.result_frame = ctk.CTkFrame(
            self,
            fg_color="#F0F0F0",   # même couleur que la fenêtre principale
            corner_radius=10,
            border_width=2,
            border_color="#000000",   # bordure noire
            width=450,                # largeur augmentée
            height=60                 # hauteur raisonnable
        )
        self.result_frame.pack(pady=20)
        self.result_frame.pack_propagate(False)  # pour respecter la taille fixée
        tr = self.translations[self.current_lang]
        self.result_lbl = ctk.CTkLabel(
            self.result_frame,
            text=tr['no_result'],
            justify="center",
            font=self.btn_font,
            text_color="#000000",      # texte noir par défaut
            fg_color="transparent"     # fond transparent pour hériter du frame
        )
        self.result_lbl.pack(expand=True, fill="both", pady=10)


        # — Gauge circulaire —
        # Utilise la couleur de fond du cadre résultat
        
        self.gauge_canvas = tk.Canvas(
            self,
            width=220, height=220,
            bg='#dbdbdb',  # <-- bg_color is now always a valid color string
            highlightthickness=0
        )


        self.gauge_bg_arc = self.gauge_canvas.create_arc(
            10,10,210,210,
            start=90, extent=-360,
            style='arc', outline="#D6EAF8", width=20
        )
        self.gauge_arc = self.gauge_canvas.create_arc(
            10,10,210,210,
            start=90, extent=0,
            style='arc', outline="#5DADE2", width=20
        )
        self.gauge_text = self.gauge_canvas.create_text(
            110,110,
            text="",
            font=("Helvetica",16,"bold"),
            fill="#5DADE2"
        )
        self.gauge_canvas.pack_forget()

        # — Disclaimer & lien —
        self.disclaimer_lbl = ctk.CTkLabel(
            self,
            text=tr['disclaimer'],
            text_color="#5D6D7E",
            wraplength=500,
            justify="center",
            font=self.btn_font
        )
        self.disclaimer_lbl.pack(pady=(30,5))
        self.link_lbl = ctk.CTkLabel(
            self,
            text=tr['more_info'],
            text_color="#5DADE2",
            cursor="hand2",
            font=self.btn_font
        )
        self.link_lbl.pack(pady=(0,20))
        self.link_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://www.sante.fr/melanome-cancer-de-la-peau"))

    # — Fonctions de la zone principale — 

    def import_image(self):
        """
        Ouvre une boîte de dialogue pour sélectionner une image à importer.
        Charge l'image, crée une version floutée, et l'affiche dans la zone de prévisualisation.
        Réinitialise les résultats et la barre de progression.
        """
        path = filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.bmp")])
        if not path:
            return
        self.current_path = path
        img = Image.open(path).convert("RGB").resize((400,240), Image.LANCZOS)
        blurred = img.filter(ImageFilter.GaussianBlur(15))
        self.original_img = CTkImage(light_image=img, size=(400,240))
        self.blurred_img = CTkImage(light_image=blurred, size=(400,240))
        self.preview_lbl.configure(image=self.blurred_img, text="")
        self.show_clear = False
        tr = self.translations[self.current_lang]
        self.toggle_btn.configure(text=tr['show_clear'])
        
        # --- AJOUT ICI ---
        self.result_lbl.configure(
            text="PAS DE RESULTAT",
            text_color="#000000",
            fg_color="white"
        )
        self.result_frame.configure(
        border_width=2,
        border_color="#000000",
        fg_color="#F0F0F0"
        )
        # -----------------
        
        self.gauge_canvas.pack_forget()
        self.progress.set(0.0)


    def toggle_blur(self):
        """
        Permute l'affichage entre l'image floutée et l'image nette.
        Modifie le texte du bouton en conséquence.
        """
        if not self.original_img:
            return
        tr = self.translations[self.current_lang]
        if self.show_clear:
            self.preview_lbl.configure(image=self.blurred_img)
            self.toggle_btn.configure(text=tr['show_clear'])
        else:
            self.preview_lbl.configure(image=self.original_img)
            self.toggle_btn.configure(text=tr['show_blur'])
        self.show_clear = not self.show_clear

    def start_analysis(self):
        """
        Démarre l'analyse de l'image sélectionnée :
        - Vérifie que le champ label et un profil sont bien renseignés.
        - Affiche la barre de progression animée.
        - Lance la prédiction sur l'image via le detector.
        - Enregistre l'historique et affiche le résultat.
        """
        import tkinter.messagebox as messagebox
        label = self.label_entry.get().strip()
        tr = self.translations[self.current_lang]
        # Vérifie si le champ label est vide
        if not label:
            messagebox.showerror(
                "Erreur",
                "Veuillez remplir le champ 'Partie du corps/numéro Photo' avant d'analyser une image."
            )
            return
        # Vérifie si un profil est sélectionné
        if not self.master.current_profile:
            messagebox.showerror(
                "Erreur",
                "Veuillez créer un profil avant d'analyser une image."
            )
            return
        if not self.current_path:
            return
        self.analyse_btn.configure(state="disabled")
        self.progress.pack()
        self._prog = 0
        self._run_progress()


    def _run_progress(self):
        """
        Anime la barre de progression pendant l'analyse.
        Appelle la prédiction une fois l'animation terminée.
        """
        if self._prog < 100:
            self._prog += 5
            self.progress.set(self._prog / 100)
            self.after(80, self._run_progress)
        else:
            pred, conf = self.detector.predict(self.current_path)
            # Enregistrement de l’historique via le master
            label = self.label_entry.get() or "untitled"
            self.master.add_history(label, pred, conf, self.current_path)
            self.last_pred, self.last_conf = pred, conf
            self._display_result(pred, conf)
            self.master.refresh_history()
            self.analyse_btn.configure(state="normal")

    def _display_result(self, pred, conf):
        """
        Affiche le résultat de la prédiction dans le cadre résultat
        et met à jour la jauge de confiance.

        Args:
            pred (int): Classe prédite (0 = mélanome, 1 = bénin).
            conf (float): Pourcentage de confiance.
        """
        tr = self.translations[self.current_lang]
        color = "#58D68D" if pred==1 else "#EC7063"  # vert ou orange
        self.progress.pack_forget()
        # Bordure noire, fond vert/orange
        self.result_frame.configure(
            border_color="#000000",
            border_width=2,
            fg_color=color
        )
        lbl = (tr['not_detected'] if pred==1 else tr['detected'])
        # Texte noir, fond transparent (hérite du frame)
        self.result_lbl.configure(
            text=lbl,
            text_color="#000000",
            fg_color="transparent"
        )
        self.gauge_canvas.pack(pady=10, before=self.disclaimer_lbl)
        self._animate_gauge(0, conf)


    def _animate_gauge(self, current, target):
        """
        Anime la jauge de confiance du résultat de la prédiction.

        Args:
            current (float): Valeur actuelle de la jauge.
            target (float): Valeur cible à atteindre.
        """
        if current <= target:
            angle = -(current/100)*360
            self.gauge_canvas.itemconfigure(self.gauge_arc, extent=angle)
            self.gauge_canvas.itemconfigure(
                self.gauge_text,
                text=f"{self.translations[self.current_lang]['confidence']}:\n       {int(current)}%",
                fill="#5DADE2"
            )
            self.after(20, lambda: self._animate_gauge(current+1, target))

    def open_website(self):
        """
        Ouvre dans le navigateur la page d'information médicale sur le mélanome.
        """
        webbrowser.open("https://www.sante.fr/melanome-cancer-de-la-peau")

    def _load_history_entry(self, entry):
        """
        Recharge l'affichage principal à partir d'une entrée d'historique.

        Args:
            entry (dict): Dictionnaire contenant les informations de l'historique (label, image, prédiction, confiance).
        Effets :
            Met à jour le champ label, l'image affichée, l'état du flou, et affiche le résultat associé.
        """
        self.label_entry.delete(0, "end")
        self.label_entry.insert(0, entry.get('label', ''))

        image_path = entry.get('image_path')
        if image_path:
            try:
                img = Image.open(image_path).convert("RGB").resize((400, 240))
                blurred = img.filter(ImageFilter.GaussianBlur(15))
                self.original_img = CTkImage(light_image=img, size=(400, 240))
                self.blurred_img = CTkImage(light_image=blurred, size=(400, 240))
                self.current_path = image_path  # <-- Très important !
                self.show_clear = False
                self.preview_lbl.configure(image=self.blurred_img, text="")
                self.toggle_btn.configure(text=self.translations[self.current_lang]['show_clear'])
            except Exception:
                self.preview_lbl.configure(image=None, text=self.translations[self.current_lang]['no_image'])
                self.original_img = None
                self.blurred_img = None
                self.current_path = None
        else:
            self.preview_lbl.configure(image=None, text=self.translations[self.current_lang]['no_image'])
            self.original_img = None
            self.blurred_img = None
            self.current_path = None

        pred = entry.get('pred')
        conf = entry.get('conf')
        if pred is not None and conf is not None:
            self._display_result(pred, conf)
        else:
            self.result_lbl.configure(text="")
            self.gauge_canvas.pack_forget()

