"""Alan ipuçları: bir alan için yönetmelik madde metinlerini ve ek özetlerini derler.

Arayüzlerde bir alanın üzerine gelindiğinde gösterilen sarı ipucu penceresinin içeriği buradan gelir.
"""
from __future__ import annotations

import re

from . import alanlar as A
from . import mevzuat_metin as M

EK_OZET: dict[str, str] = {
    "Ek-1": "Bina tehlike sınıflandırması. Ek-1/A düşük tehlike (bürolar, okullar, hapishaneler; en çok 126 m² bölüm). Ek-1/B orta tehlike 1-4 "
            "(ör. ahşap/mobilya, kâğıt-matbaa, kablo-plastik, tekstil: OT-3; mum, kibrit, alkol damıtma, pamuk iplikhanesi, yonga levha: OT-4). "
            "Ek-1/C yüksek tehlike 1-4 (boya/vernik, plastik köpük, selüloz nitrat, havai fişek). OT-1/2 alanlarda boyama gibi yüksek yangın yükü varsa OT-3 sayılır.",
    "Ek-3/B": "Yapı elemanlarının yangına dayanım süreleri: kaçış yolu çatısı REI 30; kompartıman duvarı REI 60 veya Ek-3/C; korunumlu şaft ve kaçış merdiveni yuvası REI 120; "
              "yangın kesici ve asma tavan EI 30; asansör kat kapısı E 30 (E 60: yapı yüksekliği >51,50 m).",
    "Ek-3/C": "Yangına dayanım süreleri (dk) kullanım sınıfı, yağmurlama sistemi, bina yüksekliği (<21,50 / <30,50 / >30,50 m) ve bodrum derinliğine (>10 / <10 / <5 m) göre. "
              "Endüstriyel yapı yağmurlamasız: bodrum 120/90/60, üst katlar 90/120/İzin verilmez. Yağmurlamalı: bodrum 90/60/30, üst katlar 60/90/120.",
    "Ek-4": "En fazla kompartıman alanı: konut sınırsız; konaklama 4000; sağlık 1500; eğitim 6000; büro 8000; ticaret 2000 m²; endüstriyel OT-3 ve üstü 6000, OT-1/2 15000 m²; "
            "depo OT-3 ve üstü 1000, OT-1/2 5000 m²; kapalı otopark sınırsız. Uygun yangın kontrol sistemleri (algılama, yağmurlama, duman tahliye) varsa sınır 2 katına çıkar veya sınırsızdır; "
            "tek katlı yapıda (OT-1/2 endüstriyel ve depo) sınırlama yoktur.",
    "Ek-5/A": "Kullanıcı yükü katsayıları (m²/kişi): fabrika üretim/paketleme 10; depo, ambar, makine dairesi 30; atölye, galeri, müze 5; mağaza 5; ofis 10; mutfak ve çamaşırhane 10; "
              "lokanta, kantin, toplantı salonu 1,5 (net alan); otopark 30; otel odası 20; hastane odası 20. İlk dört satır net, diğerleri brüt alan esaslıdır.",
    "Ek-5/B": "Çıkışlara götüren en uzun kaçış uzaklıkları ve birim genişlik (50 cm başına kişi). Endüstriyel yapı: tek yön 15 m (yağmurlamalı 25), iki yön 30 m (yağmurlamalı 60); "
              "dış kapı 100, diğer kapı 80, merdiven 60, koridor 100 kişi; çıkmaz koridor 15 m (yağmurlamalı 20). Kolay alevlenici malzeme üretmeyen endüstriyel yapılarda uzaklıklar ½ oranında artırılabilir.",
    "Ek-7": "Otomatik algılama gereken binalar: konut >51,50 m; konaklama >6,50 m ve >1000 m²; büro >30,50 m ve >5000 m²; depo >6,50 m ve >5000 m²; yüksek tehlikeli yerler >6,50 m ve >1000 m². "
            "Endüstriyel, ticaret, kurum ve toplanma yapılarına ilişkin satırlar Danıştay kararıyla iptal edilmiştir.",
    "Ek-8": "Yağmurlama sisteminde su deposu en az hacmi (Ek-8/A), tasarım yoğunlukları (Ek-8/B) ve yangın dolabı/hidrant için ilave su ihtiyaçları (Ek-8/C).",
    "Ek-8/A": "Su deposu en az hacmi (m³), en alt-en üst başlık arası h ≤15 / 15-30 / 30-45 m için: Düşük ıslak 9/10/11; OT-1 ıslak 55/70/80; OT-1 kuru ve OT-2 ıslak 105/125/140; "
              "OT-2 kuru ve OT-3 ıslak 135/160/185; OT-3 kuru ve OT-4 ıslak 160/185/200; OT-4 kuru ve yüksek tehlike: hidrolik hesap.",
    "Ek-8/B": "Yağmurlama tasarım yoğunluğu (mm/dk) ve koruma alanı (m², ıslak/kuru): düşük 2,25 / 84; OT-1 5 / 72-90; OT-2 5 / 144-180; OT-3 5 / 216-270; OT-4 5 / 360; "
              "YT-1 7,7 / 260-325; YT-2 10 / 260-325; YT-3 12,5 / 260-325; YT-4 yoğun su.",
    "Ek-8/C": "İlave su ihtiyacı (yangın dolabı l/dk, hidrant l/dk, süre dk): düşük 100/400/30; OT-1-2 100/400/60; OT-3-4 100/1000/60; yüksek tehlike 200/1500/90.",
    "Ek-9": "Bina dışında LPG tüp deposu emniyet uzaklıkları (bina/komşu arsa; cadde, okul, hastane vb.): ≤1250 kg 0/3 m; 1251-2700 kg 3/6 m; 2701-4500 kg 6/12 m; >4500 kg 8/15 m.",
    "Ek-10": "Dökme LPG tankı emniyet uzaklıkları (yeraltı/yerüstü, m): <0,5 m³ 3/3; 0,5-3 m³ 3/3; 3,1-10 m³ 5/7,5; 10,1-50 m³ 7,5/10; 50,1-120 m³ 10/15; 120-250 m³ 15/23; …. "
             "4 saat dayanıklı ≥1,5 m duvar mesafeyi 1/3, ek olarak 2 saat alt yüzey yalıtımı yeni mesafeyi 1/2 azaltır.",
    "Ek-11": "Yanıcı/parlayıcı sıvı bildirim eşikleri (litre): zemin ve üstü depo hacimleri Sınıf IA 20-60, IB/IC/II 100-300; açıkta depolar IA 20-200, IB/IC/II 40-600. "
             "Eşiği aşınca bildirim, üst sınırı aşınca itfaiye izni gerekir.",
    "Ek-12": "Yanıcı/parlayıcı sıvı depolama: Ek-12/A depo binasında (litre) IA 2500, IB 5000, IC 10000, II 30000, IIIA 100000, IIIB 200000 (orijinal kap); Ek-12/B bina içi tecrit depo "
             "(15 m²: 70 L/m², korunumlu 175; 50 m²: 140, korunumlu 350); Ek-12/C açık yerüstü tank, Ek-12/Ç yeraltı tank mesafeleri; Ek-12/D taşınabilir kaplarda koruyucu bölge.",
    "Ek-12/B": "Bina içi tecrit yanıcı sıvı deposu: en çok 15 m² (REI 60; 70 L/m², yangın korunumlu 175 L/m²) veya 50 m² (120 dk; 140 L/m², korunumlu 350 L/m²).",
    "Ek-14": "Mevcut yapılarda çıkışlara götüren en uzun kaçış uzaklıkları (Ek-5/B ile aynı değerler); kolay alevlenici malzeme üretmeyen endüstriyel tesislerde uzaklık en çok 2 katına kadar artırılabilir.",
}

