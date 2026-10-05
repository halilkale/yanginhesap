"""Binaların Yangından Korunması Hakkında Yönetmelik — hesap modülleri.

Her modül `Girdi` alır, `Sonuc` listesi döndürür. Madde numaraları yönetmelik
metnindeki (20/11/2021 tarihli 4825 sayılı CK ile değişik) numaralardır.
"""
from __future__ import annotations

import math
from typing import Callable

from . import tablolar as T
from .modeller import (
    BILGI, GEREKLI, GEREKMEZ, KONTROL, KOSULLU, UYGUN, UYGUN_DEGIL, Girdi, Sonuc,
)

SQRT2 = math.sqrt(2)


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------
def _r(x: float, n: int = 2) -> float:
    return round(float(x), n)


def kapsama_adedi(boy: float, en: float, yaricap: float) -> int:
    """Her noktası bir cihaza en çok `yaricap` uzaklıkta olacak şekilde dikdörtgen
    alanı kareler ile kaplayan en az cihaz adedi (kare kenarı = yaricap*√2)."""
    if boy <= 0 or en <= 0 or yaricap <= 0:
        return 0
    a = yaricap * SQRT2
    return max(1, math.ceil(boy / a - 1e-9)) * max(1, math.ceil(en / a - 1e-9))


def aralik_adedi(boy: float, en: float, aralik: float) -> int:
    """Cihazlar arası uzaklık en çok `aralik` olacak şekilde ızgara adedi."""
    if boy <= 0 or en <= 0 or aralik <= 0:
        return 0
    return max(1, math.ceil(boy / aralik - 1e-9)) * max(1, math.ceil(en / aralik - 1e-9))


def _yuksek_bina(g: Girdi) -> bool:
    """Madde 4(ccc): bina yüksekliği > 21,50 m veya yapı yüksekliği > 30,50 m."""
    return g.bina_yuksekligi > 21.50 or g.yapi_yuksekligi > 30.50


def _tehlike_ad(g: Girdi) -> str:
    return T.TEHLIKE_SINIFLARI[g.tehlike]


def _konut_degil(g: Girdi) -> bool:
    return g.kullanim != "apartman"


def _tesis_toplam_taban(g: Girdi) -> float:
    return g.tesis_toplam_taban_alani or g.taban_alani


def _karsilastir(deger: float, limit: float, ust: bool = True) -> str:
    """ust=True -> deger <= limit uygun; ust=False -> deger >= limit uygun."""
    ok = deger <= limit + 1e-9 if ust else deger >= limit - 1e-9
    return UYGUN if ok else UYGUN_DEGIL


# ---------------------------------------------------------------------------
# 1. Sınıflandırma (Madde 8, 14, 18, 19, Ek-1)
# ---------------------------------------------------------------------------
def siniflandirma(g: Girdi) -> list[Sonuc]:
    B = "1. Sınıflandırma"
    s: list[Sonuc] = []
    s.append(Sonuc(B, "Kullanım sınıfı", T.KULLANIM_SINIFLARI[g.kullanim], "", BILGI, "Madde 8, 14"))
    s.append(Sonuc(B, "Tehlike sınıfı", _tehlike_ad(g), "", BILGI, "Madde 19, Ek-1",
                   "Boyama işlemi vb. yüksek yangın yükü olan Orta Tehlike-1/2 alanlar Orta Tehlike-3 sayılır (Ek-1/B dipnotu)."))
    grup = T.tehlike_grubu(g.tehlike)
    s.append(Sonuc(B, "Su deposu / pompa tasarım süresi", T.SU_SURESI_DK[grup], "dk", BILGI, "Madde 92(3)",
                   "Düşük 30 dk, orta 60 dk, yüksek 90 dk. Binada farklı tehlike sınıfları varsa en yükseği esas alınır (Madde 19(1))."))
    yb = _yuksek_bina(g)
    s.append(Sonuc(B, "Yüksek bina mı?", "Evet" if yb else "Hayır", "", BILGI, "Madde 4(ccc)",
                   f"Bina yüksekliği {g.bina_yuksekligi:g} m (sınır 21,50 m), yapı yüksekliği {g.yapi_yuksekligi:g} m (sınır 30,50 m)."))
    if g.kullanim == "yuksek_tehlikeli" or g.tehlike.startswith("YT"):
        s.append(Sonuc(B, "Yüksek tehlikeli alan", "Evet", "", BILGI, "Madde 17, 19(2)c",
                       "Parlayıcı/patlayıcı madde ve akaryakıt işlenen yerlerde Sekizinci Kısım (Madde 101–123) hükümleri de uygulanır."))
    if g.karisik_kullanim:
        s.append(Sonuc(B, "Karışık kullanım", "Evet", "", KOSULLU, "Madde 18",
                       "Bölümler yüksek tehlike sınıfına uygun yangın bölmesiyle ayrılamıyorsa, daha yüksek koruma isteyen sınıfın kuralları tüm binaya uygulanır."))
    if g.toplam_kapali_alan > 10000:
        s.append(Sonuc(B, "Yangın tahliye projesi", "Gerekli", "", GEREKLI, "Madde 7(4)",
                       "Toplam kapalı alan 10 000 m²'den büyük imalathane/atölye/depo: tahliye projesi bina girişinde ve itfaiyenin ulaşabileceği yerde bulundurulur."))
    else:
        s.append(Sonuc(B, "Yangın tahliye projesi", "Zorunlu değil", "", GEREKMEZ, "Madde 7(4)",
                       f"Toplam kapalı alan {g.toplam_kapali_alan:,.0f} m² ≤ 10 000 m²."))
    if g.kullanim in ("endustriyel", "depo", "yuksek_tehlikeli") and g.toplam_kapali_alan > 2000 and g.orman_yakin:
        s.append(Sonuc(B, "Orman alanı içinde/bitişiğindeki endüstriyel tesis", "İlave tedbirler gerekli", "", GEREKLI,
                       "Madde 7(12), 21(5)", "Toplam kapalı alan 2000 m²'den büyük: dış yangın bölgesi ve ilave tedbirler (Madde 21, 22, 27, 28, 92, 95)."))
    return s


# ---------------------------------------------------------------------------
# 2. Yangın dayanımı (Madde 23, 25, 26, Ek-3/B, Ek-3/C)
# ---------------------------------------------------------------------------
def yangin_dayanimi(g: Girdi) -> list[Sonuc]:
    B = "2. Yangın dayanımı"
    s: list[Sonuc] = []
    anahtar = (g.kullanim, bool(g.yagmurlama_var))
    satir = T.EK3C[anahtar]
    h = g.bina_yuksekligi
    ust_idx = 3 if h <= 21.50 else (4 if h <= 30.50 else 5)
    ust = satir[ust_idx]
    sp = "yağmurlama sistemli" if g.yagmurlama_var else "yağmurlama sistemi yok"
    ek = ""
    if g.kullanim == "yuksek_tehlikeli":
        ek = " Ek-3/C'de yüksek tehlikeli yer satırı yoktur; endüstriyel yapı satırı esas alınmıştır."
    if ust == T.IY:
        s.append(Sonuc(B, "Taşıyıcı sistem / kompartıman yangın dayanımı (üst katlar)", T.IY, "", UYGUN_DEGIL, "Ek-3/C",
                       f"Bina yüksekliği {h:g} m, {sp}: bu yükseklikte yağmurlama sistemi olmadan yapı yapılamaz." + ek))
    else:
        s.append(Sonuc(B, "Taşıyıcı sistem / kompartıman yangın dayanımı (üst katlar)", ust, "dk", BILGI, "Ek-3/C",
                       f"{T.TEHLIKE_SINIFLARI[g.tehlike]}; bina yüksekliği {h:g} m ({T.EK3C_SUTUNLAR[ust_idx]}), {sp}." + ek))
    if g.yagmurlama_var and ust == 120:
        s.append(Sonuc(B, "Taşıyıcı olmayan elemanlar (sprinklerli, > 30,50 m)", 90, "dk", BILGI, "Ek-3/C dipnot (3)",
                       "Taşıyıcı sistemin parçası olmayan elemanlar için 90 dakikaya düşürülebilir."))
    if g.bodrum_kat_sayisi > 0:
        d = g.bodrum_derinligi
        b_idx = 0 if d > 10 else (1 if d > 5 else 2)
        b_val = satir[b_idx]
        s.append(Sonuc(B, "Bodrum katlar yangın dayanımı", b_val, "dk", BILGI, "Ek-3/C",
                       f"Bodrum derinliği {d:g} m ({T.EK3C_SUTUNLAR[b_idx]}). Binaları ayıran kompartıman duvarları için en az 60 dk (dipnot 2)."))
        if isinstance(b_val, (int, float)) and isinstance(ust, (int, float)):
            s.append(Sonuc(B, "Bodrum üstü döşeme yangın dayanımı", max(b_val, ust, 90), "dk", BILGI, "Ek-3/C dipnot (1), Ek-3/B-3d",
                           "Bodrumun üstündeki döşeme, üst katlar için olan süre daha fazlaysa onu sağlamalıdır; bodrum-zemin arası döşeme en az 90 dk veya Ek-3/C (büyük olan)."))
    # Çelik / betonarme / ahşap
    if g.tasiyici == "celik":
        muaf = g.kat_sayisi == 1 and g.taban_alani < 5000
        if muaf:
            s.append(Sonuc(B, "Çelik taşıyıcı yalıtımı", "Gerekmez", "", GEREKMEZ, "Madde 23(4)",
                           "Alanı 5000 m²'den az tek katlı yapı; çevreye yangın yayma tehlikesi olmamalı ve yangın yükü çeliği 540 °C üzerine çıkarmamalıdır."))
        else:
            s.append(Sonuc(B, "Çelik taşıyıcı yalıtımı", "Gerekli", "", GEREKLI, "Madde 23(4)",
                           f"Çelik yapı muaf değil (kat sayısı {g.kat_sayisi}, taban alanı {g.taban_alani:,.0f} m²). Püskürtme sıva, yangına dayanıklı boya, sarma/kutulama veya kütlesel yalıtımla {ust if isinstance(ust,(int,float)) else '—'} dk sağlanmalı."))
    elif g.tasiyici == "betonarme":
        if g.net_beton_kolon_mm or g.net_beton_kiris_mm or g.net_beton_doseme_mm:
            for ad, val, lim in (("Kolon", g.net_beton_kolon_mm, 35), ("Kiriş", g.net_beton_kiris_mm, 25), ("Döşeme", g.net_beton_doseme_mm, 20)):
                if val:
                    s.append(Sonuc(B, f"Net beton paspayı — {ad} (120 dk)", val, "mm", _karsilastir(val, lim, ust=False), "Madde 23(5)",
                                   f"120 dk için en az {lim} mm gerekir."))
        else:
            s.append(Sonuc(B, "Net beton paspayı (120 dk için)", "Kolon ≥ 35, kiriş ≥ 25, döşeme ≥ 20", "mm", KONTROL, "Madde 23(5)",
                           "Gerçek paspayı değerleri girilirse kontrol edilir."))
    elif g.tasiyici == "ahsap" and g.ahsap_b_mm and g.ahsap_h_mm:
        sure = ust if isinstance(ust, (int, float)) else 0
        beta = g.ahsap_yanma_hizi
        kay = beta * sure
        if g.ahsap_yuzey >= 4:
            b2, h2 = g.ahsap_b_mm - 2 * kay, g.ahsap_h_mm - 2 * kay
        else:  # 3 yüzey (kiriş) — üst yüzey korunumlu
            b2, h2 = g.ahsap_b_mm - 2 * kay, g.ahsap_h_mm - kay
        durum = UYGUN if b2 > 0 and h2 > 0 else UYGUN_DEGIL
        s.append(Sonuc(B, "Ahşap eleman — kalan kesit", f"{max(b2,0):.0f} × {max(h2,0):.0f}", "mm", durum, "Madde 23(6)",
                       f"Yanma hızı {beta:g} mm/dk × {sure:g} dk = {kay:.0f} mm kömürleşme. Kalan kesit gerçek yükü güvenlik katsayısı 1,0 ile taşıyabilmelidir (statik hesapla doğrulanmalı)."))
    # Yangın duvarı / diğer
    s.append(Sonuc(B, "Bitişik nizam yangın duvarı", 90, "dk", BILGI, "Madde 25(1)", "Yangın duvarlarında delik/boşluk bulunamaz; kapı vb. boşluklar duvar süresinin yarısı kadar (45 dk) dayanıklı ve kendiliğinden kapanır."))
    s.append(Sonuc(B, "Yüksek bina düşey şaft duvarı / kapağı", "120 / 90", "dk", BILGI if _yuksek_bina(g) else GEREKMEZ, "Madde 25(3)"))
    if _yuksek_bina(g):
        s.append(Sonuc(B, "Üst katlarda kompartıman", "En çok 3 kat / kompartıman", "", GEREKLI, "Madde 24(4)",
                       "Bina yüksekliği 21,50 m'den fazla konut dışı binalarda, bu yükseklikten yukarıdaki katlar en çok üçer kat kompartıman olarak düzenlenir."))
    # Cephe / çatı
    if g.bina_yuksekligi > 28.50:
        s.append(Sonuc(B, "Dış cephe malzemesi", "Zor yanıcı", "", GEREKLI, "Madde 27(1)", "Bina yüksekliği 28,50 m'den fazla: zor yanıcı; diğerlerinde en az zor alevlenici."))
    else:
        s.append(Sonuc(B, "Dış cephe malzemesi", "En az zor alevlenici", "", GEREKLI, "Madde 27(1)",
                       "Katlar arası pencere gibi korumasız boşluklar arasında düşeyde en az 100 cm yangına dayanıklı dolu yüzey (veya sprinklerle korunan cephe)."))
    s.append(Sonuc(B, "Çatı kaplaması", "BROOF sınıfı; altı en az zor alevlenici", "", GEREKLI, "Madde 28(2)"))
    if _yuksek_bina(g):
        s.append(Sonuc(B, "Çatı taşıyıcı sistemi ve kaplaması", "Yanmaz malzeme", "", GEREKLI, "Madde 28(3)"))
    # Ek-3/B tablosu
    for ad, deger, ref in T.EK3B_SABIT:
        s.append(Sonuc(B + " — Yapı elemanları tablosu", ad, deger, "", BILGI, ref))
    return s


