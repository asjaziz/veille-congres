import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import json
import re
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, x64) Chrome/120.0.0.0 Safari/537.36"
}

def parse_french_date(text):
    """
    Tente d'extraire et de convertir une date texte en objet datetime.date.
    Format de sortie attendu: JJ/MM/AAAA
    """
    months = {
        'janvier': '01', 'février': '02', 'fevrier': '02', 'mars': '03',
        'avril': '04', 'mai': '05', 'juin': '06', 'juillet': '07',
        'août': '08', 'aout': '08', 'septembre': '09', 'octobre': '10',
        'novembre': '11', 'décembre': '12', 'decembre': '12'
    }
    
    # Recherche format DD/MM/YYYY ou DD-MM-YYYY
    match_numeric = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', text)
    if match_numeric:
        d, m, y = match_numeric.groups()
        try:
            return date(int(y), int(m), int(d))
        except ValueError:
            pass

    # Recherche format textuel ex: "16 juin 2026"
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
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.content, "html.parser")
        articles = soup.find_all("article")
        
        for art in articles:
            link_elem = art.find("a", href=True)
            if not link_elem:
                continue
            item_url = link_elem["href"]
            
            # Extraction direct sur page individuelle si possible
            title_elem = art.find(["h2", "h3", "h1"])
            title = title_elem.get_text(strip=True) if title_elem else "Événement UIT"
            
            # Extraction de la date dans le post
            time_elem = art.find("time")
            date_obj = parse_french_date(time_elem.get_text()) if time_elem else None
            
            if not date_obj:
                date_obj = date.today() # Par défaut si non spécifié
                
            events.append({
                "titre": title,
                "date_obj": date_obj,
                "lieu": "Kénitra, Maroc",
                "topics": ["Sciences du Sport", "Recherche", "Innovation"],
                "lien": item_url,
                "source": "UIT",
                "visuel_url": ""
            })
    except Exception as e:
        print(f"Erreur UIT: {e}")
    return events

def scrape_uca():
    events = []
    url = "https://www.uca.ma/fr/events"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.content, "html.parser")
        cards = soup.select(".event-item, .article, .card, div.news-box")
        
        for card in cards:
            a_tag = card.find("a", href=True)
            if not a_tag:
                continue
            item_url = urljoin(url, a_tag["href"])
            title = a_tag.get_text(strip=True) or "Colloque / Conférence UCA"
            
            date_text = card.get_text()
            date_obj = parse_french_date(date_text) or date.today()
            
            events.append({
                "titre": title,
                "date_obj": date_obj,
                "lieu": "Marrakech, Maroc",
                "topics": ["Activités Physiques", "Sciences de la Santé"],
                "lien": item_url,
                "source": "UCA",
                "visuel_url": ""
            })
    except Exception as e:
        print(f"Erreur UCA: {e}")
    return events

def scrape_usmba():
    events = []
    url = "https://www.usmba.ac.ma/~usmba2/"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.content, "html.parser")
        links = soup.find_all("a", href=True)
        
        for a in links:
            href = a["href"]
            text = a.get_text(strip=True)
            if any(k in text.lower() for k in ["congrès", "colloque", "conférence", "séminaire", "journée"]):
                item_url = urljoin(url, href)
                date_obj = parse_french_date(text) or date.today()
                events.append({
                    "titre": text,
                    "date_obj": date_obj,
                    "lieu": "Fès, Maroc",
                    "topics": ["Sciences", "Académique"],
                    "lien": item_url,
                    "source": "USMBA",
                    "visuel_url": ""
                })
    except Exception as e:
        print(f"Erreur USMBA: {e}")
    return events

def scrape_ens_umi():
    events = []
    url = "https://www.ens.umi.ac.ma/evenements/liste/"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.content, "html.parser")
        
        # Structure 'The Events Calendar'
        event_articles = soup.select(".tribe-events-calendar-list__event, article, .type-tribe_events")
        for art in event_articles:
            a_tag = art.find("a", class_=re.compile("url|title"), href=True) or art.find("a", href=True)
            if not a_tag:
                continue
            item_url = a_tag["href"]
            title = a_tag.get_text(strip=True)
            
            date_elem = art.find(class_=re.compile("datetime|date"))
            date_text = date_elem.get_text() if date_elem else art.get_text()
            date_obj = parse_french_date(date_text) or date.today()

            events.append({
                "titre": title,
                "date_obj": date_obj,
                "lieu": "Meknès, Maroc",
                "topics": ["Éducation Physique", "Sport", "Pédagogie"],
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
    raw_events.extend(scrape_uca())
    raw_events.extend(scrape_usmba())
    raw_events.extend(scrape_ens_umi())
    
    formatted_events = []
    seen_links = set()

    for item in raw_events:
        # 1. Filtrer les événements passés
        if item["date_obj"] < today:
            continue
            
        # 2. Éviter les doublons d'URL
        if item["lien"] in seen_links:
            continue
        seen_links.add(item["lien"])
        
        # Formatting pour le JSON final
        formatted_events.append({
            "titre": item["titre"],
            "date": item["date_obj"].strftime("%d/%m/%Y"),
            "lieu": item["lieu"],
            "topics": item["topics"],
            "lien": item["lien"],
            "source": item["source"],
            "visuel_url": item["visuel_url"]
        })
        
    # Tri par date la plus proche
    formatted_events.sort(key=lambda x: datetime.strptime(x["date"], "%d/%m/%Y"))

    with open("veille_congres.json", "w", encoding="utf-8") as f:
        json.dump(formatted_events, f, ensure_ascii=False, indent=2)

    print(f"Extraction réussie : {len(formatted_events)} événements futurs conservés.")

if __name__ == "__main__":
    main()
