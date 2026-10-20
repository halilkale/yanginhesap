"""Ayrıntılı hesap dökümü: her hesabın formülü, yerine konan sayılar ve sonucu adım adım.

Hesap motoru (`hesaplar.py`) ile aynı tablolar ve kurallar kullanılır; tutarlılık `tests/test_dokum.py` ile sınanır.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import hesaplar as H
from . import tablolar as T
from .modeller import Girdi


@dataclass
class Blok:
    baslik: str
    madde: str = ""
    adimlar: list[str] = field(default_factory=list)
    sonuc: str = ""
    durum: str = ""


@dataclass
class Bolum:
    ad: str
    bloklar: list[Blok] = field(default_factory=list)


def n(x, d: int = 2) -> str:
    """Türkçe sayı biçimi: binlik nokta, ondalık virgül; gereksiz sıfırlar atılır."""
    if isinstance(x, str):
        return x
    s = f"{x:,.{d}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    if "," in s:
        s = s.rstrip("0").rstrip(",")
    return s


def _kontrol(deger, sinir, ust=True, birim="") -> tuple[str, str]:
    ok = deger <= sinir + 1e-9 if ust else deger >= sinir - 1e-9
    isaret = "≤" if ust else "≥"
    return (f"{n(deger)} {birim} {isaret} {n(sinir)} {birim} ?  →  {'SAĞLANIYOR' if ok else 'SAĞLANMIYOR'}".replace("  ", " "), "UYGUN" if ok else "UYGUN DEĞİL")


def _durum_bul(sonuclar, kalem: str, bolum: str = "") -> str:
    for r in sonuclar:
        if kalem in r.kalem and bolum in r.bolum:
            return r.durum
    return ""


# ---------------------------------------------------------------------------
def hesap_dokumu(g: Girdi) -> list[Bolum]:
    S = H.hesapla(g)
    out: list[Bolum] = []
    out.append(_sinif(g))
    out.append(_dayanim(g))
    out.append(_kompartiman(g, S))
    out.append(_kullanici_ve_kacis(g, S))
    out.append(_merdiven_kapi(g))
    out.append(_sprinkler(g))
    out.append(_su(g, S))
    out.append(_dolap_hidrant(g))
    out.append(_algilama(g))
    out.append(_duman(g))
    out.append(_kazan(g))
    out.append(_tehlikeli(g))
    out.append(_cevre(g))
    out.append(_ekip(g))
    return [b for b in out if b.bloklar]


# --- 1 --------------------------------------------------------------------
def _sinif(g: Girdi) -> Bolum:
    b = Bolum("1. Sınıflandırma ve temel büyüklükler")
    grup = T.tehlike_grubu(g.tehlike)
    b.bloklar.append(Blok("Kullanım ve tehlike sınıfı", "Madde 8, 14, 19, Ek-1",
                          [f"Kullanım sınıfı: {T.KULLANIM_SINIFLARI[g.kullanim]}", f"Tehlike sınıfı: {T.TEHLIKE_SINIFLARI[g.tehlike]} (grup: {grup})",
                           f"Su deposu/pompa tasarım süresi (Madde 92(3)): düşük 30 dk, orta 60 dk, yüksek 90 dk → {T.SU_SURESI_DK[grup]} dk"],
                          f"{T.TEHLIKE_SINIFLARI[g.tehlike]}"))
    yb = H._yuksek_bina(g)
    b.bloklar.append(Blok("Yüksek bina testi", "Madde 4(ccc)",
                          [f"Bina yüksekliği {n(g.bina_yuksekligi)} m > 21,50 m ?  → {'evet' if g.bina_yuksekligi > 21.5 else 'hayır'}",
                           f"Yapı yüksekliği {n(g.yapi_yuksekligi)} m > 30,50 m ?  → {'evet' if g.yapi_yuksekligi > 30.5 else 'hayır'}"],
                          "Yüksek bina" if yb else "Yüksek bina değil"))
    b.bloklar.append(Blok("Yangın tahliye projesi gerekliliği", "Madde 7(4)",
                          [f"Toplam kapalı alan {n(g.toplam_kapali_alan, 0)} m² > 10.000 m² ?"],
                          "Gerekli" if g.toplam_kapali_alan > 10000 else "Zorunlu değil"))
    return b


# --- 2 --------------------------------------------------------------------
def _dayanim(g: Girdi) -> Bolum:
    b = Bolum("2. Yangın dayanımı")
    satir = T.EK3C[(g.kullanim, bool(g.yagmurlama_var))]
    h = g.bina_yuksekligi
    idx = 3 if h <= 21.5 else (4 if h <= 30.5 else 5)
    adim = [f"Ek-3/C satırı: {T.KULLANIM_SINIFLARI[g.kullanim]} — {'yağmurlama sistemli' if g.yagmurlama_var else 'yağmurlama sistemi yok'}",
            f"Bina yüksekliği {n(h)} m → sütun: {T.EK3C_SUTUNLAR[idx]}", f"Tablo değeri: {satir[idx]}"]
    b.bloklar.append(Blok("Üst katlar taşıyıcı sistem / kompartıman dayanımı", "Ek-3/C", adim, f"{satir[idx]}" + ("" if satir[idx] == T.IY else " dk")))
    if g.bodrum_kat_sayisi > 0:
        d = g.bodrum_derinligi
        bi = 0 if d > 10 else (1 if d > 5 else 2)
        b.bloklar.append(Blok("Bodrum katlar dayanımı", "Ek-3/C",
                              [f"Bodrum derinliği {n(d)} m → sütun: {T.EK3C_SUTUNLAR[bi]}", f"Tablo değeri: {satir[bi]}",
                               "Bodrum üstü döşeme için: max(bodrum süresi, üst kat süresi, 90 dk) (Ek-3/C dipnot 1, Ek-3/B-3d)"],
                              f"{satir[bi]} dk"))
    if g.tasiyici == "ahsap" and g.ahsap_b_mm and g.ahsap_h_mm and isinstance(satir[idx], (int, float)):
        kay = g.ahsap_yanma_hizi * satir[idx]
        b2 = g.ahsap_b_mm - 2 * kay
        h2 = g.ahsap_h_mm - (2 * kay if g.ahsap_yuzey >= 4 else kay)
        b.bloklar.append(Blok("Ahşap eleman kalan kesit", "Madde 23(6)",
                              [f"Kömürleşme = yanma hızı × süre = {n(g.ahsap_yanma_hizi)} mm/dk × {satir[idx]} dk = {n(kay)} mm",
                               f"Kalan b = {n(g.ahsap_b_mm, 0)} − 2×{n(kay)} = {n(b2)} mm",
                               f"Kalan h = {n(g.ahsap_h_mm, 0)} − {'2×' if g.ahsap_yuzey >= 4 else ''}{n(kay)} = {n(h2)} mm"],
                              f"Kalan kesit {n(max(b2, 0), 0)} × {n(max(h2, 0), 0)} mm (statik hesapla doğrulanmalı)"))
    if g.tasiyici == "celik":
        muaf = g.kat_sayisi == 1 and g.taban_alani < 5000
        b.bloklar.append(Blok("Çelik taşıyıcı yalıtımı", "Madde 23(4)",
                              [f"Tek katlı mı? (kat sayısı {g.kat_sayisi})  ve  taban alanı {n(g.taban_alani, 0)} m² < 5.000 m² ?  → {'evet (muaf)' if muaf else 'hayır (muaf değil)'}"],
                              "Yalıtım gerekmez" if muaf else "Yalıtım gerekli"))
    return b


# --- 3 --------------------------------------------------------------------
def _kompartiman(g: Girdi, S) -> Bolum:
    b = Bolum("3. Yangın kompartımanı")
    limit, nota, ack = T.ek4_limit(g.kullanim, g.tehlike)
    alan = g.ozet_alan()
    ks = g.algilama_var or g.yagmurlama_var or g.duman_tahliye_var
    adim = [f"Ek-4 satırı: {ack}", f"Kompartıman alanı (proje): {n(alan, 0)} m²"]
    if limit is None:
        sonuc, durum = "Sınırlama yok", "UYGUN"
    else:
        adim.append(f"Tablo sınırı: {n(limit, 0)} m²")
        adim.append(f"Uygun yangın kontrol sistemleri (algılama/yağmurlama/duman tahliye): {'var' if ks else 'yok'}; bina {'tek' if g.kat_sayisi == 1 else 'çok'} katlı")
        if nota == 1 and ks:
            adim.append(f"Dipnot 1: sınır 2 katı → {n(limit * 2, 0)} m²")
            sonuc, durum = _kontrol(alan, limit * 2, True, "m²")
        elif (nota == 2 and ks) or (nota == 3 and (g.kat_sayisi == 1 or ks)):
            adim.append(f"Dipnot {nota}: kompartıman alanı sınırsız")
            sonuc, durum = "Sınırsız (koşullu — itfaiye değerlendirmesi)", "KOŞULLU UYGUN"
        else:
            sonuc, durum = _kontrol(alan, limit, True, "m²")
            if durum != "UYGUN":
                adim.append(f"Gerekli kompartıman sayısı = ⌈{n(g.en_buyuk_kat_alani, 0)} / {n(limit, 0)}⌉ = {math.ceil(g.en_buyuk_kat_alani / limit)}")
    b.bloklar.append(Blok("Kompartıman alanı", "Madde 24, Ek-4", adim, sonuc, durum))
    return b


# --- 4 --------------------------------------------------------------------
def _kullanici_ve_kacis(g: Girdi, S) -> Bolum:
    b = Bolum("4. Kullanıcı yükü ve kaçış yolları")
    e5 = T.EK5B[T.KULLANIM_EK5B[g.kullanim]]
    spr = 1 if g.yagmurlama_var else 0
    genel = 0.0
    for kat in g.katlar:
        adim = []
        toplam = 0.0
        for m in kat.mahaller:
            if not m.sayilir:
                adim.append(f"{m.ad}: aynı anda kullanılmayan mahal, hesaba katılmadı (Madde 31(6))")
                continue
            ham = m.alan / m.katsayi if m.katsayi > 0 else 0.0
            sat = f"{m.ad}: {n(m.alan)} m² ÷ {n(m.katsayi)} m²/kişi = {n(ham)} kişi"
            nm = ham
            if m.kisi_belirli and m.kisi_belirli > 0:
                nm = max(ham, m.kisi_belirli)
                sat += f"; belirli kişi sayısı {n(m.kisi_belirli)} → max = {n(nm)} kişi"
            toplam += nm
            adim.append(sat)
        genel += toplam
        adim.append("Toplam = " + " + ".join(n(x) for x in _mahal_kisileri(kat)) + f" = {n(toplam)} kişi")
        b.bloklar.append(Blok(f"Kullanıcı yükü — {kat.ad}", "Madde 32(1), Ek-5/A", adim, f"{n(toplam)} kişi"))
        N = toplam
        if N <= 0:
            continue
        # genişlik
        adim = []
        for ad, anahtar in [("Dışarı çıkış kapısı", "dis_kapi"), ("Diğer kapılar", "diger_kapi"), ("Kaçış merdiveni", "merdiven"), ("Rampa/koridor", "koridor")]:
            u = e5[anahtar]
            adim.append(f"{ad}: W = N ÷ {u} kişi × 50 cm = {n(N)} ÷ {u} × 50 = {n(N / u * 50)} cm")
        tur_ad, anahtar = H.CIKIS_TURU_AD[kat.cikis_turu]
        w_gerek = N / e5[anahtar] * 50
        if N > 2000: w_min = 200
        elif N > 500: w_min = 150
        elif N >= 50: w_min = 100
        else: w_min = 80
        if H._yuksek_bina(g):
            w_min = max(w_min, 120)
        adim.append(f"Asgari tekil çıkış genişliği (N = {n(N)} kişi): {w_min} cm" + (" (yüksek bina ≥120)" if H._yuksek_bina(g) else ""))
        if kat.mevcut_genislik_cm > 0:
            adim.append(f"Kontrol ({tur_ad}): mevcut {n(kat.mevcut_genislik_cm)} cm ≥ gerekli {n(w_gerek)} cm ?")
            _, dr = _kontrol(kat.mevcut_genislik_cm, w_gerek, False)
            sonuc = f"mevcut {n(kat.mevcut_genislik_cm)} cm / gerekli {n(w_gerek)} cm"
        else:
            dr, sonuc = "", f"gerekli en az {n(w_gerek)} cm (mevcut değer girilmedi)"
        b.bloklar.append(Blok(f"Çıkış genişliği — {kat.ad}", "Madde 32(2), 33(1), Ek-5/B", adim, sonuc, dr))
        if kat.tekil_cikis_genislik_cm > 0:
            s_, d_ = _kontrol(kat.tekil_cikis_genislik_cm, w_min, False, "cm")
            b.bloklar.append(Blok(f"En dar tekil çıkış — {kat.ad}", "Madde 33(1)", [f"En dar çıkış {n(kat.tekil_cikis_genislik_cm)} cm ≥ asgari {w_min} cm ?"], s_, d_))
        # çıkış sayısı
        gs = 2
        if N > 1000: gs = 4
        elif N > 500: gs = 3
        tek = (g.kullanim in ("endustriyel", "depo", "buro", "ticaret") and g.yapi_yuksekligi < 21.5 and N < 50 and g.yanmaz_malzeme_yapim
               and not g.kolay_alevlenici and kat.en_uzak_mesafe_m and kat.en_uzak_mesafe_m <= e5["tek"][spr])
        if tek:
            gs = 1
        adim = [f"Kural: en az 2 çıkış; N > 500 → en az 3; N > 1000 → en az 4  (N = {n(N)})",
                f"Madde 52 tek çıkış istisnası: {'şartlar sağlandı' if tek else 'uygulanmıyor'}"]
        if kat.cikis_sayisi:
            adim.append(f"Projedeki çıkış sayısı {kat.cikis_sayisi} ≥ {gs} ?")
            dr = "UYGUN" if kat.cikis_sayisi >= gs else "UYGUN DEĞİL"
        else:
            dr = ""
        b.bloklar.append(Blok(f"Çıkış sayısı — {kat.ad}", "Madde 39, 52", adim, f"en az {gs} çıkış", dr))
        # kaçış uzaklığı
        yon = "iki" if kat.yon == "iki" else "tek"
        taban = e5[yon][spr]
        carpan = 1.0
        if g.kullanim == "endustriyel" and not g.kolay_alevlenici:
            carpan = 2.0 if g.mevcut_yapi else 1.5
        elif g.kullanim == "depo" and not g.kolay_alevlenici and g.mevcut_yapi:
            carpan = 2.0
        limit = taban * carpan
        adim = [f"Ek-5/B ({'yağmurlamalı' if spr else 'yağmurlamasız'}, {yon} yön): {taban} m",
                f"Çarpan: {n(carpan)} ({'kolay alevlenici madde yok → artırım' if carpan > 1 else 'artırım yok'})", f"Sınır = {taban} × {n(carpan)} = {n(limit)} m"]
        dr = ""
        sonuc = f"sınır {n(limit)} m"
        if kat.en_uzak_mesafe_m > 0:
            t_, dr = _kontrol(kat.en_uzak_mesafe_m, limit, True, "m")
            adim.append("Ölçülen en uzak mesafe: " + t_)
            sonuc = f"ölçülen {n(kat.en_uzak_mesafe_m)} m / sınır {n(limit)} m"
        if kat.kus_ucusu_mesafe_m > 0:
            adim.append(f"Kuş uçuşu: {n(kat.kus_ucusu_mesafe_m)} m ≤ 2/3 × {n(limit)} = {n(limit * 2 / 3)} m ?")
        if kat.cikmaz_mesafe_m > 0:
            adim.append(f"Çıkmaz koridor: {n(kat.cikmaz_mesafe_m)} m ≤ {e5['cikmaz'][spr]} m ?")
        if kat.mekan_diyagonal_m > 0 and kat.cikislar_arasi_mesafe_m > 0:
            oran = 3 if g.yagmurlama_var else 2
            adim.append(f"Çıkışlar arası: {n(kat.cikislar_arasi_mesafe_m)} m ≥ diyagonal {n(kat.mekan_diyagonal_m)} / {oran} = {n(kat.mekan_diyagonal_m / oran)} m ?")
        b.bloklar.append(Blok(f"Kaçış uzaklığı — {kat.ad}", "Madde 32(3)-(6), 39(3), Ek-5/B", adim, sonuc, dr))
    if g.katlar:
        b.bloklar.append(Blok("Tüm katlar toplam kullanıcı yükü", "Madde 32", [f"Σ katlar = {n(genel)} kişi"], f"{n(genel)} kişi"))
    return b


def _mahal_kisileri(kat) -> list[float]:
    out = []
    for m in kat.mahaller:
        if not m.sayilir:
            continue
        x = m.alan / m.katsayi if m.katsayi > 0 else 0.0
        if m.kisi_belirli and m.kisi_belirli > 0:
            x = max(x, m.kisi_belirli)
        out.append(x)
    return out


# --- 5 --------------------------------------------------------------------
def _merdiven_kapi(g: Girdi) -> Bolum:
    b = Bolum("5. Kaçış merdivenleri ve kapılar")
    for m in g.merdivenler:
        adim, drm = [], []
        if m.rihts_mm:
            adim.append("Rıht: " + _kontrol(m.rihts_mm, 175, True, "mm")[0]); drm.append(_kontrol(m.rihts_mm, 175)[1])
        if m.basamak_genislik_mm:
            adim.append("Basış: " + _kontrol(m.basamak_genislik_mm, 250, False, "mm")[0]); drm.append(_kontrol(m.basamak_genislik_mm, 250, False)[1])
        if m.sahanlik_arasi_basamak:
            ok = 4 <= m.sahanlik_arasi_basamak <= 17
            adim.append(f"Sahanlık arası basamak: 4 ≤ {m.sahanlik_arasi_basamak} ≤ 17 ?  → {'SAĞLANIYOR' if ok else 'SAĞLANMIYOR'}"); drm.append("UYGUN" if ok else "UYGUN DEĞİL")
        if m.sahanlik_arasi_kot_cm:
            adim.append("Sahanlıklar arası kot: " + _kontrol(m.sahanlik_arasi_kot_cm, 300, True, "cm")[0]); drm.append(_kontrol(m.sahanlik_arasi_kot_cm, 300)[1])
        if m.bas_yuksekligi_cm:
            adim.append("Baş yüksekliği: " + _kontrol(m.bas_yuksekligi_cm, 210, False, "cm")[0]); drm.append(_kontrol(m.bas_yuksekligi_cm, 210, False)[1])
        if m.genislik_cm:
            w = 120 if H._yuksek_bina(g) else 80
            adim.append("Temiz genişlik: " + _kontrol(m.genislik_cm, w, False, "cm")[0]); drm.append(_kontrol(m.genislik_cm, w, False)[1])
        kg = 90 if (g.bodrum_kat_sayisi > 0 or m.hizmet_verilen_kat >= 4) else 60
        if m.kapi_dayanim_dk:
            adim.append(f"Kapı dayanımı ({m.hizmet_verilen_kat} kata hizmet → en az {kg} dk): " + _kontrol(m.kapi_dayanim_dk, kg, False, "dk")[0]); drm.append(_kontrol(m.kapi_dayanim_dk, kg, False)[1])
        if m.duvar_dayanim_dk:
            adim.append("Yuva duvarı: " + _kontrol(m.duvar_dayanim_dk, 120, False, "dk")[0]); drm.append(_kontrol(m.duvar_dayanim_dk, 120, False)[1])
        if adim:
            b.bloklar.append(Blok(f"Kaçış merdiveni {m.ad}", "Madde 33, 38, 41, 47", adim, "Tümü uygun" if all(x == "UYGUN" for x in drm) else "Uygunsuz madde var",
                                  "UYGUN" if all(x == "UYGUN" for x in drm) else "UYGUN DEĞİL"))
    for k in g.kapilar:
        adim, drm = [], []
        if k.temiz_genislik_cm:
            tek = k.kanat_sayisi <= 1
            ust = 120 if tek else None
            ok = k.temiz_genislik_cm >= 80 and (ust is None or k.temiz_genislik_cm <= ust)
            adim.append(f"Temiz genişlik: 80 ≤ {n(k.temiz_genislik_cm)} cm" + (f" ≤ 120 cm (tek kanatlı)" if tek else " (iki/çok kanatlı: üst sınır yok)") + f" ?  → {'SAĞLANIYOR' if ok else 'SAĞLANMIYOR'}")
            if not ok and tek and k.temiz_genislik_cm > 120:
                adim.append("Tek kanatlı çıkış kapısı en çok 120 cm olabilir (Madde 33(5)b, 47(4)); bu genişlik için kapı iki kanatlı yapılmalıdır.")
            drm.append("UYGUN" if ok else "UYGUN DEĞİL")
        if k.yukseklik_cm:
            adim.append("Yükseklik: " + _kontrol(k.yukseklik_cm, 200, False, "cm")[0]); drm.append(_kontrol(k.yukseklik_cm, 200, False)[1])
        if k.acma_kuvveti_N:
            adim.append("Açma kuvveti: " + _kontrol(k.acma_kuvveti_N, 110, True, "N")[0]); drm.append(_kontrol(k.acma_kuvveti_N, 110)[1])
        if adim:
            b.bloklar.append(Blok(f"Kapı {k.ad}", "Madde 33(5), 47", adim, "Tümü uygun" if all(x == "UYGUN" for x in drm) else "Uygunsuz madde var",
                                  "UYGUN" if all(x == "UYGUN" for x in drm) else "UYGUN DEĞİL"))
    return b


# --- 6 --------------------------------------------------------------------
def _sprinkler(g: Girdi) -> Bolum:
    b = Bolum("6. Yağmurlama (sprinkler)")
    adim = [f"Yapı yüksekliği {n(g.yapi_yuksekligi)} m > 30,50 m (konut dışı) ?  → {'evet' if g.yapi_yuksekligi > 30.5 and g.kullanim != 'apartman' else 'hayır'}   [Madde 96(2)a]",
            f"Kapalı otopark {n(g.otopark_alani, 0)} m² > 600 m² ?  → {'evet' if g.otopark_alani > 600 else 'hayır'}   [Madde 96(2)c]",
            f"Kolay alevlenici madde var ve toplam alan {n(g.toplam_kapali_alan, 0)} m² > 1.000 m² ?  → {'evet' if g.kolay_alevlenici and g.toplam_kapali_alan > 1000 else 'hayır'}   [Madde 96(2)e]"]
    zorunlu = (g.kullanim != "apartman" and g.yapi_yuksekligi > 30.5) or g.otopark_alani > 600 or (g.kolay_alevlenici and g.toplam_kapali_alan > 1000) \
        or (g.kullanim == "ticaret" and g.toplam_kapali_alan > 2000)
    dr = ("UYGUN" if g.yagmurlama_var else "UYGUN DEĞİL") if zorunlu else ""
    b.bloklar.append(Blok("Sprinkler zorunluluğu", "Madde 96(2)", adim, "Mecburi" if zorunlu else "Zorunlu değil", dr))
    if g.yagmurlama_var:
        if g.spr_baslik_alani_m2 > 0:
            bas, kay = g.spr_baslik_alani_m2, "kullanıcı girdisi"
        elif g.tehlike in ("DT", "OT1"):
            bas, kay = 21.0, "Madde 96(5)"
        elif g.tehlike.startswith("OT"):
            bas, kay = 12.0, "TS EN 12845 (tipik)"
        else:
            bas, kay = 9.0, "TS EN 12845 (tipik)"
        adet = math.ceil(g.toplam_kapali_alan / bas)
        b.bloklar.append(Blok("Yaklaşık başlık adedi", "Madde 96(5)",
                              [f"Başlık başına koruma alanı: {n(bas)} m² ({kay})", f"Adet = ⌈ {n(g.toplam_kapali_alan, 0)} m² ÷ {n(bas)} m² ⌉ = {adet}",
                               f"Yedek başlık = en az 6 (veya sistemin %1'i) = {max(6, math.ceil(adet * 0.01))}"], f"≈ {adet} adet (ön hesap)"))
    return b


# --- 7 --------------------------------------------------------------------
def _su(g: Girdi, S) -> Bolum:
    b = Bolum("7. Yangın suyu deposu ve pompa")
    grup = T.tehlike_grubu(g.tehlike)
    sure = T.SU_SURESI_DK[grup]
    dolap_d, hid_d, _ = T.EK8C[T.ek8c_anahtar(g.tehlike)]
    adim = []
    q_spr = q_dolap = q_hid = 0.0
    if g.yagmurlama_var:
        r = H._spr_debi(g)
        if r:
            yog, alan, q_spr, nt, kul = r
            adim.append(f"Sprinkler: Ek-8/B {T.TEHLIKE_SINIFLARI[kul]} — yoğunluk {n(yog)} mm/dk, koruma alanı {n(alan, 0)} m² ({'kuru' if g.yagmurlama_tipi == 'kuru' else 'ıslak'})"
                        + (f" [{nt}]" if nt else ""))
            adim.append(f"Q_sprinkler = {n(yog)} mm/dk × {n(alan, 0)} m² = {n(q_spr, 0)} l/dk")
        else:
            adim.append("Sprinkler: Yüksek Tehlike-4 / yoğun su — hidrolik hesap gerekir")
    if g.dolap_var:
        birim = dolap_d if (g.yagmurlama_var or not g.sadece_dolap) else (400 if g.dolap_tipi == "yassi" else 100)
        q_dolap = g.es_zamanli_dolap * birim
        adim.append(f"Q_dolap = {g.es_zamanli_dolap} eş zamanlı dolap × {birim} l/dk = {n(q_dolap, 0)} l/dk   [Ek-8/C]")
    if g.hidrant_var:
        q_hid = max(1900.0, hid_d) if g.sadece_hidrant else hid_d
        adim.append(f"Q_hidrant = {n(q_hid, 0)} l/dk   [Ek-8/C" + (", sadece hidrant: ≥1900" if g.sadece_hidrant else "") + "]")
    qt = q_spr + q_dolap + q_hid
    if qt <= 0:
        return b
    adim.append(f"Q_toplam = {n(q_spr, 0)} + {n(q_dolap, 0)} + {n(q_hid, 0)} = {n(qt, 0)} l/dk = {n(qt * 0.06)} m³/h")
    v = qt * sure / 1000
    adim.append(f"Süre ({grup} tehlike) = {sure} dk")
    adim.append(f"V = Q_toplam × süre ÷ 1000 = {n(qt, 0)} × {sure} ÷ 1000 = {n(v)} m³")
    vt = None
    if g.yagmurlama_var:
        tv = T.EK8A.get((g.tehlike, "kuru" if g.yagmurlama_tipi == "kuru" else "islak"))
        if tv and g.spr_yukseklik_h <= 45:
            idx = 0 if g.spr_yukseklik_h <= 15 else (1 if g.spr_yukseklik_h <= 30 else 2)
            vt = tv[idx]
            adim.append(f"Ek-8/A tablo: h = {n(g.spr_yukseklik_h)} m ({['h≤15', '15<h≤30', '30<h≤45'][idx]}) → {vt} m³")
    oneri = max(v, vt or 0)
    adim.append(f"Önerilen = max(hesap {n(v)}; tablo {vt if vt is not None else '—'}) = {n(oneri)} m³")
    dr = ""
    sonuc = f"{n(oneri)} m³"
    if g.mevcut_su_deposu_m3 > 0:
        adim.append(f"Mevcut depo {n(g.mevcut_su_deposu_m3)} m³ ≥ {n(oneri)} m³ ?")
        dr = "UYGUN" if g.mevcut_su_deposu_m3 >= oneri else "UYGUN DEĞİL"
        sonuc += f" (mevcut {n(g.mevcut_su_deposu_m3)} m³)"
    b.bloklar.append(Blok("Su deposu hacmi", "Madde 92, Ek-8/A-B-C", adim, sonuc, dr))
    # pompa
    adim = [f"Q_pompa = Q_toplam × 60 ÷ 1000 = {n(qt, 0)} × 0,06 = {n(qt * 0.06)} m³/h"]
    hy = g.statik_yukseklik_mSS + g.boru_kaybi_mSS + g.akma_basinci_mSS
    sonuc = f"Q ≥ {n(qt * 0.06)} m³/h"
    dr = ""
    if g.statik_yukseklik_mSS or g.boru_kaybi_mSS:
        adim.append(f"Hy = statik {n(g.statik_yukseklik_mSS)} + boru kaybı {n(g.boru_kaybi_mSS)} + akma basıncı {n(g.akma_basinci_mSS)} = {n(hy)} mSS")
        sonuc += f"; Hy = {n(hy)} mSS"
        if g.pompa_anma_basma_mSS > 0:
            adim.append(f"Pompa anma basma {n(g.pompa_anma_basma_mSS)} mSS ≥ Hy {n(hy)} mSS ?")
            dr = "UYGUN" if g.pompa_anma_basma_mSS >= hy else "KOŞULLU UYGUN"
    if g.pompa_anma_basma_mSS > 0 and g.pompa_kapali_vana_basma_mSS > 0:
        lim = 1.4 * g.pompa_anma_basma_mSS
        adim.append(f"Kapalı vana basma {n(g.pompa_kapali_vana_basma_mSS)} ≤ 1,40 × {n(g.pompa_anma_basma_mSS)} = {n(lim)} mSS ?")
    if g.pompa_anma_basma_mSS > 0 and g.pompa_150_debi_basma_mSS > 0:
        lim = 0.65 * g.pompa_anma_basma_mSS
        adim.append(f"%150 debide basma {n(g.pompa_150_debi_basma_mSS)} ≥ 0,65 × {n(g.pompa_anma_basma_mSS)} = {n(lim)} mSS ?")
    if g.pompa_anma_debi_m3h > 0:
        adim.append(f"Pompa azami karşılanabilir debi = 1,30 × {n(g.pompa_anma_debi_m3h)} = {n(1.3 * g.pompa_anma_debi_m3h)} m³/h ≥ {n(qt * 0.06)} m³/h ?")
    b.bloklar.append(Blok("Yangın pompası", "Madde 93", adim, sonuc, dr))
    return b


# --- 8 --------------------------------------------------------------------
def _dolap_hidrant(g: Girdi) -> Bolum:
    b = Bolum("8. Yangın dolabı, hidrant ve söndürücüler")
    aralik = 45 if g.yagmurlama_var else 30
    kat = max(1, g.kat_sayisi)
    nd = H.aralik_adedi(g.bina_boyu, g.bina_eni, aralik) * kat
    b.bloklar.append(Blok("Yangın dolabı adedi (ön hesap)", "Madde 94(b)2",
                          [f"Dolaplar arası azami uzaklık = {aralik} m ({'yağmurlamalı: 45 m' if g.yagmurlama_var else 'yağmurlamasız: 30 m'})",
                           f"Adet/kat = ⌈{n(g.bina_boyu, 0)} ÷ {aralik}⌉ × ⌈{n(g.bina_eni, 0)} ÷ {aralik}⌉ = {math.ceil(g.bina_boyu / aralik)} × {math.ceil(g.bina_eni / aralik)} = {H.aralik_adedi(g.bina_boyu, g.bina_eni, aralik)}",
                           f"Toplam = {H.aralik_adedi(g.bina_boyu, g.bina_eni, aralik)} × {kat} kat = {nd}"], f"≈ {nd} dolap"))
    risk = {"cok_riskli": 50, "riskli": 100, "orta": 125, "az": 150}[g.hidrant_risk]
    cevre = 2 * (g.bina_boyu + g.bina_eni)
    nh = max(1, math.ceil(cevre / risk - 1e-9))
    b.bloklar.append(Blok("Hidrant adedi (ön hesap)", "Madde 95(3)",
                          [f"Bina çevresi = 2 × ({n(g.bina_boyu, 0)} + {n(g.bina_eni, 0)}) = {n(cevre, 0)} m", f"Hidrantlar arası azami uzaklık ({g.hidrant_risk}) = {risk} m",
                           f"Adet = ⌈{n(cevre, 0)} ÷ {risk}⌉ = {nh}"], f"≈ {nh} hidrant"))
    toplam_taban = H._tesis_toplam_taban(g)
    b.bloklar.append(Blok("Dış hidrant zorunluluğu", "Madde 95(7)", [f"Taban alanları toplamı {n(toplam_taban, 0)} m² > 5.000 m² ?"],
                          "Mecburi" if toplam_taban > 5000 else "Zorunlu değil"))
    kb = 500 if T.tehlike_grubu(g.tehlike) == "dusuk" else 250
    a1 = math.ceil(g.toplam_kapali_alan / kb - 1e-9)
    kare = 25 * math.sqrt(2)
    a2 = H.kapsama_adedi(g.bina_boyu, g.bina_eni, 25.0) * kat
    b.bloklar.append(Blok("Taşınabilir söndürücü adedi", "Madde 99(2),(4)",
                          [f"Alan kriteri: ⌈{n(g.toplam_kapali_alan, 0)} m² ÷ {kb} m²⌉ = {a1} adet",
                           f"Menzil kriteri (≤25 m): kare kenarı = 25 × √2 = {n(kare)} m; adet/kat = ⌈{n(g.bina_boyu, 0)} ÷ {n(kare)}⌉ × ⌈{n(g.bina_eni, 0)} ÷ {n(kare)}⌉ = {H.kapsama_adedi(g.bina_boyu, g.bina_eni, 25.0)}; × {kat} kat = {a2}",
                           f"Gerekli = max({a1}; {a2}) = {max(a1, a2)}"], f"≥ {max(a1, a2)} adet"))
    return b


# --- 9 --------------------------------------------------------------------
def _algilama(g: Girdi) -> Bolum:
    b = Bolum("9. Algılama, uyarı ve acil aydınlatma")
    a = 60 * math.sqrt(2)
    adet = H.kapsama_adedi(g.bina_boyu, g.bina_eni, 60.0)
    cikis = max([k.cikis_sayisi for k in g.katlar] + [2])
    toplam = max(adet, cikis) * max(1, g.kat_sayisi)
    b.bloklar.append(Blok("Yangın uyarı butonu adedi (ön hesap)", "Madde 75(2)",
                          [f"Erişim yarıçapı 60 m → kare kenarı = 60 × √2 = {n(a)} m", f"Adet/kat = ⌈{n(g.bina_boyu, 0)} ÷ {n(a)}⌉ × ⌈{n(g.bina_eni, 0)} ÷ {n(a)}⌉ = {adet}",
                           f"En az bir çıkış yanında bir buton → max({adet}; {cikis} çıkış) = {max(adet, cikis)}", f"Toplam = {max(adet, cikis)} × {max(1, g.kat_sayisi)} kat = {toplam}"],
                          f"≥ {toplam} buton"))
    kisi = sum(H.kat_kullanici_yuku(k) for k in g.katlar)
    sure = 120 if kisi > 200 else 60
    b.bloklar.append(Blok("Acil aydınlatma süresi", "Madde 72(3)", [f"Kullanıcı yükü {n(kisi)} kişi > 200 ?  → {'evet: 120 dk' if kisi > 200 else 'hayır: 60 dk'}"], f"{sure} dk"))
    k_ = 200 if g.isaret_aydinlatma == "icten" else 100
    dmax = k_ * g.isaret_yuksekligi_cm / 100
    adim = [f"Görülebilirlik uzaklığı = işaret yüksekliği × {k_} = {n(g.isaret_yuksekligi_cm)} cm × {k_} = {n(dmax)} m  ({'içeriden aydınlatılan' if k_ == 200 else 'dışarıdan aydınlatılan'})"]
    sonuc = f"{n(dmax)} m"
    if g.kacis_yolu_uzunlugu_m > 0:
        nn = math.ceil(g.kacis_yolu_uzunlugu_m / dmax - 1e-9)
        adim.append(f"İşaret adedi = ⌈{n(g.kacis_yolu_uzunlugu_m, 0)} m ÷ {n(dmax)} m⌉ = {nn}")
        sonuc += f"; ≥ {nn} işaret"
    b.bloklar.append(Blok("Yönlendirme işareti", "Madde 73(4)", adim, sonuc))
    return b


# --- 10 -------------------------------------------------------------------
def _duman(g: Girdi) -> Bolum:
    b = Bolum("10. Duman kontrolü ve basınçlandırma")
    for m in g.duman_mahalleri:
        hacim = m.alan_m2 * m.yukseklik_m
        q = 10 * hacim
        zor = m.tur in ("kazan", "otopark", "bodrum_depo") and m.alan_m2 > 2000
        b.bloklar.append(Blok(f"Mekanik duman tahliyesi — {m.ad}", "Madde 88(3)",
                              [f"Alan {n(m.alan_m2, 0)} m² > 2.000 m² ?  → {'evet (zorunlu)' if zor else 'hayır'}", f"Hacim = {n(m.alan_m2, 0)} × {n(m.yukseklik_m)} = {n(hacim, 0)} m³",
                               f"Debi = 10 hava değişimi/saat × {n(hacim, 0)} = {n(q, 0)} m³/h = {n(q / 3600)} m³/s"], f"{n(q, 0)} m³/h"))
    h = g.merdiven_kovasi_yuksekligi or (g.bina_yuksekligi if g.kat_sayisi > 1 else 0)
    zor = (g.kullanim != "apartman" and h > 30.5) or g.bodrum_kat_sayisi > 4 or (g.kullanim == "apartman" and g.yapi_yuksekligi > 51.5)
    adim = [f"Merdiven kovası yüksekliği {n(h)} m > 30,50 m ?  → {'evet' if h > 30.5 else 'hayır'}", f"Bodrum kat sayısı {g.bodrum_kat_sayisi} > 4 ?  → {'evet' if g.bodrum_kat_sayisi > 4 else 'hayır'}"]
    sonuc = "Basınçlandırma zorunlu" if zor else "Zorunlu değil"
    if zor:
        q = 1.0 * g.basinc_kapi_alani_m2 * 3 + g.basinc_sizinti_debisi_m3s
        adim.append(f"Asgari hava debisi = 1 m/s × {n(g.basinc_kapi_alani_m2)} m² × 3 açık kapı + sızıntı {n(g.basinc_sizinti_debisi_m3s)} = {n(q)} m³/s = {n(q * 3600, 0)} m³/h")
    b.bloklar.append(Blok("Merdiven basınçlandırması", "Madde 89", adim, sonuc))
    return b


# --- 11 -------------------------------------------------------------------
def _kazan(g: Girdi) -> Bolum:
    b = Bolum("11. Kazan dairesi, yakıt")
    if g.kazan_var and g.kazan_kw >= 50:
        iki = g.kazan_kw > 350 or g.kazan_alani_m2 > 100
        gerek = 2 if iki else 1
        b.bloklar.append(Blok("Kazan dairesi çıkış kapısı", "Madde 54(5)",
                              [f"Isıl kapasite {n(g.kazan_kw, 0)} kW > 350 kW ?  veya alan {n(g.kazan_alani_m2, 0)} m² > 100 m² ?  → {'evet: en az 2 kapı' if iki else 'hayır: en az 1 kapı'}",
                               f"Projedeki kapı sayısı {g.kazan_kapi_sayisi} ≥ {gerek} ?"], f"en az {gerek} kapı", "UYGUN" if g.kazan_kapi_sayisi >= gerek else "UYGUN DEĞİL"))
    if g.yakit_tank_L > 0:
        izin = {"bodrum_varil": 1000, "bodrum_sac": 3000, "bodrum_komur": 40000, "bina_disi": 40000}.get(g.yakit_yeri)
        adim = [f"Havuzlama = tank hacminin 1/3'ü = {n(g.yakit_tank_L, 0)} ÷ 3 = {n(g.yakit_tank_L / 3, 0)} L"]
        if izin:
            adim.insert(0, f"Depolama sınırı ({g.yakit_yeri}) {n(izin, 0)} L ≥ {n(g.yakit_tank_L, 0)} L ?")
        b.bloklar.append(Blok("Yakıt deposu", "Madde 56", adim, f"havuzlama ≥ {n(g.yakit_tank_L / 3, 0)} L"))
    return b


# --- 12 -------------------------------------------------------------------
def _tehlikeli(g: Girdi) -> Bolum:
    b = Bolum("12. Tehlikeli maddeler")
    if g.lpg_tup_kg > 0:
        _, bina, cadde = H._band(T.EK9, g.lpg_tup_kg)
        b.bloklar.append(Blok("LPG tüp deposu emniyet uzaklığı", "Ek-9", [f"{n(g.lpg_tup_kg, 0)} kg → tablo bandı"], f"bina/arsa sınırı {bina} m; cadde/okul vb. {cadde} m"))
    if g.lpg_tank_m3 > 0:
        _, ya, yu, ar = H._band(T.EK10, g.lpg_tank_m3)
        adim = [f"Tank su hacmi {n(g.lpg_tank_m3)} m³ → yeraltı {ya} m, yerüstü {yu} m"]
        d = yu
        if g.lpg_tank_tur == "yerustu":
            if g.lpg_duvar_4saat:
                d = d * 2 / 3
                adim.append(f"4 saat dayanıklı duvar: mesafe 1/3 azalır → {n(yu)} × 2/3 = {n(d)} m")
                if g.lpg_alt_yalitim_2saat:
                    d /= 2
                    adim.append(f"Alt yüzey 2 saat yalıtım: yeni mesafe 1/2 → {n(d)} m")
        else:
            d = max(ya, 3)
        b.bloklar.append(Blok("Dökme LPG tankı emniyet uzaklığı", "Ek-10", adim, f"{n(d)} m"))
    if g.sivi_tanklar:
        adim, top = [], 0.0
        for t in g.sivi_tanklar:
            bol = T.IA_ESDEGER_BOLEN[t.sinif]
            top += t.hacim_L / bol
            adim.append(f"{t.ad} (Sınıf {t.sinif}): {n(t.hacim_L, 0)} L ÷ {bol} = {n(t.hacim_L / bol)} L (IA cinsinden)")
        adim.append(f"Toplam = {n(top)} L ≤ 12.500 L ?")
        b.bloklar.append(Blok("Yanıcı sıvı — Sınıf IA eşdeğeri", "Madde 118(2), 119(2)d", adim, f"{n(top)} L", "UYGUN" if top <= 12500 else "UYGUN DEĞİL"))
    return b


# --- 13 -------------------------------------------------------------------
def _cevre(g: Girdi) -> Bolum:
    b = Bolum("13. Çevre ve itfaiye erişimi")
    if g.orman_yakin and g.kullanim in ("endustriyel", "depo") and g.toplam_kapali_alan > 2000:
        e = g.arazi_egimi_yuzde
        a_, d_ = (4.0, 2.0) if e > 55 else ((2.0, 1.5) if e >= 30 else (1.0, 1.0))
        b.bloklar.append(Blok("Dış yangın bölgesi mesafesi", "Madde 21(5)",
                              [f"Temel mesafe 100 m; arazi eğimi %{n(e)} → aşağı yön ×{n(a_)}, diğer yönler ×{n(d_)}", f"Aşağı yön = 100 × {n(a_)} = {n(100 * a_, 0)} m", f"Diğer yönler = 100 × {n(d_)} = {n(100 * d_, 0)} m"],
                              f"{n(100 * a_, 0)} m / {n(100 * d_, 0)} m"))
    return b


# --- 14 -------------------------------------------------------------------
def _ekip(g: Girdi) -> Bolum:
    b = Bolum("14. Acil durum ekipleri")
    hesap = sum(H.kat_kullanici_yuku(k) for k in g.katlar)
    kisi = g.calisan_sayisi if g.calisan_sayisi > 0 else hesap
    if kisi > 50 and g.kullanim != "apartman":
        b.bloklar.append(Blok("Ekip kurulması", "Madde 126",
                              [f"Binadaki kişi sayısı {n(kisi, 0)} > 50 ?  → evet", "Söndürme ≥3 + Kurtarma ≥3 + Koruma ≥2 + İlk yardım ≥2 = 10 kişi"], "En az 10 kişilik 4 ekip"))
    else:
        b.bloklar.append(Blok("Ekip kurulması", "Madde 126", [f"Binadaki kişi sayısı {n(kisi, 0)} > 50 ?  → hayır"], "Zorunlu değil"))
    return b


# ---------------------------------------------------------------------------
def dokum_duz_metin(bolumler: list[Bolum]) -> str:
    """GUI ve metin çıktıları için düz metin."""
    satir: list[str] = []
    for bo in bolumler:
        satir.append("=" * 100)
        satir.append(bo.ad.upper())
        satir.append("=" * 100)
        for bl in bo.bloklar:
            satir.append("")
            satir.append(f"▌ {bl.baslik}" + (f"   [{bl.madde}]" if bl.madde else ""))
            for a in bl.adimlar:
                satir.append(f"    • {a}")
            son = f"    ► SONUÇ: {bl.sonuc}" + (f"   — {bl.durum}" if bl.durum else "")
            satir.append(son)
        satir.append("")
    return "\n".join(satir)
