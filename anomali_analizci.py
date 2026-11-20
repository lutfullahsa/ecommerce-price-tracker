import json
from datetime import datetime, timedelta
from pathlib import Path


class FiyatAnomaliAnalizci:
    def __init__(self, veritabani, gun_araligi=30):
        self.db = veritabani
        self.gun_araligi = gun_araligi

    def analiz_et(self) -> list[dict]:
        sinir_tarih = (datetime.now() - timedelta(days=self.gun_araligi)).isoformat()
        urunler = self.db.baglanti.execute(
            "SELECT id, urun_adi, platform, hedef_fiyat FROM urunler WHERE aktif_mi = 1"
        ).fetchall()

        rapor = []
        for urun_id, urun_adi, platform, hedef_fiyat in urunler:
            gecmis = self.db.baglanti.execute(
                """
                SELECT fiyat, para_birimi, kontrol_tarihi
                FROM fiyat_gecmisi
                WHERE urun_id = ? AND kontrol_tarihi >= ?
                ORDER BY id ASC
                """,
                (urun_id, sinir_tarih),
            ).fetchall()

            if not gecmis:
                continue

            fiyatlar = [row[0] for row in gecmis]
            para_birimi = gecmis[-1][1]
            guncel_fiyat = fiyatlar[-1]
            dip_fiyat = min(fiyatlar)
            zirve_fiyat = max(fiyatlar)
            ortalama_fiyat = round(sum(fiyatlar) / len(fiyatlar), 2)

            durum = "Normal Piyasa Seyri"
            sahte_indirim = False

            if len(fiyatlar) >= 3:
                onceki_fiyat = fiyatlar[-2]
                ondan_onceki = fiyatlar[-3]
                if onceki_fiyat > ondan_onceki * 1.10 and guncel_fiyat < onceki_fiyat and guncel_fiyat >= ondan_onceki:
                    durum = "SAHTE İNDİRİM UYARISI (Önce Şişirilmiş)"
                    sahte_indirim = True

            if not sahte_indirim:
                if guncel_fiyat <= dip_fiyat and len(fiyatlar) > 1:
                    durum = f"GERÇEK FIRSAT (Son {self.gun_araligi} Günün Dip Fiyatı)"
                elif guncel_fiyat > ortalama_fiyat * 1.15:
                    durum = "Piyasa Ortalamasının Üzerinde"

            rapor.append({
                "urun_adi": urun_adi,
                "platform": platform,
                "guncel_fiyat": guncel_fiyat,
                "dip_fiyat": dip_fiyat,
                "zirve_fiyat": zirve_fiyat,
                "ortalama_fiyat": ortalama_fiyat,
                "para_birimi": para_birimi,
                "sahte_indirim": sahte_indirim,
                "durum": durum,
            })

        return rapor

    def raporu_kaydet_ve_yazdir(self, cikti_yolu="cikti/anomali_raporu.json") -> list[dict]:
        rapor = self.analiz_et()
        print(f"\n--- Son {self.gun_araligi} Gün Fiyat Anomali & Sahte İndirim Analizi ---")
        for r in rapor:
            print(
                f"- {r['urun_adi']} ({r['platform']}) | Güncel: {r['guncel_fiyat']} | "
                f"Dip: {r['dip_fiyat']} | Ort: {r['ortalama_fiyat']} {r['para_birimi']} -> {r['durum']}"
            )

        hedef = Path(cikti_yolu)
        hedef.parent.mkdir(parents=True, exist_ok=True)
        with hedef.open("w", encoding="utf-8") as f:
            json.dump(rapor, f, ensure_ascii=False, indent=4)
        return rapor
