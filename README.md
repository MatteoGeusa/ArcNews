# 📰 ArcNews Bot - Telegram Notifier

> **Automated News Scraper & Telegram Broadcasting System for Arc Raiders**

Questo progetto è un bot automatizzato scritto in Python che monitora il sito ufficiale di Arc Raiders, scarica le ultime notizie e le invia istantaneamente a un canale Telegram formattate in Markdown.

Il sistema è progettato per essere efficiente, evitando duplicati e monitorando le performance di esecuzione.

---

## 🚀 Tecnologie Utilizzate

Il progetto sfrutta uno stack Python leggero e performante:

* **Python 3.x**: Linguaggio core.
* **BeautifulSoup4 (`bs4`)**: Per il parsing dell'HTML e l'estrazione dei contenuti (titoli, date, immagini).
* **Requests**: Per gestire le chiamate HTTP verso il sito web.
* **SQLite3**: Database leggero su file per la persistenza dei dati e la deduplicazione.
* **Markdownify**: Per convertire l'HTML delle news in testo formattato leggibile su Telegram.
* **Logging**: Modulo nativo per il tracciamento dettagliato delle operazioni e degli errori.

---

## ⚙️ Come Funziona

Il cuore del sistema risiede in `main.py` e `scraper.py`. Ecco il flusso logico che garantisce stabilità e performance:

### 1. Fetching Intelligente
Il bot scarica la lista delle news dalla pagina indice. Invece di scaricare immediatamente i dettagli di ogni articolo, esegue un **pre-check**:
* Verifica se il **link** esiste già nel database (`link_exists`).
* **Ottimizzazione "Tolerance"**: Se il bot incontra **5 notizie consecutive** che sono già presenti nel database (parametro `MAX_OLD_NEWS_TOLERANCE`), interrompe l'esecuzione. Questo evita di scansionare centinaia di vecchi articoli inutilmente, risparmiando banda e tempo.

### 2. Integrità dei Dati e Checksum
Per garantire che una notizia sia univoca e per rilevare eventuali modifiche, il bot utilizza un sistema di **Hashing MD5**:
1.  Viene generata una stringa univoca combinando: `Titolo` + `Contenuto` + `Lista Foto`.
2.  Viene calcolato l'hash **MD5** di questa stringa (il `checksum`).
3.  Durante l'inserimento nel database (`upsert_news`), se il link esiste ma il checksum è diverso, la notizia viene aggiornata. Se il link non esiste, viene creata.

### 3. Conversione e Invio
* L'HTML grezzo viene pulito (rimozione script/style) e convertito in **Markdown**.
* Se il testo supera i limiti di Telegram, viene troncato intelligentemente senza spezzare le parole.
* Le immagini vengono allegate e il messaggio viene inviato tramite le API di Telegram.

---

## 📊 Sistema di Logging e Statistiche

Il bot non si limita a funzionare, ma "si racconta" attraverso il file `bot_execution.log`.
Ogni esecuzione traccia una **performance breakdown** precisa:

* **Net Time**: Tempo speso in attesa della rete (scaricamento HTML).
* **DB Time**: Tempo speso per query SQL (lettura/scrittura).
* **TG Time**: Tempo impiegato per l'upload verso i server di Telegram.

Esempio di output nei log:
```text
STOP (End of List) | Tot: 2.45s | Net: 1.10s | DB: 0.05s | TG: 1.20s | New: 1 | Skip: 12 | Err: 0