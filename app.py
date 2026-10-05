"""Yangın Koruma Hesap Uygulaması (Streamlit arayüzü).

Çalıştırma:  streamlit run app.py
"""
from __future__ import annotations

import dataclasses
import datetime as dt

import pandas as pd
import streamlit as st

from yangin import hesaplar as H
from yangin import rapor
from yangin import tablolar as T
from yangin.modeller import (
    BILGI, GEREKLI, GEREKMEZ, KONTROL, KOSULLU, UYGUN, UYGUN_DEGIL,
    DumanMahali, Girdi, Kapi, Kat, Mahal, Merdiven, SivirTank,
)
from yangin.ornek import ornek_fabrika

st.set_page_config(page_title="Yangın Koruma Hesabı", page_icon="🔥", layout="wide")

LIST_ALANLAR = {"katlar", "merdivenler", "kapilar", "duman_mahalleri", "sivi_tanklar"}
SADE_ALANLAR = [f.name for f in dataclasses.fields(Girdi) if f.name not in LIST_ALANLAR]

EK5A_AD = [a for a, _, _ in T.EK5A]
EK5A_KATSAYI = {a: k for a, k, _ in T.EK5A}
CIKIS_TURLERI = {"dis_kapi": "Dışarı çıkış kapısı", "diger_kapi": "Diğer kapı / koridor kapısı", "merdiven": "Kaçış merdiveni", "koridor": "Rampa / koridor"}
YONLER = {"iki": "İki yön", "tek": "Tek yön"}


# ---------------------------------------------------------------------------
# Durum yönetimi
# ---------------------------------------------------------------------------
def _df_mahal(g: Girdi) -> pd.DataFrame:
    satirlar = []
    for k in g.katlar:
        for m in k.mahaller:
            tur = next((a for a, kat, _ in T.EK5A if abs(kat - m.katsayi) < 1e-9 and "Diğer" not in a), "Diğer / özel katsayı (elle gir)")
            satirlar.append({"Kat": k.ad, "Mahal": m.ad, "Tür (Ek-5/A)": tur, "Alan (m²)": m.alan,
                             "Özel katsayı (m²/kişi)": m.katsayi if tur.startswith("Diğer") else 0.0,
                             "Belirli kişi sayısı": m.kisi_belirli or 0.0, "Sayılır": m.sayilir})
    if not satirlar:
        satirlar = [{"Kat": "Zemin kat", "Mahal": "Üretim holü", "Tür (Ek-5/A)": EK5A_AD[0], "Alan (m²)": 0.0,
                     "Özel katsayı (m²/kişi)": 0.0, "Belirli kişi sayısı": 0.0, "Sayılır": True}]
    return pd.DataFrame(satirlar)


def _df_kat(g: Girdi) -> pd.DataFrame:
    satirlar = [{"Kat": k.ad, "Çıkış sayısı": k.cikis_sayisi, "Çıkış türü": CIKIS_TURLERI[k.cikis_turu],
                 "Mevcut toplam genişlik (cm)": k.mevcut_genislik_cm, "En dar tekil çıkış (cm)": k.tekil_cikis_genislik_cm,
                 "Yön": YONLER[k.yon], "En uzak mesafe (m)": k.en_uzak_mesafe_m, "Kuş uçuşu (m)": k.kus_ucusu_mesafe_m,
                 "Çıkmaz koridor (m)": k.cikmaz_mesafe_m, "Mekân diyagonali (m)": k.mekan_diyagonal_m,
                 "Çıkışlar arası (m)": k.cikislar_arasi_mesafe_m} for k in g.katlar]
    if not satirlar:
        satirlar = [{"Kat": "Zemin kat", "Çıkış sayısı": 2, "Çıkış türü": CIKIS_TURLERI["dis_kapi"], "Mevcut toplam genişlik (cm)": 0.0,
                     "En dar tekil çıkış (cm)": 0.0, "Yön": YONLER["iki"], "En uzak mesafe (m)": 0.0, "Kuş uçuşu (m)": 0.0,
                     "Çıkmaz koridor (m)": 0.0, "Mekân diyagonali (m)": 0.0, "Çıkışlar arası (m)": 0.0}]
    return pd.DataFrame(satirlar)