# ---------------------------------------------------------------------------
# 3. Yangın kompartımanı (Madde 24, Ek-4)
# ---------------------------------------------------------------------------
def kompartiman(g: Girdi) -> list[Sonuc]:
    B = "3. Yangın kompartımanı"
    s: list[Sonuc] = []
    limit, nota, ack = T.ek4_limit(g.kullanim, g.tehlike)
    alan = g.ozet_alan()
    kontrol_sistemi = g.algilama_var or g.yagmurlama_var or g.duman_tahliye_var
    tek_katli = g.kat_sayisi == 1
    s.append(Sonuc(B, "Tablo sınırı (Ek-4)", "Sınırlama yok" if limit is None else limit, "" if limit is None else "m²", BILGI, "Madde 24(6), Ek-4", ack))
    s.append(Sonuc(B, "Kompartıman alanı (proje)", alan, "m²", BILGI, "Madde 24"))
    if limit is None:
        s.append(Sonuc(B, "Kompartıman alanı kontrolü", "Sınırlama yok", "", UYGUN, "Ek-4"))
        return s
    etkin = limit
    gerekce = f"Tablo sınırı {limit:,.0f} m²."
    sinirsiz = False
    if nota == 1 and kontrol_sistemi:
        etkin = limit * 2
        gerekce += " Uygun yangın kontrol sistemleri var: sınır 2 katına çıkarılabilir (Ek-4 not 1)."
    elif nota == 2 and kontrol_sistemi:
        sinirsiz = True
        gerekce += " Uygun yangın kontrol sistemleri var: kompartıman alanı sınırsız (Ek-4 not 2)."
    elif nota == 3:
        if tek_katli:
            sinirsiz = True
            gerekce += " Bina tek katlı: sınırlama yok (Ek-4 not 3)."
        elif kontrol_sistemi:
            sinirsiz = True
            gerekce += " Uygun yangın kontrol sistemleri var: kompartıman alanı sınırsız (Ek-4 not 3)."
    if sinirsiz:
        s.append(Sonuc(B, "Kompartıman alanı kontrolü", "Sınırsız", "", KOSULLU, "Ek-4",
                       gerekce + " Kılavuz: sayılan sistemlerin tamamı şart değildir; yeterlilik itfaiye biriminin değerlendirmesine bağlıdır."))
    else:
        durum = _karsilastir(alan, etkin)
        s.append(Sonuc(B, "Kompartıman alanı kontrolü", f"{alan:,.0f} / {etkin:,.0f}", "m²", durum, "Ek-4", gerekce))
        if durum == UYGUN_DEGIL:
            n = math.ceil(g.en_buyuk_kat_alani / etkin)
            s.append(Sonuc(B, "Gerekli kompartıman sayısı (kat başına)", n, "adet", GEREKLI, "Ek-4",
                           f"{g.en_buyuk_kat_alani:,.0f} m² / {etkin:,.0f} m² → yangın duvarı/kompartıman ayrımı veya kontrol sistemleri (algılama, yağmurlama, duman tahliye) eklenmeli."))
    if g.tehlike == "DT":
        s.append(Sonuc(B, "Düşük tehlikeli kompartıman (en çok)", 126, "m²", _karsilastir(alan, 126), "Madde 19(2)a",
                       "Düşük tehlikeli yer: en az 30 dk dayanımlı ve tek kompartıman alanı 126 m²'den büyük olmayan yerler."))
    s.append(Sonuc(B, "Kompartıman çevreleyen elemanlar", "REI 60+ (Ek-3/B-6, 7)", "", BILGI, "Madde 4(tt), 24(7)",
                   "Birleşim noktalarında süreklilik sağlanmalı; kompartımanlar arasında yangına dayanıksız açıklık bulunamaz."))
    return s


# ---------------------------------------------------------------------------
# 4. Kullanıcı yükü, çıkış sayısı ve genişlikleri, kaçış uzaklıkları
# ---------------------------------------------------------------------------
CIKIS_TURU_AD = {
    "dis_kapi": ("Dışarı çıkış kapısı", "dis_kapi"),
    "diger_kapi": ("Diğer kapılar ve koridor kapıları", "diger_kapi"),
    "merdiven": ("Kaçış merdiveni", "merdiven"),
    "koridor": ("Rampa ve koridor", "koridor"),
}


def kat_kullanici_yuku(kat) -> float:
    toplam = 0.0
    for m in kat.mahaller:
        if not m.sayilir:
            continue
        n = (m.alan / m.katsayi) if m.katsayi > 0 else 0.0
        if m.kisi_belirli is not None and m.kisi_belirli > 0:
            n = max(n, m.kisi_belirli)
        toplam += n
    return toplam


def kullanici_yuku_ve_kacis(g: Girdi) -> list[Sonuc]:
    B = "4. Kullanıcı yükü ve kaçış yolları"
    s: list[Sonuc] = []
    satir_ad = T.KULLANIM_EK5B[g.kullanim]
    e5 = T.EK5B[satir_ad]
    spr = 1 if g.yagmurlama_var else 0
    toplam_kisi = 0.0
    for kat in g.katlar:
        K = f"{B} — {kat.ad}"
        n = kat_kullanici_yuku(kat)
        toplam_kisi += n
        s.append(Sonuc(K, "Kat kullanıcı yükü", _r(n, 2), "kişi", BILGI, "Madde 32(1), Ek-5/A",
                       "Mahal alanı / kullanıcı yükü katsayısı; kişi sayısı belirli mahallerde hesaplanandan az olmamak üzere belirtilen sayı alınır. "
                       "Tuvalet, soyunma, depo gibi aynı anda kullanılmayan mahaller sayılmayabilir (Madde 31(6))."))
        if n <= 0:
            continue
        # --- gerekli genişlikler (tüm eleman türleri)
        for tur, (ad, anahtar) in CIKIS_TURU_AD.items():
            birim = e5[anahtar]
            w = n / birim * 50.0
            s.append(Sonuc(K, f"Gerekli toplam genişlik — {ad}", _r(w, 2), "cm", BILGI, "Madde 32(2), 33(1), Ek-5/B",
                           f"{n:.2f} kişi / {birim} kişi (birim genişlik 50 cm) × 50 cm."))
        # --- asgari tekil genişlik
        if n > 2000:
            w_min, ack = 200, "2001 ve daha fazla kişi: tek bir kaçış yolu en az 200 cm"
        elif n > 500:
            w_min, ack = 150, "501–2000 kişi: tek bir kaçış yolu en az 150 cm"
        elif n >= 50:
            w_min, ack = 100, "50–500 kişi: tek bir kaçış yolu en az 100 cm"
        else:
            w_min, ack = 80, "50 kişiden az: hiçbir çıkış 80 cm'den dar olamaz"
        if _yuksek_bina(g):
            w_min = max(w_min, 120)
            ack += "; yüksek binalarda en az 120 cm (Madde 33(2))"
        s.append(Sonuc(K, "Asgari tekil çıkış/kaçış yolu genişliği", w_min, "cm", BILGI, "Madde 33(1)-(2)",
                       ack + ". Koridor/hol olarak da kullanılıyorsa en az 110 cm; hiçbir kaçış yolu 80 cm'den dar olamaz."))
        # --- çıkış sayısı
        gerek_sayi = 1
        if (n > 25 and g.tehlike.startswith("YT")) or n > 50:
            gerek_sayi = 2
        gerek_sayi = max(gerek_sayi, 2)  # Madde 39(1): aksi belirtilmedikçe en az 2
        if n > 1000:
            gerek_sayi = max(gerek_sayi, 4)
        elif n > 500:
            gerek_sayi = max(gerek_sayi, 3)
        tek_cikis_istisna = False
        if g.kullanim in ("endustriyel", "depo", "buro", "ticaret"):
            tek_cikis_istisna = (g.yapi_yuksekligi < 21.50 and n < 50 and g.yanmaz_malzeme_yapim and not g.kolay_alevlenici)
            if tek_cikis_istisna and kat.en_uzak_mesafe_m and kat.en_uzak_mesafe_m <= e5["tek"][spr]:
                gerek_sayi = 1
        s.append(Sonuc(K, "Gerekli en az çıkış sayısı", gerek_sayi, "adet", GEREKLI, "Madde 39(1)-(2), 52",
                       ">500 kişi: en az 3; >1000 kişi: en az 4. Fabrika/depo/büroda tek çıkış, ancak yapı yüksekliği <21,50 m, kat kullanıcısı <50, "
                       "en uzak mesafe Ek-5/B'ye uygun, yanmaz malzemeyle yapılmış ve kolay alevlenici/parlayıcı üretim-depolama yok ise yeterlidir (Madde 52)."))
        if kat.cikis_sayisi:
            s.append(Sonuc(K, "Projedeki çıkış sayısı", kat.cikis_sayisi, "adet", _karsilastir(kat.cikis_sayisi, gerek_sayi, ust=False), "Madde 39"))
        # --- seçilen elemanın genişliği
        ad, anahtar = CIKIS_TURU_AD[kat.cikis_turu]
        w_gerek = n / e5[anahtar] * 50.0
        if kat.mevcut_genislik_cm > 0:
            s.append(Sonuc(K, f"Mevcut toplam genişlik — {ad}", kat.mevcut_genislik_cm, "cm",
                           _karsilastir(kat.mevcut_genislik_cm, w_gerek, ust=False), "Madde 33(1)",
                           f"Gerekli {w_gerek:.1f} cm; mevcut {kat.mevcut_genislik_cm:.1f} cm."))
        else:
            s.append(Sonuc(K, f"Mevcut toplam genişlik — {ad}", "—", "cm", KONTROL, "Madde 33(1)", f"Gerekli en az {w_gerek:.1f} cm."))
        if kat.tekil_cikis_genislik_cm > 0:
            s.append(Sonuc(K, "En dar tekil çıkış genişliği", kat.tekil_cikis_genislik_cm, "cm",
                           _karsilastir(kat.tekil_cikis_genislik_cm, w_min, ust=False), "Madde 33(1)", f"Asgari {w_min} cm."))
        if gerek_sayi == 2 or kat.cikis_sayisi == 2:
            yarim = w_gerek / 2
            s.append(Sonuc(K, "İki çıkışlı mekânda her çıkışın en az genişliği", _r(max(yarim, w_min), 1), "cm", BILGI, "Madde 33(4)",
                           "Her bir çıkış toplam kullanıcı yükünün en az yarısını karşılayacak genişlikte olmalıdır."))
        # --- kaçış uzaklığı
        yon = "iki" if kat.yon == "iki" else "tek"
        taban = e5["iki" if yon == "iki" else "tek"][spr]
        carpan = 1.0
        not_ = ""
        if g.kullanim == "endustriyel" and not g.kolay_alevlenici:
            carpan = 2.0 if g.mevcut_yapi else 1.5
            not_ = (" Kolay alevlenici malzeme üretimi yapılmayan endüstriyel yapı: "
                    + ("mevcut yapıda (Ek-14) en çok 2 katına." if g.mevcut_yapi else "Ek-5/B dipnotu: ½ oranında artırılabilir."))
        elif g.kullanim == "depo" and not g.kolay_alevlenici and g.mevcut_yapi:
            carpan = 2.0
            not_ = " Mevcut yapı Ek-14 dipnotu: en çok 2 katına."
        limit = taban * carpan
        s.append(Sonuc(K, f"En çok kaçış uzaklığı ({yon} yön)", _r(limit, 1), "m", BILGI, "Madde 32(3)-(4), Ek-5/B",
                       f"Tablo değeri {taban} m ({'yağmurlama sistemli' if spr else 'yağmurlama sistemi yok'}), çarpan {carpan:g}." + not_))
        if kat.en_uzak_mesafe_m > 0:
            s.append(Sonuc(K, "Ölçülen en uzak kaçış uzaklığı", kat.en_uzak_mesafe_m, "m",
                           _karsilastir(kat.en_uzak_mesafe_m, limit), "Madde 32(3)",
                           "Mekân içinde en uzak nokta, çevreleyen duvarlardan 40 cm önde alınır (Madde 32(6))."))
        if kat.kus_ucusu_mesafe_m > 0:
            lim2 = limit * 2 / 3
            s.append(Sonuc(K, "Kuş uçuşu (direkt) kaçış uzaklığı", kat.kus_ucusu_mesafe_m, "m",
                           _karsilastir(kat.kus_ucusu_mesafe_m, lim2), "Madde 32(5)",
                           f"Alt bölümlere ayrılmış büyük alanlarda direkt uzaklık izin verilen en çok uzaklığın 2/3'ünü (= {lim2:.1f} m) aşmamalıdır."))
        if kat.cikmaz_mesafe_m > 0:
            lim3 = e5["cikmaz"][spr]
            s.append(Sonuc(K, "Çıkmaz koridor uzunluğu", kat.cikmaz_mesafe_m, "m",
                           _karsilastir(kat.cikmaz_mesafe_m, lim3), "Madde 4(i), Ek-5/B", f"En çok {lim3} m."))
        if kat.mekan_diyagonal_m > 0 and kat.cikislar_arasi_mesafe_m > 0:
            oran = 3 if g.yagmurlama_var else 2
            lim4 = kat.mekan_diyagonal_m / oran
            s.append(Sonuc(K, "Çıkışlar arası mesafe", kat.cikislar_arasi_mesafe_m, "m",
                           _karsilastir(kat.cikislar_arasi_mesafe_m, lim4, ust=False), "Madde 39(3)",
                           f"Bölünmemiş tek mekânda 2 çıkış: en az diyagonalin {'1/3' if oran==3 else '1/2'}'i = {lim4:.1f} m."))
    if len(g.katlar) > 0:
        s.append(Sonuc(B, "Toplam kullanıcı yükü (tüm katlar)", _r(toplam_kisi, 1), "kişi", BILGI, "Madde 32"))
    return s