# Tablo sütunları için dayanak: {tablo: {sütun: madde metni}}
TABLO_MADDE: dict[str, dict[str, str]] = {
    "mahal": {"kat": "Madde 31(3), 32", "mahal": "Madde 31(6)", "tur": "Madde 32(1), Ek-5/A", "alan": "Madde 32(1), Ek-5/A", "ozel": "Ek-5/A",
              "belirli": "Ek-5/A", "sayilir": "Madde 31(6)"},
    "kat": {"kat": "Madde 31(3)", "cikis": "Madde 39(1), 39(2)", "tur": "Madde 32(2), 33, Ek-5/B", "genislik": "Madde 33(1), Ek-5/B", "tekil": "Madde 33(1)",
            "yon": "Madde 32(3), Ek-5/B", "mesafe": "Madde 32(3), 32(6), Ek-5/B", "kus": "Madde 32(5)", "cikmaz": "Madde 4(i), Ek-5/B",
            "diyagonal": "Madde 39(3)", "arasi": "Madde 39(3)"},
    "merdiven": {"ad": "Madde 38", "gen": "Madde 33(1), 33(2)", "riht": "Madde 41(7)", "basis": "Madde 41(7)", "sbasamak": "Madde 41(3)", "skot": "Madde 41(6)",
                 "bas": "Madde 41(6)", "kat": "Madde 47(3)", "kapi": "Madde 47(3)", "duvar": "Madde 38(3)", "kullanici": "Madde 41(3)", "dengeli": "Madde 41(3), 41(8)"},
    "kapi": {"ad": "Madde 47", "gen": "Madde 33(5), 47(1)", "yuk": "Madde 47(1)", "kanat": "Madde 47(4)", "kisi": "Madde 47(2)", "yone": "Madde 47(2)",
             "esik": "Madde 47(1)", "kuvvet": "Madde 47(6)"},
    "duman": {"ad": "Madde 88", "tur": "Madde 88(3)", "alan": "Madde 88(3)", "yuk": "Madde 88(3)"},
    "tank": {"ad": "Madde 113", "sinif": "Madde 113, 118(2)", "hacim": "Madde 114, Ek-11, Ek-12", "tur": "Madde 119, 120, Ek-12/C"},
}

