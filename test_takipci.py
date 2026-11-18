import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import requests
from kaziyici import FiyatKaziyici
from veritabani import FiyatVeritabani


class TestFiyatTakipci(unittest.TestCase):
    def setUp(self):
        self.test_db_yolu = "cikti/test_fiyat_takip.db"
        self.db = FiyatVeritabani(self.test_db_yolu)

    def tearDown(self):
        self.db.kapat()
        yol = Path(self.test_db_yolu)
        if yol.exists():
            yol.unlink()

    def test_fiyat_ayristirma(self):
        self.assertEqual(FiyatKaziyici.fiyati_sayiya_cevir("1.499,90 TL"), 1499.90)
        self.assertEqual(FiyatKaziyici.fiyati_sayiya_cevir("£51.77"), 51.77)
        self.assertEqual(FiyatKaziyici.fiyati_sayiya_cevir("$1,250.50"), 1250.50)
        self.assertEqual(FiyatKaziyici.fiyati_sayiya_cevir("249,00 ₺"), 249.00)
        self.assertIsNone(FiyatKaziyici.fiyati_sayiya_cevir("Stokta Yok"))

    def test_veritabani_urun_ve_fiyat_gecmisi(self):
        urun_id = self.db.urun_ekle_veya_getir(
            urun_adi="Test Kulaklık",
            url="https://ornek.com",
            platform="TestStore",
            hedef_fiyat=900.0
        )
        self.assertIsNotNone(urun_id)

        # Aynı URL tekrar eklendiğinde aynı ID dönmeli
        ayni_id = self.db.urun_ekle_veya_getir(
            urun_adi="Test Kulaklık",
            url="https://ornek.com"
        )
        self.assertEqual(urun_id, ayni_id)

        self.db.fiyat_kaydet(urun_id, 950.0, "Stokta", "TRY")
        self.db.fiyat_kaydet(urun_id, 880.0, "Stokta", "TRY")

        gecmis = self.db.son_iki_fiyati_getir(urun_id)
        self.assertEqual(len(gecmis), 2)
        self.assertEqual(gecmis[0][0], 880.0)
        self.assertEqual(gecmis[1][0], 950.0)

    @patch('kaziyici.requests.get')
    def test_retry_mekanizmasi(self, mock_get):
        # 3 denemede de hata aldırıyoruz
        mock_get.side_effect = requests.exceptions.RequestException("Bağlantı Hatası")
        kaziyici = FiyatKaziyici()
        sonuc = kaziyici.urun_bilgisi_cek("http://test.com")
        
        self.assertEqual(mock_get.call_count, 3)
        self.assertFalse(sonuc["basarili"])
        self.assertIn("Bağlantı hatası", sonuc["hata"])


if __name__ == "__main__":
    unittest.main()
