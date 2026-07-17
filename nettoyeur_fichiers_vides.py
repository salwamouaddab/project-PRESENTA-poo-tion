"""
Nettoyeur de fichiers vides - Tkinter
----------------------------------------
Scanne un dossier (et ses sous-dossiers) pour trouver les fichiers vides (0 octet)
et permet de les supprimer en un clic.

Lancement : python nettoyeur_fichiers_vides.py
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ---------- Couleurs (meme theme que la calculatrice) ----------
BG_COLOR = "#1e1e2e"
PANEL_BG = "#282a3a"
FG_COLOR = "#ffffff"
BTN_PRIMARY_BG = "#3b82f6"
BTN_PRIMARY_HOVER = "#60a5fa"
BTN_DANGER_BG = "#ef4444"
BTN_DANGER_HOVER = "#f87171"
BTN_SUCCESS_BG = "#22c55e"
BTN_SUCCESS_HOVER = "#4ade80"
LIST_BG = "#282a3a"
LIST_FG = "#ffffff"
LIST_SELECT_BG = "#3b3d54"


class RoundedButton(tk.Canvas):
    """Bouton avec coins arrondis (meme technique que dans la calculatrice)."""

    def __init__(self, parent, text, command, bg, hover_bg,
                 width=160, height=44, radius=14, font_size=13, **kwargs):
        super().__init__(parent, width=width, height=height,
                          bg=BG_COLOR, highlightthickness=0, **kwargs)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg

        self.shape = self._draw_rounded_rect(2, 2, width - 2, height - 2,
                                               radius, fill=bg, outline="")
        self.label = self.create_text(width / 2, height / 2, text=text,
                                       fill="#ffffff", font=("Segoe UI", font_size, "bold"))

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, event):
        self.itemconfig(self.shape, fill=self.hover_bg)

    def _on_leave(self, event):
        self.itemconfig(self.shape, fill=self.bg)

    def _on_click(self, event):
        if self.command:
            self.command()


class EmptyFileCleaner(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nettoyeur de fichiers vides")
        self.configure(bg=BG_COLOR)
        self.geometry("650x520")
        self.minsize(550, 420)

        self.folder_path = tk.StringVar(value="Aucun dossier choisi")
        self.selected_dir = None
        self.empty_files = []

        self._build_ui()

    def _build_ui(self):
        # ---------- Barre du haut : choix du dossier ----------
        top_frame = tk.Frame(self, bg=BG_COLOR)
        top_frame.pack(fill="x", padx=15, pady=15)

        path_label = tk.Label(top_frame, textvariable=self.folder_path,
                               bg=PANEL_BG, fg=FG_COLOR, anchor="w",
                               font=("Segoe UI", 11), padx=12, pady=10)
        path_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        choose_btn = RoundedButton(top_frame, "📁 Choisir dossier", self.choose_folder,
                                    BTN_PRIMARY_BG, BTN_PRIMARY_HOVER, width=170)
        choose_btn.pack(side="left")

        # ---------- Liste des fichiers vides ----------
        list_frame = tk.Frame(self, bg=BG_COLOR)
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=LIST_BG, fieldbackground=LIST_BG,
                         foreground=LIST_FG, rowheight=26, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=PANEL_BG, foreground=FG_COLOR,
                         font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", LIST_SELECT_BG)])

        columns = ("path",)
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("path", text="Fichiers vides trouvés")
        self.tree.column("path", anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ---------- Bas : status + actions ----------
        self.status_var = tk.StringVar(value="Choisissez un dossier pour commencer.")
        status_label = tk.Label(self, textvariable=self.status_var, bg=BG_COLOR, fg="#9ca3af",
                                 font=("Segoe UI", 10), anchor="w")
        status_label.pack(fill="x", padx=18, pady=(0, 5))

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        scan_btn = RoundedButton(btn_frame, "🔍 Scanner", self.scan_folder,
                                  BTN_PRIMARY_BG, BTN_PRIMARY_HOVER, width=140)
        scan_btn.pack(side="left", padx=(0, 10))

        delete_selected_btn = RoundedButton(btn_frame, "🗑 Supprimer sélection", self.delete_selected,
                                             BTN_DANGER_BG, BTN_DANGER_HOVER, width=190)
        delete_selected_btn.pack(side="left", padx=(0, 10))

        delete_all_btn = RoundedButton(btn_frame, "🧹 Tout supprimer", self.delete_all,
                                        BTN_SUCCESS_BG, BTN_SUCCESS_HOVER, width=170)
        delete_all_btn.pack(side="left")

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Choisir un dossier à scanner")
        if folder:
            self.selected_dir = folder
            self.folder_path.set(folder)
            self.status_var.set("Dossier choisi. Cliquez sur 'Scanner'.")
            self.tree.delete(*self.tree.get_children())
            self.empty_files = []

    def scan_folder(self):
        if not self.selected_dir:
            messagebox.showwarning("Attention", "Choisissez d'abord un dossier.")
            return

        self.tree.delete(*self.tree.get_children())
        self.empty_files = []

        for root, dirs, files in os.walk(self.selected_dir):
            for name in files:
                full_path = os.path.join(root, name)
                try:
                    if os.path.getsize(full_path) == 0:
                        self.empty_files.append(full_path)
                        self.tree.insert("", "end", values=(full_path,))
                except OSError:
                    continue

        if self.empty_files:
            self.status_var.set(f"{len(self.empty_files)} fichier(s) vide(s) trouvé(s).")
        else:
            self.status_var.set("Aucun fichier vide trouvé. Dossier propre ✅")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Sélectionnez au moins un fichier dans la liste.")
            return

        paths = [self.tree.item(item, "values")[0] for item in selected_items]
        self._confirm_and_delete(paths, selected_items)

    def delete_all(self):
        if not self.empty_files:
            messagebox.showinfo("Info", "Aucun fichier vide à supprimer.")
            return
        all_items = self.tree.get_children()
        self._confirm_and_delete(list(self.empty_files), all_items)

    def _confirm_and_delete(self, paths, tree_items):
        confirm = messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer {len(paths)} fichier(s) vide(s) ? Cette action est irréversible."
        )
        if not confirm:
            return

        deleted = 0
        for path in paths:
            try:
                os.remove(path)
                deleted += 1
                if path in self.empty_files:
                    self.empty_files.remove(path)
            except OSError:
                pass

        for item in tree_items:
            if self.tree.exists(item):
                self.tree.delete(item)

        self.status_var.set(f"{deleted} fichier(s) supprimé(s).")


if __name__ == "__main__":
    app = EmptyFileCleaner()
    app.mainloop()