"""Örnek proje (arayüzde 'Örnek yükle' ve testlerde kullanılır)."""
from .modeller import DumanMahali, Girdi, Kapi, Kat, Mahal, Merdiven, SivirTank


def ornek_fabrika() -> Girdi:
    g = Girdi(
        proje_adi="Örnek Mobilya Fabrikası", tesis_adi="Örnek Sanayi A.Ş.", adres="Organize Sanayi Bölgesi, 1. Cadde No:5",
        hazirlayan="", kullanim="endustriyel", tehlike="OT3",
        yapi_yuksekligi=12, bina_yuksekligi=10, kat_sayisi=2, bodrum_kat_sayisi=0,
        taban_alani=6000, toplam_kapali_alan=9000, en_buyuk_kat_alani=6000, bina_boyu=120, bina_eni=50, cephe_genisligi=120,
        yagmurlama_var=True, yagmurlama_tipi="islak", algilama_var=True, duman_tahliye_var=True,
        tasiyici="celik", kolay_alevlenici=True,
        spr_yukseklik_h=10, es_zamanli_dolap=2, hidrant_risk="riskli",
        statik_yukseklik_mSS=14, boru_kaybi_mSS=18, akma_basinci_mSS=70,
        pompa_anma_debi_m3h=150, pompa_anma_basma_mSS=100, pompa_kapali_vana_basma_mSS=130, pompa_150_debi_basma_mSS=70,
        mevcut_su_deposu_m3=200,
        calisan_sayisi=180, kacis_yolu_uzunlugu_m=120, itfaiye_son_nokta_mesafe_m=30,
        ic_yol_genislik_m=6, ic_yol_ic_yaricap_m=12, ic_yol_dis_yaricap_m=16, ic_yol_egim_yuzde=4, ic_yol_serbest_yukseklik_m=4.5, ic_yol_tasima_yuku_ton=20,
        kazan_var=True, kazan_kw=600, kazan_alani_m2=60, kazan_kapi_sayisi=2, kazan_sivi_yakit=False,
        jenerator_var=True, yagli_trafo_var=False, yangin_butonu_adedi=12,
    )
    g.katlar = [
        Kat(ad="Zemin kat", mahaller=[
            Mahal("Üretim holü", 4800, 10), Mahal("Hammadde deposu", 900, 30), Mahal("Yemekhane (net)", 150, 1.5, sayilir=True)],
            cikis_sayisi=4, cikis_turu="dis_kapi", mevcut_genislik_cm=480, tekil_cikis_genislik_cm=120, yon="iki",
            en_uzak_mesafe_m=70, mekan_diyagonal_m=130, cikislar_arasi_mesafe_m=60, cikmaz_mesafe_m=12),
        Kat(ad="1. kat (ofis)", mahaller=[Mahal("Ofisler", 900, 10)],
            cikis_sayisi=2, cikis_turu="merdiven", mevcut_genislik_cm=300, tekil_cikis_genislik_cm=140, yon="iki",
            en_uzak_mesafe_m=40, cikmaz_mesafe_m=10),
    ]
    g.merdivenler = [Merdiven("KM-1", 150, 170, 280, 10, 260, 230, 2, 60, 120)]
    g.kapilar = [Kapi("Ana çıkış", 200, 210, 2, 300, True, False, 80)]
    g.duman_mahalleri = [DumanMahali("Kapalı otopark", "otopark", 2200, 3.0)]
    g.sivi_tanklar = [SivirTank("Tiner tankı", "IB", 2000, "yerustu")]
    return g
