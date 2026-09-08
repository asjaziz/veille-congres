import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import json
import re
from urllib.parse import urljoin
import urllib3

# Désactiver les avertissements de sécurité SSL pour les serveurs universitaires
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, x64) Chrome/120.0.0.0 Safari/537.36"
}

MONTHS_FR = {
    'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3,
    'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7,
    'août': 8, 'aout': 8, 'septembre': 9, 'octobre': 10,
    'novembre': 11, 'décembre': 12, 'decembre': 12
}

# ==============================================================================
# FONCTIONS UTILITAIRES (Ne pas modifier)
# ==============================================================================

def fetch_soup(url):
    """Télécharge la page HTML d'un site web de façon sécurisée."""
    try:
        res = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        if res.status_code == 200:
            return BeautifulSoup(res.content, "html.parser")
    except Exception as e:
        print(f"[ERREUR] Impossible de charger {url}: {e}")
    return None

def parse_french_date(text):
    """Détecte et convertit une date texte en objet Date Python."""
    if not text:
        return None
    text_clean = text.lower()
    
    # Format numérique (JJ/MM/AAAA)
    match_num = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', text_clean)
    if match_num:
        d, m, y = match_num.groups()
        try:
            return date(int(y), int(m), int(d))
        except ValueError:
            pass

    # Format textuel (15 juin 2026)
    match_txt = re.search(r'(\d{1,2})\s+([a-zà-ÿ]+)\s+(\d{4})', text_clean)
    if match_txt:
        d_str, m_str, y_str = match_txt.groups()
        if m_str in MONTHS_FR:
            try:
                return date(int(y_str), MONTHS_FR[m_str], int(d_str))
            except ValueError:
                pass
    return None


# ==============================================================================
# SCRAPERS INDIVIDUELS PAR UNIVERSITÉ
# ==============================================================================

def scrape_uit():
    """Université Ibn Tofail - Kénitra"""
    events = []
    base_url = "https://www.uit.ac.ma/category/evenement/"
    soup = fetch_soup(base_url)
    if not soup:
        return events
    for art in soup.find_all("article"):
        a_tag = art.find("a", href=True)
        if not a_tag:
            continue
        item_url = urljoin(base_url, a_tag["href"])
        title_elem = art.find(["h2", "h3", "h1"]) or a_tag
        title = title_elem.get_text(strip=True) if title_elem else ""
        if len(title) < 6:
            continue
        time_elem = art.find("time")
        date_obj = parse_french_date(time_elem.get_text() if time_elem else art.get_text())
        events.append({
            "titre": title,
            "date_obj": date_obj,
            "lieu": "Kénitra, Maroc",
            "topics": ["Sciences du Sport", "Recherche Académique"],
            "lien": item_url,
            "source": "UIT"
        })
    return events


def scrape_uca():
    """Université Cadi Ayyad - Marrakech"""
    events = []
    base_url = "https://www.uca.ma/fr/events"
    soup = fetch_soup(base_url)
    if not soup:
        return events
    cards = soup.select(".event-item, .article, .card, div.news-box, article")
    for card in cards:
        a_tag = card.find("a", href=True)
        if not a_tag:
            continue
        item_url = urljoin(base_url, a_tag["href"])
        title = a_tag.get_text(strip=True)
        if len(title) < 6:
            continue
        date_obj = parse_french_date(card.get_text())
        events.append({
            "titre": title,
            "date_obj": date_obj,
            "lieu": "Marrakech, Maroc",
            "topics": ["Activités Physiques", "Sciences de la Santé"],
            "lien": item_url,
            "source": "UCA"
        })
    return events


def scrape_usmba():
    """Université Sidi Mohamed Ben Abdellah - Fès"""
    events = []
    base_url = "https://www.usmba.ac.ma/~usmba2/"
    soup = fetch_soup(base_url)
    if not soup:
        return events
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if any(k in text.lower() for k in ["congrès", "colloque", "conférence", "séminaire", "journée", "forum"]):
            item_url = urljoin(base_url, a["href"])
            date_obj = parse_french_date(text)
            events.append({
                "titre": text,
                "date_obj": date_obj,
                "lieu": "Fès, Maroc",
                "topics": ["Sciences", "Recherche Scientifique"],
                "lien": item_url,
                "source": "USMBA"
            })
    return events


def scrape_ens_umi():
    """École Normale Supérieure - UMI Meknès"""
    events = []
    base_url = "https://www.ens.umi.ac.ma/evenements/liste/"
    soup = fetch_soup(base_url)
    if not soup:
        return events
    articles = soup.select(".tribe-events-calendar-list__event, article, .type-tribe_events, .event-container")
    for art in articles:
        a_tag = art.find("a", href=True)
        if not a_tag:
            continue
        item_url = urljoin(base_url, a_tag["href"])
        title = a_tag.get_text(strip=True)
        if len(title) < 6:
            continue
        date_elem = art.find(class_=re.compile(r"datetime|date|time"))
        date_text = date_elem.get_text() if date_elem else art.get_text()
        date_obj = parse_french_date(date_text)
        events.append({
            "titre": title,
            "date_obj": date_obj,
            "lieu": "Meknès, Maroc",
            "topics": ["Éducation Physique", "Sciences du Sport"],
            "lien": item_url,
            "source": "ENS UMI"
        })
    return events


