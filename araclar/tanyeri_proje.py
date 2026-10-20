"""Tanyeri (Tuzla) tesisi: mahal listesi (AK Mim. planı), kompartıman malzeme listesi ve varsayımlarla proje üretir.

Kullanım:  python araclar/tanyeri_proje.py     →  belgeler/tanyeri/ klasörüne .json, .xlsx, .docx yazar
"""
import os
import sys

KOK = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, KOK)
from yangin import etiketler as E  # noqa: E402
from yangin import hesaplar as H  # noqa: E402
from yangin import rapor  # noqa: E402
from yangin.modeller import Girdi, Kat, Mahal, YanginYukuBolum, YanginYukuKalem  # noqa: E402

URETIM, DEPO, OFIS, YEMEK, TOPL, ARALIK = (E.EK5A_AD[0], E.EK5A_AD[1], E.EK5A_AD[4], E.EK5A_AD[5], E.EK5A_AD[6], None)
KAT = {a: k for a, k, _ in __import__("yangin.tablolar", fromlist=["x"]).EK5A}


def M(ad, alan, kat_tur, sayilir=True):
    """kat_tur: Ek-5/A katsayısı (m²/kişi)."""
    return Mahal(ad=ad, alan=alan, katsayi=kat_tur, sayilir=sayilir)


# Mahal listesi (plan: ZEMİN / 1. / 2. / 3. KAT MAHAL LİSTESİ). Hol, koridor, WC, merdiven holü: Madde 31(6) gereği kullanıcı yüküne sayılmaz.
zemin = [M("Z01 Giriş", 67.54, 10), M("Z02 Koridor", 3.34, 10, False), M("Z03 Personel", 13.17, 10), M("Z04 Personel/2", 20.22, 10), M("Z05 Koridor", 5.08, 10, False),
         M("Z06 Hol", 20.78, 10, False), M("Z07 Arşiv", 20.09, 30), M("Z08 WC", 13.63, 10, False), M("Z09 Erkek soyunma", 24.78, 10), M("Z10 WC", 9.83, 10, False),
         M("Z11 Koridor", 6.98, 10, False), M("Z12 Koridor", 6.83, 10, False), M("Z13 Toplantı odası (net)", 31.35, 1.5), M("Z14 Kazan dairesi", 35.96, 30),
         M("Z15 Depo", 36.36, 30), M("Z16 Merdiven holü", 8.50, 10, False)]
kat1 = [M("101 Hol", 23.21, 10, False), M("102 Satın alma / dış ticaret / satış md.", 58.40, 10), M("103 Koridor", 8.75, 10, False), M("104 BN WC", 2.97, 10, False),
        M("105 Erkek WC", 6.16, 10, False), M("106 Muhasebe / mali işler", 62.11, 10), M("107 Kalıp deposu / Enjeksiyon", 822.67, 10), M("108 WC", 9.70, 10, False),
        M("109 Merdiven holü", 5.83, 10, False), M("110 Kalite", 28.40, 10), M("111 Depo", 974.18, 30), M("112 Çizimhane", 15.71, 10), M("113 Merdiven holü", 8.50, 10, False),
        M("114 Kırma", 56.40, 10), M("115 Kırma", 23.57, 10)]
kat2 = [M("201 Hol", 23.21, 10, False), M("202 Genel müdür odası", 51.17, 10), M("203 Dinlenme", 14, 10), M("204 Koridor", 8.95, 10, False), M("205 Arşiv", 4.90, 30),
        M("206 BN WC", 2.77, 10, False), M("207 Er. WC", 5.76, 10, False), M("208 Dinlenme", 8.00, 10), M("209 Yönetim kurulu başkanı", 48.36, 10), M("210 Dinlenme", 80.88, 10),
        M("211 Üretim müdürü", 38.91, 10), M("212 Rezerv alan", 354, 30), M("213 WC", 9.70, 10, False), M("214 Merdiven holü", 6.60, 10, False), M("215 Montaj", 218.26, 10),
        M("216 Merdiven holü", 8.50, 10, False), M("217 Usta odası", 16.38, 10), M("218 Tampon / Serigrafi", 162, 10), M("219 Boyahane", 160, 10), M("220 Karanlık oda", 3.72, 10),
        M("221 Kabin", 38.64, 10), M("222 Balkon", 16, 10, False), M("223 Depo", 11.31, 30)]