def _df_merdiven(g: Girdi) -> pd.DataFrame:
    return pd.DataFrame([{"Ad": m.ad, "Genişlik (cm)": m.genislik_cm, "Rıht (mm)": m.rihts_mm, "Basış (mm)": m.basamak_genislik_mm,
                          "Sahanlık arası basamak": m.sahanlik_arasi_basamak, "Sahanlık arası kot (cm)": m.sahanlik_arasi_kot_cm,
                          "Baş yüksekliği (cm)": m.bas_yuksekligi_cm, "Hizmet verilen kat": m.hizmet_verilen_kat,
                          "Kapı dayanımı (dk)": m.kapi_dayanim_dk, "Duvar dayanımı (dk)": m.duvar_dayanim_dk,
                          "Kattaki kullanıcı": m.kullanici_sayisi_kat, "Dengelenmiş (kova)": m.dengelenmis} for m in g.merdivenler]
                        or [{"Ad": "KM-1", "Genişlik (cm)": 0.0, "Rıht (mm)": 0.0, "Basış (mm)": 0.0, "Sahanlık arası basamak": 0,
                             "Sahanlık arası kot (cm)": 0.0, "Baş yüksekliği (cm)": 0.0, "Hizmet verilen kat": 1,
                             "Kapı dayanımı (dk)": 0.0, "Duvar dayanımı (dk)": 0.0, "Kattaki kullanıcı": 0.0, "Dengelenmiş (kova)": False}])


def _df_kapi(g: Girdi) -> pd.DataFrame:
    return pd.DataFrame([{"Ad": k.ad, "Temiz genişlik (cm)": k.temiz_genislik_cm, "Yükseklik (cm)": k.yukseklik_cm, "Kanat": k.kanat_sayisi,
                          "Mekân kişi yükü": k.kisi_yuku, "Kaçış yönüne açılıyor": k.kacis_yonune_aciliyor, "Eşik var": k.esik_var,
                          "Açma kuvveti (N)": k.acma_kuvveti_N} for k in g.kapilar]
                        or [{"Ad": "K-1", "Temiz genişlik (cm)": 0.0, "Yükseklik (cm)": 0.0, "Kanat": 1, "Mekân kişi yükü": 0.0,
                             "Kaçış yönüne açılıyor": True, "Eşik var": False, "Açma kuvveti (N)": 0.0}])


def _df_duman(g: Girdi) -> pd.DataFrame:
    return pd.DataFrame([{"Ad": m.ad, "Tür": m.tur, "Alan (m²)": m.alan_m2, "Yükseklik (m)": m.yukseklik_m} for m in g.duman_mahalleri]
                        or [{"Ad": "Kazan dairesi", "Tür": "kazan", "Alan (m²)": 0.0, "Yükseklik (m)": 3.0}])


def _df_tank(g: Girdi) -> pd.DataFrame:
    return pd.DataFrame([{"Ad": t.ad, "Sınıf": t.sinif, "Hacim (L)": t.hacim_L, "Tür": t.tur} for t in g.sivi_tanklar]
                        or [{"Ad": "Tank-1", "Sınıf": "II", "Hacim (L)": 0.0, "Tür": "yerustu"}])


def durum_yukle(g: Girdi) -> None:
    """Girdi nesnesini widget durumlarına yazar (örnek yükleme / dosyadan açma)."""
    for ad in SADE_ALANLAR:
        v = getattr(g, ad)
        varsayilan = getattr(Girdi(), ad)
        if isinstance(varsayilan, float) and not isinstance(v, bool):
            v = float(v)          # number_input: min_value ile aynı sayısal tip gerekir
        elif isinstance(varsayilan, int) and not isinstance(varsayilan, bool) and not isinstance(v, bool):
            v = int(v)
        st.session_state["g_" + ad] = v
    st.session_state["df_mahal"] = _df_mahal(g)
    st.session_state["df_kat"] = _df_kat(g)
    st.session_state["df_merdiven"] = _df_merdiven(g)
    st.session_state["df_kapi"] = _df_kapi(g)
    st.session_state["df_duman"] = _df_duman(g)
    st.session_state["df_tank"] = _df_tank(g)
    st.session_state["editor_sayac"] = st.session_state.get("editor_sayac", 0) + 1


def _f(x, d=0.0) -> float:
    try:
        return float(x) if pd.notna(x) else d
    except (TypeError, ValueError):
        return d


def _s(x, d="") -> str:
    return str(x) if pd.notna(x) and str(x) != "" else d


