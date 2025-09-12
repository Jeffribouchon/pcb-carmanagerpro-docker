def scrape_leboncoin(self, url: str, limit: int = 10):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
    }
    api_url = url.replace(
        "https://www.leboncoin.fr/recherche",
        "https://api.leboncoin.fr/finder/search"
    )

    response = requests.get(api_url, headers=headers)
    ads = []
    if response.status_code != 200:
        return ads

    data = response.json()
    
    for ad in data.get("ads", [])[:limit]:
        ads.append({
            "title": ad.get("subject"),
            "price": ad.get("price"),
            "city": ad.get("location", {}).get("city"),
            "url": f"https://www.leboncoin.fr/vi/{ad.get('list_id')}.htm",
            "images": [img.get("url") for img in ad.get("images", [])] if ad.get("images") else []
        })
    return ads

def scrape_lacentrale(url: str, limit: int = 10):
    """
    Scraper pour La Centrale.
    ⚠️ Pas d'API publique → on parse le HTML directement.
    """
    from bs4 import BeautifulSoup

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    results = []

    # Chaque annonce est dans un <div class="searchCard">
    cards = soup.select("div.searchCard")[:limit]
    for card in cards:
        title_tag = card.select_one(".searchCard__makeModel")
        price_tag = card.select_one(".searchCard__price")
        link_tag = card.select_one("a")
        city_tag = card.select_one(".searchCard__dptCont")

        if not link_tag:
            continue

        results.append({
            "title": title_tag.get_text(strip=True) if title_tag else "Annonce",
            "price": price_tag.get_text(strip=True) if price_tag else "—",
            "city": city_tag.get_text(strip=True) if city_tag else "—",
            "url": "https://www.lacentrale.fr" + link_tag["href"]
        })

    return results

def search_platformcars_b2b(criteria: dict, limit: int = 10):
    """
    Recherche de véhicules sur PlatformCars B2B via l'API Odoo.
    
    criteria: dict retourné par l'IA, exemple :
    {
        "brand": "PEUGEOT",
        "model": "208",
        "fuel": "essence",
        "gearbox": "manuelle",
        "price_max": 10000,
        "mileage_max": 100000,
        "year_min": 2015,
        "year_max": 2023
    }
    """
    # Import Odoo RPC / API
    from modules.odoo.client import OdooClient
    from modules.odoo.odoo_model import OdooModel
    
    odoo_client = OdooClient()
    product_template = OdooModel(odoo_client, 'product.template')

    domain = []

    domain.append(('categ_id', '=', 5))

    # Construction du domain Odoo à partir des critères
    if "brand" in criteria:
        domain.append(("x_studio_marque", "ilike", criteria["brand"]))
    if "model" in criteria:
        domain.append(("x_studio_modele", "ilike", criteria["model"]))
    if "fuel" in criteria:
        domain.append(("x_studio_energie", "ilike", criteria["fuel"]))
    if "gearbox" in criteria:
        domain.append(("x_studio_boite_de_vitesse", "ilike", criteria["gearbox"]))
    # if "price_max" in criteria:
    #     domain.append(("list_price", "<=", criteria["price_max"]))
    # if "year_min" in criteria:
    #     domain.append(("x_studio_anne_de_mise_en_circulation", ">=", criteria["year_min"]))
    # if "year_max" in criteria:
    #     domain.append(("x_studio_anne_de_mise_en_circulation", "<=", criteria["year_max"]))

    results = []
    
    fields=["name", "list_price", "x_studio_localisation_du_vhicule", "x_studio_anne_de_mise_en_circulation", "x_studio_energie", "x_studio_boite_de_vitesse", "default_code"]
    vehicle_records = product_template.search_read(domain, fields=fields, limit=limit)

    for v in vehicle_records:
        results.append({
            "title": v.get("name", "Véhicule"),
            "price": v.get("list_price", "—"),
            "city": v.get("x_studio_localisation_du_vhicule", "—"),
            "year": v.get("x_studio_anne_de_mise_en_circulation", "—"),
            "fuel": v.get("x_studio_energie", "—"),
            "gearbox": v.get("x_studio_boite_de_vitesse", "—"),
            "url": f"https://www.platformcars-b2b.com/shop/{v.get('default_code')}"
        })

    return results