_KISALT = 640           # tek alıntının azami karakter sayısı


def _kisalt(t: str, n: int = _KISALT) -> str:
    t = re.sub(r"\s*\n\s*", "  ", t.strip())
    if len(t) <= n:
        return t
    kes = t.rfind(". ", 0, n)
    kes = kes if kes > n * 0.5 else n
    return t[:kes].rstrip(" ,;") + " …"


def _ref_ayikla(madde: str) -> tuple[list[tuple[str, str | None]], list[str]]:
    """'Madde 33(1)-(2), 52 — açıklama' → ([('33','1'),('33','2'),('52',None)], ['Ek-5/B'])."""
    on = re.split(r"\s—\s|;|:", madde)[0]
    maddeler: list[tuple[str, str | None]] = []
    for m in re.finditer(r"(?<![\d,/])(\d{1,3}(?:/[A-C])?)(?![\d,]\d)(?:\s*\((\d+|[a-zçğıöşü]{1,3})\))?(?:-\((\d+)\))?", on):
        no = m.group(1)
        if int(no.split("/")[0]) > 171:
            continue
        # "Ek-5/B" gibi ek numaralarını madde sayma
        bas = on[max(0, m.start() - 3):m.start()]
        if bas.endswith("Ek-") or bas.endswith("Ek "):
            continue
        fikra = m.group(2)
        maddeler.append((no, fikra))
        if m.group(3):
            maddeler.append((no, m.group(3)))
    ekler = []
    for m in re.finditer(r"Ek-\d+(?:/[A-ZÇ]+)?", madde):
        if m.group(0) not in ekler:
            ekler.append(m.group(0))
    return maddeler, ekler


def madde_alinti(no: str, fikra: str | None) -> str | None:
    """Madde metninden ilgili fıkra / bent / tanım alıntısı. Bulunamazsa None."""
    baslik = M.BASLIK.get(no, "")
    ust = f"Madde {no}" + (f" — {baslik}" if baslik else "")
    if no == "4" and fikra and not fikra.isdigit():
        t = M.TANIM.get(fikra)
        if t:
            return f"{ust}, {fikra}) bendi: {_kisalt(t)}"
    govde = M.MADDE.get(no)
    if not govde:
        return None
    if fikra and fikra.isdigit() and fikra in govde:
        return f"{ust}, ({fikra}). fıkra: {_kisalt(govde[fikra])}"
    if fikra and not fikra.isdigit():
        for k, v in govde.items():
            for satir in v.split("\n"):
                if re.match(rf"^{re.escape(fikra)}\)\s", satir):
                    return f"{ust}, {fikra}) bendi: {_kisalt(satir)}"
    tum = " ".join(f"({k}) {v}" if k != "_" else v for k, v in govde.items())
    return f"{ust}: {_kisalt(tum, 800)}"