def girdi_topla() -> Girdi:
    g = Girdi(**{ad: st.session_state["g_" + ad] for ad in SADE_ALANLAR})
    ters_cikis = {v: k for k, v in CIKIS_TURLERI.items()}
    ters_yon = {v: k for k, v in YONLER.items()}
    mah = st.session_state["df_mahal"].dropna(how="all")
    kat_df = st.session_state["df_kat"].dropna(how="all")
    katlar: dict[str, Kat] = {}
    for _, r in kat_df.iterrows():
        ad = _s(r["Kat"], "Kat")
        katlar[ad] = Kat(ad=ad, cikis_sayisi=int(_f(r["Çıkış sayısı"], 2)), cikis_turu=ters_cikis.get(_s(r["Çıkış türü"]), "dis_kapi"),
                         mevcut_genislik_cm=_f(r["Mevcut toplam genişlik (cm)"]), tekil_cikis_genislik_cm=_f(r["En dar tekil çıkış (cm)"]),
                         yon=ters_yon.get(_s(r["Yön"]), "iki"), en_uzak_mesafe_m=_f(r["En uzak mesafe (m)"]),
                         kus_ucusu_mesafe_m=_f(r["Kuş uçuşu (m)"]), cikmaz_mesafe_m=_f(r["Çıkmaz koridor (m)"]),
                         mekan_diyagonal_m=_f(r["Mekân diyagonali (m)"]), cikislar_arasi_mesafe_m=_f(r["Çıkışlar arası (m)"]))
    for _, r in mah.iterrows():
        kad = _s(r["Kat"], "Kat")
        katlar.setdefault(kad, Kat(ad=kad))
        ozel = _f(r["Özel katsayı (m²/kişi)"])
        tur = _s(r["Tür (Ek-5/A)"], EK5A_AD[0])
        katsayi = ozel if ozel > 0 else EK5A_KATSAYI.get(tur, 10.0)
        bel = _f(r["Belirli kişi sayısı"])
        katlar[kad].mahaller.append(Mahal(ad=_s(r["Mahal"], "Mahal"), alan=_f(r["Alan (m²)"]), katsayi=katsayi,
                                          kisi_belirli=bel if bel > 0 else None, sayilir=bool(r["Sayılır"])))
    g.katlar = list(katlar.values())
    g.merdivenler = [Merdiven(ad=_s(r["Ad"], "KM"), genislik_cm=_f(r["Genişlik (cm)"]), rihts_mm=_f(r["Rıht (mm)"]), basamak_genislik_mm=_f(r["Basış (mm)"]),
                              sahanlik_arasi_basamak=int(_f(r["Sahanlık arası basamak"])), sahanlik_arasi_kot_cm=_f(r["Sahanlık arası kot (cm)"]),
                              bas_yuksekligi_cm=_f(r["Baş yüksekliği (cm)"]), hizmet_verilen_kat=int(_f(r["Hizmet verilen kat"], 1)),
                              kapi_dayanim_dk=_f(r["Kapı dayanımı (dk)"]), duvar_dayanim_dk=_f(r["Duvar dayanımı (dk)"]),
                              kullanici_sayisi_kat=_f(r["Kattaki kullanıcı"]), dengelenmis=bool(r["Dengelenmiş (kova)"]))
                     for _, r in st.session_state["df_merdiven"].dropna(how="all").iterrows()]
    g.kapilar = [Kapi(ad=_s(r["Ad"], "K"), temiz_genislik_cm=_f(r["Temiz genişlik (cm)"]), yukseklik_cm=_f(r["Yükseklik (cm)"]), kanat_sayisi=int(_f(r["Kanat"], 1)),
                      kisi_yuku=_f(r["Mekân kişi yükü"]), kacis_yonune_aciliyor=bool(r["Kaçış yönüne açılıyor"]), esik_var=bool(r["Eşik var"]),
                      acma_kuvveti_N=_f(r["Açma kuvveti (N)"]))
                 for _, r in st.session_state["df_kapi"].dropna(how="all").iterrows()]
    g.duman_mahalleri = [DumanMahali(ad=_s(r["Ad"], "Mahal"), tur=_s(r["Tür"], "diger"), alan_m2=_f(r["Alan (m²)"]), yukseklik_m=_f(r["Yükseklik (m)"], 3.0))
                         for _, r in st.session_state["df_duman"].dropna(how="all").iterrows()]
    g.sivi_tanklar = [SivirTank(ad=_s(r["Ad"], "Tank"), sinif=_s(r["Sınıf"], "II"), hacim_L=_f(r["Hacim (L)"]), tur=_s(r["Tür"], "yerustu"))
                      for _, r in st.session_state["df_tank"].dropna(how="all").iterrows()]
    return g


# ---------------------------------------------------------------------------
# Widget yardımcıları (anahtar = "g_" + alan adı)
# ---------------------------------------------------------------------------
def _key(ad: str) -> str:
    return "g_" + ad


def metin(label, ad, **kw):
    return st.text_input(label, key=_key(ad), **kw)


def sayi(label, ad, adim=1.0, minimum=0.0, yardim=None, format="%.2f"):
    return st.number_input(label, min_value=minimum, step=adim, key=_key(ad), help=yardim, format=format)


def tam(label, ad, minimum=0, yardim=None):
    return st.number_input(label, min_value=minimum, step=1, key=_key(ad), help=yardim)


def evet(label, ad, yardim=None):
    return st.checkbox(label, key=_key(ad), help=yardim)


def sec(label, ad, secenekler: dict, yardim=None):
    return st.selectbox(label, list(secenekler), key=_key(ad), format_func=lambda k: secenekler[k], help=yardim)


def tablo(ad_state, kolonlar, baslik, yardim=None):
    st.markdown(f"**{baslik}**")
    if yardim:
        st.caption(yardim)
    st.session_state[ad_state] = st.data_editor(
        st.session_state[ad_state], num_rows="dynamic", width="stretch", column_config=kolonlar,
        key=f"ed_{ad_state}_{st.session_state.get('editor_sayac', 0)}", hide_index=True)


