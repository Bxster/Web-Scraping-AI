from google.colab import drive
drive.mount('/content/drive')

!pip install spacy pytesseract pillow builtwith
!python -m spacy download it_core_news_lg
!apt install tesseract-ocr-ita

import spacy
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import random
import pytesseract
from PIL import Image
import io
import builtwith
from urllib.parse import urlparse
import urllib3
from requests.exceptions import RequestException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KEYWORDS = [
    # Concetti base
    "ai", "ia", "intelligenza artificiale", "machine learning",
    "deep learning", "apprendimento automatico", "apprendimento profondo",
    "apprendimento per rinforzo", "apprendimento supervisionato",
    "apprendimento non supervisionato",

    # Tecnologie chiave
    "rete neurale", "reti neurali", "visione artificiale",
    "elaborazione del linguaggio naturale", "nlp",
    "computer vision", "robotica avanzata", "reti generative avversarie",
    "trasformatori", "modelli linguistici", "modelli generativi",

    # Applicazioni pratiche
    "analisi predittiva", "modello predittivo", "automazione intelligente",
    "sistema di raccomandazione", "chatbot", "assistente virtuale",
    "process automation", "rilevamento oggetti", "riconoscimento vocale",
    "sistemi esperti", "mappa termica predittiva",

    # Strumenti/Framework
    "tensorflow", "pytorch", "openai", "keras", "huggingface",
    "scikit-learn", "opencv", "nltk", "spacy", "ibm watson",
    "google ai", "azure machine learning", "amazon sageMaker",

    # Concetti avanzati
    "trasferimento di apprendimento", "active learning",
    "federated learning", "quantum machine learning",
    "spiking neural networks", "reti bayesiane",

    # Sinonimi italiani
    "sistemi intelligenti", "algoritmi autonomi",
    "macchine autoapprendenti", "modelli cognitivi",
    "sistemi adattivi", "analisi dati avanzata",
    "ottimizzazione algoritmica", "decisione automatizzata",

    # Settori applicativi
    "smart manufacturing", "diagnostica predittiva",
    "analisi sentiment", "personalizzazione algoritmica",
    "gestione intelligente", "logistica autonoma",

    # Termini tecnici aggiuntivi
    "embedding", "attention mechanism", "fine-tuning",
    "data mining", "feature engineering", "hyperparameter tuning",

    # Brand/Prodotti specifici
    "chatgpt", "dall-e", "midjourney", "stable diffusion",
    "bard", "copilot", "alphafold", "lamda",

    # Smart Grid
    "rete elettrica intelligente", "grid optimization",
    "dynamic load balancing",

    # Energie Rinnovabili
    "energy forecasting", "output prediction",
    "intermittency management",

    # Manutenzione
    "manutenzione predittiva", "failure prediction",
    "asset health monitoring"
]

nlp = spacy.load("it_core_news_lg")

ai_patterns = []
for keyword in KEYWORDS:
    tokens = [{"LOWER": t.lower()} for t in re.split(r'\s+', keyword)]
    if tokens:
        ai_patterns.append({"label": "AI", "pattern": tokens})

ruler = nlp.add_pipe("entity_ruler")
ruler.add_patterns(ai_patterns)