def mevzuat_alintilari(madde: str, en_cok: int = 4) -> list[str]:
    """Bir 'Madde …, Ek-…' dayanak metni için yönetmelik alıntıları listesi."""
    maddeler, ekler = _ref_ayikla(madde)
    cikti: list[str] = []
    gorulen = set()
    for no, fikra in maddeler:
        if (no, fikra) in gorulen:
            continue
        gorulen.add((no, fikra))
        a = madde_alinti(no, fikra)
        if a:
            cikti.append(a)
        if len(cikti) >= en_cok:
            break
    for ek in ekler:
        o = EK_OZET.get(ek) or EK_OZET.get(ek.split("/")[0])
        if o:
            cikti.append(f"{ek}: {o}")
    return cikti


def ipucu_bolumleri(alan_adi: str) -> list[tuple[str, str]]:
    """[(stil, metin)] — stil: baslik | govde | not | mevzuat."""
    a = next((x for x in A.TUM_ALANLAR if x.alan == alan_adi), None)
    if a is None:
        return []
    out = [("baslik", a.baslik)]
    if a.aciklama:
        out.append(("govde", a.aciklama))
    kunye = []
    if a.birim:
        kunye.append(f"Birim: {a.birim}")
    if a.kaynak:
        kunye.append(f"Nereden bulunur: {a.kaynak}")
    kunye.append({"Z": "Kim: işveren (zorunlu)", "V": "Kim: işveren (varsa)", "M": "Kim: mühendis / montaj firması"}[a.kim])
    out.append(("not", "   ·   ".join(kunye)))
    if a.madde:
        out.append(("etiket", "Mevzuat — programdaki etkisi: " + a.madde))
        for alinti in mevzuat_alintilari(a.madde):
            out.append(("mevzuat", alinti))
    else:
        out.append(("not", "Mevzuatta doğrudan bir hüküm yoktur; rapor/kimlik bilgisidir."))
    return out


def tablo_ipucu_bolumleri(tablo: str, kolon: str) -> list[tuple[str, str]]:
    t = next((x for x in A.TABLO_SAYFALARI if x.anahtar == tablo), None)
    if t is None:
        return []
    from . import etiketler as E
    baslik = next((b for k, b, *_ in E.TABLOLAR[tablo] if k == kolon), kolon)
    out = [("baslik", baslik)]
    if t.aciklamalar.get(kolon):
        out.append(("govde", t.aciklamalar[kolon]))
    madde = TABLO_MADDE.get(tablo, {}).get(kolon, "")
    if madde:
        out.append(("etiket", "Mevzuat: " + madde))
        for alinti in mevzuat_alintilari(madde):
            out.append(("mevzuat", alinti))
    return out


def sonuc_ipucu_bolumleri(kalem: str, madde: str, aciklama: str) -> list[tuple[str, str]]:
    out = [("baslik", kalem)]
    if aciklama:
        out.append(("govde", aciklama))
    if madde:
        out.append(("etiket", "Dayanak: " + madde))
        for alinti in mevzuat_alintilari(madde, en_cok=3):
            out.append(("mevzuat", alinti))
    return out


def duz_metin(bolumler: list[tuple[str, str]]) -> str:
    """Streamlit vb. için tek parça metin (markdown)."""
    satirlar = []
    for stil, m in bolumler:
        if stil == "baslik":
            satirlar.append(f"**{m}**")
        elif stil == "mevzuat":
            satirlar.append(f"> {m}")
        elif stil == "etiket":
            satirlar.append(f"*{m}*")
        else:
            satirlar.append(m)
    return "\n\n".join(satirlar)
