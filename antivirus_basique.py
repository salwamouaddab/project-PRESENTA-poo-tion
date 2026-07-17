"""
Antivirus basique - Tkinter
--------------------------------
ATTENTION : Ceci n'est PAS un antivirus professionnel. C'est un outil basique qui :
  1) repère les extensions suspectes et les doubles extensions (ex: facture.pdf.exe)
  2) calcule le hash SHA-256 de chaque fichier et le compare a une liste locale
  3) (optionnel) verifie le hash sur VirusTotal si tu fournis ta cle API gratuite

Aucun vrai moteur antivirus ne peut etre fait sans une base de donnees enorme
mise a jour en continu (c'est le travail de Kaspersky, Windows Defender, etc.).
Cet outil est complementaire, pas un remplacement.

Cle API VirusTotal (gratuite) : https://www.virustotal.com/gui/join-us
-> Une fois inscrit : Profil > API Key. Le tier gratuit = 4 requetes/minute.

Lancement : python antivirus_basique.py
"""

import os
import hashlib
import json
import threading
import time
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

# ---------- Couleurs (meme theme que les autres outils) ----------
BG_COLOR = "#1e1e2e"
PANEL_BG = "#282a3a"
FG_COLOR = "#ffffff"
BTN_PRIMARY_BG = "#3b82f6"
BTN_PRIMARY_HOVER = "#60a5fa"
BTN_DANGER_BG = "#ef4444"
BTN_DANGER_HOVER = "#f87171"
BTN_SUCCESS_BG = "#22c55e"
BTN_SUCCESS_HOVER = "#4ade80"
BTN_WARNING_BG = "#f59e0b"
BTN_WARNING_HOVER = "#fbbf24"
LIST_BG = "#282a3a"
LIST_FG = "#ffffff"
LIST_SELECT_BG = "#3b3d54"

# Extensions executables/scripts a surveiller
SUSPICIOUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".vbs", ".js", ".scr", ".jar",
    ".ps1", ".msi", ".com", ".pif", ".gadget", ".hta", ".wsf",
}

# Extensions "de confiance" utilisees pour detecter les doubles extensions pieges
TRUSTED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".txt",
    ".xls", ".xlsx", ".mp3", ".mp4", ".zip", ".rar",
}

LOCAL_HASHES_FILE = "malicious_hashes.txt"  # une ligne = un hash SHA-256 connu comme malveillant


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg, hover_bg,
                 width=170, height=42, radius=14, font_size=12, **kwargs):
        super().__init__(parent, width=width, height=height,
                          bg=BG_COLOR, highlightthickness=0, **kwargs)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.shape = self._draw_rounded_rect(2, 2, width - 2, height - 2, radius, fill=bg, outline="")
        self.create_text(width / 2, height / 2, text=text, fill="#ffffff",
                          font=("Segoe UI", font_size, "bold"))
        self.bind("<Enter>", lambda e: self.itemconfig(self.shape, fill=self.hover_bg))
        self.bind("<Leave>", lambda e: self.itemconfig(self.shape, fill=self.bg))
        self.bind("<Button-1>", lambda e: self.command() if self.command else None)

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


def sha256_of_file(path, block_size=65536):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(block_size), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def load_local_hashes():
    if not os.path.exists(LOCAL_HASHES_FILE):
        return set()
    with open(LOCAL_HASHES_FILE, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}


def check_virustotal(file_hash, api_key):
    """Interroge VirusTotal par hash (pas d'upload du fichier). Retourne (malicious_count, total)."""
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    req = urllib.request.Request(url, headers={"x-apikey": api_key})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            stats = data["data"]["attributes"]["last_analysis_stats"]
            malicious = stats.get("malicious", 0) + stats.get("suspicious", 0)
            total = sum(stats.values())
            return malicious, total
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None  # fichier inconnu de VirusTotal
        return "erreur", None
    except Exception:
        return "erreur", None


class AntivirusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antivirus basique")
        self.configure(bg=BG_COLOR)
        self.geometry("800x580")
        self.minsize(650, 450)

        self.selected_dir = None
        self.api_key = None
        self.use_virustotal = tk.BooleanVar(value=False)
        self.local_hashes = load_local_hashes()
        self.scanning = False

        self._build_ui()

    def _build_ui(self):
        # ---------- Haut : dossier + options ----------
        top_frame = tk.Frame(self, bg=BG_COLOR)
        top_frame.pack(fill="x", padx=15, pady=15)

        self.folder_path = tk.StringVar(value="Aucun dossier choisi")
        path_label = tk.Label(top_frame, textvariable=self.folder_path, bg=PANEL_BG, fg=FG_COLOR,
                               anchor="w", font=("Segoe UI", 11), padx=12, pady=10)
        path_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

        choose_btn = RoundedButton(top_frame, "📁 Choisir dossier", self.choose_folder,
                                    BTN_PRIMARY_BG, BTN_PRIMARY_HOVER, width=170)
        choose_btn.pack(side="left")

        # ---------- Options ----------
        options_frame = tk.Frame(self, bg=BG_COLOR)
        options_frame.pack(fill="x", padx=15, pady=(0, 10))

        vt_check = tk.Checkbutton(options_frame, text="Vérifier aussi sur VirusTotal (nécessite une clé API)",
                                   variable=self.use_virustotal, command=self.toggle_virustotal,
                                   bg=BG_COLOR, fg=FG_COLOR, selectcolor=PANEL_BG,
                                   activebackground=BG_COLOR, activeforeground=FG_COLOR,
                                   font=("Segoe UI", 10))
        vt_check.pack(side="left")

        # ---------- Liste des résultats ----------
        list_frame = tk.Frame(self, bg=BG_COLOR)
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=LIST_BG, fieldbackground=LIST_BG, foreground=LIST_FG,
                         rowheight=26, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=PANEL_BG, foreground=FG_COLOR,
                         font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Treeview", background=[("selected", LIST_SELECT_BG)])

        columns = ("fichier", "statut", "detail")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("fichier", text="Fichier")
        self.tree.heading("statut", text="Statut")
        self.tree.heading("detail", text="Détail")
        self.tree.column("fichier", width=350, anchor="w")
        self.tree.column("statut", width=120, anchor="center")
        self.tree.column("detail", width=220, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.tag_configure("danger", foreground="#f87171")
        self.tree.tag_configure("warning", foreground="#fbbf24")
        self.tree.tag_configure("clean", foreground="#4ade80")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ---------- Bas : status + progress + actions ----------
        self.status_var = tk.StringVar(value="Choisissez un dossier pour commencer.")
        status_label = tk.Label(self, textvariable=self.status_var, bg=BG_COLOR, fg="#9ca3af",
                                 font=("Segoe UI", 10), anchor="w")
        status_label.pack(fill="x", padx=18, pady=(0, 5))

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=18, pady=(0, 10))

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        scan_btn = RoundedButton(btn_frame, "🔍 Lancer le scan", self.start_scan,
                                  BTN_PRIMARY_BG, BTN_PRIMARY_HOVER, width=160)
        scan_btn.pack(side="left", padx=(0, 10))

        delete_btn = RoundedButton(btn_frame, "🗑 Supprimer sélection", self.delete_selected,
                                    BTN_DANGER_BG, BTN_DANGER_HOVER, width=190)
        delete_btn.pack(side="left")

    def toggle_virustotal(self):
        if self.use_virustotal.get() and not self.api_key:
            key = simpledialog.askstring("Clé API VirusTotal",
                                          "Colle ta clé API VirusTotal (gratuite) :", show="*")
            if key:
                self.api_key = key.strip()
            else:
                self.use_virustotal.set(False)

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Choisir un dossier à scanner")
        if folder:
            self.selected_dir = folder
            self.folder_path.set(folder)
            self.status_var.set("Dossier choisi. Cliquez sur 'Lancer le scan'.")
            self.tree.delete(*self.tree.get_children())

    def start_scan(self):
        if self.scanning:
            return
        if not self.selected_dir:
            messagebox.showwarning("Attention", "Choisissez d'abord un dossier.")
            return
        if self.use_virustotal.get() and not self.api_key:
            messagebox.showwarning("Attention", "Ajoute une clé API VirusTotal ou décoche l'option.")
            return

        self.tree.delete(*self.tree.get_children())
        self.scanning = True
        thread = threading.Thread(target=self._scan_worker, daemon=True)
        thread.start()

    def _scan_worker(self):
        all_files = []
        for root, dirs, files in os.walk(self.selected_dir):
            for name in files:
                all_files.append(os.path.join(root, name))

        total = len(all_files)
        self.progress["maximum"] = max(total, 1)
        self.progress["value"] = 0

        vt_call_count = 0

        for i, path in enumerate(all_files, start=1):
            name = os.path.basename(path)
            ext = os.path.splitext(name)[1].lower()
            status, detail, tag = "Clean", "-", "clean"

            # 1) Double extension piege (ex: facture.pdf.exe)
            parts = name.lower().split(".")
            if len(parts) > 2:
                inner_ext = "." + parts[-2]
                outer_ext = "." + parts[-1]
                if inner_ext in TRUSTED_EXTENSIONS and outer_ext in SUSPICIOUS_EXTENSIONS:
                    status, detail, tag = "DANGER", "Double extension suspecte", "danger"

            # 2) Extension executable simple -> avertissement (pas forcement dangereux)
            if status == "Clean" and ext in SUSPICIOUS_EXTENSIONS:
                status, detail, tag = "Suspect", "Extension exécutable", "warning"

            # 3) Hash local
            file_hash = None
            if self.local_hashes or self.use_virustotal.get():
                file_hash = sha256_of_file(path)
                if file_hash and file_hash.lower() in self.local_hashes:
                    status, detail, tag = "DANGER", "Hash connu comme malveillant", "danger"

            # 4) VirusTotal (limite : 4 requêtes/minute en gratuit)
            if self.use_virustotal.get() and status != "DANGER" and file_hash:
                if vt_call_count > 0 and vt_call_count % 4 == 0:
                    self.status_var.set("Pause (limite VirusTotal 4/min)...")
                    time.sleep(15)
                malicious, checked_total = check_virustotal(file_hash, self.api_key)
                vt_call_count += 1
                if malicious == "erreur":
                    detail = "Erreur VirusTotal" if status == "Clean" else detail
                elif malicious is not None and malicious > 0:
                    status, detail, tag = "DANGER", f"VirusTotal: {malicious}/{checked_total}", "danger"

            self.tree.insert("", "end", values=(path, status, detail), tags=(tag,))
            self.progress["value"] = i
            self.status_var.set(f"Scan en cours... {i}/{total}")

        self.scanning = False
        self.status_var.set(f"Scan terminé. {total} fichier(s) analysé(s).")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Sélectionnez au moins un fichier dans la liste.")
            return

        paths = [self.tree.item(item, "values")[0] for item in selected_items]
        confirm = messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer {len(paths)} fichier(s) ? Cette action est irréversible."
        )
        if not confirm:
            return

        deleted = 0
        for item, path in zip(selected_items, paths):
            try:
                os.remove(path)
                deleted += 1
                self.tree.delete(item)
            except OSError:
                pass

        self.status_var.set(f"{deleted} fichier(s) supprimé(s).")


if __name__ == "__main__":
    app = AntivirusApp()
    app.mainloop()