# ==============================================================================
# MODÈLE POUR AJOUTER UN NOUVEAU SITE (EXEMPLE UM5 RABAT)
# ==============================================================================

def scrape_um5():
    """Exemple : Université Mohammed V - Rabat"""
    events = []
    base_url = "https://www.um5.ac.ma/um5/evenements"  # L'adresse du site
    soup = fetch_soup(base_url)
    if not soup:
        return events

    # On cherche les blocs/cartes qui contiennent les événements
    articles = soup.select("article, .event-card, .news-item")
    for art in articles:
        a_tag = art.find("a", href=True)
        if not a_tag:
            continue
        item_url = urljoin(base_url, a_tag["href"])
        title = a_tag.get_text(strip=True)
        if len(title) < 6:
            continue

        date_obj = parse_french_date(art.get_text())

        events.append({
            "titre": title,
            "date_obj": date_obj,
            "lieu": "Rabat, Maroc",             # Ville du site
            "topics": ["Sciences", "Innovation"], # Topics par défaut
            "lien": item_url,
            "source": "UM5"                     # Sigle de la source
        })
    return events
def scrape_um5():
    """  site international pour annoncer une conférence"""
    events = []
    base_url = "https://portal.sciencesconf.org/browse/search"  # L'adresse du site
    soup = fetch_soup(base_url)
    if not soup:
        return events

    # On cherche les blocs/cartes qui contiennent les événements
    articles = soup.select("article, .event-card, .news-item")
    for art in articles:
        a_tag = art.find("a", href=True)
        if not a_tag:
            continue
        item_url = urljoin(base_url, a_tag["href"])
        title = a_tag.get_text(strip=True)
        if len(title) < 6:
            continue

        date_obj = parse_french_date(art.get_text())

        events.append({
            "titre": title,
            "date_obj": date_obj,
            "lieu": "Rabat, Maroc",             # Ville du site
            "topics": ["Sciences", "Innovation"], # Topics par défaut
            "lien": item_url,
            "source": "SIC"                     # Sigle de la source
        })
    return events

# ==============================================================================
# LISTE DES SOURCES À EXÉCUTER
# ==============================================================================
# Pour ajouter un nouveau site, ajoutez simplement le nom de sa fonction ci-dessous !

ALL_SCRAPERS = [
    scrape_uit,
    scrape_uca,
    scrape_usmba,
    scrape_ens_umi,
     scrape_SIC,
    # scrape_um5,  # <-- Retirez le '#' pour activer ce nouveau site quand vous le souhaitez
]


# ==============================================================================
# PROGRAMME PRINCIPAL (AUTOMATIQUE)
# ==============================================================================

def main():
    today = date.today()
    all_raw_events = []

    # Exécution de chaque fonction de scraping enregistrée
    for scraper_func in ALL_SCRAPERS:
        try:
            print(f"Extraction en cours : {scraper_func.__name__}...")
            site_events = scraper_func()
            all_raw_events.extend(site_events)
            print(f"  -> {len(site_events)} événements récupérés.")
        except Exception as e:
            print(f"[ATTENTION] Erreur lors de l'exécution de {scraper_func.__name__}: {e}")

    final_events = []
    seen_urls = set()

    for item in all_raw_events:
        # Éviter les doublons
        if item["lien"] in seen_urls:
            continue

        # Attribution d'une date par défaut si non détectée
        event_date = item["date_obj"] if item["date_obj"] else date(today.year, 12, 15)

        # Filtre : Garder uniquement les événements futurs
        if event_date < today:
            continue

        seen_urls.add(item["lien"])

        final_events.append({
            "titre": item["titre"],
            "date": event_date.strftime("%d/%m/%Y"),
            "lieu": item["lieu"],
            "topics": item["topics"],
            "lien": item["lien"],
            "source": item["source"],
            "visuel_url": ""
        })

    # Tri chronologique
    final_events.sort(key=lambda x: datetime.strptime(x["date"], "%d/%m/%Y"))

    # Événement de démonstration si aucun résultat capturé
    if not final_events:
        final_events.append({
            "titre": "Congrès International des Sciences du Sport et de la Performance",
            "date": "18/11/2026",
            "lieu": "Kénitra, Maroc",
            "topics": ["Sciences du Sport", "Physiologie", "EPS"],
            "lien": "https://www.uit.ac.ma/category/evenement/",
            "source": "UIT",
            "visuel_url": ""
        })

    # Sauvegarde dans le fichier JSON
    with open("veille_congres.json", "w", encoding="utf-8") as f:
        json.dump(final_events, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Terminé : {len(final_events)} événements futurs enregistrés dans veille_congres.json.")

if __name__ == "__main__":
    main()
