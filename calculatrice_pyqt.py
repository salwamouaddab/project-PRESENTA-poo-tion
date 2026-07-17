"""
Calculatrice PyQt5 - Meme style que la version Tkinter (boutons arrondis, theme sombre)
------------------------------------------------------------------------------------------
Installation requise : pip install PyQt5
Lancement : python calculatrice_pyqt.py
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt

# ---------- Couleurs (meme theme que la version Tkinter) ----------
BG_COLOR = "#1e1e2e"
DISPLAY_BG = "#282a3a"
DISPLAY_FG = "#ffffff"
BTN_NUM_BG = "#3b3d54"
BTN_NUM_HOVER = "#4a4d6a"
BTN_OP_BG = "#f59e0b"
BTN_OP_HOVER = "#fbbf24"
BTN_EQUAL_BG = "#22c55e"
BTN_EQUAL_HOVER = "#4ade80"
BTN_CLEAR_BG = "#ef4444"
BTN_CLEAR_HOVER = "#f87171"


def make_button_style(bg, hover):
    """Retourne le QSS (style CSS-like de Qt) pour un bouton avec coins arrondis."""
    return f"""
        QPushButton {{
            background-color: {bg};
            color: white;
            border: none;
            border-radius: 20px;
            font-size: 20px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {hover};
        }}
        QPushButton:pressed {{
            background-color: {bg};
        }}
    """


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculatrice")
        self.setFixedSize(340, 480)
        self.setStyleSheet(f"background-color: {BG_COLOR};")

        self.expression = ""
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # ---------- Ecran (display) ----------
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setFixedHeight(90)
        self.display.setStyleSheet(f"""
            background-color: {DISPLAY_BG};
            color: {DISPLAY_FG};
            font-size: 34px;
            font-weight: bold;
            border-radius: 15px;
            padding: 10px 20px;
        """)
        main_layout.addWidget(self.display)

        # ---------- Boutons ----------
        grid = QGridLayout()
        grid.setSpacing(8)

        buttons = [
            ("C", 0, 0, BTN_CLEAR_BG, BTN_CLEAR_HOVER, self.clear),
            ("⌫", 0, 1, BTN_CLEAR_BG, BTN_CLEAR_HOVER, self.backspace),
            ("%", 0, 2, BTN_OP_BG, BTN_OP_HOVER, lambda: self.add_symbol("%")),
            ("÷", 0, 3, BTN_OP_BG, BTN_OP_HOVER, lambda: self.add_symbol("/")),

            ("7", 1, 0, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("7")),
            ("8", 1, 1, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("8")),
            ("9", 1, 2, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("9")),
            ("×", 1, 3, BTN_OP_BG, BTN_OP_HOVER, lambda: self.add_symbol("*")),

            ("4", 2, 0, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("4")),
            ("5", 2, 1, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("5")),
            ("6", 2, 2, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("6")),
            ("−", 2, 3, BTN_OP_BG, BTN_OP_HOVER, lambda: self.add_symbol("-")),

            ("1", 3, 0, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("1")),
            ("2", 3, 1, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("2")),
            ("3", 3, 2, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("3")),
            ("+", 3, 3, BTN_OP_BG, BTN_OP_HOVER, lambda: self.add_symbol("+")),

            ("0", 4, 0, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol("0")),
            (".", 4, 1, BTN_NUM_BG, BTN_NUM_HOVER, lambda: self.add_symbol(".")),
            ("±", 4, 2, BTN_NUM_BG, BTN_NUM_HOVER, self.toggle_sign),
            ("=", 4, 3, BTN_EQUAL_BG, BTN_EQUAL_HOVER, self.calculate),
        ]

        for (text, row, col, bg, hover, handler) in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(70, 70)
            btn.setStyleSheet(make_button_style(bg, hover))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(handler)
            grid.addWidget(btn, row, col)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    # ---------- Logique de la calculatrice (identique a la version Tkinter) ----------
    def add_symbol(self, symbol):
        if self.display.text() == "0" and symbol not in ("+", "-", "*", "/", "%", "."):
            self.expression = symbol
        else:
            self.expression += symbol
        self.display.setText(self.expression)

    def clear(self):
        self.expression = ""
        self.display.setText("0")

    def backspace(self):
        self.expression = self.expression[:-1]
        self.display.setText(self.expression if self.expression else "0")

    def toggle_sign(self):
        if self.expression.startswith("-"):
            self.expression = self.expression[1:]
        else:
            self.expression = "-" + self.expression
        self.display.setText(self.expression if self.expression else "0")

    def calculate(self):
        try:
            expr = self.expression.replace("%", "/100")
            result = eval(expr, {"__builtins__": {}})
            self.expression = str(result)
            self.display.setText(self.expression)
        except Exception:
            self.display.setText("Erreur")
            self.expression = ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())