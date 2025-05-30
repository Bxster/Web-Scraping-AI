import pandas as pd
from google.colab import drive
import os

# 1. Monta Google Drive
drive.mount('/content/drive')

print("--- Configurazione File ---")
# Percorso del file CSV di input
input_file_path = "/content/drive/My Drive/risultati_AI.csv"

# Percorso per il nuovo file CSV (filtraggio dei "presente", rinomina ed eliminazione colonne)
output_file_path = "/content/drive/My Drive/risultati_AI_filtrato.csv"

# Dizionario per la rinomina delle colonne: {'vecchio_nome': 'nuovo_nome'}
mappa_rinomina_colonne = {
    "Ricavi vendite e prestazioni migl EUR Ultimo anno disp.": "Ricavi vendite e prestazioni migl EUR 2024",
    "Dipendenti Ultimo anno disp.": "Dipendenti 2024"
}

# Lista delle colonne da eliminare (come da richiesta precedente)
colonne_da_eliminare = [
    "Partita IVA",
    "Codice fiscale",
    "BvD ID number",
    "Ricavi vendite e prestazioni migl EUR 2022",
    "UTILE/PERDITA DI ESERCIZIO migl EUR Ultimo anno disp.", # Nota: questa colonna ha un nome simile a una da rinominare, assicurati sia corretto
    "UTILE/PERDITA DI ESERCIZIO migl EUR 2023",
    "UTILE/PERDITA DI ESERCIZIO migl EUR 2022",
    "Dipendenti 2022"
]

print(f"\nLeggendo il file: {input_file_path}...")
try:
    df = pd.read_csv(input_file_path)
    print("File letto con successo.")
    print(f"Numero di righe nel file: {len(df)}")
    print(f"Colonne originali: {df.columns.tolist()}")
except FileNotFoundError:
    print(f"ERRORE: File non trovato al percorso '{input_file_path}'. Controlla il percorso e riprova.")
    exit()
except Exception as e:
    print(f"ERRORE durante la lettura del file CSV: {e}")
    exit()

# --- FASE 1: Rinomina Colonne ---
print("\n--- Rinomina Colonne ---")
colonne_rinominate_effettivamente = {}
mappa_rinomina_valida = {}

for vecchio_nome, nuovo_nome in mappa_rinomina_colonne.items():
    if vecchio_nome in df.columns:
        mappa_rinomina_valida[vecchio_nome] = nuovo_nome
    else:
        print(f"Avviso: La colonna da rinominare '{vecchio_nome}' non è stata trovata nel DataFrame.")

if mappa_rinomina_valida:
    try:
        df.rename(columns=mappa_rinomina_valida, inplace=True)
        print("Rinomina colonne completata con successo per:")
        for vecchio, nuovo in mappa_rinomina_valida.items():
            print(f"  - '{vecchio}' -> '{nuovo}'")
        colonne_rinominate_effettivamente = mappa_rinomina_valida
    except Exception as e:
        print(f"ERRORE durante la rinomina delle colonne: {e}")
else:
    print("Nessuna colonna valida trovata per la rinomina.")

# --- FASE 2: Eliminazione Colonne ---
print("\n--- Eliminazione Colonne ---")
# Aggiorniamo la lista delle colonne da eliminare nel caso una colonna
# che doveva essere eliminata sia stata prima rinominata (improbabile qui ma buona pratica)
# Questa logica è complessa se una colonna rinominata è anche da eliminare con il nuovo nome.
# Per questo scenario specifico, assumiamo che le colonne da eliminare NON siano quelle appena rinominate.
# Se una colonna da eliminare ha lo stesso nome di una *vecchia* colonna rinominata,
# e quella vecchia colonna è stata rinominata, non sarà più trovata per l'eliminazione
# con il suo vecchio nome, il che è corretto.

colonne_effettivamente_da_eliminare = [col for col in colonne_da_eliminare if col in df.columns]

if not colonne_effettivamente_da_eliminare:
    print("Nessuna delle colonne specificate per l'eliminazione è stata trovata nel file (dopo eventuale rinomina).")
else:
    print(f"Colonne che verranno eliminate (se presenti): {colonne_effettivamente_da_eliminare}")
    try:
        df.drop(columns=colonne_effettivamente_da_eliminare, inplace=True)
        print("Eliminazione colonne completata con successo.")
    except KeyError as e: # Anche se il check precedente dovrebbe evitarlo
        print(f"ERRORE: Una o più colonne specificate per l'eliminazione non sono state trovate: {e}")
    except Exception as e:
        print(f"ERRORE durante l'eliminazione delle colonne: {e}")

# --- FASE 3: Filtraggio Righe ---
print("\n--- Filtraggio Righe (AI_Detection='Presente') ---")
colonna_filtro = "AI_Detection"
valore_filtro = "Presente"

if colonna_filtro in df.columns:
    righe_prima_filtro = len(df)
    df_filtrato = df[df[colonna_filtro] == valore_filtro].copy()
    righe_dopo_filtro = len(df_filtrato)
    print(f"Filtraggio completato sulla colonna '{colonna_filtro}' per il valore '{valore_filtro}'.")
    print(f"Righe prima del filtro: {righe_prima_filtro}")
    print(f"Righe dopo il filtro: {righe_dopo_filtro}")

    # Sostituisci il DataFrame originale con quello filtrato
    df = df_filtrato
else:
    print(f"Avviso: La colonna '{colonna_filtro}' non è stata trovata nel DataFrame. Nessun filtraggio applicato.")

# --- FASE 4: Salvataggio ---
print("\n--- Salvataggio File ---")
if df is not None: # Controlla se df esiste (potrebbe non esistere se la lettura fallisce)
    try:
        df.to_csv(output_file_path, index=False)
        print(f"File modificato salvato con successo in: {output_file_path}")
    except Exception as e:
        print(f"ERRORE durante il salvataggio del file CSV: {e}")
else:
    print("DataFrame non disponibile per il salvataggio.")


print("\n--- Operazione completata ---")
