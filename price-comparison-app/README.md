# Price Comparison App — MVP (scraper)

Scraper pour SuperPC.ma. Etape 1 du projet : un seul site, base
SQLite locale, pas encore de matching multi-sources.

## Installation

```bash
cd scraper
pip install -r requirements.txt
```

## ⚠️ Etape obligatoire avant de lancer le scraper

Les selecteurs CSS dans `scraper/parsers.py` (`.product-card`,
`.product-name`, `.product-price`, `.product-specs`) sont des
**placeholders**. Le vrai HTML de superpc.ma/pc-occasion doit etre
inspecte pour connaitre les vraies classes :

1. Ouvrir https://www.superpc.ma/pc-occasion dans le navigateur
2. Clic droit sur une carte produit > "Inspecter"
3. Noter les vraies classes CSS (nom, prix, specs, lien)
4. Remplacer les selecteurs dans `parse_listing_page()` (parsers.py)

Sans cette etape, le scraper tournera sans erreur mais ne trouvera
aucun produit (message explicite affiche dans ce cas).

## Lancer le scraper

```bash
cd scraper
python spiders/superpc_spider.py
```

Cree/met a jour `price_compare.db` (SQLite) avec les tables
`products` et `price_history`.

## Lancer les tests (avec du HTML factice, sans toucher au vrai site)

```bash
cd scraper
python test_parser.py
```

## Structure

```
scraper/
├── config.py              # rate limiting, headers, DB path
├── models.py               # dataclass Product
├── parsers.py               # HTML -> Product (SELECTEURS A AJUSTER)
├── db.py                     # sauvegarde SQLite + historique des prix
├── test_parser.py             # tests avec HTML factice
├── spiders/
│   └── superpc_spider.py       # orchestration : fetch -> parse -> save
└── requirements.txt
```

## Prochaines etapes (apres validation du scraper)

1. Ajuster les vrais selecteurs CSS et valider sur le site reel
2. Ajouter un scheduler (cron ou Celery) pour scraper toutes les X heures
3. Construire l'API (FastAPI) qui interroge `price_compare.db`
4. Construire le frontend (React) avec recherche + filtre budget
5. Plus tard : ajouter d'autres sources et gerer le matching de produits
