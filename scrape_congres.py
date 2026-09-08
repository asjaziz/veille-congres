"""
Script de veille automatique des événements académiques marocains.
Sources : UIT, ENS UMI, UCA, USMBA
Sortie : veille_congres.json (pour gadget Blogger)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as dateparser
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"
}

TODAY = datetime.now()

SITES = [
    {"nom": "UIT", "url_list": "https://www.uit.ac.ma/category/evenement/"},
    {"nom": "ENS UMI", "url_list": "https://www.ens.umi.ac.ma/evenements/liste/"},
    {"nom": "UCA", "url_list": "https://www.uca.ma/fr/events"},
    {"nom": "USMBA", "url_list": "https://www.usmba.ac.ma/~usmba2/"}
]


def parse_date_french(date_str):
    if not date_str:
        return None
    try:
        return dateparser.parse(date_str, languages=["fr"], dayfirst=True)
    except Exception:
        return None


def is_future(date_obj):
    return date_obj is not None and date_obj >= TODAY


def extract_topics_from_text(text):
    if not text:
        return []
    text = text.lower()
    keywords = [
        "climat", "changement climatique", "environnement",
        "matériaux", "smart materials", "technologies",
        "astronomie", "jeunesse", "youth",
        "intelligence artificielle", "IA", "deep learning", "machine learning",
        "innovation", "économie de la connaissance",
        "ingénierie", "technologie", "sommet"
    ]
    found = [kw.title() for kw in keywords if kw in text]
    seen = set()
    unique = []
    for t in found:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique.append(t)
    return unique if unique else ["Non spécifié"]


def get_text_safe(tag):
    return tag.get_text(" ", strip=True) if tag else ""


def scrape_uit():
    """Scrape UIT - va sur chaque page individuelle pour récupérer le vrai lien."""
    events = []
    try:
        resp = requests.get(SITES[0]["url_list"], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("article") or soup.find_all("div", class_=lambda c: c and "post" in c.lower() if c else False)

        for article in articles[:15]:  # Limite à 15 pour éviter trop de requêtes
            title_tag = article.find("h2") or article.find("h3")
            if not title_tag:
                continue
            
            # LIEN de la page liste
            link_tag = title_tag.find("a", href=True)
            if not link_tag:
                continue
            
            lien_liste = link_tag["href"]
            title = get_text_safe(title_tag)

            # ALLER SUR LA PAGE INDIVIDUELLE pour récupérer le vrai lien
            try:
                resp_detail = requests.get(lien_liste, headers=HEADERS, timeout=10)
                soup_detail = BeautifulSoup(resp_detail.text, "html.parser")
                
                # Le vrai lien est souvent dans un bouton "Read more" ou dans le permalink
                permalink = soup_detail.find("link", rel="canonical")
                if permalink and permalink.get("href"):
                    lien_final = permalink["href"]
                else:
                    # Sinon, utiliser l'URL de la page elle-même
                    lien_final = lien_liste
                
                # Date sur la page détail
                date_tag = soup_detail.find("time") or soup_detail.find("span", class_=lambda c: c and "date" in c.lower() if c else False)
                date_str = get_text_safe(date_tag)
                pub_date = parse_date_french(date_str)

                # Topics
                content = soup_detail.find("div", class_=lambda c: c and ("content" in c.lower() or "entry" in c.lower()) if c else False)
                summary = get_text_safe(content) if content else get_text_safe(soup_detail)
                topics = extract_topics_from_text(summary)
                lieu = "Non spécifié"

                if is_future(pub_date):
                    events.append({
                        "titre": title,
                        "date": pub_date.strftime("%d/%m/%Y") if pub_date else "Non spécifié",
                        "lieu": lieu,
                        "topics": topics,
                        "lien": lien_final,  # ← VRAI LIEN INDIVIDUEL !
                        "source": "UIT",
                        "visuel_url": ""
                    })
            except Exception as e:
                print(f"[UIT détail] Erreur pour {lien_liste}: {e}")
                # En cas d'erreur, utiliser le lien de la liste
                events.append({
                    "titre": title,
                    "date": "Non spécifié",
                    "lieu": "Non spécifié",
                    "topics": ["Non spécifié"],
                    "lien": lien_liste,
                    "source": "UIT",
                    "visuel_url": ""
                })
                
    except Exception as e:
        print(f"[UIT] Erreur: {e}")
    return events


def scrape_uca():
    """Scrape UCA - va sur chaque page individuelle."""
    events = []
    try:
        resp = requests.get(SITES[2]["url_list"], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.find_all("div", class_=lambda c: c and ("event" in c.lower() or "post" in c.lower()) if c else False)

        for item in items[:15]:
            title_tag = item.find("h3") or item.find("h2")
            if not title_tag:
                continue
            
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue
            
            lien_liste = link_tag["href"]
            title = get_text_safe(title_tag)

            try:
                resp_detail = requests.get(lien_liste, headers=HEADERS, timeout=10)
                soup_detail = BeautifulSoup(resp_detail.text, "html.parser")
                
                permalink = soup_detail.find("link", rel="canonical")
                lien_final = permalink["href"] if permalink and permalink.get("href") else lien_liste
                
                date_tag = soup_detail.find("span", class_=lambda c: c and "date" in c.lower() if c else False)
                date_str = get_text_safe(date_tag) if date_tag else ""
                date_obj = parse_date_french(date_str)

                content = soup_detail.find("div", class_=lambda c: c and ("content" in c.lower() or "entry" in c.lower()) if c else False)
                summary = get_text_safe(content) if content else get_text_safe(soup_detail)
                topics = extract_topics_from_text(summary)
                lieu = "Non spécifié"

                if is_future(date_obj):
                    events.append({
                        "titre": title,
                        "date": date_obj.strftime("%d/%m/%Y") if date_obj else "Non spécifié",
                        "lieu": lieu,
                        "topics": topics,
                        "lien": lien_final,
                        "source": "UCA",
                        "visuel_url": ""
                    })
            except Exception as e:
                print(f"[UCA détail] Erreur: {e}")
                
    except Exception as e:
        print(f"[UCA] Erreur: {e}")
    return events


def scrape_usmba():
    """Scrape USMBA."""
    events = []
    try:
        resp = requests.get(SITES[3]["url_list"], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.find_all("div", class_=lambda c: c and ("event" in c.lower() or "post" in c.lower()) if c else False)

        for item in items[:15]:
            title_tag = item.find("h3") or item.find("h4")
            if not title_tag:
                continue
            title = get_text_safe(title_tag)
            
            link_tag = item.find("a", href=True)
            lien = link_tag["href"] if link_tag else SITES[3]["url_list"]

            date_tag = item.find("span", class_=lambda c: c and "date" in c.lower() if c else False)
            date_str = get_text_safe(date_tag) if date_tag else ""
            date_obj = parse_date_french(date_str)

            summary = get_text_safe(item.find("p")) or get_text_safe(item)
            topics = extract_topics_from_text(summary)

            lieu_match = re.search(r"(Facs|Facult|Campus|Universit|F\s*)[^,\n]+", summary, re.IGNORECASE)
            lieu = lieu_match.group(0).strip() if lieu_match else "Non spécifié"

            if is_future(date_obj):
                events.append({
                    "titre": title,
                    "date": date_obj.strftime("%d/%m/%Y") if date_obj else "Non spécifié",
                    "lieu": lieu,
                    "topics": topics,
                    "lien": lien,
                    "source": "USMBA",
                    "visuel_url": ""
                })
    except Exception as e:
        print(f"[USMBA] Erreur: {e}")
    return events


def scrape_ens_umi():
    """Scrape ENS UMI."""
    events = []
    try:
        resp = requests.get(SITES[1]["url_list"], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.find_all("div", class_=lambda c: c and "event" in c.lower() if c else False)

        for item in items[:10]:
            title_tag = item.find("h3")
            if not title_tag:
                continue
            title = get_text_safe(title_tag)
            
            link_tag = item.find("a", href=True)
            lien = link_tag["href"] if link_tag else SITES[1]["url_list"]
            
            date_tag = item.find("span", class_=lambda c: c and "date" in c.lower() if c else False)
            date_str = get_text_safe(date_tag) if date_tag else ""
            date_obj = parse_date_french(date_str)

            summary = get_text_safe(item.find("p")) or get_text_safe(item)
            topics = extract_topics_from_text(summary)
            lieu = "Non spécifié"

            if is_future(date_obj):
                events.append({
                    "titre": title,
                    "date": date_obj.strftime("%d/%m/%Y") if date_obj else "Non spécifié",
                    "lieu": lieu,
                    "topics": topics,
                    "lien": lien,
                    "source": "ENS UMI",
                    "visuel_url": ""
                })
    except Exception as e:
        print(f"[ENS UMI] Erreur: {e}")
    return events


def run_scraping():
    all_events = []
    all_events.extend(scrape_uit())
    all_events.extend(scrape_uca())
    all_events.extend(scrape_usmba())
    all_events.extend(scrape_ens_umi())

    seen = set()
    unique = []
    for e in all_events:
        key = e["titre"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(e)

    def parse_for_sort(ev):
        d = parse_date_french(ev["date"])
        return d if d else datetime.max

    unique.sort(key=parse_for_sort)
    return unique[:10]


def export_json(events, filename="veille_congres.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON exporté: {filename} ({len(events)} événements)")


if __name__ == "__main__":
    events = run_scraping()
    export_json(events)
