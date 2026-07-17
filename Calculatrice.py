"""
Calculatrice Tkinter - Style moderne avec boutons arrondis
-----------------------------------------------------------
Nécessite seulement Python + Tkinter (déjà inclus dans Python standard).
Pour lancer : python calculatrice.py
"""

import tkinter as tk

# ---------- Couleurs (thème sombre moderne) ----------
BG_COLOR = "#1e1e2e"
DISPLAY_BG = "#282a3a"
DISPLAY_FG = "#ffffff"
BTN_NUM_BG = "#3b3d54"
BTN_NUM_FG = "#ffffff"
BTN_NUM_HOVER = "#4a4d6a"
BTN_OP_BG = "#f59e0b"
BTN_OP_FG = "#ffffff"
BTN_OP_HOVER = "#fbbf24"
BTN_EQUAL_BG = "#22c55e"
BTN_EQUAL_HOVER = "#4ade80"
BTN_CLEAR_BG = "#ef4444"
BTN_CLEAR_HOVER = "#f87171"


class RoundedButton(tk.Canvas):
    """Bouton avec coins arrondis dessiné sur un Canvas (tkinter n'a pas
    de bouton arrondi natif, donc on le dessine nous-mêmes)."""

    def __init__(self, parent, text, command, bg, fg, hover_bg,
                 width=70, height=70, radius=20, font_size=18, **kwargs):
        super().__init__(parent, width=width, height=height,
                          bg=BG_COLOR, highlightthickness=0, **kwargs)
        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg
        self.radius = radius
        self.width = width
        self.height = height

        self.shape = self._draw_rounded_rect(2, 2, width - 2, height - 2,
                                               radius, fill=bg, outline="")
        self.label = self.create_text(width / 2, height / 2, text=text,
                                       fill=fg, font=("Segoe UI", font_size, "bold"))

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


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculatrice")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.expression = ""
        self._build_display()
        self._build_buttons()

    def _build_display(self):
        frame = tk.Frame(self, bg=DISPLAY_BG)
        frame.grid(row=0, column=0, columnspan=4, padx=15, pady=(15, 10), sticky="nsew")

        self.display_var = tk.StringVar(value="0")
        display = tk.Label(frame, textvariable=self.display_var, anchor="e",
                            bg=DISPLAY_BG, fg=DISPLAY_FG, font=("Segoe UI", 32, "bold"),
                            padx=15, pady=25)
        display.pack(fill="both", expand=True)

    def _build_buttons(self):
        buttons = [
            ("C", 1, 0, BTN_CLEAR_BG, BTN_CLEAR_BG, self.clear),
            ("⌫", 1, 1, BTN_CLEAR_BG, BTN_CLEAR_BG, self.backspace),
            ("%", 1, 2, BTN_OP_BG, BTN_OP_BG, lambda: self.add_symbol("%")),
            ("÷", 1, 3, BTN_OP_BG, BTN_OP_BG, lambda: self.add_symbol("/")),

            ("7", 2, 0, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("7")),
            ("8", 2, 1, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("8")),
            ("9", 2, 2, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("9")),
            ("×", 2, 3, BTN_OP_BG, BTN_OP_BG, lambda: self.add_symbol("*")),

            ("4", 3, 0, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("4")),
            ("5", 3, 1, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("5")),
            ("6", 3, 2, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("6")),
            ("−", 3, 3, BTN_OP_BG, BTN_OP_BG, lambda: self.add_symbol("-")),

            ("1", 4, 0, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("1")),
            ("2", 4, 1, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("2")),
            ("3", 4, 2, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("3")),
            ("+", 4, 3, BTN_OP_BG, BTN_OP_BG, lambda: self.add_symbol("+")),

            ("0", 5, 0, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol("0")),
            (".", 5, 1, BTN_NUM_BG, BTN_NUM_BG, lambda: self.add_symbol(".")),
            ("±", 5, 2, BTN_NUM_BG, BTN_NUM_BG, self.toggle_sign),
            ("=", 5, 3, BTN_EQUAL_BG, BTN_EQUAL_BG, self.calculate),
        ]

        hover_map = {
            BTN_NUM_BG: BTN_NUM_HOVER,
            BTN_OP_BG: BTN_OP_HOVER,
            BTN_EQUAL_BG: BTN_EQUAL_HOVER,
            BTN_CLEAR_BG: BTN_CLEAR_HOVER,
        }

        for (text, row, col, bg, _, cmd) in buttons:
            btn = RoundedButton(self, text=text, command=cmd, bg=bg,
                                 fg="#ffffff", hover_bg=hover_map[bg])
            btn.grid(row=row, column=col, padx=6, pady=6)

    def add_symbol(self, symbol):
        if self.display_var.get() == "0" and symbol not in ("+", "-", "*", "/", "%", "."):
            self.expression = symbol
        else:
            self.expression += symbol
        self.display_var.set(self.expression)

    def clear(self):
        self.expression = ""
        self.display_var.set("0")

    def backspace(self):
        self.expression = self.expression[:-1]
        self.display_var.set(self.expression if self.expression else "0")

    def toggle_sign(self):
        if self.expression.startswith("-"):
            self.expression = self.expression[1:]
        else:
            self.expression = "-" + self.expression
        self.display_var.set(self.expression if self.expression else "0")

    def calculate(self):
        try:
            # remplace % par /100 pour un calcul simple de pourcentage
            expr = self.expression.replace("%", "/100")
            result = eval(expr, {"__builtins__": {}})
            self.expression = str(result)
            self.display_var.set(self.expression)
        except Exception:
            self.display_var.set("Erreur")
            self.expression = ""


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()