USER_AGENTS = [
    # Desktop browsers
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Mobile browsers
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/119.0.6045.193 Mobile/15E148 Safari/9520.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    # Altri
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "it-IT,it;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

def extract_main_content(soup):
    # Selettor prioritari (classi comuni per contenuti principali)
    priority_selectors = [
        {'tag': 'article', 'class': ['post-content', 'article-body', 'content']},
        {'tag': 'div', 'id': ['main-content', 'article-content', 'page-content']},
    ]

    for selector in priority_selectors:
        elements = soup.find_all(selector['tag'], class_=selector.get('class'))
        for el in elements:
            text = el.get_text(strip=True, separator=' ')
            if len(text) > 100:  # Soglia caratteri
                return text

    # Fallback a metodi originali
    selectors = ['main', 'article', 'div.content', 'section', 'div.container']
    for selector in selectors:
        content = soup.select_one(selector)
        if content and len(content.text) > 100:
            return content.get_text(strip=True, separator=' ')

    # Ultimo tentativo: body con filtraggio JS boilerplate
    if soup.body:
        text = soup.body.get_text(separator=' ', strip=True)
        return re.sub(r'\s{2,}', ' ', text)
    return ''

def get_website_content(url):
    retry_attempts = 3
    delay = 2

    for attempt in range(retry_attempts):
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                url = f"http://{url}"

            # Usa una sessione persistente
            with requests.Session() as session:
                response = session.get(
                    url,
                    headers=get_random_headers(),
                    timeout=(10, 30),  # Maggior tolleranza per connessione e lettura
                    verify=True,  # Verifica SSL abilitata con gestione eccezioni
                    allow_redirects=True,
                    proxies=None  # Nessun proxy (rimosso per rispetto limiti gratuiti)
                )

            if response.status_code == 200:
                # Verifica che sia effettivamente HTML
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return extract_main_content(soup)
                else:
                    return None  # Ignora contenuti non HTML

            elif response.status_code == 429:  # Rate limiting
                wait = float(response.headers.get('Retry-After', delay * 2))
                time.sleep(wait)
                delay *= 2  # Backoff esponenziale

        except requests.exceptions.SSLError:
            # Fallback a verifica non sicura solo in caso di errori SSL critici
            response = requests.get(url, headers=get_random_headers(), timeout=(10, 30), verify=False)
            if response.status_code == 200:
                return extract_main_content(BeautifulSoup(response.text, 'html.parser'))

        except Exception as e:
            if attempt < retry_attempts - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return f"Errore: {str(e)} dopo {retry_attempts} tentativi"

    return None

def analyze_content(text):
    if not text:
        return False

    text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', ' ', text).lower()

    # Controllo rapido con regex
    if re.search(r'\b(ai|intelligenza artificiale|machine learning)\b', text):
        return True

    # Analisi NLP
    doc = nlp(text)
    return any(ent.label_ == "AI" for ent in doc.ents)

def analyze_website(url):
    try:
        content = get_website_content(url)
        if content:
            return "Presente" if analyze_content(content) else "Assente"
        return "Errore: Contenuto non disponibile"
    except Exception as e:
        return f"Errore: {str(e)}"

# Caricamento dati
df = pd.read_csv("/content/drive/My Drive/Colab Notebooks/ImpreseEnergetiche.csv")
path_to_save = "/content/drive/My Drive/risultati_AI.csv"
df = df.dropna(subset=["URL"]).drop_duplicates(subset=["URL"])

results = []
start_time = time.time()
total_items = len(df)

for idx, url in enumerate(df['URL']):
    # Aggiornamento progresso ogni 5 elementi o all'ultimo elemento
    if idx % 5 == 0 or idx == total_items - 1:
        elapsed = time.time() - start_time
        processed = idx + 1
        remaining = max(total_items - processed, 0)

        # Calcolo ETA
        if processed > 0:
            avg_time_per_item = elapsed / processed
            eta_seconds = avg_time_per_item * remaining
        else:
            eta_seconds = 0

        # Formattazione tempo
        eta_min = int(eta_seconds // 60)
        eta_sec = int(eta_seconds % 60)
        elapsed_min = int(elapsed // 60)
        elapsed_sec = int(elapsed % 60)
        percent_complete = (processed / total_items) * 100

        # Stampa formattata
        progress_msg = (
            f"Progresso: {processed}/{total_items} ({percent_complete:.1f}%)\n"
            f"Tempo trascorso: {elapsed_min}m{elapsed_sec:02.0f}s\n"
            f"ETA: {eta_min}m{eta_sec:02.0f}s\n"
            "────────────────────"
        )
        print(progress_msg)

    results.append(analyze_website(url))
    time.sleep(random.uniform(0.8, 3.5))

df['AI_Detection'] = results

print("\n📊 Risultati finali:")
print(df['AI_Detection'].value_counts())

df.to_csv(path_to_save, index=False)

print(f"\nDati salvati in: {path_to_save}")
