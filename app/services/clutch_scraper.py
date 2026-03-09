import requests
from bs4 import BeautifulSoup

def scrape_clutch():

    url = "https://clutch.co/developers"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    companies = []

    cards = soup.select(".provider-info")

    for card in cards[:10]:

        name = card.select_one("h3")
        location = card.select_one(".locality")

        companies.append({
            "name": name.text.strip() if name else None,
            "location": location.text.strip() if location else None
        })

    return companies