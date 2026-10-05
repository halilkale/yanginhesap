"""Girdi modelleri ve sonuç satırı."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from typing import Optional

# Sonuç durumları
UYGUN = "UYGUN"
UYGUN_DEGIL = "UYGUN DEĞİL"
GEREKLI = "GEREKLİ"
GEREKMEZ = "GEREKMEZ"
KOSULLU = "KOŞULLU UYGUN"
BILGI = "BİLGİ"
KONTROL = "VERİ GİRİLMEDİ"


@dataclass
class Sonuc:
    bolum: str
    kalem: str
    deger: object = ""
    birim: str = ""
    durum: str = BILGI
    madde: str = ""
    aciklama: str = ""


@dataclass
class Mahal:
    ad: str = "Üretim holü"
    alan: float = 0.0          # m² (Ek-5/A: ilk 4 satır net, diğerleri brüt alan)
    katsayi: float = 10.0      # m²/kişi
    kisi_belirli: Optional[float] = None   # Kişi sayısı belirli ise (ör. vardiya mevcudu)
    sayilir: bool = True       # Madde 31(6): aynı anda kullanılmayan mahaller sayılmayabilir


@dataclass
class Kat:
    ad: str = "Zemin kat"
    mahaller: list = field(default_factory=list)
    # Kaçış verileri
    cikis_sayisi: int = 2
    cikis_turu: str = "dis_kapi"   # dis_kapi | diger_kapi | merdiven | koridor
    mevcut_genislik_cm: float = 0.0       # seçilen elemanın toplam temiz genişliği
    tekil_cikis_genislik_cm: float = 0.0  # en dar tekil çıkışın temiz genişliği
    yon: str = "iki"               # iki | tek
    en_uzak_mesafe_m: float = 0.0  # ölçülen en uzak noktadan çıkışa uzaklık
    kus_ucusu_mesafe_m: float = 0.0
    cikmaz_mesafe_m: float = 0.0
    mekan_diyagonal_m: float = 0.0
    cikislar_arasi_mesafe_m: float = 0.0


@dataclass
class Merdiven:
    ad: str = "KM-1"
    genislik_cm: float = 0.0
    rihts_mm: float = 0.0
    basamak_genislik_mm: float = 0.0
    sahanlik_arasi_basamak: int = 0
    sahanlik_arasi_kot_cm: float = 0.0
    bas_yuksekligi_cm: float = 0.0
    hizmet_verilen_kat: int = 1
    kapi_dayanim_dk: float = 0.0
    duvar_dayanim_dk: float = 0.0
    kullanici_sayisi_kat: float = 0.0
    dengelenmis: bool = False
    korunumlu: bool = True


@dataclass
class Kapi:
    ad: str = "K-1"
    temiz_genislik_cm: float = 0.0
    yukseklik_cm: float = 0.0
    kanat_sayisi: int = 1
    kisi_yuku: float = 0.0
    kacis_yonune_aciliyor: bool = True
    esik_var: bool = False
    acma_kuvveti_N: float = 0.0


@dataclass
class DumanMahali:
    ad: str = "Kazan dairesi"
    tur: str = "kazan"      # kazan | otopark | bodrum_depo | diger
    alan_m2: float = 0.0
    yukseklik_m: float = 3.0


@dataclass
class SivirTank:
    ad: str = "Tank-1"
    sinif: str = "II"       # IA IB IC II IIIA IIIB
    hacim_L: float = 0.0
    tur: str = "yerustu"    # yerustu | yeralti | depo_icinde


@dataclass
class Girdi:
    # ------------------ Genel ------------------
    proje_adi: str = "Fabrika Binası"
    tesis_adi: str = ""
    adres: str = ""
    hazirlayan: str = ""
    tarih: str = ""
    kullanim: str = "endustriyel"
    tehlike: str = "OT3"
    mevcut_yapi: bool = False
    karisik_kullanim: bool = False
    tasiyici: str = "betonarme"      # betonarme | celik | ahsap | kagir
    kolay_alevlenici: bool = False   # kolay alevlenici/parlayıcı madde üretimi veya bulundurma
    yanmaz_malzeme_yapim: bool = True   # Madde 52(ç)

    # ------------------ Geometri ------------------
    yapi_yuksekligi: float = 10.0
    bina_yuksekligi: float = 10.0
    kat_sayisi: int = 1
    bodrum_kat_sayisi: int = 0
    bodrum_derinligi: float = 0.0
    taban_alani: float = 5000.0
    tesis_toplam_taban_alani: float = 0.0   # 0 ise taban_alani esas alınır
    toplam_kapali_alan: float = 5000.0
    en_buyuk_kat_alani: float = 5000.0
    bina_boyu: float = 100.0
    bina_eni: float = 50.0
    cephe_genisligi: float = 100.0
    kompartiman_alani: float = 0.0      # 0 ise en_buyuk_kat_alani
    otopark_alani: float = 0.0          # bina içi kapalı otopark toplamı

    # ------------------ Aktif sistemler ------------------
    yagmurlama_var: bool = True
    yagmurlama_tipi: str = "islak"      # islak | kuru
    algilama_var: bool = True
    duman_tahliye_var: bool = False
    hidrant_var: bool = True
    dolap_var: bool = True

    # ------------------ Kullanıcı yükü ve kaçış ------------------
    katlar: list = field(default_factory=list)   # list[Kat]
    merdivenler: list = field(default_factory=list)
    kapilar: list = field(default_factory=list)
    calisan_sayisi: float = 0.0   # vardiya en yüksek mevcut (Madde 126 için); 0 ise hesaplanan yük

    # ------------------ Sulu söndürme ------------------
    spr_yukseklik_h: float = 10.0       # en alt ve en üst başlık arası (m), Ek-8/A
    spr_baslik_alani_m2: float = 0.0    # 0 = otomatik (DT/OT1: 21, OT: 12, YT: 9)
    spr_koruma_alani_m2: float = 0.0    # 0 = Ek-8/B
    es_zamanli_dolap: int = 2
    dolap_tipi: str = "yari_sert"       # yari_sert (25 mm, 100 l/dk) | yassi (400 l/dk)
    hidrant_risk: str = "orta"          # cok_riskli | riskli | orta | az
    statik_yukseklik_mSS: float = 0.0
    boru_kaybi_mSS: float = 0.0
    akma_basinci_mSS: float = 70.0
    pompa_anma_debi_m3h: float = 0.0
    pompa_anma_basma_mSS: float = 0.0
    pompa_kapali_vana_basma_mSS: float = 0.0
    pompa_150_debi_basma_mSS: float = 0.0
    pompa_adedi: int = 1
    yedek_pompa_adedi: int = 1
    mevcut_su_deposu_m3: float = 0.0
    sadece_hidrant: bool = False
    sadece_dolap: bool = False

    # ------------------ Orman / çevre / erişim ------------------
    orman_yakin: bool = False
    arazi_egimi_yuzde: float = 0.0
    itfaiye_son_nokta_mesafe_m: float = 0.0
    ic_yol_genislik_m: float = 0.0
    ic_yol_cikmaz: bool = False
    ic_yol_ic_yaricap_m: float = 0.0
    ic_yol_dis_yaricap_m: float = 0.0
    ic_yol_egim_yuzde: float = 0.0
    ic_yol_serbest_yukseklik_m: float = 0.0
    ic_yol_tasima_yuku_ton: float = 0.0

    # ------------------ Aydınlatma / uyarı ------------------
    isaret_yuksekligi_cm: float = 20.0
    isaret_aydinlatma: str = "icten"     # icten | distan
    kacis_yolu_uzunlugu_m: float = 0.0
    acil_aydinlatma_sure_dk: float = 0.0
    acil_aydinlatma_lux_baslangic: float = 0.0
    acil_aydinlatma_lux_bitis: float = 0.0
    acil_aydinlatma_max_min_orani: float = 0.0
    yangin_butonu_adedi: int = 0

    # ------------------ Basınçlandırma ------------------
    merdiven_kovasi_yuksekligi: float = 0.0
    basinc_kapi_alani_m2: float = 2.1
    basinc_sizinti_debisi_m3s: float = 0.0
    duman_mahalleri: list = field(default_factory=list)

    # ------------------ Kazan / yakıt ------------------
    kazan_var: bool = False
    kazan_kw: float = 0.0
    kazan_alani_m2: float = 0.0
    kazan_kapi_sayisi: int = 1
    kazan_sivi_yakit: bool = False
    yakit_tank_L: float = 0.0
    yakit_yeri: str = "bina_disi"   # bodrum_varil | bodrum_sac | bodrum_komur | bina_disi | bagimsiz
    yakit_havuz_L: float = 0.0
    yagli_trafo_var: bool = False
    jenerator_var: bool = False

    # ------------------ Tehlikeli madde ------------------
    lpg_tup_kg: float = 0.0
    lpg_tank_m3: float = 0.0
    lpg_tank_tur: str = "yerustu"
    lpg_duvar_4saat: bool = False
    lpg_alt_yalitim_2saat: bool = False
    sivi_tanklar: list = field(default_factory=list)
    sivi_depo_alani_m2: float = 0.0
    sivi_depo_yangin_korunum: bool = False
    sivi_depo_dayanim_dk: float = 0.0
    sivi_depo_orijinal_kap: bool = True
    sivi_depolama_yeri: str = "zemin_ustu"   # zemin_ustu | acikta

    # ------------------ Betonarme / ahşap ------------------
    net_beton_kolon_mm: float = 0.0
    net_beton_kiris_mm: float = 0.0
    net_beton_doseme_mm: float = 0.0
    ahsap_b_mm: float = 0.0
    ahsap_h_mm: float = 0.0
    ahsap_yanma_hizi: float = 0.7
    ahsap_yuzey: int = 4

    # ---------------------------------------------------------------
    def ozet_alan(self) -> float:
        return self.kompartiman_alani or self.en_buyuk_kat_alani

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "Girdi":
        d = dict(d)
        kats = [Kat(**{**k, "mahaller": [Mahal(**m) for m in k.get("mahaller", [])]}) for k in d.pop("katlar", [])]
        merd = [Merdiven(**m) for m in d.pop("merdivenler", [])]
        kap = [Kapi(**m) for m in d.pop("kapilar", [])]
        dm = [DumanMahali(**m) for m in d.pop("duman_mahalleri", [])]
        st = [SivirTank(**m) for m in d.pop("sivi_tanklar", [])]
        known = {f.name for f in fields(cls)}
        g = cls(**{k: v for k, v in d.items() if k in known})
        g.katlar, g.merdivenler, g.kapilar, g.duman_mahalleri, g.sivi_tanklar = kats, merd, kap, dm, st
        return g

    @classmethod
    def from_json(cls, s: str) -> "Girdi":
        return cls.from_dict(json.loads(s))
