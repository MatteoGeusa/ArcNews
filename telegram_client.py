import requests
import json
import config

class TelegramClient:
    def __init__(self):
        self.token = config.TELEGRAM_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_unified(self, message_md, photo_urls):
        """
        Orchestra l'invio decidendo la strategia migliore in base a lunghezza testo e foto.
        """
        CAPTION_LIMIT = 1024
        
        try:
            if not photo_urls:
                return self._send_text(message_md)
            
            if len(message_md) > CAPTION_LIMIT:
                print("Testo troppo lungo per caption. Invio testo e album separati.")
                text_sent = self._send_text(message_md)
                if text_sent:
                    if len(photo_urls) == 1:
                        return self._send_photo(photo_urls[0], caption="")
                    else:
                        return self._send_album(photo_urls, caption="")
                return False

            elif len(photo_urls) == 1:
                return self._send_photo(photo_urls[0], message_md)
            
            else:
                return self._send_album(photo_urls, message_md)

        except requests.exceptions.RequestException as e:
            if e.response is not None:
                print(f"❌ Errore Telegram API: {e.response.text}")
            else:
                print(f"❌ Errore Connessione: {e}")
            return False

    def _send_text(self, text):
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        return True

    def _send_photo(self, photo_url, caption):
        url = f"{self.base_url}/sendPhoto"
        payload = {
            'chat_id': self.chat_id,
            'photo': photo_url,
            'caption': caption,
            'parse_mode': 'Markdown'
        }
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        return True

    def _send_album(self, photo_urls, caption):
        url = f"{self.base_url}/sendMediaGroup"
        media_group = []
        safe_urls = photo_urls[:10]

        for i, img_url in enumerate(safe_urls):
            media_item = {'type': 'photo', 'media': img_url}
            
            if i == 0 and caption:
                media_item['caption'] = caption
                media_item['parse_mode'] = 'Markdown'
            
            media_group.append(media_item)

        payload = {
            'chat_id': self.chat_id,
            'media': json.dumps(media_group),
        }
        
        resp = requests.post(url, data=payload)
        resp.raise_for_status()
        return True