# ---------------------------------------------------------------------------
# Başlangıç
# ---------------------------------------------------------------------------
if "baslatildi" not in st.session_state:
    durum_yukle(Girdi())
    st.session_state["g_tarih"] = dt.date.today().strftime("%d.%m.%Y")
    st.session_state["baslatildi"] = True

st.title("🔥 Yangın Koruma Hesap Uygulaması")
st.caption("Binaların Yangından Korunması Hakkında Yönetmelik (RG 19.12.2007/26735, 4825 sayılı CK ile değişik) — fabrika / endüstriyel yapılar odaklı hesap ve kontrol. "
           "Sonuçlar Excel veya Word raporu olarak indirilebilir.")

with st.sidebar:
    st.header("Proje")
    if st.button("Örnek fabrika yükle", width="stretch"):
        durum_yukle(ornek_fabrika())
        st.rerun()
    if st.button("Formu sıfırla", width="stretch"):
        durum_yukle(Girdi())
        st.rerun()
    yuklenen = st.file_uploader("Kayıtlı projeyi aç (.json)", type=["json"])
    if yuklenen is not None and st.session_state.get("son_yuklenen") != yuklenen.file_id:
        try:
            durum_yukle(Girdi.from_json(yuklenen.getvalue().decode("utf-8")))
            st.session_state["son_yuklenen"] = yuklenen.file_id
            st.rerun()
        except Exception as e:  # noqa: BLE001
            st.error(f"Dosya okunamadı: {e}")
    st.divider()
    st.markdown("**Nasıl kullanılır?**\n1. Sekmeleri soldan sağa doldurun.\n2. *Sonuçlar ve Rapor* sekmesinde hesap sonuçlarını görün.\n3. Excel/Word raporunu indirin.\n\n"
                "Boş bırakılan (0) ölçülü değerler için *VERİ GİRİLMEDİ* uyarısı üretilir ve gerekli değer yine de hesaplanır.")

tabs = st.tabs(["1 Genel", "2 Kullanıcı yükü ve kaçış", "3 Merdiven ve kapılar", "4 Su ve söndürme", "5 Algılama, duman, aydınlatma",
                "6 Kazan ve tehlikeli madde", "7 Çevre ve ekipler", "8 Sonuçlar ve Rapor"])

