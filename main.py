import json
import time
from pathlib import Path
from veritabani import FiyatVeritabani
from kaziyici import FiyatKaziyici
from raporlayici import FiyatRaporlayici
from loglayici import logger_olustur
from bildirimci import TelegramBildirimci
from karsilastirici import RakipKarsilastirici
from dashboard import HtmlDashboardOlusturucu

logger = logger_olustur()


def hedefleri_yukle(dosya_yolu="hedefler.json"):
    yol = Path(dosya_yolu)
    if not yol.exists():
        raise FileNotFoundError(f"Hedef dosyası bulunamadı: {dosya_yolu}")
    with yol.open("r", encoding="utf-8") as f:
        return json.load(f)


def calistir():
    logger.info("Bot çalışmaya başladı.")
    db = FiyatVeritabani()
    telegram = TelegramBildirimci()
    kaziyici = FiyatKaziyici()
    raporlayici = FiyatRaporlayici()

    try:
        hedefler = hedefleri_yukle()
        sonuclar = []

        print(f"{len(hedefler)} ürün için canlı fiyat kontrolü başlatılıyor...\n")

        for hedef in hedefler:
            urun_kaydi = db.urun_ekle_veya_getir(
                urun_adi=hedef["urun_adi"],
                url=hedef["url"],
                platform=hedef.get("platform", "Genel"),
                hedef_fiyat=hedef.get("hedef_fiyat")
            )
            urun_id = urun_kaydi

            gecmis = db.son_iki_fiyati_getir(urun_id)
            onceki_fiyat = gecmis[0][0] if gecmis else None

            veri = kaziyici.urun_bilgisi_cek(
                url=hedef["url"],
                fiyat_secici=hedef["fiyat_secici"],
                stok_secici=hedef.get("stok_secici")
            )

            if veri["basarili"]:
                para_birimi = hedef.get("para_birimi", "TRY")
                db.fiyat_kaydet(
                    urun_id=urun_id,
                    fiyat=veri["fiyat"],
                    stok_durumu=veri["stok_durumu"],
                    para_birimi=para_birimi
                )
                sonuclar.append({
                    "basarili": True,
                    "urun_adi": hedef["urun_adi"],
                    "platform": hedef.get("platform", "Genel"),
                    "grup_kodu": hedef.get("grup_kodu"),
                    "fiyat": veri["fiyat"],
                    "para_birimi": para_birimi,
                    "hedef_fiyat": hedef.get("hedef_fiyat"),
                    "onceki_fiyat": onceki_fiyat,
                    "stok_durumu": veri["stok_durumu"]
                })

                hedef_fiyat = hedef.get("hedef_fiyat")
                if hedef_fiyat is not None and veri["fiyat"] <= hedef_fiyat:
                    telegram.firsat_bildirimi_gonder(
                        urun_adi=hedef["urun_adi"],
                        yeni_fiyat=veri["fiyat"],
                        hedef_fiyat=hedef_fiyat,
                        para_birimi=para_birimi,
                        url=hedef["url"]
                    )
            else:
                logger.error(f"{hedef['urun_adi']} için hata: {veri['hata']}")
                sonuclar.append({
                    "basarili": False,
                    "urun_adi": hedef["urun_adi"],
                    "hata": veri["hata"]
                })

            # Sunucuyu yormamak için nazik bekleme
            time.sleep(1)

        raporlayici.konsol_ozeti_yazdir(sonuclar)
        raporlayici.excel_raporu_olustur(db)

        # Rakip karşılaştırma matrisi
        karsilastirici = RakipKarsilastirici()
        matris = karsilastirici.matris_olustur(sonuclar)
        
        print("\n--- Rakip Fiyat Karşılaştırma Matrisi ---")
        for satir in matris:
            print(f"Grup: {satir['grup_kodu']} | Avantaj: %{satir['yuzde_avantaj']} | En Ucuz: {satir['en_ucuz_platform']} ({satir['en_dusuk_fiyat']} {satir['para_birimi']})")

        cikti_yolu = Path("cikti/rakip_karsilastirma.json")
        cikti_yolu.parent.mkdir(exist_ok=True)
        with cikti_yolu.open("w", encoding="utf-8") as f:
            json.dump(matris, f, ensure_ascii=False, indent=4)
        HtmlDashboardOlusturucu.dashboard_olustur(db)

        logger.info("Bot başarıyla tamamlandı.")

    except Exception as e:
        logger.critical(f"Beklenmedik bir hata oluştu: {e}", exc_info=True)
    finally:
        db.kapat()


if __name__ == "__main__":
    calistir()