def merdiven_kapi(g: Girdi) -> list[Sonuc]:
    B = "5. Kaçış merdivenleri ve kapılar"
    s: list[Sonuc] = []
    for m in g.merdivenler:
        K = f"{B} — {m.ad}"
        if m.genislik_cm:
            w_min = 120 if _yuksek_bina(g) else 80
            s.append(Sonuc(K, "Merdiven temiz genişliği", m.genislik_cm, "cm", _karsilastir(m.genislik_cm, w_min, ust=False), "Madde 33(1)-(2)",
                           "Temiz genişlik: küpeştenin çıkıntısının 80 mm'si dâhil. 200 cm'yi aşan merdivenler 100–160 cm'lik parçalara bölünür (Madde 33(3))."))
        if m.rihts_mm:
            s.append(Sonuc(K, "Basamak yüksekliği (rıht)", m.rihts_mm, "mm", _karsilastir(m.rihts_mm, 175), "Madde 41(7)", "En çok 175 mm."))
        if m.basamak_genislik_mm:
            s.append(Sonuc(K, "Basamak genişliği (basış)", m.basamak_genislik_mm, "mm", _karsilastir(m.basamak_genislik_mm, 250, ust=False), "Madde 41(7)", "En az 250 mm."))
        if m.sahanlik_arasi_basamak:
            ok = 4 <= m.sahanlik_arasi_basamak <= 17
            s.append(Sonuc(K, "Sahanlıklar arası basamak sayısı", m.sahanlik_arasi_basamak, "adet", UYGUN if ok else UYGUN_DEGIL, "Madde 41(3)", "En az 4, en çok 17 basamak."))
        if m.sahanlik_arasi_kot_cm:
            s.append(Sonuc(K, "Sahanlıklar arası kot farkı", m.sahanlik_arasi_kot_cm, "cm", _karsilastir(m.sahanlik_arasi_kot_cm, 300), "Madde 41(6)", "En çok 300 cm."))
        if m.bas_yuksekligi_cm:
            s.append(Sonuc(K, "Baş kurtarma yüksekliği", m.bas_yuksekligi_cm, "cm", _karsilastir(m.bas_yuksekligi_cm, 210, ust=False), "Madde 41(6)", "En az 210 cm."))
        if m.dengelenmis:
            yasak = g.bina_yuksekligi > 15.50 or m.kullanici_sayisi_kat > 100
            s.append(Sonuc(K, "Dengelenmiş (kova) merdiven", "Kullanılıyor", "", UYGUN_DEGIL if yasak else UYGUN, "Madde 41(3)",
                           "Bina yüksekliği 15,50 m'den veya kattaki kullanıcı sayısı 100 kişiden fazla ise dengelenmiş kaçış merdivenine izin verilmez. Kova hattında en dar basamak genişliği ≥125 mm (Madde 41(8))."))
        kapi_gerek = 90 if (g.bodrum_kat_sayisi > 0 or m.hizmet_verilen_kat >= 4) else 60
        if m.kapi_dayanim_dk:
            s.append(Sonuc(K, "Merdiven kapısı yangın dayanımı", m.kapi_dayanim_dk, "dk", _karsilastir(m.kapi_dayanim_dk, kapi_gerek, ust=False), "Madde 47(3)",
                           f"{m.hizmet_verilen_kat} kata hizmet veriyor: en az {kapi_gerek} dk, duman sızdırmaz, kendiliğinden kapanır."))
        else:
            s.append(Sonuc(K, "Merdiven kapısı yangın dayanımı", "—", "dk", KONTROL, "Madde 47(3)", f"En az {kapi_gerek} dk gerekir."))
        if m.duvar_dayanim_dk:
            s.append(Sonuc(K, "Merdiven yuvası duvar dayanımı", m.duvar_dayanim_dk, "dk", _karsilastir(m.duvar_dayanim_dk, 120, ust=False), "Madde 38(3), Ek-3/B-9a", "En az 120 dk; yuvada yanıcı malzeme kullanılamaz."))
    if not g.merdivenler:
        s.append(Sonuc(B, "Kaçış merdiveni", "Girdi yok", "", KONTROL, "Madde 38–46",
                       "Rıht ≤175 mm, basış ≥250 mm, sahanlık ≤17 basamak, kot farkı ≤300 cm, baş yüksekliği ≥210 cm, duvar 120 dk, kapı 60/90 dk."))
    for k in g.kapilar:
        K = f"{B} — Kapı {k.ad}"
        if k.temiz_genislik_cm:
            hi = 120 if k.kanat_sayisi == 1 else 1e9
            ok = k.temiz_genislik_cm >= 80 and k.temiz_genislik_cm <= hi
            s.append(Sonuc(K, "Temiz genişlik", k.temiz_genislik_cm, "cm", UYGUN if ok else UYGUN_DEGIL, "Madde 33(5), 47(1),(4)",
                           "Tek kanatlı çıkış kapısında 80–120 cm; kaçış yolu kapıları en az 80 cm."))
        if k.yukseklik_cm:
            s.append(Sonuc(K, "Yükseklik", k.yukseklik_cm, "cm", _karsilastir(k.yukseklik_cm, 200, ust=False), "Madde 47(1)", "En az 200 cm; eşik olmamalı."))
        if k.esik_var:
            s.append(Sonuc(K, "Eşik", "Var", "", UYGUN_DEGIL, "Madde 47(1)", "Kaçış yolu kapılarında eşik olmamalıdır."))
        if k.kisi_yuku > 50:
            s.append(Sonuc(K, "Açılış yönü", "Kaçış yönüne" if k.kacis_yonune_aciliyor else "Kaçış yönüne değil",
                           "", UYGUN if k.kacis_yonune_aciliyor else UYGUN_DEGIL, "Madde 47(2)", "Kullanıcı yükü 50 kişiyi aşan mekânlarda kaçış yönüne açılmalı."))
        if k.acma_kuvveti_N:
            s.append(Sonuc(K, "Açma kuvveti", k.acma_kuvveti_N, "N", _karsilastir(k.acma_kuvveti_N, 110), "Madde 47(6)", "En çok 110 N."))
    return s


# ---------------------------------------------------------------------------
# 6. Sprinkler, su deposu, pompa
# ---------------------------------------------------------------------------
def sprinkler_zorunlulugu(g: Girdi) -> list[Sonuc]:
    B = "6. Yağmurlama (sprinkler) sistemi"
    s: list[Sonuc] = []
    nedenler = []
    if _konut_degil(g) and g.yapi_yuksekligi > 30.50:
        nedenler.append("Yapı yüksekliği 30,50 m'den fazla (Madde 96(2)a)")
    if g.otopark_alani > 600:
        nedenler.append(f"Kapalı otopark toplam alanı {g.otopark_alani:,.0f} m² > 600 m² (Madde 96(2)c)")
    if g.kolay_alevlenici and g.toplam_kapali_alan > 1000:
        nedenler.append(f"Kolay alevlenici/parlayıcı madde üretilen veya bulundurulan yapı, alan {g.toplam_kapali_alan:,.0f} m² > 1000 m² (Madde 96(2)e)")
    if g.kullanim == "ticaret" and g.toplam_kapali_alan > 2000:
        nedenler.append("Katlı mağaza/ticaret toplam alanı > 2000 m² (Madde 96(2)d)")
    if nedenler:
        s.append(Sonuc(B, "Otomatik yağmurlama sistemi", "Mecburi", "", GEREKLI if not g.yagmurlama_var else UYGUN, "Madde 96(2)", "; ".join(nedenler)))
        if not g.yagmurlama_var:
            s[-1].durum = UYGUN_DEGIL
            s[-1].aciklama += ". Projede yağmurlama sistemi yok."
    else:
        s.append(Sonuc(B, "Otomatik yağmurlama sistemi", "Madde 96(2) kapsamında zorunlu değil", "", GEREKMEZ, "Madde 96(2)",
                       "Zorunlu olmasa da kompartıman alanı (Ek-4), kaçış uzaklığı (Ek-5/B), yangın dayanımı (Ek-3/C) ve kaçış mesafeleri sprinkler varlığında avantaj sağlar; ayrıca itfaiye görüşü gerekebilir."))
    if g.kullanim in ("endustriyel", "depo") and g.tehlike.startswith("YT") and not g.yagmurlama_var:
        s.append(Sonuc(B, "Yüksek tehlikeli alan sprinkler/sabit söndürme", "Değerlendirilmeli", "", KOSULLU, "Madde 96, 98",
                       "Su ile reaksiyona giren maddeler varsa yağmurlama yapılmaz (Madde 96(4)); uygun gazlı/köpüklü/kuru tozlu sabit sistem (Madde 98)."))
    # Baş sayısı
    grup = g.tehlike
    if g.spr_baslik_alani_m2 > 0:
        bas_alani = g.spr_baslik_alani_m2
        kaynak = "kullanıcı girdisi"
    elif grup in ("DT", "OT1"):
        bas_alani, kaynak = 21.0, "Madde 96(5): Düşük ve Orta Tehlike-1'de standart başlık en çok 21 m²"
    elif grup.startswith("OT"):
        bas_alani, kaynak = 12.0, "TS EN 12845 (Madde 96(5) atfı) tipik azami 12 m² — yönetmelikte sayısal değer yoktur"
    else:
        bas_alani, kaynak = 9.0, "TS EN 12845 (Madde 96(5) atfı) tipik azami 9 m² — yönetmelikte sayısal değer yoktur"
    korunan = g.toplam_kapali_alan if g.yagmurlama_var else 0
    if korunan > 0:
        adet = math.ceil(korunan / bas_alani)
        s.append(Sonuc(B, "Başlık başına koruma alanı", bas_alani, "m²", BILGI, "Madde 96(5)", kaynak))
        s.append(Sonuc(B, "Yaklaşık yağmurlama başlığı adedi", adet, "adet", BILGI, "Madde 96(5)",
                       f"{korunan:,.0f} m² / {bas_alani:g} m² (ön hesap; kesin adet TS EN 12845'e göre yerleşim projesiyle belirlenir)."))
        s.append(Sonuc(B, "Yedek başlık", max(6, math.ceil(adet * 0.01)), "adet", GEREKLI, "Madde 96(8)", "Sistemin büyüklüğüne göre yeterli sayıda, en az 6 adet yedek başlık ve değiştirme anahtarı."))
    return s


