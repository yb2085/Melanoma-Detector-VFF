# INTERFACE/ui/sidebar.py

import customtkinter as ctk
from customtkinter import CTkScrollableFrame
import LINK.profile_manager as pm
from PIL import Image, ImageFilter
from customtkinter import CTkImage
import os
import tkinter as tk

class SidebarFrame(ctk.CTkFrame):
    
    def __init__(self, master, profiles, translations, btn_font, title_font):
        super().__init__(master, width=250, corner_radius=0)
        self.master       = master
        self.profiles     = profiles
        self.translations = translations
        # On récupère la langue depuis le master (MainApp)
        self.current_lang = master.current_lang
        self.btn_font     = btn_font
        self.title_font   = title_font
        self.current_profile = None
        self._build_sidebar()


        # Sélection initiale
        tr = self.translations[self.current_lang]
        if self.profiles:
            self.current_profile = self.profiles[0]
            names = [self._format_profile_name(p) for p in self.profiles]
            self.profile_option.configure(values=names)
            self.profile_option.set(names[0])
            self._refresh_history()
        else:
            self.profile_option.set(tr['add_profile'])

    def _build_sidebar(self):
        tr = self.translations[self.current_lang]

        # Titre
        ctk.CTkLabel(self, text=tr['add_profile'], font=self.title_font)\
           .pack(pady=(20,10))

        # Sélecteur de profil
        names = [self._format_profile_name(p) for p in self.profiles] or [tr['add_profile']]
        self.profile_option = ctk.CTkOptionMenu(
            self,
            values=names,
            command=self._on_profile_change,
            width=350,
            font=self.btn_font
        )
        self.profile_option.pack(pady=(0,10))

        # Boutons Ajouter / Supprimer
        ctk.CTkButton(
            self,
            text=tr['add_profile'],
            font=self.btn_font,
            command=self._open_add_profile_modal
        ).pack(pady=(0,10))
        ctk.CTkButton(
            self,
            text=tr['delete_profile'],
            font=self.btn_font,
            fg_color="#EC7063",
            hover_color="#E74C3C",
            command=self._delete_profile
        ).pack(pady=(0,20))

        # Historique
        ctk.CTkLabel(self, text=tr['history'], font=self.btn_font)\
           .pack(pady=(0,5))
        self.history_frame = CTkScrollableFrame(self, width=320, height=350)
        self.history_frame.pack(pady=(0,10), fill="y")

    def _format_profile_name(self, p):
        return f"{p['nom']} {p['prenom']}"

    def _on_profile_change(self, choice):
        # Met à jour current_profile dans sidebar et dans MainApp
        for p in self.profiles:
            if self._format_profile_name(p) == choice:
                self.current_profile = p
                break
        self.master.current_profile = self.current_profile
        self._refresh_history()

    def _refresh_history(self):
        # Vide l’ancien historique
        for w in self.history_frame.winfo_children():
            w.destroy()
        if not self.current_profile:
            return

        tr = self.translations[self.current_lang]
        hist = pm.get_history(self.current_profile['id'])
        for entry in reversed(hist):
            date, time = entry['timestamp'].split("T")
            detail = (tr['not_detected'] if entry['pred']==1 else tr['detected'])
            line1 = date
            line2 = f"{time} | {entry['label']} | {detail} | {entry['conf']:.0f}%"

            lbl = ctk.CTkLabel(
                self.history_frame,
                text=f"{line1}\n{line2}",
                font=("Helvetica", 11),
                width=230,
                text_color="#000000",
                justify="left",
                wraplength=230
            )
            lbl.pack(pady=4)
            lbl.bind("<Button-1>", lambda e, ent=entry: self._load_history_entry(ent))

    def _load_history_entry(self, entry):
        # Délègue à MainApp pour recharger l’état
        if hasattr(self.master, "load_history_entry"):
            self.master.load_history_entry(entry)

    def _open_add_profile_modal(self):
        tr = self.translations[self.current_lang]
        modal = ctk.CTkToplevel(self)
        modal.transient(self.master)
        modal.grab_set()
        modal.title(tr['add_profile'])
        modal.geometry("400x500")

        entries = {}
        for key in ('new_nom','new_prenom','new_age','new_taille','new_poids'):
            ctk.CTkLabel(modal, text=tr[key], font=self.btn_font)\
               .pack(pady=(10,0), padx=20, anchor="w")
            ent = ctk.CTkEntry(modal, font=self.btn_font)
            ent.pack(pady=(0,5), padx=20, fill="x")
            entries[key] = ent

        frm = ctk.CTkFrame(modal, fg_color="transparent")
        frm.pack(pady=20)
        ctk.CTkButton(
            frm, text=tr['save'], font=self.btn_font,
            width=100,
            command=lambda: self._save_profile(entries, modal)
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            frm, text=tr['cancel'], font=self.btn_font,
            width=100,
            command=modal.destroy
        ).pack(side="right", padx=10)

    def _save_profile(self, entries, modal):
        tr = self.translations[self.current_lang]
        nom    = entries['new_nom'].get()
        prenom = entries['new_prenom'].get()
        age    = entries['new_age'].get()
        taille = entries['new_taille'].get()
        poids  = entries['new_poids'].get()
        if nom and prenom:
            newp = pm.add_profile(nom, prenom, age, taille, poids)
            self.profiles.append(newp)
            names = [self._format_profile_name(p) for p in self.profiles]
            self.profile_option.configure(values=names)
            self.profile_option.set(self._format_profile_name(newp))
            self.current_profile = newp
            self.master.current_profile = newp
            self._refresh_history()
            modal.destroy()

    def _delete_profile(self):
        if not self.current_profile:
            return
        # Supprime et recharge la liste
        self.profiles = pm.delete_profile(self.current_profile['id'])
        names = [self._format_profile_name(p) for p in self.profiles]
        if self.profiles:
            self.profile_option.configure(values=names)
            self.current_profile = self.profiles[0]
            self.profile_option.set(names[0])
            self.master.current_profile = self.current_profile
        else:
            tr = self.translations[self.current_lang]
            self.profile_option.configure(values=[tr['add_profile']])
            self.profile_option.set(tr['add_profile'])
            self.current_profile = None
            self.master.current_profile = None
        self._refresh_history()
