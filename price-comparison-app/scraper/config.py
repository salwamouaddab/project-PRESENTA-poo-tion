"""
Configuration centrale du scraper.
Toutes les valeurs sensibles ou ajustables passent par ici,
jamais en dur dans les spiders.
"""

import os

# --- Politesse envers les sites scrapes ---
REQUEST_DELAY_SECONDS = 3          # delai minimum entre 2 requetes vers le meme site
REQUEST_TIMEOUT_SECONDS = 10
MAX_RETRIES = 3

# User-Agent honnete : on ne se fait pas passer pour un navigateur.
# Certains sites bloquent les user-agents par defaut de `requests`.
USER_AGENT = "PriceCompareBot/0.1 (+contact: hello@example.com)"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "fr-FR,fr;q=0.9,ar;q=0.8",
}

# --- Base de donnees ---
# SQLite pour le MVP local. On passera a PostgreSQL (via DATABASE_URL)
# quand le projet grandira.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///price_compare.db",
)

# --- Cible du scraping (MVP : un seul site) ---
SUPERPC_BASE_URL = "https://www.superpc.ma"
SUPERPC_LISTING_PATH = "/pc-occasion"