def _spr_debi(g: Girdi):
    """(yoğunluk mm/dk, koruma alanı m², debi l/dk, açıklama) veya None (yoğun su/hidrolik)."""
    kod = g.tehlike
    kuru = g.yagmurlama_tipi == "kuru"
    kullanilan = kod
    notlar = []
    if kuru:
        if kod == "DT":
            kullanilan = "OT1"
            notlar.append("Düşük Tehlike kuru/değişken sistemde Orta Tehlike-1 kullanılır")
        elif kod == "OT4":
            kullanilan = "YT1"
            notlar.append("Orta Tehlike-4 kuru/değişken sistemde Yüksek Tehlike-1 kullanılır")
    yog, ia, ik = T.EK8B[kullanilan]
    if yog is None:
        return None
    alan = ik if kuru else ia
    if g.spr_koruma_alani_m2 > 0:
        alan = g.spr_koruma_alani_m2
        notlar.append("koruma alanı kullanıcı tarafından belirlenmiş (hidrolik tasarım)")
    return yog, alan, yog * alan, "; ".join(notlar), kullanilan


def su_deposu_ve_pompa(g: Girdi) -> list[Sonuc]:
    B = "7. Yangın suyu deposu ve pompa"
    s: list[Sonuc] = []
    grup = T.tehlike_grubu(g.tehlike)
    sure = T.SU_SURESI_DK[grup]
    dolap_d, hid_d, ek8c_sure = T.EK8C[T.ek8c_anahtar(g.tehlike)]
    q_spr = 0.0
    spr_aciklama = ""
    if g.yagmurlama_var:
        r = _spr_debi(g)
        if r is None:
            s.append(Sonuc(B, "Yağmurlama debisi", "Hidrolik hesap", "", KONTROL, "Ek-8/B", "Yüksek Tehlike-4: yoğun su; hidrolik hesap gerekir (debi kullanıcı tarafından hesaplanıp koruma alanı/yoğunluk girilmelidir)."))
        else:
            yog, alan, q_spr, nt, kul = r
            spr_aciklama = f"{yog:g} mm/dk × {alan:g} m² = {q_spr:,.0f} l/dk" + (f" ({nt})" if nt else "")
            s.append(Sonuc(B, "Yağmurlama sistemi tasarım yoğunluğu", yog, "mm/dk", BILGI, "Ek-8/B", f"{T.TEHLIKE_SINIFLARI[kul]}"))
            s.append(Sonuc(B, "Yağmurlama koruma alanı", alan, "m²", BILGI, "Ek-8/B", "Islak/ön etkili sistemde ıslak sütun; kuru/değişken sistemde kuru sütun değeri."))
            s.append(Sonuc(B, "Yağmurlama debisi", _r(q_spr, 1), "l/dk", BILGI, "Madde 92(5), Ek-8/B", spr_aciklama))
    # Yangın dolabı debisi
    q_dolap = 0.0
    if g.dolap_var:
        if g.dolap_tipi == "yassi":
            birim = 400
            tip_ad = "yassı hortumlu (TS EN 671-2): 400 l/dk"
        else:
            birim = 100
            tip_ad = "yarı-sert hortumlu (TS EN 671-1): 100 l/dk"
        # Ek-8/C: yağmurlama + dolap sisteminde ilave debi
        if g.yagmurlama_var or not g.sadece_dolap:
            birim_eff = dolap_d
            kaynak = f"Ek-8/C ilave yangın dolabı debisi {dolap_d} l/dk"
        else:
            birim_eff = birim
            kaynak = f"Madde 94 tasarım debisi — {tip_ad}"
        q_dolap = g.es_zamanli_dolap * birim_eff
        s.append(Sonuc(B, "Yangın dolabı debisi", q_dolap, "l/dk", BILGI, "Madde 92(5)-(6), 94, Ek-8/C",
                       f"{g.es_zamanli_dolap} eş zamanlı dolap × {birim_eff} l/dk. {kaynak}. (Kılavuz örneğinde 2 dolap alınmıştır.)"))
    q_hid = 0.0
    if g.hidrant_var:
        q_hid = hid_d
        if g.sadece_hidrant:
            q_hid = max(1900.0, hid_d)
        s.append(Sonuc(B, "Hidrant debisi", q_hid, "l/dk", BILGI, "Madde 92(5),(7), 95(2), Ek-8/C",
                       "Yapıda sadece çevre hidrant sistemi varsa en az 1900 l/dk × 90 dk (Madde 92(7)); yağmurlama + hidrant birlikteyse Ek-8/C ilave hidrant debisi."))
    q_toplam = q_spr + q_dolap + q_hid
    if q_toplam > 0:
        s.append(Sonuc(B, "Toplam yangın suyu debisi", _r(q_toplam, 1), "l/dk", BILGI, "Madde 92(5)", f"{_r(q_toplam/1000*60, 1)} m³/h"))
        v = q_toplam * sure / 1000.0
        parca = []
        if q_spr: parca.append(f"yağmurlama {q_spr*sure/1000:.1f}")
        if q_dolap: parca.append(f"dolap {q_dolap*sure/1000:.1f}")
        if q_hid: parca.append(f"hidrant {q_hid*sure/1000:.1f}")
        s.append(Sonuc(B, "Hesaplanan su deposu hacmi (Madde 92(5))", _r(v, 1), "m³", BILGI, "Madde 92(3),(5)",
                       f"({q_spr:,.0f} + {q_dolap:,.0f} + {q_hid:,.0f}) l/dk × {sure} dk = {v:.1f} m³ ({' + '.join(parca)} m³)."))
        v_tablo = None
        if g.yagmurlama_var:
            tip = "kuru" if g.yagmurlama_tipi == "kuru" else "islak"
            tv = T.EK8A.get((g.tehlike, tip))
            if tv:
                idx = 0 if g.spr_yukseklik_h <= 15 else (1 if g.spr_yukseklik_h <= 30 else 2)
                if g.spr_yukseklik_h > 45:
                    s.append(Sonuc(B, "Ek-8/A tablo hacmi", "h > 45 m", "", KONTROL, "Madde 92(4)", "Tablo 45 m'ye kadar; hidrolik hesap kullanılır."))
                else:
                    v_tablo = tv[idx]
                    s.append(Sonuc(B, "Ek-8/A tablo hacmi (ön hesap)", v_tablo, "m³", BILGI, "Madde 92(4), Ek-8/A",
                                   f"h = {g.spr_yukseklik_h:g} m ({['h≤15','15<h≤30','30<h≤45'][idx]}); {T.TEHLIKE_SINIFLARI[g.tehlike]} {tip}. "
                                   "Madde 92(4): ön hesap için Ek-8/A veya (5). fıkra usulü kullanılabilir; hidrolik hesap yapılırsa onun sonucu esas alınır."))
            else:
                s.append(Sonuc(B, "Ek-8/A tablo hacmi", "Hidrolik hesap kullanılır", "", KONTROL, "Ek-8/A", "Bu tehlike sınıfı/sistem için tabloda değer yoktur."))
        oneri = max(v, v_tablo or 0)
        if g.sadece_hidrant:
            oneri = max(oneri, 1900 * 90 / 1000)
            s.append(Sonuc(B, "Sadece hidrant sistemi (en az)", 171.0, "m³", BILGI, "Madde 92(7)", "1900 l/dk × 90 dk."))
        if g.orman_yakin and g.kullanim in ("endustriyel", "depo") and g.toplam_kapali_alan > 2000:
            ormanv = 5700 * 60 / 1000
            oneri = max(oneri, ormanv)
            s.append(Sonuc(B, "Orman alanı dış hidrant deposu (en az)", _r(ormanv, 1), "m³", GEREKLI, "Madde 92(7), 7(12)",
                           "Orman alanlarında dış hidrant sisteminin su ihtiyacı için en az 5700 l/dk × 60 dk depo."))
        s.append(Sonuc(B, "Önerilen en az yangın suyu deposu", _r(oneri, 1), "m³", BILGI, "Madde 92",
                       "Hesaplanan ve tablo değerlerinin büyüğü (muhafazakâr yaklaşım). Depo yangın rezervi başka amaçla kullanılamaz (Madde 92(2))."))
        if g.mevcut_su_deposu_m3 > 0:
            s.append(Sonuc(B, "Mevcut/proje yangın suyu deposu", g.mevcut_su_deposu_m3, "m³", _karsilastir(g.mevcut_su_deposu_m3, oneri, ust=False), "Madde 92", f"Gerekli {oneri:.1f} m³."))
        # Pompa
        qp = q_toplam * 0.06  # l/dk -> m³/h
        s.append(Sonuc(B, "Yangın pompası en az anma debisi", _r(qp, 1), "m³/h", BILGI, "Madde 93", "Toplam debi (l/dk × 60 / 1000)."))
        hy = g.statik_yukseklik_mSS + g.boru_kaybi_mSS + g.akma_basinci_mSS
        if g.statik_yukseklik_mSS or g.boru_kaybi_mSS:
            s.append(Sonuc(B, "Yangın pompası en az basma yüksekliği Hy", _r(hy, 2), "mSS", BILGI, "Madde 93, 95(2), Kılavuz",
                           f"Hy = statik yükseklik {g.statik_yukseklik_mSS:g} + boru kayıpları {g.boru_kaybi_mSS:g} + akma basıncı {g.akma_basinci_mSS:g} mSS (hidrant çıkışında 700 kPa ≈ 70 mSS)."))
        else:
            s.append(Sonuc(B, "Yangın pompası basma yüksekliği Hy", "—", "mSS", KONTROL, "Madde 93",
                           "Hy = statik yükseklik + tesisat basınç kayıpları + akma basıncı. Kritik devre hidrolik hesabından statik yükseklik ve boru kaybı girilmelidir."))
        # Pompa karakteristiği
        if g.pompa_anma_basma_mSS > 0 and (g.statik_yukseklik_mSS or g.boru_kaybi_mSS):
            if g.pompa_anma_basma_mSS >= hy:
                s.append(Sonuc(B, "Pompa anma basma yüksekliği ≥ Hy", g.pompa_anma_basma_mSS, "mSS", UYGUN, "Madde 93",
                               f"Anma basma yüksekliği {g.pompa_anma_basma_mSS:g} mSS ≥ gerekli Hy {hy:.1f} mSS."))
            else:
                s.append(Sonuc(B, "Pompa anma basma yüksekliği ≥ Hy", g.pompa_anma_basma_mSS, "mSS", KOSULLU, "Madde 93",
                               f"Anma basma yüksekliği {g.pompa_anma_basma_mSS:g} mSS < gerekli Hy {hy:.1f} mSS. Pompa eğrisinde toplam debideki ({qp:.1f} m³/h) "
                               "basma yüksekliği Hy'ye eşit veya büyükse yeterli olabilir; eğri noktası ile doğrulayın."))
        if g.pompa_anma_basma_mSS > 0:
            if g.pompa_kapali_vana_basma_mSS > 0:
                lim = 1.4 * g.pompa_anma_basma_mSS
                s.append(Sonuc(B, "Pompa kapalı vana basma yüksekliği", g.pompa_kapali_vana_basma_mSS, "mSS", _karsilastir(g.pompa_kapali_vana_basma_mSS, lim), "Madde 93(1)", f"Anma değerinin en fazla %140'ı = {lim:.1f} mSS."))
            if g.pompa_150_debi_basma_mSS > 0:
                lim = 0.65 * g.pompa_anma_basma_mSS
                s.append(Sonuc(B, "Pompa %150 debide basma yüksekliği", g.pompa_150_debi_basma_mSS, "mSS", _karsilastir(g.pompa_150_debi_basma_mSS, lim, ust=False), "Madde 93(1)", f"Anma değerinin en az %65'i = {lim:.1f} mSS."))
        if g.pompa_anma_debi_m3h > 0:
            kap = g.pompa_anma_debi_m3h * 1.3
            s.append(Sonuc(B, "Pompa kullanılabilir azami debi", _r(kap, 1), "m³/h", _karsilastir(qp, kap), "Madde 93(1)", "Pompa anma debisinin %130'una kadar sistem talebi karşılayabilir."))
            s.append(Sonuc(B, "Seçilen pompa anma debisi", g.pompa_anma_debi_m3h, "m³/h", _karsilastir(g.pompa_anma_debi_m3h, qp, ust=False), "Madde 93", f"Gerekli en az {qp:.1f} m³/h."))
        if g.pompa_adedi <= 1:
            s.append(Sonuc(B, "Yedek pompa", "Aynı kapasitede 1 adet", "", UYGUN if g.yedek_pompa_adedi >= 1 else UYGUN_DEGIL, "Madde 93(2)", "Tek pompa kullanılıyorsa aynı kapasitede yedek pompa gerekir."))
        else:
            ok = g.yedek_pompa_adedi >= math.ceil(g.pompa_adedi / 2)
            s.append(Sonuc(B, "Yedek pompa", f"Toplam kapasitenin en az %50'si", "", UYGUN if ok else UYGUN_DEGIL, "Madde 93(2)",
                           f"{g.pompa_adedi} asıl pompa için en az {math.ceil(g.pompa_adedi/2)} yedek pompa; projede {g.yedek_pompa_adedi}."))
        s.append(Sonuc(B, "Pompa odası sıcaklığı", "≥ +4 °C (elektrikli) / ≥ +10 °C (dizel)", "", BILGI, "Madde 93(9)"))
    return s


