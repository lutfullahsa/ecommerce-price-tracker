from datetime import datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font


class FiyatRaporlayici:
    def __init__(self, cikti_klasoru="cikti"):
        self.cikti_klasoru = Path(cikti_klasoru)
        self.cikti_klasoru.mkdir(parents=True, exist_ok=True)

    def konsol_ozeti_yazdir(self, sonuclar):
        print("\n" + "=" * 65)
        print(f"FİYAT TAKİP ÖZETİ - {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("=" * 65)

        for s in sonuclar:
            if not s.get("basarili"):
                print(f"[HATA] {s['urun_adi']} -> {s['hata']}")
                continue

            alarm = ""
            if s.get("hedef_fiyat") and s["fiyat"] <= s["hedef_fiyat"]:
                alarm = f" [FIRSAT! Hedef <= {s['hedef_fiyat']} {s['para_birimi']}]"

            degisim = ""
            if s.get("onceki_fiyat") is not None:
                fark = round(s["fiyat"] - s["onceki_fiyat"], 2)
                if fark < 0:
                    degisim = f" (Düştü: {fark} {s['para_birimi']})"
                elif fark > 0:
                    degisim = f" (Arttı: +{fark} {s['para_birimi']})"
                else:
                    degisim = " (Sabit)"

            print(
                f"- {s['urun_adi']} | {s['fiyat']} {s['para_birimi']} "
                f"| {s['stok_durumu']}{degisim}{alarm}"
            )
        print("=" * 65 + "\n")

    def excel_raporu_olustur(self, veritabani, dosya_adi="fiyat_raporu.xlsx"):
        imlec = veritabani.baglanti.execute("""
            SELECT 
                u.urun_adi,
                u.platform,
                fg.fiyat,
                fg.para_birimi,
                u.hedef_fiyat,
                fg.stok_durumu,
                fg.kontrol_tarihi,
                u.url
            FROM fiyat_gecmisi fg
            JOIN urunler u ON u.id = fg.urun_id
            ORDER BY fg.id DESC
        """)
        satirlar = imlec.fetchall()

        wb = Workbook()
        ws = wb.active
        ws.title = "Fiyat Geçmişi"

        basliklar = [
            "Ürün Adı", "Platform", "Güncel Fiyat", "Para Birimi",
            "Hedef Fiyat", "Stok Durumu", "Kontrol Tarihi", "URL"
        ]
        ws.append(basliklar)
        for hucre in ws[1]:
            hucre.font = Font(bold=True)

        for satir in satirlar:
            ws.append(list(satir))

        hedef_yol = self.cikti_klasoru / dosya_adi
        wb.save(hedef_yol)
        print(f"Excel raporu kaydedildi: {hedef_yol}")
