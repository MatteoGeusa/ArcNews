import requests
import re
from bs4 import BeautifulSoup
import config
import logging

class ArcNewsScraper:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }

    def get_article_details(self, article_link):
        """Scarica il dettaglio di una singola news."""
        try:
            r = requests.get(article_link, headers=self.HEADERS, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            
            article_container = soup.find('div', class_=re.compile("payload-richtext"))
            
            content = ""
            photos = []
            
            if article_container:
                content = article_container.decode_contents().strip()
                images = article_container.find_all('img')
                photos = [img.get('src') for img in images if img.get('src')]
            
            return content, photos
        except Exception as e:
            print(f"Errore scraping dettagli {article_link}: {e}")
            return "", []

def fetch_latest_news(self):
        """
        Scarica la lista delle news.
        Restituisce una lista di dizionari o una lista vuota in caso di errore.
        """
        results = []

        try:
            response = requests.get(config.NEWS_URL, headers=self.HEADERS, timeout=15)
            
            # Solleva un'eccezione se lo status code è 4xx o 5xx
            response.raise_for_status() 

            # 2. Parsing HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            target_class_pattern = re.compile("news-article-card_container")
            articles_html = soup.find_all('a', class_=target_class_pattern)

            # 3. Estrazione Dati
            for article in articles_html:
                try:
                    title_tag = article.find('div', class_=re.compile("news-article-card_title"))
                    
                    if not title_tag:
                        continue
                    
                    title = title_tag.get_text(strip=True)
                    
                    date_tag = article.find('div', class_=re.compile("news-article-card_date"))
                    date_raw = date_tag.get_text(strip=True) if date_tag else "Data sconosciuta"

                    partial_link = article.get('href')
                    full_link = config.BASE_URL + partial_link
                    
                    results.append({
                        "title": title,
                        "date_raw": date_raw,
                        "link": full_link
                    })

                except Exception:
                    continue
            
            return results

        except requests.exceptions.RequestException as e:
            logging.error(f"Errore di connessione durante il fetch delle news: {e}")            
            return []
        except Exception as e:
            logging.critical(f"Errore imprevisto nello scraper: {e}", exc_info=True)
            return []