# ---------------------------------------------------------------------------
# 8. Yangın dolabı, itfaiye bağlantıları, hidrant, söndürücü
# ---------------------------------------------------------------------------
def dolap_hidrant_sondurucu(g: Girdi) -> list[Sonuc]:
    B = "8. Yangın dolabı, hidrant ve söndürücüler"
    s: list[Sonuc] = []
    # --- yangın dolabı zorunluluğu
    nedenler = []
    if _yuksek_bina(g):
        nedenler.append("yüksek bina")
    if g.kullanim in ("endustriyel", "depo") and g.toplam_kapali_alan > 1000:
        nedenler.append(f"toplam kapalı alan {g.toplam_kapali_alan:,.0f} m² > 1000 m² (imalathane/atölye/depo)")
    if g.otopark_alani > 600:
        nedenler.append(f"kapalı otopark {g.otopark_alani:,.0f} m² > 600 m²")
    if g.kazan_var and g.kazan_kw > 350:
        nedenler.append(f"kazan dairesi ısıl kapasitesi {g.kazan_kw:g} kW > 350 kW")
    if nedenler:
        s.append(Sonuc(B, "Yangın dolabı", "Mecburi", "", UYGUN if g.dolap_var else UYGUN_DEGIL, "Madde 94(b)1", "; ".join(nedenler)))
    else:
        s.append(Sonuc(B, "Yangın dolabı", "Madde 94(b)1 kapsamında zorunlu değil", "", GEREKMEZ, "Madde 94(b)1"))
    aralik = 45 if (g.yagmurlama_var) else 30
    n_dolap = aralik_adedi(g.bina_boyu, g.bina_eni, aralik) * max(1, g.kat_sayisi)
    if nedenler:
        s.append(Sonuc(B, "Dolaplar arası azami uzaklık", aralik, "m", BILGI, "Madde 94(b)2",
                       "Her katta ve yangın duvarlarıyla ayrılmış her bölümde 30 m; bina yağmurlama sistemi ile korunuyor ve katlara itfaiye su alma ağzı bırakılmışsa (ıslak tip yağmurlama branşmanından beslenen) 45 m'ye çıkarılabilir."))
        s.append(Sonuc(B, "Yaklaşık yangın dolabı adedi", n_dolap, "adet", BILGI, "Madde 94(b)2",
                       f"{g.bina_boyu:g} × {g.bina_eni:g} m kat alanı, {aralik} m ızgara × {max(1,g.kat_sayisi)} kat (ön hesap; dolaplar çıkış ve merdiven sahanlığı yakınında yerleştirilir)."))
        tip = "yassı hortum: DN50, en çok 20 m, 400 l/dk, ≥400 kPa (TS EN 671-2)" if g.dolap_tipi == "yassi" else "yarı-sert hortum: Ø25 mm, en çok 30 m, 100 l/dk, ≥400 kPa (TS EN 671-1)"
        s.append(Sonuc(B, "Yangın dolabı tipi ve tasarım değerleri", tip, "", BILGI, "Madde 94(b)4-6", "Lüle girişinde basınç 900 kPa'yı geçerse basınç düşürücü kullanılır."))
    # --- itfaiye su alma ağzı
    boyut_60 = max(g.bina_boyu, g.bina_eni) > 60
    if _yuksek_bina(g) or (g.en_buyuk_kat_alani > 1000 and g.kullanim in ("ticaret", "otopark")) or boyut_60:
        gerek = []
        if _yuksek_bina(g): gerek.append("yüksek bina")
        if boyut_60: gerek.append(f"bir boyutu 60 m'yi geçiyor ({max(g.bina_boyu, g.bina_eni):g} m)")
        s.append(Sonuc(B, "İtfaiye su alma ağzı", "Gerekli", "", GEREKLI, "Madde 94(a)1-2",
                       "; ".join(gerek) + ". Herhangi bir noktadan su alma ağzına mesafe ≤ 60 m; korunmuş mekânda (merdiven/güvenlik holü), storz 50/65 mm."))
    # --- itfaiye su verme bağlantısı
    nd = []
    if _yuksek_bina(g): nd.append("yüksek bina")
    if g.taban_alani > 1000: nd.append(f"bina oturma alanı {g.taban_alani:,.0f} m² > 1000 m²")
    if g.cephe_genisligi > 75: nd.append(f"cephe genişliği {g.cephe_genisligi:g} m > 75 m")
    if nd:
        s.append(Sonuc(B, "İtfaiye su verme bağlantısı", "Mecburi", "", GEREKLI, "Madde 97",
                       "; ".join(nd) + ". En az DN100, 2 adet 65 mm storz rakor, çek valf; itfaiye aracının ulaşma mesafesi ≤ 18 m."))
    else:
        s.append(Sonuc(B, "İtfaiye su verme bağlantısı", "Zorunlu değil", "", GEREKMEZ, "Madde 97"))
    # --- hidrant
    toplam_taban = _tesis_toplam_taban(g)
    hid_zorunlu = toplam_taban > 5000 or (g.orman_yakin and g.kullanim in ("endustriyel", "depo") and g.toplam_kapali_alan > 2000)
    ack = f"Taban alanları toplamı {toplam_taban:,.0f} m²" + (" > 5000 m²" if toplam_taban > 5000 else " ≤ 5000 m²")
    if g.orman_yakin and g.toplam_kapali_alan > 2000:
        ack += "; orman alanı kapsamında dış hidrant sistemi yapılır (Madde 95(7))"
    s.append(Sonuc(B, "Dış hidrant sistemi", "Mecburi" if hid_zorunlu else "Zorunlu değil", "",
                   (UYGUN if g.hidrant_var else UYGUN_DEGIL) if hid_zorunlu else GEREKMEZ, "Madde 95(7)", ack))
    aralik_h = {"cok_riskli": 50, "riskli": 100, "orta": 125, "az": 150}[g.hidrant_risk]
    cevre = 2 * (g.bina_boyu + g.bina_eni)
    n_h = max(1, math.ceil(cevre / aralik_h - 1e-9))
    if g.hidrant_var:
        s.append(Sonuc(B, "Hidrantlar arası azami uzaklık", aralik_h, "m", BILGI, "Madde 95(3)",
                       {"cok_riskli": "çok riskli", "riskli": "riskli", "orta": "orta riskli", "az": "az riskli"}[g.hidrant_risk] + " bölge (yönetmelik tehlike sınıfı–bölge eşleştirmesi vermez; seçim proje sorumlusunundur)."))
        s.append(Sonuc(B, "Yaklaşık hidrant adedi", n_h, "adet", BILGI, "Madde 95(1),(3)", f"Bina çevresi {cevre:.0f} m / {aralik_h} m; hidrantlar binadan ortalama 5–15 m uzakta, çevreyi kapsayacak şekilde."))
        s.append(Sonuc(B, "Hidrant tasarım debisi ve basıncı", "≥ 1900 l/dk; çıkışta ≥ 700 kPa", "", BILGI, "Madde 95(2)", "Debi bina tehlike sınıfına göre artırılır; ring yoksa en küçük boru çapı DN100."))
    # --- taşınabilir söndürücü
    kat_basi = 500 if T.tehlike_grubu(g.tehlike) == "dusuk" else 250
    adet_alan = math.ceil(g.toplam_kapali_alan / kat_basi - 1e-9)
    adet_menzil = kapsama_adedi(g.bina_boyu, g.bina_eni, 25.0) * max(1, g.kat_sayisi)
    adet = max(adet_alan, adet_menzil)
    s.append(Sonuc(B, "6 kg kuru kimyevi tozlu söndürücü — alana göre", adet_alan, "adet", BILGI, "Madde 99(2)",
                   f"{'Düşük' if kat_basi==500 else 'Orta/yüksek'} tehlike: her {kat_basi} m² yapı inşaat alanı için 1 adet. {g.toplam_kapali_alan:,.0f} / {kat_basi}."))
    s.append(Sonuc(B, "Söndürücü — ulaşma mesafesine göre", adet_menzil, "adet", BILGI, "Madde 99(4)", "Söndürme cihazına ulaşma mesafesi en çok 25 m (her noktadan en yakın cihaza)."))
    s.append(Sonuc(B, "Gerekli en az söndürücü adedi", adet, "adet", GEREKLI, "Madde 99", "İki kriterin büyüğü. Depo, tesisat dairesi ve otoparklarda ayrıca tekerlekli tip söndürücü bulundurulur (Madde 99(3))."))
    return s


