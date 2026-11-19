import html
import json
from pathlib import Path


class HtmlDashboardOlusturucu:
    @staticmethod
    def dashboard_olustur(veritabani, cikti_yolu="cikti/dashboard.html", matris_yolu="cikti/rakip_karsilastirma.json"):
        products = veritabani.baglanti.execute("SELECT id, urun_adi FROM urunler").fetchall()
        urun_verileri = []
        toplam_fiyat_sayisi = 0
        tum_tarihler = set()

        for p_id, name in products:
            history = veritabani.baglanti.execute(
                "SELECT fiyat, kontrol_tarihi FROM fiyat_gecmisi WHERE urun_id = ? ORDER BY kontrol_tarihi ASC",
                (p_id,)
            ).fetchall()
            fiyat_haritasi = {}
            for fiyat, tarih_str in history:
                gun = tarih_str[:10]
                tum_tarihler.add(gun)
                fiyat_haritasi[gun] = fiyat

            urun_verileri.append({
                "urun_adi": name,
                "fiyat_haritasi": fiyat_haritasi
            })
            toplam_fiyat_sayisi += len(history)

        sirali_tarihler = sorted(tum_tarihler)
        grafik_veri_setleri = [
            {
                "label": u["urun_adi"],
                "data": [u["fiyat_haritasi"].get(t, None) for t in sirali_tarihler],
                "tension": 0.25,
                "spanGaps": True
            }
            for u in urun_verileri
        ]

        matris = []
        max_tasarruf = 0.0
        matris_yol = Path(matris_yolu)
        if matris_yol.exists():
            with matris_yol.open("r", encoding="utf-8") as f:
                matris = json.load(f)
                if matris:
                    max_tasarruf = max(float(m.get("yuzde_avantaj", 0)) for m in matris)

        tablo_satirlari = "".join(
            f"<tr><td>{html.escape(str(m.get('grup_kodu', '-')))}</td>"
            f"<td>%{float(m.get('yuzde_avantaj', 0)):.2f}</td>"
            f"<td>{html.escape(str(m.get('en_ucuz_platform', '-')))}</td>"
            f"<td>{m.get('en_dusuk_fiyat', '-')} {html.escape(str(m.get('para_birimi', 'TRY')))}</td></tr>"
            for m in matris
        ) or "<tr><td colspan='4'>Henüz rakip karşılaştırma verisi bulunmuyor.</td></tr>"

        html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fiyat Takip Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f6f9; color: #1f2937; padding: 24px; max-width: 1100px; margin: auto; }}
        .kpi-container {{ display: flex; gap: 20px; margin-bottom: 24px; flex-wrap: wrap; }}
        .kpi-card {{ background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); flex: 1; min-width: 200px; text-align: center; }}
        .kpi-card h3 {{ margin: 0 0 8px; font-size: 14px; color: #6b7280; }}
        .kpi-card p {{ margin: 0; font-size: 26px; font-weight: 700; color: #111827; }}
        .chart-container {{ background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); margin-bottom: 24px; }}
        table {{ width: 100%; border-collapse: collapse; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }}
        th, td {{ padding: 12px 16px; border-bottom: 1px solid #e5e7eb; text-align: left; }}
        th {{ background: #f9fafb; font-weight: 600; }}
    </style>
</head>
<body>
    <h1>E-Ticaret Fiyat Takip Dashboard</h1>
    <div class="kpi-container">
        <div class="kpi-card"><h3>Takip Edilen Ürün</h3><p>{len(products)}</p></div>
        <div class="kpi-card"><h3>Toplam Fiyat Ölçümü</h3><p>{toplam_fiyat_sayisi}</p></div>
        <div class="kpi-card"><h3>En Yüksek Rakip Avantajı</h3><p>%{max_tasarruf:.2f}</p></div>
    </div>
    <div class="chart-container"><canvas id="priceChart"></canvas></div>
    
    <h2>Rakip Fiyat Karşılaştırma Matrisi</h2>
    <table>
        <thead><tr><th>Grup Kodu</th><th>Fiyat Avantajı</th><th>En Ucuz Satıcı</th><th>En Düşük Fiyat</th></tr></thead>
        <tbody>{tablo_satirlari}</tbody>
    </table>

    <script>
        const ctx = document.getElementById('priceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(sirali_tarihler, ensure_ascii=False)},
                datasets: {json.dumps(grafik_veri_setleri, ensure_ascii=False)}
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ position: 'top' }} }}
            }}
        }});
    </script>
</body>
</html>"""

        Path(cikti_yolu).parent.mkdir(parents=True, exist_ok=True)
        with open(cikti_yolu, "w", encoding="utf-8") as f:
            f.write(html_content)
