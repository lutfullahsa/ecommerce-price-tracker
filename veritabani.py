import sqlite3
from datetime import datetime
from pathlib import Path


class FiyatVeritabani:
    def __init__(self, db_yolu="cikti/fiyat_takip.db"):
        Path(db_yolu).parent.mkdir(parents=True, exist_ok=True)
        self.baglanti = sqlite3.connect(db_yolu)
        self.baglanti.execute("PRAGMA foreign_keys = ON;")
        self.tablolari_olustur()

    def tablolari_olustur(self):
        with self.baglanti:
            self.baglanti.execute("""
                CREATE TABLE IF NOT EXISTS urunler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    urun_adi TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    platform TEXT,
                    hedef_fiyat REAL,
                    aktif_mi INTEGER DEFAULT 1,
                    eklenme_tarihi TEXT NOT NULL
                )
            """)
            self.baglanti.execute("""
                CREATE TABLE IF NOT EXISTS fiyat_gecmisi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    urun_id INTEGER NOT NULL,
                    fiyat REAL NOT NULL,
                    para_birimi TEXT DEFAULT 'TRY',
                    stok_durumu TEXT DEFAULT 'Stokta',
                    kontrol_tarihi TEXT NOT NULL,
                    FOREIGN KEY (urun_id) REFERENCES urunler(id) ON DELETE CASCADE
                )
            """)

    def urun_ekle_veya_getir(self, urun_adi, url, platform="Genel", hedef_fiyat=None):
        tarih = datetime.now().isoformat()
        with self.baglanti:
            self.baglanti.execute("""
                INSERT OR IGNORE INTO urunler (urun_adi, url, platform, hedef_fiyat, eklenme_tarihi)
                VALUES (?, ?, ?, ?, ?)
            """, (urun_adi, url, platform, hedef_fiyat, tarih))
        
        imlec = self.baglanti.execute("SELECT id FROM urunler WHERE url = ?", (url,))
        sonuc = imlec.fetchone()
        return sonuc[0] if sonuc else None

    def fiyat_kaydet(self, urun_id, fiyat, stok_durumu="Stokta", para_birimi="TRY"):
        tarih = datetime.now().isoformat()
        with self.baglanti:
            self.baglanti.execute("""
                INSERT INTO fiyat_gecmisi (urun_id, fiyat, para_birimi, stok_durumu, kontrol_tarihi)
                VALUES (?, ?, ?, ?, ?)
            """, (urun_id, fiyat, para_birimi, stok_durumu, tarih))

    def son_iki_fiyati_getir(self, urun_id):
        imlec = self.baglanti.execute("""
            SELECT fiyat, kontrol_tarihi FROM fiyat_gecmisi
            WHERE urun_id = ?
            ORDER BY id DESC LIMIT 2
        """, (urun_id,))
        return imlec.fetchall()

    def kapat(self):
        self.baglanti.close()