# ---------------------------------------------------------------------------
# 9. Algılama, uyarı, aydınlatma, yönlendirme
# ---------------------------------------------------------------------------
def algilama_aydinlatma(g: Girdi) -> list[Sonuc]:
    B = "9. Algılama, uyarı ve acil aydınlatma"
    s: list[Sonuc] = []
    # Ek-7
    ek7 = T.EK7.get(g.kullanim)
    if ek7 is None:
        s.append(Sonuc(B, "Otomatik yangın algılama (Ek-7)", "Ek-7'de zorunlu satır yok", "", GEREKMEZ, "Madde 75(3), Ek-7",
                       "Ek-7'deki Endüstriyel, Ticaret, Kurum ve Toplanma amaçlı yapı satırları Danıştay 10. Daire kararıyla (E.2019/261, K.2021/5537; İDDK 22/2/2023 onama) iptal edilmiştir. "
                       "Bu yapılarda algılama/söndürme ilgili diğer maddelere (Madde 81, kompartıman Ek-4 dipnotları, itfaiye görüşü) göre belirlenir."))
    else:
        yy, alan = ek7
        asim_y = g.yapi_yuksekligi > yy
        asim_a = (alan is None) or (g.toplam_kapali_alan > alan)
        zorunlu = asim_y and asim_a
        s.append(Sonuc(B, "Otomatik yangın algılama (Ek-7)", "Mecburi" if zorunlu else "Zorunlu değil", "",
                       (UYGUN if g.algilama_var else UYGUN_DEGIL) if zorunlu else GEREKMEZ, "Madde 75(3), Ek-7",
                       f"Yapı yüksekliği > {yy:g} m" + (f" ve toplam kapalı alan > {alan:,} m²" if alan else "") + f" kriterleri: yükseklik {g.yapi_yuksekligi:g} m, alan {g.toplam_kapali_alan:,.0f} m²."))
    if g.kullanim in ("endustriyel", "depo", "yuksek_tehlikeli") and (g.kolay_alevlenici or g.tehlike.startswith("YT")):
        s.append(Sonuc(B, "Tahliye uyarı sistemi (tehlikeli madde bulunan endüstriyel yapı)", "Otomatik tahliye uyarısı; ön uyarı yok", "", GEREKLI, "Madde 81 (Kılavuz)",
                       "Tehlikeli maddelerin bulunduğu/işlendiği endüstriyel binalarda herhangi bir algılama otomatik olarak bina tahliye uyarı sistemlerini harekete geçirmelidir; ön uyarı sistemine izin verilmez."))
    # Buton
    kat_alani = g.en_buyuk_kat_alani
    if g.kat_sayisi >= 2 and g.kat_sayisi <= 4 and _konut_degil(g) and kat_alani > 400:
        buton = f"2–4 katlı, kat alanı {kat_alani:,.0f} m² > 400 m²"
    elif g.kat_sayisi > 4 and _konut_degil(g):
        buton = f"kat sayısı {g.kat_sayisi} > 4"
    elif _yuksek_bina(g):
        buton = "yüksek bina"
    else:
        buton = ""
    adet_b = kapsama_adedi(g.bina_boyu, g.bina_eni, 60.0)
    cikis_say = max([k.cikis_sayisi for k in g.katlar] + [2])
    if buton:
        s.append(Sonuc(B, "Yangın uyarı butonu", "Mecburi", "", UYGUN if g.yangin_butonu_adedi else GEREKLI, "Madde 75(2)", buton + "."))
    else:
        s.append(Sonuc(B, "Yangın uyarı butonu", "Madde 75(2) kapsamında zorunlu değil", "", GEREKMEZ, "Madde 75(2)",
                       "Zorunlu olmasa da uyarı sistemi bulunan binalarda butonlar kaçış yollarında tesis edilir. Yangın uyarı butonunun zorunlu olduğu yerde uyarı sistemi de mecburidir (Madde 81)."))
    adet_b2 = max(adet_b, cikis_say) * max(1, g.kat_sayisi)
    s.append(Sonuc(B, "Yangın uyarı butonu — en az adet (ön hesap)", adet_b2, "adet", BILGI, "Madde 75(2)",
                   "Her noktadan en yakın butona yatay erişim ≤ 60 m (kare ızgara kapsaması), her çıkış yanında bir buton; yerden 110–130 cm."))
    if g.yangin_butonu_adedi:
        s.append(Sonuc(B, "Projedeki buton adedi", g.yangin_butonu_adedi, "adet", _karsilastir(g.yangin_butonu_adedi, adet_b2, ust=False), "Madde 75(2)"))
    # Acil aydınlatma
    kisi = sum(kat_kullanici_yuku(k) for k in g.katlar)
    nedenler = ["kaçış yolları ve toplanma yerleri (her yapıda)"]
    if g.kullanim in ("endustriyel", "depo"):
        nedenler.append("yüksek risk oluşturan hareketli makine/atölye, elektrik dağıtım, jeneratör, pompa istasyonu")
    if kisi > 200: nedenler.append("kullanıcı yükü > 200")
    if g.tehlike.startswith("YT") or g.kullanim == "yuksek_tehlikeli": nedenler.append("yüksek tehlikeli yer")
    if _yuksek_bina(g): nedenler.append("yüksek bina")
    if g.bodrum_kat_sayisi and kisi >= 50: nedenler.append("zemin altında ≥ 50 kullanıcı")
    s.append(Sonuc(B, "Acil durum aydınlatması", "Mecburi", "", GEREKLI, "Madde 72(2)", "; ".join(nedenler)))
    sure = 120 if kisi > 200 else 60
    sure_ack = "Kullanıcı yükü 200'den fazla: 120 dk" if kisi > 200 else "Kullanıcı yükü ≤ 200: 60 dk"
    s.append(Sonuc(B, "Acil aydınlatma/yönlendirme çalışma süresi", sure, "dk", BILGI, "Madde 72(3), 73(3)", sure_ack + "."))
    if g.acil_aydinlatma_sure_dk:
        s.append(Sonuc(B, "Projedeki acil aydınlatma süresi", g.acil_aydinlatma_sure_dk, "dk", _karsilastir(g.acil_aydinlatma_sure_dk, sure, ust=False), "Madde 72(3)"))
    s.append(Sonuc(B, "Acil aydınlatma seviyesi (kaçış yolu merkez hattı)", "≥ 1 lux (başlangıç), ≥ 0.5 lux (süre sonu), max/min ≤ 40", "", BILGI, "Madde 72(4)"))
    if g.acil_aydinlatma_lux_baslangic:
        s.append(Sonuc(B, "Başlangıç aydınlık seviyesi", g.acil_aydinlatma_lux_baslangic, "lux", _karsilastir(g.acil_aydinlatma_lux_baslangic, 1.0, ust=False), "Madde 72(4)"))
    if g.acil_aydinlatma_lux_bitis:
        s.append(Sonuc(B, "Süre sonu aydınlık seviyesi", g.acil_aydinlatma_lux_bitis, "lux", _karsilastir(g.acil_aydinlatma_lux_bitis, 0.5, ust=False), "Madde 72(4)"))
    if g.acil_aydinlatma_max_min_orani:
        s.append(Sonuc(B, "En yüksek/en düşük aydınlık oranı", g.acil_aydinlatma_max_min_orani, "", _karsilastir(g.acil_aydinlatma_max_min_orani, 40), "Madde 72(4)", "1/40'tan fazla olamaz."))
    # Yönlendirme
    h = g.isaret_yuksekligi_cm
    k_ = 200 if g.isaret_aydinlatma == "icten" else 100
    dmax = k_ * h / 100.0
    s.append(Sonuc(B, "Yönlendirme işareti azami görülebilirlik uzaklığı", _r(dmax, 1), "m", BILGI, "Madde 73(4)",
                   f"İşaret yüksekliği {h:g} cm (en az 15 cm) × {k_} ({'içeriden/arkadan aydınlatılan' if k_==200 else 'dışarıdan/kenardan aydınlatılan'})."))
    if h < 15:
        s.append(Sonuc(B, "Yönlendirme işareti yüksekliği", h, "cm", UYGUN_DEGIL, "Madde 73(4)", "En az 15 cm."))
    if g.kacis_yolu_uzunlugu_m > 0:
        n = math.ceil(g.kacis_yolu_uzunlugu_m / dmax - 1e-9)
        s.append(Sonuc(B, "Kaçış yolu boyunca en az yönlendirme işareti", n, "adet", BILGI, "Madde 73(4)",
                       f"{g.kacis_yolu_uzunlugu_m:g} m / {dmax:.1f} m (her noktadan görülebilme; dönüş ve çıkışlarda ilave). Montaj yüksekliği 200–240 cm."))
    return s


# ---------------------------------------------------------------------------
# 10. Duman kontrolü ve basınçlandırma
# ---------------------------------------------------------------------------
def duman_basinclandirma(g: Girdi) -> list[Sonuc]:
    B = "10. Duman kontrolü ve basınçlandırma"
    s: list[Sonuc] = []
    for m in g.duman_mahalleri:
        K = f"{B} — {m.ad}"
        zorunlu = m.tur in ("kazan", "otopark", "bodrum_depo") and m.alan_m2 > 2000
        hacim = m.alan_m2 * m.yukseklik_m
        q = 10 * hacim
        if zorunlu:
            s.append(Sonuc(K, "Mekanik duman tahliyesi", "Mecburi", "", GEREKLI, "Madde 88(3)",
                           "Toplam alanı 2000 m²'yi aşan kazan dairesi, kapalı otopark ve bodrum depo: binanın diğer bölümlerinden bağımsız, saatte en az 10 hava değişimi."))
        else:
            s.append(Sonuc(K, "Mekanik duman tahliyesi (Madde 88(3))", "Zorunlu değil", "", GEREKMEZ, "Madde 88(3)",
                           f"Alan {m.alan_m2:,.0f} m² (2000 m² sınırı veya mahal türü uygun değil)."))
        s.append(Sonuc(K, "10 hava değişimi/saat için debi", _r(q, 0), "m³/h", BILGI, "Madde 88(3)",
                       f"10 × ({m.alan_m2:,.0f} m² × {m.yukseklik_m:g} m) = {q:,.0f} m³/h = {q/3600:.2f} m³/s. Fan kabloları 60 dk yangına dayanıklı, jeneratörden beslenmeli (Madde 85(5))."))
    if not g.duman_mahalleri:
        s.append(Sonuc(B, "Mekanik duman tahliyesi — kazan/otopark/bodrum depo", "Girdi yok", "", KONTROL, "Madde 88(3)", "2000 m²'yi aşan mahaller için ≥ 10 hava değişimi/saat."))
    if g.kullanim in ("endustriyel", "depo"):
        s.append(Sonuc(B, "Üretim/depo holünde duman tahliyesi", "Standarda göre tasarım", "", BILGI, "Madde 85–86, Ek-4 dipnotları",
                       "Yönetmelik doğal/mekanik duman tahliyesi için sayısal hava debisi vermez (ilgili standartlara atıf). Duman tahliyesi, kompartıman alanını sınırsız kılan 'uygun yangın kontrol sistemleri' arasında sayılmıştır."))
    # Basınçlandırma
    h = g.merdiven_kovasi_yuksekligi or (g.bina_yuksekligi if g.kat_sayisi > 1 else 0)
    nedenler = []
    if _konut_degil(g) and h > 30.50:
        nedenler.append(f"merdiven kovası yüksekliği {h:g} m > 30,50 m (Madde 89(1))")
    if g.bodrum_kat_sayisi > 4:
        nedenler.append(f"bodrum kat sayısı {g.bodrum_kat_sayisi} > 4 (Madde 89(2))")
    if g.kullanim == "apartman" and g.yapi_yuksekligi > 51.50:
        nedenler.append("yapı yüksekliği > 51,50 m konut (Madde 89(3))")
    if nedenler:
        s.append(Sonuc(B, "Kaçış merdiveni basınçlandırması", "Mecburi", "", GEREKLI, "Madde 89", "; ".join(nedenler)))
        n_kapi = 3
        q_kapi = 1.0 * g.basinc_kapi_alani_m2 * n_kapi + g.basinc_sizinti_debisi_m3s
        s.append(Sonuc(B, "Basınçlandırma en az hava debisi (ön hesap)", _r(q_kapi, 2), "m³/s", BILGI, "Madde 89(8)-(10)",
                       f"En az 2 iç + 1 dışarı kapı açık, her açık kapıda ortalama hız ≥ 1 m/s: 1 × {g.basinc_kapi_alani_m2:g} m² × {n_kapi} + sızıntı {g.basinc_sizinti_debisi_m3s:g} m³/s = {q_kapi*3600:,.0f} m³/h. "
                                  "Kat sayısına göre açık iç kapı sayısı artırılır; sızıntı debisi ayrıca hesaplanıp girilmelidir."))
        s.append(Sonuc(B, "Basınç farkı", "≥ 50 Pa (kapılar kapalı); ≥ 15 Pa (kapı açık)", "", BILGI, "Madde 89(5)", "Kapı açma kuvveti ≤ 110 N (Madde 89(7)); aşırı basınç damperi ve frekans kontrollü fan (Madde 89(11))."))
        if h > 25:
            s.append(Sonuc(B, "Üfleme noktaları", "Birden fazla noktadan", "", GEREKLI, "Madde 89(12)", "Yüksekliği 25 m'den fazla merdivenlerde birden fazla noktadan üfleme; yapı yüksekliği > 51,50 m'de her katta veya en çok her üç katta bir."))
    else:
        s.append(Sonuc(B, "Kaçış merdiveni basınçlandırması", "Zorunlu değil", "", GEREKMEZ, "Madde 89",
                       "Basınçlandırma yapılmıyorsa merdiven bölümünde açılabilir pencere veya tepe penceresi gerekir (Madde 89(16))."))
    return s


