"""Hesap motoru testleri. Kılavuz (Aralık 2024) örnekleri referans alınmıştır."""
import math

import pytest

from yangin import hesaplar as H
from yangin.modeller import Girdi, Kat, Mahal, Kapi, Merdiven, SivirTank, DumanMahali, UYGUN, UYGUN_DEGIL


def bul(sonuclar, kalem_parca, bolum_parca=""):
    for r in sonuclar:
        if kalem_parca in r.kalem and bolum_parca in r.bolum:
            return r
    raise AssertionError(f"Bulunamadı: {kalem_parca!r}")


def varsayilan() -> Girdi:
    g = Girdi(tehlike="OT2", kullanim="endustriyel")
    g.katlar = [Kat(ad="Zemin", mahaller=[Mahal("Üretim", 5000, 10)], cikis_sayisi=4,
                    mevcut_genislik_cm=500, en_uzak_mesafe_m=40)]
    return g


# --- Kılavuz: Yangın suyu depo hesabı örneği (ofis, Orta Tehlike-2) ----------
def test_kilavuz_su_deposu_ornegi():
    g = Girdi(kullanim="buro", tehlike="OT2", yagmurlama_var=True, yagmurlama_tipi="islak",
              es_zamanli_dolap=2, hidrant_var=True, dolap_var=True,
              statik_yukseklik_mSS=20, boru_kaybi_mSS=6.06, akma_basinci_mSS=70,
              spr_yukseklik_h=10)
    s = H.su_deposu_ve_pompa(g)
    assert bul(s, "Yağmurlama debisi").deger == pytest.approx(720)
    assert bul(s, "Yangın dolabı debisi").deger == 200
    assert bul(s, "Hidrant debisi").deger == 400
    assert bul(s, "Toplam yangın suyu debisi").deger == pytest.approx(1320)
    assert bul(s, "Hesaplanan su deposu").deger == pytest.approx(79.2)   # 43,2 + 12 + 24
    assert bul(s, "en az anma debisi").deger == pytest.approx(79.2)      # m³/h
    assert bul(s, "basma yüksekliği Hy").deger == pytest.approx(96.06)
    # Ek-8/A: OT-2 ıslak, h ≤ 15 → 105 m³ (tablo > hesap → önerilen büyük olan)
    assert bul(s, "Ek-8/A tablo").deger == 105
    assert bul(s, "Önerilen en az").deger == pytest.approx(105)


# --- Kılavuz: Çıkış kapasitesi örneği (büro, 202,64 kişi) --------------------
def test_kilavuz_cikis_kapasitesi_ornegi():
    g = Girdi(kullanim="buro", tehlike="DT", yagmurlama_var=True, yapi_yuksekligi=17.5, bina_yuksekligi=14)
    g.katlar = [Kat(ad="Tipik kat", mahaller=[Mahal("Ofisler", 2026.4, 10)], cikis_turu="merdiven", mevcut_genislik_cm=260)]
    s = H.kullanici_yuku_ve_kacis(g)
    assert bul(s, "Kat kullanıcı yükü").deger == pytest.approx(202.64)
    assert bul(s, "Gerekli toplam genişlik — Kaçış merdiveni").deger == pytest.approx(168.87, abs=0.02)
    assert bul(s, "Gerekli toplam genişlik — Rampa ve koridor").deger == pytest.approx(101.32, abs=0.01)
    assert bul(s, "Mevcut toplam genişlik").durum == UYGUN


# --- Ek-3/C -------------------------------------------------------------------
@pytest.mark.parametrize("spr,h,beklenen", [
    (False, 10, 90), (True, 10, 60), (False, 25, 120), (True, 25, 90), (True, 35, 120),
])
def test_ek3c_endustriyel(spr, h, beklenen):
    g = Girdi(kullanim="endustriyel", yagmurlama_var=spr, bina_yuksekligi=h, yapi_yuksekligi=h)
    r = bul(H.yangin_dayanimi(g), "Taşıyıcı sistem / kompartıman")
    assert r.deger == beklenen


def test_ek3c_izin_verilmez():
    g = Girdi(kullanim="endustriyel", yagmurlama_var=False, bina_yuksekligi=35, yapi_yuksekligi=35)
    r = bul(H.yangin_dayanimi(g), "Taşıyıcı sistem / kompartıman")
    assert r.durum == UYGUN_DEGIL


