import os
import urllib.request
import urllib.parse
from pathlib import Path
from loglayici import logger_olustur

class TelegramBildirimci:
    def __init__(self):
        self.logger = logger_olustur("TelegramBildirimci")
        self.token = None
        self.chat_id = None
        self._yukle()

    def _yukle(self):
        env_dosyasi = Path(".env")
        if env_dosyasi.exists():
            with env_dosyasi.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key == "TELEGRAM_BOT_TOKEN":
                        self.token = value
                    elif key == "TELEGRAM_CHAT_ID":
                        self.chat_id = value
        
        # OS environment overrides
        if os.getenv("TELEGRAM_BOT_TOKEN"):
            self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if os.getenv("TELEGRAM_CHAT_ID"):
            self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def firsat_bildirimi_gonder(self, urun_adi, yeni_fiyat, hedef_fiyat, para_birimi, url):
        if not self.token or not self.chat_id:
            self.logger.info("Telegram bilgileri tanımlı değil, bildirim gönderilmiyor.")
            return

        mesaj = (
            f"🎯 Fırsat Bildirimi!\n\n"
            f"Ürün: {urun_adi}\n"
            f"Fiyat: {yeni_fiyat} {para_birimi}\n"
            f"Hedef: {hedef_fiyat} {para_birimi}\n"
            f"Link: {url}"
        )

        try:
            url_base = f"https://api.telegram.org/bot{self.token}/sendMessage"
            params = {
                "chat_id": self.chat_id,
                "text": mesaj
            }
            encoded_params = urllib.parse.urlencode(params)
            full_url = f"{url_base}?{encoded_params}"
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                if response.status == 200:
                    self.logger.info(f"{urun_adi} için bildirim gönderildi.")
                else:
                    self.logger.error(f"Telegram API hatası: {response.status}")
        except Exception as e:
            self.logger.error(f"Telegram bildirim hatası: {e}")
