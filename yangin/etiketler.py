"""Arayüz ve form için ortak seçenek etiketleri, tablo kolonları ve satır dönüşümü."""
from __future__ import annotations

from . import tablolar as T
from .modeller import DumanMahali, Girdi, Kapi, Kat, Mahal, Merdiven, SivirTank

LIST_ALANLAR = {"katlar", "merdivenler", "kapilar", "duman_mahalleri", "sivi_tanklar"}
EK5A_AD = [a for a, _, _ in T.EK5A]
EK5A_KATSAYI = {a: k for a, k, _ in T.EK5A}
CIKIS_TURLERI = {"dis_kapi": "Dışarı çıkış kapısı", "diger_kapi": "Diğer kapı / koridor kapısı", "merdiven": "Kaçış merdiveni", "koridor": "Rampa / koridor"}
YONLER = {"iki": "İki yön", "tek": "Tek yön"}
TASIYICI = {"betonarme": "Betonarme", "celik": "Çelik", "ahsap": "Ahşap", "kagir": "Kâgir"}
YAGMURLAMA = {"islak": "Islak / ön etkili", "kuru": "Kuru / değişken"}
DOLAP = {"yari_sert": "Yarı-sert hortum Ø25 (100 l/dk)", "yassi": "Yassı hortum DN50 (400 l/dk)"}
HIDRANT = {"cok_riskli": "Çok riskli (50 m)", "riskli": "Riskli (100 m)", "orta": "Orta riskli (125 m)", "az": "Az riskli (150 m)"}
ISARET = {"icten": "İçeriden/arkadan aydınlatılan (×200)", "distan": "Dışarıdan/kenardan aydınlatılan (×100)"}
YAKIT = {"bodrum_varil": "Bodrumda varil", "bodrum_sac": "Bodrumda sızıntısız sac kap", "bodrum_komur": "Bina içi bodrum, 120 dk kâgir oda",
         "bina_disi": "Bina dışında yeraltı/yerüstü tank", "bagimsiz": "Ayrı, bağımsız tek katlı bina"}
LPG_TUR = {"yerustu": "Yerüstü", "yeralti": "Yeraltı"}
SIVI_YER = {"zemin_ustu": "Zemin seviyesi ve üstündeki depo hacimleri", "acikta": "Açıkta kurulu depolar"}

# Liste tabloları: (anahtar, başlık, tür, seçenekler, genişlik)
TABLOLAR = {
    "mahal": [("kat", "Kat", "t", None, 110), ("mahal", "Mahal", "t", None, 150), ("tur", "Tür (Ek-5/A)", "c", EK5A_AD, 280),
              ("alan", "Alan (m²)", "f", None, 80), ("ozel", "Özel katsayı (m²/kişi)", "f", None, 120),
              ("belirli", "Belirli kişi", "f", None, 80), ("sayilir", "Sayılır", "b", None, 60)],
    "kat": [("kat", "Kat", "t", None, 110), ("cikis", "Çıkış sayısı", "i", None, 80), ("tur", "Çıkış türü", "c", list(CIKIS_TURLERI.values()), 190),
            ("genislik", "Mevcut toplam gen. (cm)", "f", None, 130), ("tekil", "En dar tekil (cm)", "f", None, 110),
            ("yon", "Yön", "c", list(YONLER.values()), 80), ("mesafe", "En uzak mesafe (m)", "f", None, 120),
            ("kus", "Kuş uçuşu (m)", "f", None, 90), ("cikmaz", "Çıkmaz koridor (m)", "f", None, 120),
            ("diyagonal", "Mekân diyagonali (m)", "f", None, 130), ("arasi", "Çıkışlar arası (m)", "f", None, 120)],
    "merdiven": [("ad", "Ad", "t", None, 70), ("gen", "Genişlik (cm)", "f", None, 90), ("riht", "Rıht (mm)", "f", None, 70), ("basis", "Basış (mm)", "f", None, 70),
                 ("sbasamak", "Sahanlık arası basamak", "i", None, 130), ("skot", "Sahanlık arası kot (cm)", "f", None, 130),
                 ("bas", "Baş yüksekliği (cm)", "f", None, 120), ("kat", "Hizmet verilen kat", "i", None, 110),
                 ("kapi", "Kapı dayanımı (dk)", "f", None, 110), ("duvar", "Duvar dayanımı (dk)", "f", None, 110),
                 ("kullanici", "Kattaki kullanıcı", "f", None, 100), ("dengeli", "Dengelenmiş", "b", None, 80)],
    "kapi": [("ad", "Ad", "t", None, 90), ("gen", "Temiz genişlik (cm)", "f", None, 120), ("yuk", "Yükseklik (cm)", "f", None, 100),
             ("kanat", "Kanat", "i", None, 60), ("kisi", "Mekân kişi yükü", "f", None, 110), ("yone", "Kaçış yönüne açılıyor", "b", None, 140),
             ("esik", "Eşik var", "b", None, 70), ("kuvvet", "Açma kuvveti (N)", "f", None, 110)],
    "duman": [("ad", "Ad", "t", None, 160), ("tur", "Tür", "c", ["kazan", "otopark", "bodrum_depo", "diger"], 120),
              ("alan", "Alan (m²)", "f", None, 100), ("yuk", "Yükseklik (m)", "f", None, 100)],
    "tank": [("ad", "Ad", "t", None, 160), ("sinif", "Sınıf", "c", list(T.IA_ESDEGER_BOLEN), 80), ("hacim", "Hacim (L)", "f", None, 100),
             ("tur", "Tür", "c", ["yerustu", "yeralti", "depo_icinde"], 120)],
}