# ---------------------------------------------------------------------------
# 11. Kazan dairesi, yakıt, trafo, jeneratör
# ---------------------------------------------------------------------------
def kazan_yakit(g: Girdi) -> list[Sonuc]:
    B = "11. Kazan dairesi, yakıt, trafo ve jeneratör"
    s: list[Sonuc] = []
    if g.kazan_var:
        if g.kazan_kw >= 50:
            iki = g.kazan_kw > 350 or g.kazan_alani_m2 > 100
            gerek = 2 if iki else 1
            s.append(Sonuc(B, "Kazan dairesi çıkış kapısı sayısı", gerek, "adet", _karsilastir(g.kazan_kapi_sayisi, gerek, ust=False), "Madde 54(5)",
                           f"Isıl kapasite {g.kazan_kw:g} kW, döşeme alanı {g.kazan_alani_m2:g} m². 50–350 kW: en az 1; >350 kW veya >100 m²: en az 2 kapı (birbirinin ters yönünde, 90 dk, duman sızdırmaz, kendiliğinden kapanır). Projede {g.kazan_kapi_sayisi} adet."))
        s.append(Sonuc(B, "Kazan dairesi bölme dayanımı", 120, "dk", BILGI, "Madde 54(2)", "Binanın diğer kısımlarından en az 120 dk dayanıklı bölmelerle ayrılır."))
        s.append(Sonuc(B, "Kazan dairesi söndürücü / dolap", "1 × 6 kg ABC toz; büyük kazan dairesinde yangın dolabı", "", GEREKLI, "Madde 54(8), 94",
                       "Kazan dairesi ısıl kapasitesi 350 kW'ın üzerindeyse yangın dolabı mecburidir."))
        if g.kazan_sivi_yakit:
            s.append(Sonuc(B, "Pis su çukuru (sıvı yakıtlı kazan dairesi)", "≥ 0,25 m³", "", GEREKLI, "Madde 54(7)", "Betondan, yakıt ayırıcıdan geçen akıntı için."))
        if g.kazan_alani_m2 > 2000:
            s.append(Sonuc(B, "Kazan dairesi mekanik duman tahliyesi", "Mecburi (≥ 10 hava değişimi/saat)", "", GEREKLI, "Madde 88(3)"))
    if g.yakit_tank_L > 0:
        v = g.yakit_tank_L
        yer = g.yakit_yeri
        izin = {"bodrum_varil": 1000, "bodrum_sac": 3000, "bodrum_komur": 40000, "bina_disi": 40000}.get(yer)
        ad = {"bodrum_varil": "bodrumda varil içinde (≤1000 L)", "bodrum_sac": "bodrumda sızıntısız sac kapta (≤3000 L)",
              "bodrum_komur": "bina içi bodrumda 120 dk kâgir odada sızıntısız tank (≤40000 L)", "bina_disi": "bina dışında sızıntısız yeraltı/yerüstü tank (≤40000 L)",
              "bagimsiz": "ayrı, bağımsız, tek katlı binada (40000 L üzeri)"}[yer]
        if izin is not None:
            s.append(Sonuc(B, "Kalorifer yakıt depolama miktarı", v, "L", _karsilastir(v, izin), "Madde 56(3)", f"{ad}."))
        else:
            s.append(Sonuc(B, "Kalorifer yakıt depolama miktarı", v, "L", UYGUN if v > 40000 else KOSULLU, "Madde 56(3)d",
                           "Stok ihtiyacı 40000 L'den fazlaysa tanklar binadan ayrı, bağımsız, tek katlı binaya yerleştirilir ve Sekizinci Kısım tedbirleri alınır."))
        gerekli_havuz = v / 3
        s.append(Sonuc(B, "Yakıt tankı havuzlama hacmi (en az)", _r(gerekli_havuz, 0), "L", BILGI if not g.yakit_havuz_L else _karsilastir(g.yakit_havuz_L, gerekli_havuz, ust=False), "Madde 56(1)",
                       f"Tank kapasitesinin en az üçte biri = {gerekli_havuz:,.0f} L" + (f"; projede {g.yakit_havuz_L:,.0f} L." if g.yakit_havuz_L else ".")))
        s.append(Sonuc(B, "Yakıt deposu–kazan dairesi bölmesi", 120, "dk", BILGI, "Madde 56(1)"))
    if g.yagli_trafo_var:
        s.append(Sonuc(B, "Trafo odası", "Duvar/taban/tavan ≥ 120 dk; yağ toplama çukuru; otomatik algılama ve söndürme", "", GEREKLI, "Madde 65"))
    elif g.kullanim in ("endustriyel", "depo"):
        s.append(Sonuc(B, "Trafo odası (varsa)", "Duvar/taban/tavan ≥ 120 dk", "", BILGI, "Madde 65(1)"))
    if g.jenerator_var:
        s.append(Sonuc(B, "Jeneratör odası", "Duvar/taban/tavan ≥ 120 dk; ana yakıt deposu Madde 56'ya uygun", "", GEREKLI, "Madde 66"))
    if not s:
        s.append(Sonuc(B, "Kazan/yakıt/trafo/jeneratör", "Bu tesiste girilmedi", "", GEREKMEZ, "Madde 53–66"))
    return s


# ---------------------------------------------------------------------------
# 12. Tehlikeli maddeler (LPG, yanıcı sıvılar)
# ---------------------------------------------------------------------------
def _band(tablo, deger):
    for satir in tablo:
        if deger <= satir[0]:
            return satir
    return tablo[-1]


def tehlikeli_madde(g: Girdi) -> list[Sonuc]:
    B = "12. Tehlikeli maddeler"
    s: list[Sonuc] = []
    if g.lpg_tup_kg > 0:
        _, bina, cadde = _band(T.EK9, g.lpg_tup_kg)
        s.append(Sonuc(B, "LPG tüp deposu emniyet uzaklığı — bina/komşu arsa sınırı", bina, "m", BILGI, "Madde 106–107, Ek-9", f"{g.lpg_tup_kg:,.0f} kg LPG."))
        s.append(Sonuc(B, "LPG tüp deposu emniyet uzaklığı — cadde, kaldırım, okul, cami, hastane, kamuya açık yer", cadde, "m", BILGI, "Ek-9"))
    if g.lpg_tank_m3 > 0:
        _, yeralti, yerustu, aralik = _band(T.EK10, g.lpg_tank_m3)
        if g.lpg_tank_tur == "yeralti":
            d = max(yeralti, 3)
            s.append(Sonuc(B, "Dökme LPG yeraltı tankı emniyet uzaklığı", d, "m", BILGI, "Ek-10", "Tank emniyet valfi ve dolum ağzından ölçülür; binaya/arsa sınırına en az 3 m."))
        else:
            d = yerustu
            ack = f"Beher tank su hacmi {g.lpg_tank_m3:g} m³: tablo değeri {yerustu} m."
            if g.lpg_duvar_4saat:
                d = d * 2 / 3
                ack += " 4 saat dayanıklı ≥1,5 m duvar: mesafeler 1/3 azaltılır (Ek-10 not c)."
                if g.lpg_alt_yalitim_2saat:
                    d = d / 2
                    ack += " Alt yüzey 2 saat yalıtım: yeni mesafeler 1/2 oranında azaltılır (Ek-10 not d)."
            s.append(Sonuc(B, "Dökme LPG yerüstü tankı emniyet uzaklığı", _r(d, 1), "m", BILGI, "Ek-10", ack))
        s.append(Sonuc(B, "Tanklar arası uzaklık", aralik if aralik != "D/4" else "komşu tank çapları toplamının ¼'ü", "m" if aralik != "D/4" else "", BILGI, "Ek-10"))
    # Yanıcı sıvı tankları
    if g.sivi_tanklar:
        ia_eq = 0.0
        sinif_top: dict[str, float] = {}
        for t in g.sivi_tanklar:
            ia_eq += t.hacim_L / T.IA_ESDEGER_BOLEN[t.sinif]
            sinif_top[t.sinif] = sinif_top.get(t.sinif, 0) + t.hacim_L
        s.append(Sonuc(B, "Toplam yanıcı sıvı (Sınıf IA cinsinden)", _r(ia_eq, 1), "L", _karsilastir(ia_eq, 12500), "Madde 118(2), 119(2)d",
                       "IA + IB/2 + IC/4 + II/12 + IIIA/40 + IIIB/80. Toplam 12 500 L IA eşdeğerini geçemez (aynı depo hacmi/tek havuzlama bölgesi)."))
        i_ii = sum(v for k, v in sinif_top.items() if k in ("IA", "IB", "IC", "II", "IIIA", "IIIB"))
        s.append(Sonuc(B, "Toplam depolanan sıvı", _r(i_ii, 0), "L", BILGI, "Madde 114"))
        # Ek-11 bildirim / izin
        yer = g.sivi_depolama_yeri
        e11 = T.EK11[yer]
        q_ia = sinif_top.get("IA", 0)
        q_diger = sum(sinif_top.get(k, 0) for k in ("IB", "IC", "II"))
        for ad, q, (lo, hi) in (("Sınıf IA", q_ia, e11["IA"]), ("Sınıf IB/IC/II", q_diger, e11["IB_IC_II"])):
            if q > 0:
                if q > hi:
                    d = "Bildirim + itfaiye izni"
                elif q > lo:
                    d = "Bildirim"
                else:
                    d = "Eşik altında"
                s.append(Sonuc(B, f"Ek-11 — {ad}", f"{q:,.0f} L → {d}", "", GEREKLI if q > lo else GEREKMEZ, "Madde 114, Ek-11",
                               f"{'Zemin seviyesi ve üstü depo hacimleri' if yer=='zemin_ustu' else 'Açıkta kurulu depolar'}: {lo}–{hi} L. Değerleri aşan miktarlarda bildirim, üst sınırı aşarsa ayrıca itfaiye izni."))
        # Açık/yeraltı tank mesafeleri
        for t in g.sivi_tanklar:
            if t.hacim_L <= 0:
                continue
            if t.tur == "yerustu":
                _, arsa, idari, aralik = _band(T.EK12C, t.hacim_L)
                s.append(Sonuc(B, f"{t.ad} (yerüstü, Sınıf {t.sinif}, {t.hacim_L:,.0f} L) — komşu arsa sınırı/yol/demiryoluna", arsa, "m", BILGI, "Madde 119, Ek-12/C", f"İdari binalara {idari} m; tanklar arası {aralik if aralik!='D/4' else 'komşu tank çapları toplamının ¼ü'} m."))
            elif t.tur == "yeralti":
                _, arsa, aralik = _band(T.EK12C2, t.hacim_L)
                s.append(Sonuc(B, f"{t.ad} (yeraltı, Sınıf {t.sinif}, {t.hacim_L:,.0f} L) — komşu arsa sınırı/yola", arsa, "m", BILGI, "Madde 120(2), Ek-12/Ç", f"Tanklar arası {aralik if aralik!='D/4' else 'komşu tank çapları toplamının ¼ü'} m."))
        yerustu = [t for t in g.sivi_tanklar if t.tur == "yerustu"]
        if yerustu:
            en_buyuk = max(t.hacim_L for t in yerustu)
            s.append(Sonuc(B, "Yerüstü tank havuzlama hacmi (en az)", _r(en_buyuk, 0), "L", BILGI, "Madde 119(2)a",
                           "Aynı büyüklükte tanklarda bir tankın, farklı boylarda en büyük tankın hacmine eşit. Taşınabilir tanklarda toplamın %75'i (en az en büyük tank)."))
            s.append(Sonuc(B, "Tehlike bölgesi", "Tank cidarından 5 m, zeminden 0,8 m: 2. Bölge", "", BILGI, "Madde 119(4)", "Havuzlama içi: set üst kenarının 0,8 m üzerine kadar 1. Bölge; ex-proof donanım (Madde 117)."))
        depo_ici = [t for t in g.sivi_tanklar if t.tur == "depo_icinde"]
        if depo_ici:
            for sinif in sorted({t.sinif for t in depo_ici}):
                q = sum(t.hacim_L for t in depo_ici if t.sinif == sinif)
                lim_kap, lim_tank = T.EK12A[sinif]
                lim = lim_kap if g.sivi_depo_orijinal_kap else lim_tank
                if lim is None:
                    s.append(Sonuc(B, f"Depo binası içi — Sınıf {sinif}", q, "L", UYGUN_DEGIL, "Madde 118, Ek-12/A", "Sınıf IA taşınabilir tankta depolanamaz."))
                else:
                    s.append(Sonuc(B, f"Depo binası içi — Sınıf {sinif}", q, "L", _karsilastir(q, lim), "Madde 118, Ek-12/A",
                                   f"{'Orijinal kap' if g.sivi_depo_orijinal_kap else 'Taşınabilir tank'} toplam sınırı {lim:,} L."))
            s.append(Sonuc(B, "Depo binası", "Duvar ≥ 120 dk; Sınıf I için bodrum yok; havalandırma ≥ 6 hava değişimi/saat (ex-proof)", "", BILGI, "Madde 118(1),(8),(9)", "Depo hacimleri 1. Tehlike Bölgesidir; en çok 5 yığın, yığınlar arası 3 m."))
    # Fabrika/atölye içi izole sıvı depolama Ek-12/B
    if g.sivi_depo_alani_m2 > 0:
        toplam_L = sum(t.hacim_L for t in g.sivi_tanklar if t.tur == "depo_icinde")
        alan = g.sivi_depo_alani_m2
        uygun_satir = None
        for amax, lm2, dk, kor in T.EK12B:
            if alan <= amax and kor == g.sivi_depo_yangin_korunum and g.sivi_depo_dayanim_dk >= dk:
                uygun_satir = (amax, lm2, dk, kor)
                break
        if uygun_satir:
            izin = uygun_satir[1] * alan
            s.append(Sonuc(B, "Fabrika/atölye içi tecrit edilmiş yanıcı sıvı deposu (Ek-12/B)", _r(izin, 0), "L", _karsilastir(toplam_L, izin) if toplam_L else BILGI, "Madde 118(3), Ek-12/B",
                           f"Alan {alan:g} m², dayanım ≥ {uygun_satir[2]} dk, yangın korunumu {'var' if uygun_satir[3] else 'yok'}: izin verilen {uygun_satir[1]} L/m² × {alan:g} m² = {izin:,.0f} L."))
        else:
            s.append(Sonuc(B, "Fabrika/atölye içi tecrit edilmiş yanıcı sıvı deposu (Ek-12/B)", "Koşullar sağlanmıyor", "", UYGUN_DEGIL, "Madde 118(3), Ek-12/B",
                           "En çok 15 m² (60 dk; 70 L/m², korunumlu 175 L/m²) veya 50 m² (120 dk; 140 L/m², korunumlu 350 L/m²). Alan veya dayanım süresi bu satırlara uymuyor."))
    if not s:
        s.append(Sonuc(B, "LPG ve yanıcı sıvı depolama", "Bu tesiste girilmedi", "", GEREKMEZ, "Madde 101–123"))
    return s


