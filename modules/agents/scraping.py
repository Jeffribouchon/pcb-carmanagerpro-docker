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