# ---- 1 Genel
with tabs[0]:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Proje")
        metin("Proje adı", "proje_adi")
        metin("Tesis / firma", "tesis_adi")
        metin("Adres", "adres")
        metin("Hazırlayan", "hazirlayan")
        metin("Tarih", "tarih")
        evet("Mevcut yapı (Onuncu Kısım hükümleri / Ek-14)", "mevcut_yapi")
        evet("Karışık kullanım (fabrika + büro vb., yangın bölmesiyle ayrılamıyor)", "karisik_kullanim", "Madde 18")
    with c2:
        st.subheader("Sınıflandırma")
        sec("Kullanım sınıfı (Madde 8)", "kullanim", T.KULLANIM_SINIFLARI)
        tesis_secenek = ["(Seçiniz)"] + [f"{k} — {ad} → {T.TEHLIKE_SINIFLARI[sn]}" for k, ad, sn in T.EK1_TESISLER]
        secilen = st.selectbox("Üretim/tesis türü (Ek-1/B-C) — tehlike sınıfını önerir", tesis_secenek, key="tesis_turu")
        if secilen != "(Seçiniz)":
            oneri = T.EK1_TESISLER[tesis_secenek.index(secilen) - 1][2]
            if st.session_state.get("son_tesis_turu") != secilen:
                st.session_state["g_tehlike"] = oneri
                st.session_state["son_tesis_turu"] = secilen
        sec("Tehlike sınıfı (Madde 19)", "tehlike", T.TEHLIKE_SINIFLARI, "Binada farklı tehlike sınıfları varsa en yükseği seçilir. Boyama işlemi gibi yüksek yangın yükü olan OT-1/2 alanlar OT-3 sayılır.")
        evet("Kolay alevlenici / parlayıcı madde üretiliyor veya bulunduruluyor", "kolay_alevlenici", "Madde 52(d), 96(2)e, Ek-5/B dipnotu")
        evet("Yapımda yanmaz ürünler kullanılmış", "yanmaz_malzeme_yapim", "Madde 52(ç)")
        sec("Taşıyıcı sistem", "tasiyici", {"betonarme": "Betonarme", "celik": "Çelik", "ahsap": "Ahşap", "kagir": "Kâgir"})
    with c3:
        st.subheader("Aktif sistemler")
        evet("Otomatik yağmurlama (sprinkler)", "yagmurlama_var")
        sec("Yağmurlama sistemi tipi", "yagmurlama_tipi", {"islak": "Islak / ön etkili", "kuru": "Kuru / değişken"})
        evet("Otomatik yangın algılama", "algilama_var")
        evet("Duman tahliye sistemi", "duman_tahliye_var")
        evet("Dış hidrant sistemi", "hidrant_var")
        evet("Yangın dolabı sistemi", "dolap_var")
    st.subheader("Geometri")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        sayi("Yapı yüksekliği (m)", "yapi_yuksekligi", 0.5, yardim="Bodrum ve çatı arası dâhil tüm katların toplam yüksekliği (Madde 4)")
        sayi("Bina yüksekliği (m)", "bina_yuksekligi", 0.5, yardim="Kot aldığı noktadan saçak seviyesine (Madde 4)")
    with g2:
        tam("Zemin üstü kat sayısı", "kat_sayisi", 1)
        tam("Bodrum kat sayısı", "bodrum_kat_sayisi")
        sayi("Bodrum derinliği (m)", "bodrum_derinligi", 0.5, yardim="En alt bodrum döşemesi ile zemin kat döşemesi arası")
    with g3:
        sayi("Bina taban (oturum) alanı (m²)", "taban_alani", 50.0)
        sayi("Tesis toplam taban alanı (m²)", "tesis_toplam_taban_alani", 50.0, yardim="Parseldeki tüm binaların taban alanları toplamı; 0 ise bu bina esas alınır (Madde 95(7))")
        sayi("Toplam kapalı alan (m²)", "toplam_kapali_alan", 50.0)
    with g4:
        sayi("En büyük kat alanı (m²)", "en_buyuk_kat_alani", 50.0)
        sayi("Kompartıman alanı (m²)", "kompartiman_alani", 50.0, yardim="0 ise en büyük kat alanı esas alınır")
        sayi("Kapalı otopark alanı (m²)", "otopark_alani", 10.0)
    g5, g6, g7 = st.columns(3)
    with g5:
        sayi("Bina boyu (m)", "bina_boyu", 1.0)
    with g6:
        sayi("Bina eni (m)", "bina_eni", 1.0)
    with g7:
        sayi("Cephe genişliği (m)", "cephe_genisligi", 1.0)
    st.subheader("Betonarme / ahşap taşıyıcı (isteğe bağlı)")
    b1, b2, b3, b4, b5 = st.columns(5)
    with b1: sayi("Net beton paspayı — kolon (mm)", "net_beton_kolon_mm", 5.0)
    with b2: sayi("Net beton paspayı — kiriş (mm)", "net_beton_kiris_mm", 5.0)
    with b3: sayi("Net beton paspayı — döşeme (mm)", "net_beton_doseme_mm", 5.0)
    with b4:
        sayi("Ahşap eleman genişliği b (mm)", "ahsap_b_mm", 10.0)
        sayi("Ahşap eleman yüksekliği h (mm)", "ahsap_h_mm", 10.0)
    with b5:
        sayi("Yanma hızı (mm/dk)", "ahsap_yanma_hizi", 0.05, yardim="Madde 23(6): 0,6–0,8 mm/dk")
        tam("Yangına maruz yüzey sayısı", "ahsap_yuzey", 3)

# ---- 2 Kullanıcı yükü ve kaçış
with tabs[1]:
    st.info("Önce *Mahaller* tablosuna her katın mahallerini girin (alan ve Ek-5/A türü). Sonra *Kat kaçış verileri* tablosunda aynı kat adlarıyla çıkış bilgilerini girin. "
            "Tuvalet, soyunma, depo gibi aynı anda kullanılmayan mahalleri 'Sayılır' kutusunu kaldırarak hesap dışı bırakabilirsiniz (Madde 31(6)). "
            "Ek-5/A: ilk satırlardaki net alan, diğerlerinde brüt alan esas alınır.")
    tablo("df_mahal", {
        "Kat": st.column_config.TextColumn("Kat", required=True),
        "Mahal": st.column_config.TextColumn("Mahal"),
        "Tür (Ek-5/A)": st.column_config.SelectboxColumn("Tür (Ek-5/A)", options=EK5A_AD, required=True, width="large"),
        "Alan (m²)": st.column_config.NumberColumn("Alan (m²)", min_value=0.0, format="%.1f"),
        "Özel katsayı (m²/kişi)": st.column_config.NumberColumn("Özel katsayı (m²/kişi)", min_value=0.0, help="Yalnızca 'Diğer / özel' türünde"),
        "Belirli kişi sayısı": st.column_config.NumberColumn("Belirli kişi sayısı", min_value=0.0, help="Kişi sayısı belirli mahallerde hesaplanandan az olmamak üzere bu sayı alınır"),
        "Sayılır": st.column_config.CheckboxColumn("Sayılır"),
    }, "Mahaller (kullanıcı yükü)")
    tablo("df_kat", {
        "Çıkış türü": st.column_config.SelectboxColumn("Çıkış türü", options=list(CIKIS_TURLERI.values()), required=True),
        "Yön": st.column_config.SelectboxColumn("Yön", options=list(YONLER.values()), required=True),
        "Çıkış sayısı": st.column_config.NumberColumn("Çıkış sayısı", min_value=0, step=1),
    }, "Kat kaçış verileri",
        "Çıkış türü: kontrol edilecek eleman (dışarı çıkış kapısı, kaçış merdiveni vb.). Genişlik = o türdeki çıkışların toplam temiz genişliği. "
        "Mesafeler en uzak noktadan en yakın çıkışa (Madde 32).")

