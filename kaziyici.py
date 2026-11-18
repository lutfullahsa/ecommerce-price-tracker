import json
import re
import time
import requests
from bs4 import BeautifulSoup
from loglayici import logger_olustur

logger = logger_olustur()

class FiyatKaziyici:
    def __init__(self, zaman_asimi=15):
        self.zaman_asimi = zaman_asimi
        self.basliklar = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/129.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    @staticmethod
    def fiyati_sayiya_cevir(ham_metin):
        if ham_metin is None:
            return None
        if isinstance(ham_metin, (int, float)):
            return round(float(ham_metin), 2)

        temiz = re.sub(r"[^\d.,]", "", str(ham_metin)).strip()
        if not temiz:
            return None

        if "," in temiz and "." in temiz:
            if temiz.rfind(",") > temiz.rfind("."):
                temiz = temiz.replace(".", "").replace(",", ".")
            else:
                temiz = temiz.replace(",", "")
        elif "," in temiz:
            parcalar = temiz.split(",")
            if len(parcalar[-1]) == 2:
                temiz = temiz.replace(",", ".")
            else:
                temiz = temiz.replace(",", "")

        try:
            return round(float(temiz), 2)
        except ValueError:
            return None

    def _json_ld_fiyat_bul(self, corba):
        for script in corba.find_all("script", type="application/ld+json"):
            try:
                veri = json.loads(script.string or "")
                ogeler = veri if isinstance(veri, list) else [veri]
                for oge in ogeler:
                    if isinstance(oge, dict) and oge.get("@type") == "Product":
                        teklifler = oge.get("offers", {})
                        if isinstance(teklifler, list) and teklifler:
                            teklifler = teklifler[0]
                        if isinstance(teklifler, dict) and "price" in teklifler:
                            fiyat = self.fiyati_sayiya_cevir(teklifler["price"])
                            stok_url = str(teklifler.get("availability", "")).lower()
                            stok = "Tükendi" if "outofstock" in stok_url else "Stokta"
                            if fiyat is not None:
                                return fiyat, stok
            except (json.JSONDecodeError, TypeError):
                continue
        return None, None

    def urun_bilgisi_cek(self, url, fiyat_secici=None, stok_secici=None):
        for deneme in range(3):
            try:
                yanit = requests.get(url, headers=self.basliklar, timeout=self.zaman_asimi)
                yanit.raise_for_status()
                corba = BeautifulSoup(yanit.text, "html.parser")

                # 1. Öncelik: E-ticaret sitelerinin standart JSON-LD ürün verisi
                fiyat, stok_durumu = self._json_ld_fiyat_bul(corba)

                # 2. Öncelik: Özel CSS seçici (Yedek veya yerel test sayfaları için)
                if fiyat is None and fiyat_secici:
                    fiyat_etiketi = corba.select_one(fiyat_secici)
                    if fiyat_etiketi:
                        fiyat = self.fiyati_sayiya_cevir(fiyat_etiketi.get_text())

                if fiyat is None:
                    return {"basarili": False, "hata": "Sayfadan fiyat bilgisi okunamadı (Bot koruması veya seçici uyuşmazlığı)."}

                if stok_durumu is None:
                    stok_durumu = "Stokta"
                    if stok_secici:
                        stok_etiketi = corba.select_one(stok_secici)
                        if stok_etiketi:
                            stok_metni = stok_etiketi.get_text(strip=True).lower()
                            if any(k in stok_metni for k in ["tükendi", "gelince haber ver", "out of stock"]):
                                stok_durumu = "Tükendi"

                return {"basarili": True, "fiyat": fiyat, "stok_durumu": stok_durumu}

            except requests.RequestException as hata:
                logger.warning(f"Bağlantı hatası (Deneme {deneme + 1}/3): {url} - {hata}")
                if deneme < 2:
                    time.sleep(2)
                else:
                    return {"basarili": False, "hata": f"Bağlantı hatası: {hata}"}