# ---------------------------------------------------------------------------
# 13. Çevre, orman ve itfaiye erişimi
# ---------------------------------------------------------------------------
def cevre_erisim(g: Girdi) -> list[Sonuc]:
    B = "13. Çevre ve itfaiye erişimi"
    s: list[Sonuc] = []
    if g.itfaiye_son_nokta_mesafe_m > 0:
        s.append(Sonuc(B, "İtfaiye aracının yaklaşabildiği son noktadan cepheye yatay uzaklık", g.itfaiye_son_nokta_mesafe_m, "m",
                       _karsilastir(g.itfaiye_son_nokta_mesafe_m, 45), "Madde 22(2)", "En çok 45 m."))
    else:
        s.append(Sonuc(B, "İtfaiye aracı yaklaşma uzaklığı", "≤ 45 m", "m", KONTROL, "Madde 22(2)"))
    if g.ic_yol_genislik_m > 0:
        gerek = 8.0 if g.ic_yol_cikmaz else 4.0
        s.append(Sonuc(B, "İç ulaşım yolu genişliği", g.ic_yol_genislik_m, "m", _karsilastir(g.ic_yol_genislik_m, gerek, ust=False), "Madde 22(3)", f"Olağan en az 4 m; çıkmaz sokakta en az 8 m (gerekli {gerek:g} m)."))
    if g.ic_yol_ic_yaricap_m > 0:
        s.append(Sonuc(B, "Dönemeç iç yarıçapı", g.ic_yol_ic_yaricap_m, "m", _karsilastir(g.ic_yol_ic_yaricap_m, 11, ust=False), "Madde 22(3)", "En az 11 m."))
    if g.ic_yol_dis_yaricap_m > 0:
        s.append(Sonuc(B, "Dönemeç dış yarıçapı", g.ic_yol_dis_yaricap_m, "m", _karsilastir(g.ic_yol_dis_yaricap_m, 15, ust=False), "Madde 22(3)", "En az 15 m."))
    if g.ic_yol_egim_yuzde > 0:
        s.append(Sonuc(B, "İç yol eğimi", g.ic_yol_egim_yuzde, "%", _karsilastir(g.ic_yol_egim_yuzde, 6), "Madde 22(3)", "En çok %6; düşey kurp en az R=100 m."))
    if g.ic_yol_serbest_yukseklik_m > 0:
        s.append(Sonuc(B, "Serbest yükseklik", g.ic_yol_serbest_yukseklik_m, "m", _karsilastir(g.ic_yol_serbest_yukseklik_m, 4, ust=False), "Madde 22(3)", "En az 4 m."))
    if g.ic_yol_tasima_yuku_ton > 0:
        s.append(Sonuc(B, "Taşıma yükü", g.ic_yol_tasima_yuku_ton, "ton", _karsilastir(g.ic_yol_tasima_yuku_ton, 15, ust=False), "Madde 22(3)", "10 tonluk arka dingil yükü düşünülerek en az 15 ton."))
    # Orman
    if g.orman_yakin and g.kullanim in ("endustriyel", "depo") and g.toplam_kapali_alan > 2000:
        e = g.arazi_egimi_yuzde
        if e > 55:
            asagi, diger, ack = 4.0, 2.0, "eğim > %55: aşağı yönde 4 kat, diğer yönlerde 2 kat"
        elif e >= 30:
            asagi, diger, ack = 2.0, 1.5, "eğim %30–55: aşağı yönde 2 kat, diğer yönlerde 1,5 kat"
        else:
            asagi, diger, ack = 1.0, 1.0, "eğim < %30: artırım yok"
        s.append(Sonuc(B, "Dış yangın bölgesi mesafesi (yapı cephesi/depolama sahasından)", 100, "m", GEREKLI, "Madde 21(5)", "Orman yangınlarının alev/sıcaklığının tesise sirayetini engellemek için 100 m mesafe içinde dış yangın bölgesi oluşturulur."))
        s.append(Sonuc(B, "Eğime göre dış yangın bölgesi — aşağı yön", 100 * asagi, "m", BILGI, "Madde 21(5)", ack))
        s.append(Sonuc(B, "Eğime göre dış yangın bölgesi — diğer yönler", 100 * diger, "m", BILGI, "Madde 21(5)", ack))
        s.append(Sonuc(B, "Dış yangın bölgesi düzenlemesi", "0–1,5 m yanıcısız; 1,5–10 m yanıcı/ağaç yok; 10–30 m ağaç arası ≥3 m; 30–100 m dal temizliği", "", GEREKLI, "Madde 21(5)a-ç",
                       "1,5 m içi çakıl/beton gibi yanmaz kaplama; 1,5–10 m'de eğim >%20 ise 3,5 m'ye kadar yanmaz kaplama; zemin yüzeyi 6 ayda bir kuru nebattan temizlenir."))
        s.append(Sonuc(B, "Orman sınırı ile parsel arası yol", "≥ 10 m", "", GEREKLI, "Madde 21(7), 22(5)", "Orman alanlarına bitişik parsel oluşturulamaz; itfaiye ulaşımı için beton iç ulaşım yolu."))
        s.append(Sonuc(B, "Dış cephe (orman alanı)", "Hiç yanmaz; doğrama ≥ 30 dk, çift cam", "", GEREKLI, "Madde 27(4)", "Binaya 15 m'den yakın eklentilerin dış cepheleri de hiç yanmaz veya en az 30 dk dayanıklı olmalıdır."))
        s.append(Sonuc(B, "Çatı (orman alanı)", "Taşıyıcı hiç yanmaz; altı en az zor yanıcı", "", GEREKLI, "Madde 28(4)"))
    return s


# ---------------------------------------------------------------------------
# 14. Acil durum ekipleri ve organizasyon
# ---------------------------------------------------------------------------
def ekipler(g: Girdi) -> list[Sonuc]:
    B = "14. Acil durum ekipleri"
    s: list[Sonuc] = []
    hesap_yuk = sum(kat_kullanici_yuku(k) for k in g.katlar)
    kisi = g.calisan_sayisi if g.calisan_sayisi > 0 else hesap_yuk
    kaynak = "girilen azami çalışan sayısı" if g.calisan_sayisi > 0 else "hesaplanan kullanıcı yükü"
    if kisi > 50 and g.kullanim != "apartman":
        s.append(Sonuc(B, "Acil durum ekipleri kurulması", "Mecburi", "", GEREKLI, "Madde 126(1)",
                       f"Binada {kisi:,.0f} kişi ({kaynak}) > 50 kişi: söndürme, kurtarma, koruma ve ilk yardım ekipleri."))
        s.append(Sonuc(B, "Söndürme ekibi", "en az 3 kişi", "", GEREKLI, "Madde 126(3)"))
        s.append(Sonuc(B, "Kurtarma ekibi", "en az 3 kişi", "", GEREKLI, "Madde 126(3)"))
        s.append(Sonuc(B, "Koruma ekibi", "en az 2 kişi", "", GEREKLI, "Madde 126(3)"))
        s.append(Sonuc(B, "İlk yardım ekibi", "en az 2 kişi", "", GEREKLI, "Madde 126(3)"))
        s.append(Sonuc(B, "Toplam asgari ekip personeli", 10, "kişi", GEREKLI, "Madde 126(3)", "Her ekipte bir ekip başı bulunur (Madde 126(4)). Vardiyalı çalışmada her vardiyada ekip bulunması önerilir."))
        s.append(Sonuc(B, "Yangın söndürme ve tahliye tatbikatı", "Yılda en az 1 kez", "", GEREKLI, "Madde 129(1)"))
    else:
        s.append(Sonuc(B, "Acil durum ekipleri", "Madde 126(1) kapsamında zorunlu değil", "", GEREKMEZ, "Madde 126(2)",
                       f"{kisi:,.0f} kişi ≤ 50: bina sahibi/yöneticisi/amirinin uygun göreceği tedbirler alınır."))
    s.append(Sonuc(B, "Yangın güvenliği sorumlusu", "Görevlendirilmeli", "", GEREKLI, "Madde 124–125"))
    return s


# ---------------------------------------------------------------------------
# Tümü
# ---------------------------------------------------------------------------
MODULLER: list[tuple[str, Callable[[Girdi], list[Sonuc]]]] = [
    ("Sınıflandırma", siniflandirma),
    ("Yangın dayanımı", yangin_dayanimi),
    ("Kompartıman", kompartiman),
    ("Kullanıcı yükü ve kaçış", kullanici_yuku_ve_kacis),
    ("Merdiven ve kapılar", merdiven_kapi),
    ("Yağmurlama", sprinkler_zorunlulugu),
    ("Su deposu ve pompa", su_deposu_ve_pompa),
    ("Dolap, hidrant, söndürücü", dolap_hidrant_sondurucu),
    ("Algılama ve aydınlatma", algilama_aydinlatma),
    ("Duman ve basınçlandırma", duman_basinclandirma),
    ("Kazan ve yakıt", kazan_yakit),
    ("Tehlikeli maddeler", tehlikeli_madde),
    ("Çevre ve erişim", cevre_erisim),
    ("Acil durum ekipleri", ekipler),
]


def hesapla(g: Girdi) -> list[Sonuc]:
    out: list[Sonuc] = []
    for _, fn in MODULLER:
        out.extend(fn(g))
    return out


def ozet(sonuclar: list[Sonuc]) -> dict[str, int]:
    d: dict[str, int] = {}
    for r in sonuclar:
        d[r.durum] = d.get(r.durum, 0) + 1
    return d