def test_ek3c_buro_gercek_tablo():
    # Metin çıkarımında kayan satır: görselle doğrulandı (sprinklerli büro, <21,50 m → 30)
    g = Girdi(kullanim="buro", yagmurlama_var=True, bina_yuksekligi=10, yapi_yuksekligi=10)
    assert bul(H.yangin_dayanimi(g), "Taşıyıcı sistem / kompartıman").deger == 30


def test_bodrum_siniri():
    g = Girdi(kullanim="endustriyel", yagmurlama_var=False, bodrum_kat_sayisi=1, bodrum_derinligi=4)
    assert bul(H.yangin_dayanimi(g), "Bodrum katlar").deger == 60
    g.bodrum_derinligi = 12
    assert bul(H.yangin_dayanimi(g), "Bodrum katlar").deger == 120


# --- Ek-4 ---------------------------------------------------------------------
def test_ek4_tek_katli_sinirsiz():
    g = Girdi(kullanim="endustriyel", tehlike="OT2", kat_sayisi=1, en_buyuk_kat_alani=40000,
              yagmurlama_var=False, algilama_var=False)
    assert bul(H.kompartiman(g), "kontrolü").deger == "Sınırsız"


def test_ek4_cok_katli_limit_asimi():
    g = Girdi(kullanim="endustriyel", tehlike="OT3", kat_sayisi=3, en_buyuk_kat_alani=9000,
              yagmurlama_var=False, algilama_var=False, duman_tahliye_var=False)
    r = bul(H.kompartiman(g), "kontrolü")
    assert r.durum == UYGUN_DEGIL
    assert bul(H.kompartiman(g), "Gerekli kompartıman sayısı").deger == 2


def test_ek4_kontrol_sistemi_sinirsiz():
    g = Girdi(kullanim="endustriyel", tehlike="OT3", kat_sayisi=3, en_buyuk_kat_alani=9000, yagmurlama_var=True)
    assert bul(H.kompartiman(g), "kontrolü").deger == "Sınırsız"


# --- Kaçış uzaklığı (Ek-5/B) ----------------------------------------------------
def test_kacis_uzakligi_endustriyel():
    g = varsayilan()
    g.yagmurlama_var = True
    r = bul(H.kullanici_yuku_ve_kacis(g), "En çok kaçış uzaklığı")
    assert r.deger == 90.0           # 60 m × 1,5 (kolay alevlenici üretim yok)
    g.kolay_alevlenici = True
    assert bul(H.kullanici_yuku_ve_kacis(g), "En çok kaçış uzaklığı").deger == 60.0
    g.yagmurlama_var = False
    assert bul(H.kullanici_yuku_ve_kacis(g), "En çok kaçış uzaklığı").deger == 30.0


def test_cikis_sayisi_ve_genislik():
    g = varsayilan()                               # 500 kişi
    s = H.kullanici_yuku_ve_kacis(g)
    assert bul(s, "Kat kullanıcı yükü").deger == 500
    assert bul(s, "Gerekli toplam genişlik — Dışarı çıkış kapısı").deger == pytest.approx(250)   # 500/100*50
    assert bul(s, "Gerekli en az çıkış sayısı").deger == 2
    g.katlar[0].mahaller[0].alan = 6000            # 600 kişi → en az 3 çıkış
    assert bul(H.kullanici_yuku_ve_kacis(g), "Gerekli en az çıkış sayısı").deger == 3


def test_madde52_tek_cikis():
    g = Girdi(kullanim="endustriyel", yapi_yuksekligi=8, bina_yuksekligi=8, yagmurlama_var=True)
    g.katlar = [Kat(mahaller=[Mahal("Atölye", 300, 10)], en_uzak_mesafe_m=20)]   # 30 kişi
    assert bul(H.kullanici_yuku_ve_kacis(g), "Gerekli en az çıkış sayısı").deger == 1


# --- Sprinkler / hidrant / söndürücü ----------------------------------------------
def test_sprinkler_zorunlu_kolay_alevlenici():
    g = Girdi(kullanim="endustriyel", kolay_alevlenici=True, toplam_kapali_alan=1500, yagmurlama_var=False)
    r = bul(H.sprinkler_zorunlulugu(g), "Otomatik yağmurlama")
    assert r.durum == UYGUN_DEGIL


def test_su_deposu_yt_hidrolik():
    g = Girdi(kullanim="endustriyel", tehlike="YT4", yagmurlama_var=True)
    s = H.su_deposu_ve_pompa(g)
    assert "Hidrolik" in str(bul(s, "Yağmurlama debisi").deger) or bul(s, "Yağmurlama debisi").durum != UYGUN


