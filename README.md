# AI Technology Mapping in Italian Energy Sector - Web Scraper

This repository contains the Python code and data files used for the project "Technology mapping sull'utilizzo dell'IA nelle aziende italiane del settore energetico" (Technology mapping on the use of AI in Italian companies in the energy sector). This project was conducted as part of the Master's Degree in Business Organization (Organizzazione dell'Impresa) at Università Politecnica delle Marche.

## Project Overview

The primary objective of this project was to create a detailed technology map focused on the development and adoption of Artificial Intelligence (AI) within the Italian energy sector. The core of this involved:

1.  Identifying key players (energy companies) operating at the intersection of AI and the energy sector in Italy.
2.  Scraping their official websites to detect mentions and applications of AI technologies.
3.  Building a structured dataset to analyze the penetration and use-cases of AI.

This repository specifically hosts the web scraping script and the input/output data from this phase.

## Methodology

The approach involved automated analysis of publicly accessible web content (company websites) using:

*   **Web Scraping:** To retrieve HTML content from a list of company URLs.
*   **Natural Language Processing (NLP):** To recognize specific AI-related terminology within the extracted text.
*   **Optical Character Recognition (OCR):** To extract text from images on websites where direct text was insufficient.

### Operational Flow

The script performs the following steps for each URL in the input file:

1.  **Load Input URLs:** Reads a predefined list of company URLs from an input CSV/Excel file (`ImpreseEnergetiche_Input.xlsx`).
2.  **Fetch Web Content:**
    *   Sends HTTP GET requests using the `requests` library.
    *   Implements User-Agent rotation, randomized delays, error handling (e.g., for 429 errors, SSL issues), and timeouts to ensure robust and respectful scraping.
    *   Verifies `Content-Type` is `text/html`.
3.  **Extract Relevant Text:**
    *   Parses HTML using `BeautifulSoup4`.
    *   Attempts to isolate main content using selectors for common tags like `<article>`, `<main>`, specific IDs/classes, falling back to `<body>` if necessary.
    *   Applies a minimum character threshold for significance.
4.  **AI Detection in Content:**
    *   **Preprocessing:** Converts text to lowercase, removes non-alphanumeric characters (except spaces/accented).
    *   **Regex Search:** Initial quick check for basic AI terms (e.g., "ai", "intelligenza artificiale", "machine learning").
    *   **spaCy NLP Analysis:** If the regex search is inconclusive or for more robust confirmation, the text is analyzed using `spaCy` (model `it_core_news_lg`). An `EntityRuler` is configured with a predefined list of AI-related `KEYWORDS` (covering concepts, technologies, applications, and tools like "reti neurali", "NLP", "analisi predittiva", "TensorFlow", "ChatGPT").
    *   **OCR for Images:** `Pytesseract` and `Pillow` are used to extract text from images, which is then also analyzed.
5.  **Record Results:** The outcome for each URL (AI "Presente", "Assente", or "Errore" with a description) is recorded.
6.  **Save Output Data:** The original input data is augmented with an `AI_Detection` column and saved to a new CSV/Excel file (`ImpreseEnergetiche_Output.xlsx`).

The analysis was performed in a Google Colaboratory environment.

## Technologies & Libraries Used

*   **Programming Language:** Python 3.x
*   **Web Scraping & HTTP:**
    *   `requests`
    *   `urllib3` (implicitly by `requests`)
*   **HTML Parsing:**
    *   `BeautifulSoup4` (bs4)
*   **Data Handling:**
    *   `pandas`
*   **Natural Language Processing (NLP):**
    *   `spaCy` (with `it_core_news_lg` model and `EntityRuler`)
*   **Optical Character Recognition (OCR):**
    *   `Pytesseract`
    *   `Pillow` (PIL)
*   **Web Technology Identification (Contextual):**
    *   `builtwith`
*   **Environment:** Google Colaboratory

## Summary of Scraping Run (from the report)

*   **Total URLs Processed:** 1,466
*   **AI Presence Detected ("Presente"):** 18.2% (267 sites)
*   **No AI Content Detected ("Assente"):** 73.6% (1,079 sites)
*   **Error (Content Not Available):** 8.2% (120 URLs - due to server blocks, SSL issues, non-HTML content etc.)

## Academic Context

This work is part of the project report for the Master's Degree in Business Organization (Organizzazione dell'Impresa) at Università Politecnica delle Marche.

*   **Course:** Organizzazione dell'Impresa
*   **University:** Università Politecnica delle Marche
*   **Academic Year:** 2024/2025
*   **Professor:** Donato Iacobucci
*   **Authors:**
    *   Gianluca Baldelli (S1121772)
    *   Federico Beni (S1123835)
    *   Fabio Tempera (S1125574)