# ---- 3 Merdiven ve kapılar
with tabs[2]:
    tablo("df_merdiven", {"Dengelenmiş (kova)": st.column_config.CheckboxColumn("Dengelenmiş (kova)")}, "Kaçış merdivenleri (Madde 38–46)")
    tablo("df_kapi", {"Kaçış yönüne açılıyor": st.column_config.CheckboxColumn("Kaçış yönüne açılıyor"), "Eşik var": st.column_config.CheckboxColumn("Eşik var")},
          "Kaçış yolu kapıları (Madde 47)")

# ---- 4 Su ve söndürme
with tabs[3]:
    s1, s2, s3 = st.columns(3)
    with s1:
        st.subheader("Yağmurlama")
        sayi("En alt ve en üst başlık arası yükseklik h (m)", "spr_yukseklik_h", 0.5, yardim="Ek-8/A tablo girişi")
        sayi("Başlık başına koruma alanı (m²)", "spr_baslik_alani_m2", 0.5, yardim="0 = otomatik (DT/OT1: 21 m², OT: 12 m², YT: 9 m²)")
        sayi("Koruma alanı (m²) — hidrolik tasarımda", "spr_koruma_alani_m2", 10.0, yardim="0 = Ek-8/B tablo değeri")
    with s2:
        st.subheader("Dolap / hidrant")
        tam("Eş zamanlı çalışan yangın dolabı sayısı", "es_zamanli_dolap", 0, "Kılavuz örneğinde 2 adet alınmıştır")
        sec("Yangın dolabı tipi", "dolap_tipi", {"yari_sert": "Yarı-sert hortum Ø25 (100 l/dk)", "yassi": "Yassı hortum DN50 (400 l/dk)"})
        sec("Hidrant bölge riski", "hidrant_risk", {"cok_riskli": "Çok riskli (50 m)", "riskli": "Riskli (100 m)", "orta": "Orta riskli (125 m)", "az": "Az riskli (150 m)"},
            "Madde 95(3) — tehlike sınıfı ile eşleştirme yönetmelikte yoktur")
        evet("Yapıda sadece çevre hidrant sistemi var", "sadece_hidrant")
        evet("Yapıda sadece yangın dolabı sistemi var", "sadece_dolap")
    with s3:
        st.subheader("Pompa ve depo")
        sayi("Statik yükseklik (mSS)", "statik_yukseklik_mSS", 1.0)
        sayi("Tesisat toplam basınç kaybı (mSS)", "boru_kaybi_mSS", 0.5)
        sayi("Akma basıncı (mSS)", "akma_basinci_mSS", 1.0, yardim="Hidrant çıkışı 700 kPa ≈ 70 mSS (Madde 95(2))")
        sayi("Mevcut/proje su deposu (m³)", "mevcut_su_deposu_m3", 5.0)
    st.subheader("Seçilen pompa karakteristiği (isteğe bağlı kontrol — Madde 93)")
    p1, p2, p3, p4, p5, p6 = st.columns(6)
    with p1: sayi("Anma debisi (m³/h)", "pompa_anma_debi_m3h", 5.0)
    with p2: sayi("Anma basma yük. (mSS)", "pompa_anma_basma_mSS", 1.0)
    with p3: sayi("Kapalı vana basma yük. (mSS)", "pompa_kapali_vana_basma_mSS", 1.0)
    with p4: sayi("%150 debide basma yük. (mSS)", "pompa_150_debi_basma_mSS", 1.0)
    with p5: tam("Asıl pompa adedi", "pompa_adedi", 1)
    with p6: tam("Yedek pompa adedi", "yedek_pompa_adedi")

