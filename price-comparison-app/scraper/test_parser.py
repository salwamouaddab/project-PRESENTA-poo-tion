"""
Test rapide du parser avec du HTML factice, pour verifier la logique
sans dependre du vrai site (utile aussi en dev/CI plus tard).
"""

from parsers import parse_listing_page, parse_price, parse_specs

SAMPLE_HTML = """
<html><body>
  <div class="product-card">
    <a href="/produit/hp-elitebook-840-g7">
      <img src="/images/hp-elitebook-840-g7.webp">
      <h3 class="product-name">HP EliteBook 840 G7</h3>
      <p class="product-specs">Intel i7 10e gen - 16 Go RAM - 512 Go SSD NVMe</p>
      <span class="product-price">A partir de 6 900 MAD</span>
    </a>
  </div>
  <div class="product-card">
    <a href="/produit/hp-zbook-15-g5">
      <img src="/images/hp-zbook-15-g5.jpg">
      <h3 class="product-name">HP ZBook 15 G5</h3>
      <p class="product-specs">Intel Xeon - Quadro P1000 - 32 Go RAM</p>
      <span class="product-price">Sur devis</span>
    </a>
  </div>
</body></html>
"""

def test_parse_price():
    assert parse_price("A partir de 6 900 MAD") == 6900.0
    assert parse_price("Sur devis") is None
    assert parse_price("") is None
    print("parse_price : OK")

def test_parse_specs():
    specs = parse_specs("Intel i7 10e gen - 16 Go RAM - 512 Go SSD NVMe")
    assert specs["ram_gb"] == 16
    assert "512" in specs["storage"]
    print("parse_specs : OK")

def test_parse_listing_page():
    products = parse_listing_page(SAMPLE_HTML)
    assert len(products) == 2

    p1 = products[0]
    assert p1.name == "HP EliteBook 840 G7"
    assert p1.price_mad == 6900.0
    assert p1.ram_gb == 16
    assert p1.product_url == "https://www.superpc.ma/produit/hp-elitebook-840-g7"

    p2 = products[1]
    assert p2.price_mad is None  # "Sur devis" -> pas de prix fixe

    print(f"parse_listing_page : OK ({len(products)} produits extraits)")
    for p in products:
        print(f"  - {p.name} | {p.processor} | {p.ram_gb}Go | {p.price_mad} MAD")

if __name__ == "__main__":
    test_parse_price()
    test_parse_specs()
    test_parse_listing_page()
    print("\nTous les tests passent.")
