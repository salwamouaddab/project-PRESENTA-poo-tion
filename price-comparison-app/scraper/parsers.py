"""
Logique de parsing HTML -> Product.

IMPORTANT : les selecteurs CSS ci-dessous (`.product-card`, `.price`, etc.)
sont des PLACEHOLDERS. Avant de lancer le scraper en vrai, il faut :
  1. Ouvrir https://www.superpc.ma/pc-occasion dans le navigateur
  2. Inspecter le HTML (clic droit > Inspecter) sur une carte produit
  3. Remplacer les selecteurs ci-dessous par les vrais noms de classes/ids

Cette etape ne peut pas etre devinee a l'avance - chaque site a sa
propre structure HTML.
"""

import re
from bs4 import BeautifulSoup
from typing import List, Optional

from models import Product
from config import SUPERPC_BASE_URL


def parse_price(raw_text: str) -> Optional[float]:
    """
    Convertit un texte de prix marocain en float.
    Gere les cas : "6 900 MAD", "A partir de 6 900 MAD", "Sur devis".

    "Sur devis" (prix sur demande) -> None, car il n'y a pas de prix fixe
    a comparer. Ces produits doivent etre exclus du tri par prix, pas
    plantes en erreur.
    """
    if not raw_text:
        return None

    text = raw_text.strip().lower()
    if "devis" in text or "contact" in text:
        return None

    # Extrait le premier groupe de chiffres, avec espaces comme separateurs
    # de milliers ("6 900" -> "6900"). Ancre sur \d au debut et a la fin
    # pour ne pas capturer les espaces isoles autour du nombre (ex: dans
    # "a partir de 6 900 mad", on veut "6 900", pas l'espace apres "de").
    digits = re.findall(r"\d[\d\s]*\d|\d", text)
    if not digits:
        return None

    cleaned = digits[0].replace(" ", "").strip()
    if not cleaned:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_specs(spec_text: str) -> dict:
    """
    Extrait processeur / RAM / stockage depuis une ligne de specs libre,
    ex: "Intel i7 10e gen - 16 Go RAM - 512 Go SSD NVMe"

    Retourne un dict avec des cles potentiellement None si non trouve -
    le texte des fiches produit n'est pas toujours structure pareil.
    """
    result = {"processor": None, "ram_gb": None, "storage": None}

    if not spec_text:
        return result

    # Processeur : tout ce qui precede le premier " - "
    parts = [p.strip() for p in spec_text.split("-")]
    if parts:
        result["processor"] = parts[0] or None

    # RAM : nombre suivi de "Go RAM" ou "GB RAM"
    ram_match = re.search(r"(\d+)\s*Go?\s*RAM", spec_text, re.IGNORECASE)
    if ram_match:
        result["ram_gb"] = int(ram_match.group(1))

    # Stockage : nombre + unite + (SSD|HDD)
    storage_match = re.search(
        r"(\d+)\s*(Go|To|GB|TB)\s*(SSD|HDD|NVMe)", spec_text, re.IGNORECASE
    )
    if storage_match:
        result["storage"] = storage_match.group(0).strip()

    return result


def parse_listing_page(html: str) -> List[Product]:
    """
    Point d'entree principal : prend le HTML brut de la page listing
    et retourne une liste de Product.

    A ADAPTER apres inspection reelle du site (voir docstring du module).
    """
    soup = BeautifulSoup(html, "html.parser")
    products = []

    # PLACEHOLDER - a remplacer par le vrai selecteur des cartes produit
    cards = soup.select(".product-card")

    for card in cards:
        name_el = card.select_one(".product-name")
        price_el = card.select_one(".product-price")
        spec_el = card.select_one(".product-specs")
        link_el = card.select_one("a")
        img_el = card.select_one("img")

        if not name_el or not link_el:
            # Sans nom ou sans lien, la carte est inexploitable - on saute
            continue

        specs = parse_specs(spec_el.get_text(strip=True) if spec_el else "")
        price = parse_price(price_el.get_text(strip=True) if price_el else "")

        raw_href = link_el.get("href", "")
        product_url = (
            raw_href if raw_href.startswith("http")
            else f"{SUPERPC_BASE_URL}{raw_href}"
        )

        products.append(Product(
            name=name_el.get_text(strip=True),
            brand="HP" if "hp" in name_el.get_text(strip=True).lower() else None,
            processor=specs["processor"],
            ram_gb=specs["ram_gb"],
            storage=specs["storage"],
            price_mad=price,
            product_url=product_url,
            image_url=img_el.get("src") if img_el else None,
            in_stock=True,
        ))

    return products