# ---- 5 Algılama, duman, aydınlatma
with tabs[4]:
    a1, a2 = st.columns(2)
    with a1:
        st.subheader("Algılama ve aydınlatma")
        tam("Projedeki yangın uyarı butonu adedi", "yangin_butonu_adedi")
        sayi("Yönlendirme işareti yüksekliği (cm)", "isaret_yuksekligi_cm", 1.0, yardim="En az 15 cm (Madde 73(4))")
        sec("İşaret aydınlatma tipi", "isaret_aydinlatma", {"icten": "İçeriden/arkadan aydınlatılan (×200)", "distan": "Dışarıdan/kenardan aydınlatılan (×100)"})
        sayi("En uzun kaçış yolu uzunluğu (m)", "kacis_yolu_uzunlugu_m", 1.0)
        sayi("Acil aydınlatma çalışma süresi (dk)", "acil_aydinlatma_sure_dk", 10.0)
        sayi("Ölçülen aydınlık — başlangıç (lux)", "acil_aydinlatma_lux_baslangic", 0.1)
        sayi("Ölçülen aydınlık — süre sonu (lux)", "acil_aydinlatma_lux_bitis", 0.1)
        sayi("En yüksek / en düşük aydınlık oranı", "acil_aydinlatma_max_min_orani", 1.0)
    with a2:
        st.subheader("Basınçlandırma")
        sayi("Merdiven kovası yüksekliği (m)", "merdiven_kovasi_yuksekligi", 0.5, yardim="0 ise bina yüksekliği esas alınır")
        sayi("Basınçlandırılan kapı alanı (m²)", "basinc_kapi_alani_m2", 0.1)
        sayi("Sızıntı debisi (m³/s)", "basinc_sizinti_debisi_m3s", 0.05, yardim="Kapalı kapılardaki sızıntı alanlarından hesaplanan debi (Madde 89(9)-(10))")
    tablo("df_duman", {"Tür": st.column_config.SelectboxColumn("Tür", options=["kazan", "otopark", "bodrum_depo", "diger"], required=True)},
          "Mekanik duman tahliyesi hesabı yapılacak mahaller (Madde 88(3))", "Kazan dairesi, kapalı otopark ve bodrum depo: toplam alan 2000 m²'yi aşarsa mekanik duman tahliyesi ve en az 10 hava değişimi/saat.")

# ---- 6 Kazan ve tehlikeli madde
with tabs[5]:
    k1, k2 = st.columns(2)
    with k1:
        st.subheader("Kazan dairesi, yakıt, trafo, jeneratör")
        evet("Kazan dairesi var", "kazan_var")
        sayi("Kazan ısıl kapasitesi (kW)", "kazan_kw", 10.0)
        sayi("Kazan dairesi döşeme alanı (m²)", "kazan_alani_m2", 5.0)
        tam("Kazan dairesi çıkış kapısı sayısı", "kazan_kapi_sayisi", 0)
        evet("Sıvı yakıtlı kazan", "kazan_sivi_yakit")
        sayi("Kalorifer yakıt deposu hacmi (L)", "yakit_tank_L", 100.0)
        sec("Yakıt deposu yeri", "yakit_yeri", {"bodrum_varil": "Bodrumda varil", "bodrum_sac": "Bodrumda sızıntısız sac kap", "bodrum_komur": "Bina içi bodrum, 120 dk kâgir oda",
                                                "bina_disi": "Bina dışında yeraltı/yerüstü tank", "bagimsiz": "Ayrı, bağımsız tek katlı bina"})
        sayi("Yakıt tankı havuzlama hacmi (L)", "yakit_havuz_L", 100.0)
        evet("Yağlı transformatör var", "yagli_trafo_var")
        evet("Jeneratör var", "jenerator_var")
    with k2:
        st.subheader("LPG")
        sayi("LPG tüp deposu — toplam miktar (kg)", "lpg_tup_kg", 100.0)
        sayi("Dökme LPG tankı — beher tank su hacmi (m³)", "lpg_tank_m3", 1.0)
        sec("LPG tank türü", "lpg_tank_tur", {"yerustu": "Yerüstü", "yeralti": "Yeraltı"})
        evet("Tank ile arsa sınırı arasında ≥1,5 m, 4 saat dayanıklı duvar var", "lpg_duvar_4saat")
        evet("Tank alt yüzeyi 2 saat ısı/yangın yalıtımlı", "lpg_alt_yalitim_2saat")
        st.subheader("Yanıcı / parlayıcı sıvı depolama")
        sec("Depolama yeri (Ek-11)", "sivi_depolama_yeri", {"zemin_ustu": "Zemin seviyesi ve üstündeki depo hacimleri", "acikta": "Açıkta kurulu depolar"})
        sayi("Fabrika/atölye içi tecrit edilmiş depo alanı (m²)", "sivi_depo_alani_m2", 1.0, yardim="Madde 118(3), Ek-12/B")
        sayi("Bu deponun yangın dayanımı (dk)", "sivi_depo_dayanim_dk", 10.0)
        evet("Bu depoda yangın korunumu (sprinkler / CO₂ / kuru kimyevi toz) var", "sivi_depo_yangin_korunum")
        evet("Orijinal kaplarda depolanıyor (aksi halde taşınabilir tank)", "sivi_depo_orijinal_kap")
    tablo("df_tank", {
        "Sınıf": st.column_config.SelectboxColumn("Sınıf", options=list(T.IA_ESDEGER_BOLEN), required=True),
        "Tür": st.column_config.SelectboxColumn("Tür", options=["yerustu", "yeralti", "depo_icinde"], required=True,
                                                help="yerustu: açıkta yerüstü tank; yeralti: yeraltı tankı; depo_icinde: depo binası içinde"),
        "Hacim (L)": st.column_config.NumberColumn("Hacim (L)", min_value=0.0),
    }, "Yanıcı/parlayıcı sıvı tankları ve kapları", "Sınıf IA toplamı eşdeğerlikle hesaplanır (Madde 118(2)); açık tank mesafeleri Ek-12/C ve Ek-12/Ç'den alınır.")

