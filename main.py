import json
import time
import logging
import config
import utils
from scraper import ArcNewsScraper
from telegram_client import TelegramClient
from database import DatabaseManager

# Configurazione base del logging
logging.basicConfig(
    filename='bot_execution.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    t_global_start = time.time()

    stats = {
        "db_time": 0.0,      # Tempo totale query DB
        "net_time": 0.0,     # Tempo totale scaricamento dati
        "tg_time": 0.0,      # Tempo totale invio Telegram
        "processed": 0,      # Numero articoli inviati
        "skipped": 0,        # Numero articoli ignorati (già vecchi)
        "errors": 0          # Numero errori (es. invio fallito)
    }

    logging.info(">>> START ESECUZIONE")

    try:
        t0 = time.time()
        db = DatabaseManager(config.DB_NAME)
        db.apply_migration()
        stats["db_time"] += (time.time() - t0)
        logging.info("DB connesso e migrazioni verificate.")

        scraper = ArcNewsScraper()
        tg_client = TelegramClient()

        t0 = time.time()
        news_list = scraper.fetch_latest_news()
        stats["net_time"] += (time.time() - t0)

        count_news = len(news_list)
        msg_count = f"Scraper ha trovato {count_news} articoli totali."
        logging.info(msg_count)

        consecutive_existing_news = 0 
        MAX_OLD_NEWS_TOLERANCE = 5
        stop_reason = "End of List" 

        for i, item in enumerate(news_list, 1):
            title = item['title']
            link = item['link']
            date_raw = item['date_raw']
            
            # Verifica esistenza
            t0 = time.time()
            exists = db.link_exists(link)
            stats["db_time"] += (time.time() - t0)

            if exists:
                stats["skipped"] += 1
                consecutive_existing_news += 1
                
                if consecutive_existing_news >= MAX_OLD_NEWS_TOLERANCE:
                    stop_reason = "Tolerance Reached"
                    logging.info("Interruzione ciclo: Tolerance Reached")
                    break
                continue
            
            # Se siamo qui, la notizia è nuova
            consecutive_existing_news = 0
            
            t0 = time.time()
            content_raw, photos = scraper.get_article_details(link)
            stats["net_time"] += (time.time() - t0)

            checksum = utils.calculate_checksum_id(title, content_raw, photos)
            sqlite_date = utils.convert_date_for_sqlite(date_raw)

            t0 = time.time()
            is_new = db.upsert_news(checksum, sqlite_date, title, link, content_raw, json.dumps(photos))
            stats["db_time"] += (time.time() - t0)

            if is_new:
                # Preparazione e invio Telegram
                clean_body = utils.clean_html_to_markdown(content_raw)
                msg_text = utils.format_telegram_message_md(title, sqlite_date, clean_body, link)
                
                t0 = time.time()
                success = tg_client.send_unified(msg_text, photos)
                stats["tg_time"] += (time.time() - t0)

                if success:
                    stats["processed"] += 1
                    logging.info(f"Inviato Telegram: {title}")
                    print(f"    -> Notifica inviata con successo.")
                else:
                    stats["errors"] += 1
                    logging.error(f"Errore invio Telegram: {title}")
            else:
                stats["skipped"] += 1

        db.close()

        total_duration = time.time() - t_global_start

        log_msg = (
            f"STOP ({stop_reason}) | "
            f"Tot: {total_duration:.2f}s | "
            f"Net: {stats['net_time']:.2f}s | "
            f"DB: {stats['db_time']:.2f}s | "
            f"TG: {stats['tg_time']:.2f}s | "
            f"New: {stats['processed']} | "
            f"Skip: {stats['skipped']} | "
            f"Err: {stats['errors']}"
        )
        logging.info(log_msg)
        print(f"\n>>> FINE: {log_msg}")

    except Exception as e:
        logging.error(f"CRITICAL CRASH: {e}", exc_info=True) # exc_info=True aggiunge il traceback completo al log
        print(f"\n!!! ERRORE CRITICO: {e}")

if __name__ == "__main__":
    main()