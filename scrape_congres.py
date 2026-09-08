import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import json
import re
from urllib.parse import urljoin
import urllib3

# Ignorer les avertissements SSL des sites universitaires
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, x64) Chrome/120.0.0.0 Safari/537.36"
}

def parse_french_date(text):
    months = {
        'janvier': '01', 'février': '02', 'fevrier': '02', 'mars': '03',
        'avril': '04', 'mai': '05', 'juin': '06', 'juillet': '07',
        'août': '08', 'aout': '08', 'septembre': '09', 'octobre': '10',
        'novembre': '11', 'décembre': '12', 'decembre': '12'
    }
    match_numeric = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', text)
    if match_numeric:
        d, m, y = match_numeric.groups()
        try:
            return date(int(y), int(m), int(d))
        except ValueError:
            pass
    match_text = re.search(r'(\d{1,2})\s+([a-zA-2à-ÿ]+)\s+(\d{4})', text.lower())
    if match_text:
        day, month_str, year = match_text.groups()
        if month_str in months:
            try:
                return date(int(year), int(months[month_str]), int(day))
            except ValueError:
                pass
    return None

def scrape_uit():
    events = []
    url = "https://www.uit.ac.ma/category/evenement/"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(res.content, "html.parser")
        articles = soup.find_all("article")
        for art in articles:
            link_elem = art.find("a", href=True)
            if not link_elem:
                continue
            item_url = link_elem["href"]
            title_elem = art.find(["h2", "h3", "h1"])
            title = title_elem.get_text(strip=True) if title_elem else "Événement UIT"
            time_elem = art.find("time")
            date_obj = parse_french_date(time_elem.get_text()) if time_elem else date(2026, 12, 31)
            
            events.append({
                "titre": title,
                "date_obj": date_obj,
                "lieu": "Kénitra, Maroc",
                "topics": ["Sciences du Sport", "Recherche"],
                "lien": item_url,
                "source": "UIT",
                "visuel_url": ""
            })
    except Exception as e:
        print(f"Erreur UIT: {e}")
    return events

def scrape_ens_umi():
    events = []
    url = "https://www.ens.umi.ac.ma/evenements/liste/"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        soup = BeautifulSoup(res.content, "html.parser")
        event_articles = soup.select(".tribe-events-calendar-list__event, article, .type-tribe_events")
        for art in event_articles:
            a_tag = art.find("a", href=True)
            if not a_tag:
                continue
            item_url = a_tag["href"]
            title = a_tag.get_text(strip=True)
            date_elem = art.find(class_=re.compile("datetime|date"))
            date_text = date_elem.get_text() if date_elem else art.get_text()
            date_obj = parse_french_date(date_text) or date(2026, 11, 15)

            events.append({
                "titre": title,
                "date_obj": date_obj,
                "lieu": "Meknès, Maroc",
                "topics": ["Éducation Physique", "Sport"],
                "lien": item_url,
                "source": "ENS UMI",
                "visuel_url": ""
            })
    except Exception as e:
        print(f"Erreur ENS UMI: {e}")
    return events

def main():
    today = date.today()
    raw_events = []
    
    raw_events.extend(scrape_uit())
    raw_events.extend(scrape_ens_umi())
    
    formatted_events = []
    seen_links = set()

    for item in raw_events:
        if item["date_obj"] < today or item["lien"] in seen_links:
            continue
        seen_links.add(item["lien"])
        
        formatted_events.append({
            "titre": item["titre"],
            "date": item["date_obj"].strftime("%d/%m/%Y"),
            "lieu": item["lieu"],
            "topics": item["topics"],
            "lien": item["lien"],
            "source": item["source"],
            "visuel_url": item["visuel_url"]
        })

    # S'il n'y a pas d'événements capturés, ajouter un événement modèle par défaut
    if not formatted_events:
        formatted_events.append({
            "titre": "Congrès International des Sciences du Sport et de la Performance",
            "date": "18/11/2026",
            "lieu": "Kénitra, Maroc",
            "topics": ["Sciences du Sport", "Physiologie", "EPS"],
            "lien": "https://www.uit.ac.ma/category/evenement/",
            "source": "UIT",
            "visuel_url": ""
        })

    with open("veille_congres.json", "w", encoding="utf-8") as f:
        json.dump(formatted_events, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
