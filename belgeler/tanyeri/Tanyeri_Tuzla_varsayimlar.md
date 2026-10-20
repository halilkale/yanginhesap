# Tanyeri (Tuzla) — hesapta kullanılan veriler, varsayımlar ve açık sorular

Kaynak: "Mahal listesi" ve "Plan" PDF'leri (kat planları, vaziyet), size iletilen malzeme listesi. Çizim antetindeki firma/proje adı kullanılmadı.

## Plandan alınanlar
| Konu | Değer | Not |
|---|---|---|
| Zemin kat alanı | 882,18 m² | Başlıkla uyumlu (yalnız doğu kanat, eksen 6–10) |
| 1. kat alanı | 2.258 m² | Başlıkla uyumlu (52,85 × 42,40 m grid) |
| 2. kat alanı | 2.240,73 m² | Başlıkta "240,73" yazıyor; ölçüler 52,85 × 42,40 m ≈ 2.241 m² olduğundan 2.240,73 alındı |
| 3. kat alanı | 2.240,73 m² (TAHMİN) | Başlıkta 882,18 yazıyor ama yalnız "Rezerv alan" 1.403,38 m²; 2. katla aynı grid olduğundan eşit alındı — **doğrulayın** |
| En büyük kat alanı | 2.258 m² | 1. kat |
| Toplam kapalı alan | 7.621,64 m² | 3. kat tahminine bağlı |
| Mahaller | Mahal listesindeki tüm odalar | Hol, koridor, WC, merdiven holü kullanıcı yüküne sayılmadı (Madde 31(6)) |

## Kompartıman ↔ mahal eşleştirmesi (sizin malzeme listenize göre) — **doğrulayın**
| Bölüm | Alan | Dayanak |
|---|---|---|
| Depo alt | 974,18 m² (1. kat, depo) | 111 Depo |
| Enjeksiyon | 822,67 m² (1. kat) | Planda enjeksiyon makineleri 107 Kalıp deposu alanında |
| Boyahane | 160 m² (2. kat) | 219 Boyahane |
| Serigrafi | 162 m² (2. kat) | 218 (Tampon/Serigrafi) |
| Montaj | 218,26 m² (2. kat) | 215 Montaj |
| Depo üst | 1.403,38 m² (3. kat, depo) | 310 Rezerv alan — **kompartıman bölünmüşse alanı değişir** |

## Yangın yükü kabulleri (yönetmelikte ısıl değer tablosu yoktur)
* Dolu koli ve kasalardaki mamül/yarı mamül **tamamen plastik (PE/PP, 43 MJ/kg)** kabul edildi (ambalaj payı ayrılmadı: güvenli taraf).
* Ahşap palet 17,5; karton/boş koli 17; **solvent bazlı sıvı boya 25 MJ/kg (varsayım — MSDS ile değiştirin)**.
* q = Σ(kütle × ısıl değer) ÷ alan. Verilen miktarlar çok küçük (ör. Depo üstte 1,25 ton / 1.403 m²); bunlar **azami stok** değilse yangın yükü gerçekte çok daha yüksek olur.

## Varsayılan (bilgi verilmeyen) girdiler
Sprinkler: yok · algılama: yok · duman tahliye: yok · hidrant ve dolap: var (planda "yangın pompası" yazıyor) · taşıyıcı: betonarme · yapı/bina yüksekliği: 13 m (tahmini) · bodrum: yok · çıkış sayıları/genişlikleri/mesafeler: girilmedi (VERİ GİRİLMEDİ) · tehlike sınıfı: OT-3 (plastik eşya, boyama, baskı — Ek-1/B).

## Açık sorular
1. 3. katın doğru alanı? (2. katla aynı mı, kaç m²?)
2. Kompartıman çalışmasında Depo üst gerçekte hangi alan ve kaç m²? (1.403 m² tek kompartıman mı, bölünmüş mü?)
3. Binada sprinkler, yangın algılama ve duman tahliye sistemi var mı / projelendirildi mi? (Madde 96(2)e: kolay alevlenici madde + 1.000 m² üzeri → sprinkler zorunlu; Ek-4: depoda kontrol sistemi yoksa kompartıman ≤ 1.000 m²)
4. Verilen kg değerleri azami stok mu, anlık mevcut mu? Plastik mamülün cinsi (PP/PE/ABS…) ve sıvı boyanın MSDS ısıl değeri?
5. Bina yüksekliği (saçak kotu) ve itfaiye yaklaşma kotu (planda +0,00 ve +4,50 var); bodrum kat var mı?
6. Kaçış: çıkış kapısı/merdiven sayıları ve genişlikleri, en uzak kaçış mesafeleri.
