# OECD Real Wage Erosion (Minimal)

Minimal pipeline to compute monthly real wage erosion metrics for OECD-style wage and CPI data with optional institutional merge.

Bu “minimal” sürüm şunları yapar:
1. Ücret ve CPI verisini okur (All-matched-datas.xlsx).
2. Seçilen kontrat ayına göre CPI’yı tekrar bazlar (o ay = 1).
3. Reel ücreti ve erosion_gap (1 - real_wage) hesaplar.
4. İsteğe bağlı: 12 aylık enflasyon volatilitesi ekler.
5. Kurumsal veri (Raw-ICTWSS.xlsx) ile (ülke + yıl) birleşimi dener.
6. Ülke–yıl bazında metrikler: mean_erosion, peak_erosion, months_to_recovery.

## Girdi Dosyaları
Kök dizinde (veya data/raw/) bulunmalı:
- All-matched-datas.xlsx
- Raw-ICTWSS.xlsx
- Research Design Paper.docx
- codebook-oecd-aias-ictwss.pdf

İsteğe bağlı dizin düzeni:
```
data/
  raw/
    All-matched-datas.xlsx
    Raw-ICTWSS.xlsx
```
Kod önce köke, sonra data/raw altına bakar.

## Beklenen Ana Sütunlar (Ücret–CPI)
| Sütun | Açıklama | Zorunlu |
|-------|----------|---------|
| Country | 3 harf ülke kodu | Evet |
| Date | YYYY-MM-01 | Evet |
| CPI_2015_100 | Fiyat endeksi | Evet |
| MonthlyWage | Aylık nominal ücret | Evet |
| AnnualWage | Ek (opsiyonel) | Hayır |
| Reference area | Ülke adı | Hayır |

## Kurumsal Veri (Raw-ICTWSS.xlsx) Olası Sütunlar
| Sütun | Anlam |
|-------|-------|
| country | Ülke kodu/adı |
| year | Yıl |
| union_density | Sendikalaşma oranı |
| coordination | Koordinasyon endeksi |
| bargaining_coverage | Kapsam |

Kod bulamazsa sütunları ekrana yazar.

## Kurulum
```
pip install -r requirements.txt
```

## Çalıştırma
```
python src/run_minimal.py --contract-month 1
python src/add_institutions.py
python src/simple_metrics.py
```

## Çıktılar
- output/processed_minimal.csv
- output/processed_with_inst.csv
- output/erosion_metrics.csv

## Kısa Kavramlar
- Rebase CPI: Kontrat ayındaki CPI=1, sonrası / base.
- Real wage: MonthlyWage / cpi_rebased
- Erosion gap: 1 - real_wage (pozitif => kayıp)
- volatility_12m: 12 aylık hareketli std (yıllık enflasyon)
- Recovery: Erosion gap ≤ 0 olan ilk ay.

## Sorun Giderme
| Problem | Çözüm |
|---------|-------|
| Tarihler NaT | Date formatını kontrol et (YYYY-MM-01). |
| Eksik sütun uyarısı | Excel başlıklarını harf duyarlılığıyla doğrula. |
| Kurumsal eşleşme boş | Ülke kodlarını senkronize et (USA vs United States). |
| Boş cpi_rebased başları | Kontrat ayı veride erken dönemde yok olabilir. |

## Genişletme Önerileri
- Otomatik kontrat ayı döngüsü (1,4,7)
- Panel regresyon (ülke & yıl FE)
- Erosion heatmap
- Otomatik rapor (nbconvert / md)

## Lisans
MIT (LICENSE dosyası).

---
Mutlu analizler! :)