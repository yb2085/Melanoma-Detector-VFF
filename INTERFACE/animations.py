import tkinter as tk

def animate_gauge(widget, canvas, arc_id, text_id, target, color, current=0, delay=20):
    """
    Anime une jauge circulaire affichée sur un Canvas Tkinter.

    Cette fonction fait progresser visuellement une jauge (arc de cercle) de 0 à la valeur cible.
    À chaque étape, l'arc et le texte du pourcentage sont mis à jour, puis la fonction se rappelle elle-même
    après un court délai, jusqu'à atteindre la valeur finale.

    Args:
        widget: Widget parent (par exemple, une frame CTk) qui possède la méthode after().
        canvas: Canvas Tkinter sur lequel la jauge est dessinée.
        arc_id: Identifiant de l'arc de progression (retourné par create_arc).
        text_id: Identifiant du texte de pourcentage (retourné par create_text).
        target (int): Valeur finale de la jauge (entre 0 et 100).
        color (str): Couleur de l'arc et du texte (ex: "#5DADE2").
        current (int, optionnel): Valeur de départ de l'animation (par défaut 0).
        delay (int, optionnel): Délai en millisecondes entre chaque incrément (par défaut 20ms).

    Effet:
        Met à jour l'affichage de la jauge sur le canvas à chaque appel.
    """
    if current <= target:
        extent = -(current / 100) * 360
        canvas.itemconfigure(arc_id, extent=extent, outline=color)
        canvas.itemconfigure(text_id, text=f"{int(current)}%", fill=color)
        widget.after(delay,
                     lambda: animate_gauge(widget, canvas, arc_id, text_id, target, color, current + 1, delay))


class Spinner:
    """
    Widget d'animation circulaire (spinner) pour indiquer une attente ou un chargement.

    Ce composant affiche un arc qui tourne en boucle, typiquement utilisé pour signaler à l'utilisateur
    qu'une opération est en cours (par exemple, un calcul ou un chargement de données).

    Attributs:
        parent: Widget parent dans lequel le spinner est affiché.
        size (int): Taille du canvas (largeur/hauteur en pixels).
        canvas: Canvas Tkinter contenant l'animation.
        arc: Identifiant de l'arc dessiné.
        _angle (int): Angle courant de l'arc (pour l'animation).
        _job: Identifiant du job after() pour pouvoir arrêter l'animation.
    """

    def __init__(self, parent, size=50, width=6, bg=None, color="#5DADE2"):
        """
        Initialise le spinner avec les paramètres d'affichage.

        Args:
            parent: Widget parent (frame ou fenêtre).
            size (int, optionnel): Taille du canvas (par défaut 50).
            width (int, optionnel): Largeur du trait de l'arc (par défaut 6).
            bg (str, optionnel): Couleur de fond du canvas (par défaut, héritée du parent ou "#F0F0F0").
            color (str, optionnel): Couleur de l'arc animé (par défaut "#5DADE2").
        """
        self.parent = parent
        self.size = size
        # Détection dynamique du fond du parent
        if bg is None:
            try:
                bg = parent.cget("fg_color")
                if bg in (None, "transparent", ""):
                    bg = "#F0F0F0"
            except Exception:
                bg = "#F0F0F0"
        self.canvas = tk.Canvas(parent,
            width=size, height=size,
            bg=bg, highlightthickness=0)
        
        pad = width  
        self.arc = self.canvas.create_arc(
            pad, pad,
            size - pad, size - pad,
            start=0, extent=120,
            style='arc',
            outline=color,
            width=width
        )
        self._angle = 0
        self._job   = None

    def pack(self, **kwargs):
        """
        Place le spinner dans le parent avec la méthode pack() de Tkinter.

        Args:
            **kwargs: Paramètres de placement (side, padx, pady, etc.).
        """
        self.canvas.pack(**kwargs)

    def place(self, **kwargs):
        """
        Place le spinner dans le parent avec la méthode place() de Tkinter.

        Args:
            **kwargs: Paramètres de placement (x, y, anchor, etc.).
        """
        self.canvas.place(**kwargs)

    def start(self, widget, delay=50):
        """
        Démarre l'animation du spinner (rotation continue de l'arc).

        Args:
            widget: Widget qui possède la méthode after() (souvent self ou le parent).
            delay (int, optionnel): Délai en millisecondes entre chaque image de l'animation (par défaut 50ms).

        Effet:
            Lance une boucle qui fait tourner l'arc jusqu'à ce que stop() soit appelé.
        """
        def _rotate():
            self._angle = (self._angle + 15) % 360
            self.canvas.itemconfigure(self.arc, start=self._angle)
            self._job = widget.after(delay, _rotate)
        _rotate()

    def stop(self):
        """
        Arrête l'animation du spinner et détruit le widget graphique.

        Effet:
            Annule la boucle d'animation et supprime le canvas du parent.
        """
        if self._job:
            self.parent.after_cancel(self._job)
        self.canvas.destroy()
