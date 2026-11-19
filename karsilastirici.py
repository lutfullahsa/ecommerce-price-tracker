import json
from pathlib import Path

class RakipKarsilastirici:
    def matris_olustur(self, sonuclar):
        gruplar = {}
        
        # Gruplandırma
        for sonuc in sonuclar:
            if not sonuc.get("basarili", False):
                continue
            
            grup_kodu = sonuc.get("grup_kodu") or sonuc.get("urun_adi")
            
            if grup_kodu not in gruplar:
                gruplar[grup_kodu] = []
            
            gruplar[grup_kodu].append(sonuc)
            
        matris = []
        for grup_kodu, urunler in gruplar.items():
            # Başarılı ürünleri fiyata göre sırala
            urunler.sort(key=lambda x: x["fiyat"])
            
            fiyatlar = [u["fiyat"] for u in urunler]
            en_dusuk_fiyat = fiyatlar[0]
            en_yuksek_fiyat = fiyatlar[-1]
            en_ucuz_platform = urunler[0].get("platform", "Bilinmiyor")
            
            # Yüzde avantaj hesaplama
            if len(urunler) > 1 and fiyatlar[1] > 0:
                ikinci_fiyat = fiyatlar[1]
                yuzde_avantaj = round(((ikinci_fiyat - en_dusuk_fiyat) / ikinci_fiyat) * 100, 2)
            else:
                yuzde_avantaj = 0.0
                
            matris.append({
                "grup_kodu": grup_kodu,
                "urun_sayisi": len(urunler),
                "en_ucuz_platform": en_ucuz_platform,
                "en_dusuk_fiyat": en_dusuk_fiyat,
                "en_yuksek_fiyat": en_yuksek_fiyat,
                "para_birimi": urunler[0].get("para_birimi", "TRY"),
                "yuzde_avantaj": yuzde_avantaj
            })
            
        return matris
