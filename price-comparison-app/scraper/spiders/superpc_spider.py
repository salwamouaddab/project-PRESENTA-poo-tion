"""
Spider pour SuperPC.ma.

Usage :
    python spiders/superpc_spider.py

Respecte un delai entre les requetes (REQUEST_DELAY_SECONDS) et
n'insiste pas sur les echecs au-dela de MAX_RETRIES.
"""

import sys
import os
import time
import requests

# Permet d'importer les modules du dossier parent (scraper/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    HEADERS, REQUEST_TIMEOUT_SECONDS, MAX_RETRIES,
    SUPERPC_BASE_URL, SUPERPC_LISTING_PATH,
)
from parsers import parse_listing_page
from db import save_products


def fetch_page(url: str) -> str:
    """
    Recupere le HTML d'une URL avec retry simple.
    Leve une exception si toutes les tentatives echouent -
    on prefere un crash visible qu'un scrape silencieusement vide.
    """
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            last_error = e
            print(f"  tentative {attempt}/{MAX_RETRIES} echouee : {e}")
            time.sleep(2 * attempt)  # backoff progressif

    raise RuntimeError(f"Impossible de recuperer {url} : {last_error}")


def run():
    url = f"{SUPERPC_BASE_URL}{SUPERPC_LISTING_PATH}"
    print(f"Scraping {url} ...")

    html = fetch_page(url)
    products = parse_listing_page(html)

    if not products:
        print(
            "Aucun produit trouve. Verifiez les selecteurs CSS dans "
            "parsers.py - ils sont probablement a ajuster pour la "
            "vraie structure HTML du site."
        )
        return

    count = save_products(products)
    print(f"{count} produits sauvegardes dans la base de donnees.")


if __name__ == "__main__":
    run()
