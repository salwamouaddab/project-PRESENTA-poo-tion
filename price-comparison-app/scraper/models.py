"""
Modeles de donnees. On utilise des dataclasses simples pour le MVP -
pas besoin d'un ORM complet tant qu'on a une seule source.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    name: str
    brand: Optional[str]
    processor: Optional[str]
    ram_gb: Optional[int]
    storage: Optional[str]
    price_mad: Optional[float]   # None si "sur devis" (prix sur demande)
    product_url: str
    image_url: Optional[str]
    in_stock: bool = True
    scraped_at: datetime = None

    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.utcnow()
