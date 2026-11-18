# E-Commerce Competitor Price Tracker / E-Ticaret Rakip Fiyat Takip Botu (v1.0)

[English](#english) | [Türkçe](#türkçe)

---

## English

### Overview
A modular Python web scraping and price monitoring tool that tracks product prices and stock availability, stores historical time-series data in a relational **SQLite** database (`urunler` & `fiyat_gecmisi`), triggers target price drop alerts, and exports formatted **Excel** reports.

### Key Features
- **Relational SQLite Architecture:** Normalized `urunler` and `fiyat_gecmisi` tables with foreign key constraints.
- **Multi-Currency Price Parser:** Accurately parses Turkish (`1.499,90 TL`), US (`$1,250.50`), and UK (`£51.77`) price formats.
- **Target Price Alerts & Excel Export:** Detects price drops against target thresholds and generates `fiyat_raporu.xlsx`.
- **Smart Extraction:** Supports structured `JSON-LD` schema data with fallback CSS selectors for live e-commerce pages.
- **Unit Tested:** Verified via Python's built-in `unittest` suite.

### Usage
```bash
python -m pip install requests beautifulsoup4 openpyxl
python main.py
python -m unittest test_takipci.py
```

---

## Türkçe

### Proje Amacı
E-ticaret sitelerindeki ürün fiyatlarını ve stok durumlarını takip eden, fiyat geçmişini ilişkisel **SQLite** veritabanında (`urunler` ve `fiyat_gecmisi`) saklayan, hedef fiyat düşüşlerinde uyarı veren ve **Excel** raporu üreten modüler bir Python otomasyon aracıdır.

### Öne Çıkan Özellikler
- **İlişkisel SQLite Veritabanı:** Yabancı anahtar (`Foreign Key`) ilişkili `urunler` ve `fiyat_gecmisi` tabloları.
- **Akıllı Fiyat Ayrıştırıcı:** Türk Lirası (`1.499,90 TL`), Dolar (`$1,250.50`) ve Sterlin (`£51.77`) formatlarını hatasız sayıya çevirir.
- **Hedef Fiyat Alarmı ve Excel Çıktısı:** Hedef fiyatın altına düşen ürünleri yakalar ve `fiyat_raporu.xlsx` raporu oluşturur.
- **Akıllı Veri Okuma:** Canlı e-ticaret sayfalarında yapılandırılmış `JSON-LD` verisini ve yedek CSS seçicilerini destekler.
- **Birim Testleri:** `unittest` kütüphanesi ile doğrulanmış test altyapısı.

### Kullanım
```bash
python -m pip install requests beautifulsoup4 openpyxl
python main.py
python -m unittest test_takipci.py
```
