"""
Couche de persistance. SQLite pour le MVP (un seul fichier, zero
configuration). Migration vers PostgreSQL plus tard = changer
juste cette couche, le reste du code ne bouge pas.
"""

import sqlite3
from contextlib import contextmanager
from typing import List

from models import Product

DB_PATH = "price_compare.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT,
    processor TEXT,
    ram_gb INTEGER,
    storage TEXT,
    price_mad REAL,
    product_url TEXT UNIQUE NOT NULL,
    image_url TEXT,
    in_stock INTEGER DEFAULT 1,
    last_scraped_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    price_mad REAL,
    scraped_at TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def upsert_product(conn: sqlite3.Connection, product: Product) -> int:
    """
    Insere le produit s'il n'existe pas (par product_url unique),
    sinon met a jour le prix et enregistre l'ancien prix dans l'historique.

    product_url comme cle d'unicite : c'est la seule donnee garantie
    stable d'un scrape a l'autre pour un meme produit sur ce site.
    """
    existing = conn.execute(
        "SELECT id, price_mad FROM products WHERE product_url = ?",
        (product.product_url,),
    ).fetchone()

    if existing is None:
        cursor = conn.execute(
            """
            INSERT INTO products
                (name, brand, processor, ram_gb, storage, price_mad,
                 product_url, image_url, in_stock, last_scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product.name, product.brand, product.processor,
                product.ram_gb, product.storage, product.price_mad,
                product.product_url, product.image_url,
                int(product.in_stock), product.scraped_at.isoformat(),
            ),
        )
        product_id = cursor.lastrowid
    else:
        product_id = existing["id"]
        conn.execute(
            """
            UPDATE products
            SET price_mad = ?, in_stock = ?, last_scraped_at = ?
            WHERE id = ?
            """,
            (product.price_mad, int(product.in_stock),
             product.scraped_at.isoformat(), product_id),
        )

    # On log le prix dans l'historique a chaque scrape, meme s'il n'a
    # pas change - ca permet plus tard de tracer "depuis quand ce prix
    # tient" sans logique supplementaire.
    conn.execute(
        "INSERT INTO price_history (product_id, price_mad, scraped_at) VALUES (?, ?, ?)",
        (product_id, product.price_mad, product.scraped_at.isoformat()),
    )

    return product_id


def save_products(products: List[Product]) -> int:
    init_db()
    with get_connection() as conn:
        for product in products:
            upsert_product(conn, product)
    return len(products)