# ---- 7 Çevre ve ekipler
with tabs[6]:
    e1, e2 = st.columns(2)
    with e1:
        st.subheader("İtfaiye erişimi (Madde 22)")
        sayi("İtfaiye aracının son yaklaşma noktasından cepheye yatay uzaklık (m)", "itfaiye_son_nokta_mesafe_m", 1.0)
        sayi("İç ulaşım yolu genişliği (m)", "ic_yol_genislik_m", 0.5)
        evet("İç yol çıkmaz", "ic_yol_cikmaz")
        sayi("Dönemeç iç yarıçapı (m)", "ic_yol_ic_yaricap_m", 0.5)
        sayi("Dönemeç dış yarıçapı (m)", "ic_yol_dis_yaricap_m", 0.5)
        sayi("Boyuna eğim (%)", "ic_yol_egim_yuzde", 0.5)
        sayi("Serbest yükseklik (m)", "ic_yol_serbest_yukseklik_m", 0.1)
        sayi("Taşıma yükü (ton)", "ic_yol_tasima_yuku_ton", 1.0)
    with e2:
        st.subheader("Orman alanı (Madde 7(12), 21)")
        evet("Tesis orman alanı içinde veya bitişiğinde", "orman_yakin")
        sayi("Arazi eğimi (%)", "arazi_egimi_yuzde", 1.0)
        st.subheader("Acil durum ekipleri (Madde 126)")
        sayi("Vardiya başına en yüksek çalışan sayısı", "calisan_sayisi", 1.0, yardim="0 ise hesaplanan kullanıcı yükü esas alınır")

# ---- 8 Sonuçlar
with tabs[7]:
    g = girdi_topla()
    try:
        sonuclar = H.hesapla(g)
    except Exception as e:  # noqa: BLE001
        st.error(f"Hesaplama hatası: {e}")
        st.stop()
    oz = H.ozet(sonuclar)
    cols = st.columns(6)
    for col, (ad, kod) in zip(cols, [("Uygun", UYGUN), ("Uygun değil", UYGUN_DEGIL), ("Gerekli önlem", GEREKLI), ("Koşullu", KOSULLU), ("Veri girilmedi", KONTROL), ("Gerekmez", GEREKMEZ)]):
        col.metric(ad, oz.get(kod, 0))
    uyg_degil = [r for r in sonuclar if r.durum == UYGUN_DEGIL]
    if uyg_degil:
        st.error("**Uygun olmayan hususlar**")
        for r in uyg_degil:
            st.markdown(f"- **{r.kalem}** ({r.bolum.split(' — ')[0]}): {rapor._fmt(r.deger)} {r.birim} — *{r.madde}*. {r.aciklama}")
    else:
        st.success("Girilen verilere göre uygun olmayan husus tespit edilmedi.")

    d1, d2, d3 = st.columns(3)
    adi = (g.proje_adi or "proje").replace(" ", "_")
    with d1:
        st.download_button("📊 Excel raporu (.xlsx)", rapor.excel_olustur(g, sonuclar), file_name=f"{adi}_yangin_hesabi.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch", type="primary")
    with d2:
        st.download_button("📝 Word raporu (.docx)", rapor.word_olustur(g, sonuclar), file_name=f"{adi}_yangin_hesabi.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width="stretch", type="primary")
    with d3:
        st.download_button("💾 Projeyi kaydet (.json)", g.to_json(), file_name=f"{adi}.json", mime="application/json", width="stretch")

    st.subheader("Tüm sonuçlar")
    f1, f2 = st.columns(2)
    bolumler = list(dict.fromkeys(r.bolum.split(" — ")[0] for r in sonuclar))
    sec_bolum = f1.multiselect("Bölüm", bolumler, default=bolumler)
    durumlar = [UYGUN, UYGUN_DEGIL, GEREKLI, KOSULLU, KONTROL, GEREKMEZ, BILGI]
    sec_durum = f2.multiselect("Durum", durumlar, default=[d for d in durumlar if d != BILGI])
    df = pd.DataFrame([{"Bölüm": r.bolum, "Kalem": r.kalem, "Değer": rapor._fmt(r.deger), "Birim": r.birim, "Durum": r.durum, "Madde": r.madde, "Açıklama": r.aciklama}
                       for r in sonuclar if r.bolum.split(" — ")[0] in sec_bolum and r.durum in sec_durum])
    renkler = {k: f"background-color: #{v}" for k, v in rapor.DURUM_RENK.items()}
    st.dataframe(df.style.map(lambda v: renkler.get(v, ""), subset=["Durum"]), width="stretch", hide_index=True, height=600)