def test_su_deposu_kuru_sistem():
    g = Girdi(kullanim="endustriyel", tehlike="OT3", yagmurlama_var=True, yagmurlama_tipi="kuru", es_zamanli_dolap=2)
    s = H.su_deposu_ve_pompa(g)
    assert bul(s, "Yağmurlama debisi").deger == pytest.approx(5.0 * 270)


def test_soendurucu_adedi():
    g = Girdi(kullanim="endustriyel", tehlike="OT2", toplam_kapali_alan=5000, bina_boyu=100, bina_eni=50, kat_sayisi=1)
    r = bul(H.dolap_hidrant_sondurucu(g), "alana göre")
    assert r.deger == 20           # 5000 / 250


def test_kapsama_adedi():
    assert H.kapsama_adedi(100, 50, 25) == math.ceil(100 / (25 * 2**0.5)) * math.ceil(50 / (25 * 2**0.5))
    assert H.kapsama_adedi(0, 50, 25) == 0


def test_hidrant_zorunlu():
    g = Girdi(kullanim="endustriyel", taban_alani=6000, hidrant_var=False)
    assert bul(H.dolap_hidrant_sondurucu(g), "Dış hidrant").durum == UYGUN_DEGIL


# --- Duman, aydınlatma, ekipler ----------------------------------------------------
def test_duman_10_hava_degisimi():
    g = Girdi(duman_mahalleri=[DumanMahali("Otopark", "otopark", 2500, 3.0)])
    s = H.duman_basinclandirma(g)
    assert bul(s, "10 hava değişimi").deger == 75000
    assert bul(s, "Mekanik duman tahliyesi").deger == "Mecburi"


def test_isaret_gorulebilirlik():
    g = Girdi(isaret_yuksekligi_cm=20, isaret_aydinlatma="icten", kacis_yolu_uzunlugu_m=100)
    s = H.algilama_aydinlatma(g)
    assert bul(s, "azami görülebilirlik").deger == 40
    assert bul(s, "en az yönlendirme işareti").deger == 3


def test_ekipler():
    g = Girdi(calisan_sayisi=120)
    assert bul(H.ekipler(g), "Toplam asgari").deger == 10
    g = Girdi(calisan_sayisi=30)
    assert H.ekipler(g)[0].durum == "GEREKMEZ"


# --- Orman ----------------------------------------------------------------------
def test_orman_egim():
    g = Girdi(kullanim="endustriyel", toplam_kapali_alan=3000, orman_yakin=True, arazi_egimi_yuzde=40)
    s = H.cevre_erisim(g)
    assert bul(s, "aşağı yön").deger == 200
    assert bul(s, "diğer yönler").deger == 150


# --- Tehlikeli madde ---------------------------------------------------------------
def test_lpg_ek10_azaltma():
    g = Girdi(lpg_tank_m3=5, lpg_tank_tur="yerustu", lpg_duvar_4saat=True, lpg_alt_yalitim_2saat=True)
    r = bul(H.tehlikeli_madde(g), "yerüstü tankı")
    assert r.deger == pytest.approx(7.5 / 3, abs=0.05)


def test_yanici_sivi_ia_esdegeri():
    g = Girdi(sivi_tanklar=[SivirTank("T1", "IA", 6000, "yerustu"), SivirTank("T2", "II", 12000 * 1, "yerustu")])
    r = bul(H.tehlikeli_madde(g), "Sınıf IA cinsinden")
    assert r.deger == pytest.approx(6000 + 12000 / 12)


# --- Bütün akış ---------------------------------------------------------------------
def test_hepsi_calisir_ve_json():
    g = varsayilan()
    g.merdivenler = [Merdiven("KM-1", 150, 170, 280, 12, 280, 230, 1, 90, 120)]
    g.kapilar = [Kapi("K-1", 120, 210, 2, 100, True, False, 90)]
    g.sivi_tanklar = [SivirTank("T1", "IIIA", 5000, "yerustu")]
    g.duman_mahalleri = [DumanMahali("Kazan", "kazan", 150, 4)]
    g.kazan_var, g.kazan_kw, g.kazan_alani_m2 = True, 500, 120
    s = H.hesapla(g)
    assert len(s) > 50
    g2 = Girdi.from_json(g.to_json())
    assert len(H.hesapla(g2)) == len(s)
    assert H.ozet(s)
