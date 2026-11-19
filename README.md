# E-Commerce Competitor Price Tracker / E-Ticaret Rakip Fiyat Takip Botu (v2.4)

## English
This project is an automated price monitoring system that tracks product prices across different platforms. It provides analytical insights, visual reports, and automated notifications to help users make data-driven purchasing decisions.

### Architecture
- veritabani.py: Relational SQLite database management.
- kaziyici.py: Web scraper with 3x retry mechanism.
- raporlayici.py: Excel and console reporting utility.
- loglayici.py: Centralized logging system.
- bildirimci.py: Telegram instant notification service.
- karsilastirici.py: Competitor price comparison engine.
- dashboard.py: Interactive HTML dashboard generation.
- main.py: Orchestration and workflow execution.

### Key Features
- Relational SQLite time-series data storage.
- Intelligent scraper with JSON-LD & CSS support.
- Robust 3x retry mechanism for network resilience.
- Instant Telegram opportunity alerts.
- Competitor Price Comparison Matrix.
- Interactive Chart.js HTML Dashboard.
- 24/7 cloud automation via GitHub Actions.

### Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `hedefler.json` (and optional `.env` from `.env.example` for Telegram alerts).
4. Run tests: `python -m unittest -v test_takipci.py`
5. Run bot: `python main.py`


---

## Türkçe
Bu proje, çeşitli platformlardaki ürün fiyatlarını takip eden otomatik bir fiyat izleme sistemidir. Veri odaklı satın alma kararları vermenize yardımcı olmak için analitik içgörüler, görsel raporlar ve otomatik bildirimler sunar.

### Mimari
- veritabani.py: İlişkisel SQLite veritabanı yönetimi.
- kaziyici.py: 3x yeniden deneme kalkanına sahip web kazıyıcı.
- raporlayici.py: Excel ve konsol raporlama aracı.
- loglayici.py: Merkezi loglama sistemi.
- bildirimci.py: Telegram anlık fırsat bildirim servisi.
- karsilastirici.py: Rakip fiyat karşılaştırma motoru.
- dashboard.py: İnteraktif HTML dashboard oluşturucu.
- main.py: Sistem orkestrasyonu ve iş akışı yönetimi.

### Öne Çıkan Özellikler
- İlişkisel SQLite zaman serisi veri depolama.
- JSON-LD ve CSS destekli akıllı kazıyıcı.
- Ağ direnci için 3x yeniden deneme (retry) kalkanı.
- Anlık Telegram fırsat bildirimleri.
- Rakip Fiyat Karşılaştırma Matrisi.
- Chart.js tabanlı interaktif HTML Dashboard.
- GitHub Actions ile 7/24 bulut otomasyonu.

### Kurulum
1. Depoyu klonlayın.
2. Gereksinimleri yükleyin: `pip install -r requirements.txt`
3. `hedefler.json` dosyasını (ve isteğe bağlı Telegram bildirimleri için `.env.example` dosyasından `.env` dosyasını) yapılandırın.
4. Testleri çalıştırın: `python -m unittest -v test_takipci.py`
5. Botu çalıştırın: `python main.py`