def _f(x, d=0.0) -> float:
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return d


def _i(x, d=0) -> int:
    return int(round(_f(x, d)))


def _bool(x) -> bool:
    return str(x) in ("1", "True", "true", "Evet", "✔")


def tablolari_uygula(g: Girdi, mahal, kat, merdiven, kapi, duman, tank) -> Girdi:
    """Etiketli satır sözlüklerini (arayüz/form) Girdi nesnesine işler."""
    ters_cikis = {b: a for a, b in CIKIS_TURLERI.items()}
    ters_yon = {b: a for a, b in YONLER.items()}
    katlar: dict[str, Kat] = {}
    for r in kat:
        ad = str(r["kat"] or "Kat")
        katlar[ad] = Kat(ad=ad, cikis_sayisi=_i(r["cikis"], 2), cikis_turu=ters_cikis.get(r["tur"], "dis_kapi"), mevcut_genislik_cm=_f(r["genislik"]),
                         tekil_cikis_genislik_cm=_f(r["tekil"]), yon=ters_yon.get(r["yon"], "iki"), en_uzak_mesafe_m=_f(r["mesafe"]),
                         kus_ucusu_mesafe_m=_f(r["kus"]), cikmaz_mesafe_m=_f(r["cikmaz"]), mekan_diyagonal_m=_f(r["diyagonal"]),
                         cikislar_arasi_mesafe_m=_f(r["arasi"]))
    for r in mahal:
        kad = str(r["kat"] or "Kat")
        katlar.setdefault(kad, Kat(ad=kad))
        ozel = _f(r["ozel"])
        katsayi = ozel if ozel > 0 else EK5A_KATSAYI.get(r["tur"], 10.0)
        bel = _f(r["belirli"])
        katlar[kad].mahaller.append(Mahal(ad=str(r["mahal"] or "Mahal"), alan=_f(r["alan"]), katsayi=katsayi,
                                          kisi_belirli=bel if bel > 0 else None, sayilir=_bool(r["sayilir"])))
    g.katlar = list(katlar.values())
    g.merdivenler = [Merdiven(ad=str(r["ad"] or "KM"), genislik_cm=_f(r["gen"]), rihts_mm=_f(r["riht"]), basamak_genislik_mm=_f(r["basis"]),
                              sahanlik_arasi_basamak=_i(r["sbasamak"]), sahanlik_arasi_kot_cm=_f(r["skot"]), bas_yuksekligi_cm=_f(r["bas"]),
                              hizmet_verilen_kat=_i(r["kat"], 1), kapi_dayanim_dk=_f(r["kapi"]), duvar_dayanim_dk=_f(r["duvar"]),
                              kullanici_sayisi_kat=_f(r["kullanici"]), dengelenmis=_bool(r["dengeli"])) for r in merdiven]
    g.kapilar = [Kapi(ad=str(r["ad"] or "K"), temiz_genislik_cm=_f(r["gen"]), yukseklik_cm=_f(r["yuk"]), kanat_sayisi=_i(r["kanat"], 1), kisi_yuku=_f(r["kisi"]),
                      kacis_yonune_aciliyor=_bool(r["yone"]), esik_var=_bool(r["esik"]), acma_kuvveti_N=_f(r["kuvvet"])) for r in kapi]
    g.duman_mahalleri = [DumanMahali(ad=str(r["ad"] or "Mahal"), tur=str(r["tur"] or "diger"), alan_m2=_f(r["alan"]), yukseklik_m=_f(r["yuk"], 3.0)) for r in duman]
    g.sivi_tanklar = [SivirTank(ad=str(r["ad"] or "Tank"), sinif=str(r["sinif"] or "II"), hacim_L=_f(r["hacim"]), tur=str(r["tur"] or "yerustu")) for r in tank]
    return g