kat3 = [M("301 Merdiven holü", 10.88, 10, False), M("302 Mescit", 9.21, 10), M("303 Yemekhane (net)", 137, 1.5), M("304 Mutfak", 50, 10), M("305 Bulaşık", 14.50, 10),
        M("306 Koridor", 2.08, 10, False), M("307 Ofis", 8.16, 10), M("308 WC", 13.08, 10, False), M("309 Personel", 4.32, 10), M("310 Rezerv alan (Depo üst)", 1403.38, 30),
        M("311 WC", 9.70, 10, False), M("312 Giyinme odası", 9.52, 10), M("313 Merdiven holü", 8.50, 10, False)]


def proje() -> Girdi:
    g = Girdi(
        proje_adi="Tanyeri — Tuzla Tesisi (yangın kompartıman çalışması)", tesis_adi="Tanyeri", adres="Tuzla", hazirlayan="",
        kullanim="endustriyel", tehlike="OT3", kolay_alevlenici=True, yanmaz_malzeme_yapim=True, tasiyici="betonarme",
        yapi_yuksekligi=13.0, bina_yuksekligi=13.0, kat_sayisi=4, bodrum_kat_sayisi=0,
        taban_alani=2258.0, toplam_kapali_alan=882.18 + 2258 + 2240.73 + 2240.73, en_buyuk_kat_alani=2258.0, kompartiman_alani=1403.38,
        bina_boyu=52.85, bina_eni=42.40, cephe_genisligi=52.85,
        yagmurlama_var=False, algilama_var=False, duman_tahliye_var=False, hidrant_var=True, dolap_var=True,
        spr_yukseklik_h=0.0, es_zamanli_dolap=2,
    )
    g.katlar = [Kat(ad="Zemin kat", mahaller=zemin, cikis_sayisi=0), Kat(ad="1. kat", mahaller=kat1, cikis_sayisi=0),
                Kat(ad="2. kat", mahaller=kat2, cikis_sayisi=0), Kat(ad="3. kat", mahaller=kat3, cikis_sayisi=0)]
    B = YanginYukuBolum
    g.yangin_yuku_bolumleri = [B("Depo alt", 974.18, "1. kat", "depo"), B("Boyahane", 160.0, "2. kat", "endustriyel"), B("Serigrafi", 162.0, "2. kat", "endustriyel"),
                               B("Montaj", 218.26, "2. kat", "endustriyel"), B("Depo üst", 1403.38, "3. kat", "depo"), B("Enjeksiyon", 822.67, "1. kat", "endustriyel")]
    PP, AH, KR, BOYA = "Plastik — PE / PP (kasa, mamül)", "Ahşap (palet, kereste, kontrplak)", "Karton / kâğıt (koli, ambalaj)", "Solvent bazlı sıvı boya / vernik (varsayım)"
    K = YanginYukuKalem
    g.yangin_yuku_kalemleri = [K("Depo alt", PP, 300), K("Depo alt", AH, 250), K("Depo alt", PP, 500),
                               K("Boyahane", PP, 100), K("Boyahane", BOYA, 100),
                               K("Serigrafi", PP, 20), K("Serigrafi", PP, 50),
                               K("Montaj", PP, 200), K("Montaj", KR, 300),
                               K("Depo üst", PP, 1000), K("Depo üst", PP, 150), K("Depo üst", PP, 100),
                               K("Enjeksiyon", PP, 50)]
    return g


if __name__ == "__main__":
    hedef = os.path.join(KOK, "belgeler", "tanyeri")
    os.makedirs(hedef, exist_ok=True)
    g = proje()
    s = H.hesapla(g)
    with open(os.path.join(hedef, "Tanyeri_Tuzla_proje.json"), "w", encoding="utf-8") as f:
        f.write(g.to_json())
    with open(os.path.join(hedef, "Tanyeri_Tuzla_rapor.xlsx"), "wb") as f:
        f.write(rapor.excel_olustur(g, s))
    with open(os.path.join(hedef, "Tanyeri_Tuzla_rapor.docx"), "wb") as f:
        f.write(rapor.word_olustur(g, s))
    print(H.ozet(s))
