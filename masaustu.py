"""Yangın Koruma Hesap Uygulaması — masaüstü arayüzü (Tkinter).

Çalıştırma:  python masaustu.py     (Windows .exe sürümü bu dosyadan derlenir)
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from yangin import form as FORM
from yangin import hesaplar as H
from yangin import rapor
from yangin import tablolar as T
from yangin.modeller import (
    BILGI, GEREKLI, GEREKMEZ, KONTROL, KOSULLU, UYGUN, UYGUN_DEGIL,
    DumanMahali, Girdi, Kapi, Kat, Mahal, Merdiven, SivirTank,
)
from yangin.etiketler import *  # noqa: F401,F403
from yangin.etiketler import _bool, _f, _i
from yangin.ornek import ornek_fabrika


# --------------------------------------------------------------------------
# Alan tanımları: (alan, etiket, tür, seçenekler)  tür: t=metin f=ondalık i=tam b=evet/hayır c=seçim
# --------------------------------------------------------------------------
SEKMELER = [
    ("Genel", [
        ("Proje", [
            ("proje_adi", "Proje adı", "t", None), ("tesis_adi", "Tesis / firma", "t", None), ("adres", "Adres", "t", None),
            ("hazirlayan", "Hazırlayan", "t", None), ("tarih", "Tarih", "t", None),
            ("mevcut_yapi", "Mevcut yapı (Ek-14 kaçış çarpanı)", "b", None),
            ("karisik_kullanim", "Karışık kullanım (Madde 18)", "b", None)]),
        ("Sınıflandırma", [
            ("kullanim", "Kullanım sınıfı (Madde 8)", "c", T.KULLANIM_SINIFLARI),
            ("@tesis", "Üretim/tesis türü (Ek-1) → tehlike önerir", "tesis", None),
            ("tehlike", "Tehlike sınıfı (Madde 19)", "c", T.TEHLIKE_SINIFLARI),
            ("kolay_alevlenici", "Kolay alevlenici/parlayıcı madde var", "b", None),
            ("yanmaz_malzeme_yapim", "Yapımda yanmaz ürünler kullanılmış", "b", None),
            ("tasiyici", "Taşıyıcı sistem", "c", TASIYICI)]),
        ("Aktif sistemler", [
            ("yagmurlama_var", "Otomatik yağmurlama (sprinkler)", "b", None), ("yagmurlama_tipi", "Yağmurlama tipi", "c", YAGMURLAMA),
            ("algilama_var", "Otomatik yangın algılama", "b", None), ("duman_tahliye_var", "Duman tahliye sistemi", "b", None),
            ("hidrant_var", "Dış hidrant sistemi", "b", None), ("dolap_var", "Yangın dolabı sistemi", "b", None)]),
        ("Geometri", [
            ("yapi_yuksekligi", "Yapı yüksekliği (m)", "f", None), ("bina_yuksekligi", "Bina yüksekliği (m)", "f", None),
            ("kat_sayisi", "Zemin üstü kat sayısı", "i", None), ("bodrum_kat_sayisi", "Bodrum kat sayısı", "i", None),
            ("bodrum_derinligi", "Bodrum derinliği (m)", "f", None), ("taban_alani", "Bina taban alanı (m²)", "f", None),
            ("tesis_toplam_taban_alani", "Tesis toplam taban alanı (m²)", "f", None), ("toplam_kapali_alan", "Toplam kapalı alan (m²)", "f", None),
            ("en_buyuk_kat_alani", "En büyük kat alanı (m²)", "f", None), ("kompartiman_alani", "Kompartıman alanı (m²) [0=kat alanı]", "f", None),
            ("otopark_alani", "Kapalı otopark alanı (m²)", "f", None), ("bina_boyu", "Bina boyu (m)", "f", None),
            ("bina_eni", "Bina eni (m)", "f", None), ("cephe_genisligi", "Cephe genişliği (m)", "f", None)]),
        ("Betonarme / ahşap (isteğe bağlı)", [
            ("net_beton_kolon_mm", "Net beton paspayı — kolon (mm)", "f", None), ("net_beton_kiris_mm", "Net beton paspayı — kiriş (mm)", "f", None),
            ("net_beton_doseme_mm", "Net beton paspayı — döşeme (mm)", "f", None), ("ahsap_b_mm", "Ahşap eleman b (mm)", "f", None),
            ("ahsap_h_mm", "Ahşap eleman h (mm)", "f", None), ("ahsap_yanma_hizi", "Yanma hızı (mm/dk)", "f", None),
            ("ahsap_yuzey", "Yangına maruz yüzey sayısı", "i", None)]),
    ]),
    ("Su ve söndürme", [
        ("Yağmurlama", [
            ("spr_yukseklik_h", "En alt-üst başlık arası yükseklik h (m)", "f", None),
            ("spr_baslik_alani_m2", "Başlık başına koruma alanı (m²) [0=otomatik]", "f", None),
            ("spr_koruma_alani_m2", "Koruma alanı (m²) [0=Ek-8/B]", "f", None)]),
        ("Dolap / hidrant", [
            ("es_zamanli_dolap", "Eş zamanlı yangın dolabı sayısı", "i", None), ("dolap_tipi", "Yangın dolabı tipi", "c", DOLAP),
            ("hidrant_risk", "Hidrant bölge riski", "c", HIDRANT),
            ("sadece_hidrant", "Sadece çevre hidrant sistemi var", "b", None), ("sadece_dolap", "Sadece yangın dolabı sistemi var", "b", None)]),
        ("Pompa ve depo", [
            ("statik_yukseklik_mSS", "Statik yükseklik (mSS)", "f", None), ("boru_kaybi_mSS", "Tesisat basınç kaybı (mSS)", "f", None),
            ("akma_basinci_mSS", "Akma basıncı (mSS)", "f", None), ("mevcut_su_deposu_m3", "Mevcut/proje su deposu (m³)", "f", None),
            ("pompa_anma_debi_m3h", "Seçilen pompa anma debisi (m³/h)", "f", None), ("pompa_anma_basma_mSS", "Anma basma yüksekliği (mSS)", "f", None),
            ("pompa_kapali_vana_basma_mSS", "Kapalı vana basma yük. (mSS)", "f", None), ("pompa_150_debi_basma_mSS", "%150 debide basma yük. (mSS)", "f", None),
            ("pompa_adedi", "Asıl pompa adedi", "i", None), ("yedek_pompa_adedi", "Yedek pompa adedi", "i", None)]),
    ]),
    ("Algılama, duman, aydınlatma", [
        ("Algılama ve aydınlatma", [
            ("yangin_butonu_adedi", "Projedeki yangın uyarı butonu adedi", "i", None), ("isaret_yuksekligi_cm", "Yönlendirme işareti yüksekliği (cm)", "f", None),
            ("isaret_aydinlatma", "İşaret aydınlatma tipi", "c", ISARET), ("kacis_yolu_uzunlugu_m", "En uzun kaçış yolu (m)", "f", None),
            ("acil_aydinlatma_sure_dk", "Acil aydınlatma süresi (dk)", "f", None), ("acil_aydinlatma_lux_baslangic", "Ölçülen aydınlık — başlangıç (lux)", "f", None),
            ("acil_aydinlatma_lux_bitis", "Ölçülen aydınlık — süre sonu (lux)", "f", None), ("acil_aydinlatma_max_min_orani", "Max/min aydınlık oranı", "f", None)]),
        ("Basınçlandırma", [
            ("merdiven_kovasi_yuksekligi", "Merdiven kovası yüksekliği (m) [0=bina yük.]", "f", None),
            ("basinc_kapi_alani_m2", "Basınçlandırılan kapı alanı (m²)", "f", None),
            ("basinc_sizinti_debisi_m3s", "Sızıntı debisi (m³/s)", "f", None)]),
    ]),
    ("Kazan ve tehlikeli madde", [
        ("Kazan, yakıt, trafo, jeneratör", [
            ("kazan_var", "Kazan dairesi var", "b", None), ("kazan_kw", "Kazan ısıl kapasitesi (kW)", "f", None),
            ("kazan_alani_m2", "Kazan dairesi alanı (m²)", "f", None), ("kazan_kapi_sayisi", "Kazan dairesi çıkış kapısı sayısı", "i", None),
            ("kazan_sivi_yakit", "Sıvı yakıtlı kazan", "b", None), ("yakit_tank_L", "Kalorifer yakıt deposu (L)", "f", None),
            ("yakit_yeri", "Yakıt deposu yeri", "c", YAKIT), ("yakit_havuz_L", "Yakıt tankı havuzlama hacmi (L)", "f", None),
            ("yagli_trafo_var", "Yağlı transformatör var", "b", None), ("jenerator_var", "Jeneratör var", "b", None)]),
        ("LPG ve yanıcı sıvı", [
            ("lpg_tup_kg", "LPG tüp deposu (kg)", "f", None), ("lpg_tank_m3", "Dökme LPG tankı beher su hacmi (m³)", "f", None),
            ("lpg_tank_tur", "LPG tank türü", "c", LPG_TUR), ("lpg_duvar_4saat", "≥1,5 m, 4 saat dayanıklı duvar var", "b", None),
            ("lpg_alt_yalitim_2saat", "Tank alt yüzeyi 2 saat yalıtımlı", "b", None),
            ("sivi_depolama_yeri", "Yanıcı sıvı depolama yeri (Ek-11)", "c", SIVI_YER),
            ("sivi_depo_alani_m2", "Fabrika içi tecrit depo alanı (m²)", "f", None), ("sivi_depo_dayanim_dk", "Bu deponun dayanımı (dk)", "f", None),
            ("sivi_depo_yangin_korunum", "Bu depoda yangın korunumu var", "b", None), ("sivi_depo_orijinal_kap", "Orijinal kaplarda depolanıyor", "b", None)]),
    ]),
    ("Çevre ve ekipler", [
        ("İtfaiye erişimi (Madde 22)", [
            ("itfaiye_son_nokta_mesafe_m", "Son yaklaşma noktasından cepheye (m)", "f", None), ("ic_yol_genislik_m", "İç yol genişliği (m)", "f", None),
            ("ic_yol_cikmaz", "İç yol çıkmaz", "b", None), ("ic_yol_ic_yaricap_m", "Dönemeç iç yarıçapı (m)", "f", None),
            ("ic_yol_dis_yaricap_m", "Dönemeç dış yarıçapı (m)", "f", None), ("ic_yol_egim_yuzde", "Boyuna eğim (%)", "f", None),
            ("ic_yol_serbest_yukseklik_m", "Serbest yükseklik (m)", "f", None), ("ic_yol_tasima_yuku_ton", "Taşıma yükü (ton)", "f", None)]),
        ("Orman ve ekipler", [
            ("orman_yakin", "Tesis orman alanı içinde/bitişiğinde", "b", None), ("arazi_egimi_yuzde", "Arazi eğimi (%)", "f", None),
            ("calisan_sayisi", "Vardiya başına en yüksek çalışan sayısı", "f", None)]),
    ]),
]

ALAN_TURU: dict[str, str] = {}
for _, bolumler in SEKMELER:
    for _, alanlar in bolumler:
        for ad, _e, tur, _x in alanlar:
            if not ad.startswith("@"):
                ALAN_TURU[ad] = tur
for ad in (f.name for f in dataclasses.fields(Girdi)):
    assert ad in LIST_ALANLAR or ad in ALAN_TURU, f"Arayüzde eksik alan: {ad}"

# --------------------------------------------------------------------------
# Liste tabloları: (anahtar, başlık, tür, seçenekler, genişlik)
# --------------------------------------------------------------------------

DURUM_RENK = {k: "#" + v for k, v in rapor.DURUM_RENK.items()}


# --------------------------------------------------------------------------
# Yardımcı bileşenler
# --------------------------------------------------------------------------
class KaydirmaCercevesi(ttk.Frame):
    def __init__(self, ana):
        super().__init__(ana)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        dikey = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.icerik = ttk.Frame(self.canvas)
        self.icerik.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.icerik, anchor="nw")
        self.canvas.configure(yscrollcommand=dikey.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        dikey.pack(side="right", fill="y")
        self.canvas.bind("<Enter>", lambda e: self._bagla())
        self.canvas.bind("<Leave>", lambda e: self._coz())

    def _bagla(self):
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _coz(self):
        for o in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.unbind_all(o)


class SatirDialogu(tk.Toplevel):
    """Tablo satırı ekleme/düzenleme penceresi."""

    def __init__(self, ana, kolonlar, degerler: dict):
        super().__init__(ana)
        self.title("Satır")
        self.transient(ana)
        self.grab_set()
        self.sonuc = None
        self.vars = {}
        for r, (anahtar, baslik, tur, secenek, _g) in enumerate(kolonlar):
            ttk.Label(self, text=baslik).grid(row=r, column=0, sticky="w", padx=8, pady=3)
            v = tk.StringVar(value=str(degerler.get(anahtar, "")))
            if tur == "b":
                v = tk.BooleanVar(value=_bool(degerler.get(anahtar, False)))
                ttk.Checkbutton(self, variable=v).grid(row=r, column=1, sticky="w", padx=8)
            elif tur == "c":
                ttk.Combobox(self, textvariable=v, values=secenek, state="readonly", width=44).grid(row=r, column=1, padx=8, pady=3)
            else:
                ttk.Entry(self, textvariable=v, width=46).grid(row=r, column=1, padx=8, pady=3)
            self.vars[anahtar] = v
        alt = ttk.Frame(self)
        alt.grid(row=len(kolonlar), column=0, columnspan=2, pady=8)
        ttk.Button(alt, text="Tamam", command=self._tamam).pack(side="left", padx=6)
        ttk.Button(alt, text="İptal", command=self.destroy).pack(side="left", padx=6)
        self.bind("<Return>", lambda e: self._tamam())
        self.wait_window()

    def _tamam(self):
        self.sonuc = {k: v.get() for k, v in self.vars.items()}
        self.destroy()


class TabloDuzenleyici(ttk.Frame):
    def __init__(self, ana, kolonlar, baslik, aciklama=""):
        super().__init__(ana)
        self.kolonlar = kolonlar
        ttk.Label(self, text=baslik, font=("", 10, "bold")).pack(anchor="w", pady=(8, 0))
        if aciklama:
            ttk.Label(self, text=aciklama, foreground="#555", wraplength=1100, justify="left").pack(anchor="w")
        cerceve = ttk.Frame(self)
        cerceve.pack(fill="both", expand=True, pady=4)
        self.agac = ttk.Treeview(cerceve, columns=[k[0] for k in kolonlar], show="headings", height=7, selectmode="browse")
        for anahtar, baslik_, _t, _s, genislik in kolonlar:
            self.agac.heading(anahtar, text=baslik_)
            self.agac.column(anahtar, width=genislik, anchor="w", stretch=False)
        yatay = ttk.Scrollbar(cerceve, orient="horizontal", command=self.agac.xview)
        dikey = ttk.Scrollbar(cerceve, orient="vertical", command=self.agac.yview)
        self.agac.configure(xscrollcommand=yatay.set, yscrollcommand=dikey.set)
        self.agac.grid(row=0, column=0, sticky="nsew")
        dikey.grid(row=0, column=1, sticky="ns")
        yatay.grid(row=1, column=0, sticky="ew")
        cerceve.rowconfigure(0, weight=1)
        cerceve.columnconfigure(0, weight=1)
        dugmeler = ttk.Frame(self)
        dugmeler.pack(anchor="w")
        for metin, komut in (("Satır ekle", self.ekle), ("Düzenle (çift tık)", self.duzenle), ("Sil", self.sil), ("Kopyala", self.kopyala)):
            ttk.Button(dugmeler, text=metin, command=komut).pack(side="left", padx=3)
        self.agac.bind("<Double-1>", lambda e: self.duzenle())

    def _goster(self, d: dict):
        return [("✔" if (t == "b" and _bool(d.get(k))) else ("" if t == "b" else d.get(k, ""))) for k, _b, t, _s, _g in self.kolonlar]

    def satirlar(self) -> list[dict]:
        out = []
        for iid in self.agac.get_children():
            degerler = self.agac.item(iid, "values")
            d = {}
            for (k, _b, t, _s, _g), v in zip(self.kolonlar, degerler):
                d[k] = (v == "✔") if t == "b" else v
            out.append(d)
        return out

    def doldur(self, satirlar: list[dict]):
        self.agac.delete(*self.agac.get_children())
        for d in satirlar:
            self.agac.insert("", "end", values=self._goster(d))

    def ekle(self):
        varsayilan = {k: ("" if t not in ("b",) else False) for k, _b, t, _s, _g in self.kolonlar}
        for k, _b, t, s, _g in self.kolonlar:
            if t == "c":
                varsayilan[k] = s[0]
            elif t in ("f", "i"):
                varsayilan[k] = 0
        d = SatirDialogu(self.winfo_toplevel(), self.kolonlar, varsayilan)
        if d.sonuc is not None:
            self.agac.insert("", "end", values=self._goster(d.sonuc))

    def duzenle(self):
        sec = self.agac.selection()
        if not sec:
            return
        deger = {}
        for (k, _b, t, _s, _g), v in zip(self.kolonlar, self.agac.item(sec[0], "values")):
            deger[k] = (v == "✔") if t == "b" else v
        d = SatirDialogu(self.winfo_toplevel(), self.kolonlar, deger)
        if d.sonuc is not None:
            self.agac.item(sec[0], values=self._goster(d.sonuc))

    def sil(self):
        for iid in self.agac.selection():
            self.agac.delete(iid)

    def kopyala(self):
        for iid in self.agac.selection():
            self.agac.insert("", "end", values=self.agac.item(iid, "values"))


# --------------------------------------------------------------------------
# Ana uygulama
# --------------------------------------------------------------------------
class Uygulama(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yangın Koruma Hesap Uygulaması — Binaların Yangından Korunması Hakkında Yönetmelik")
        self.geometry("1280x800")
        self.minsize(1000, 650)
        self.vars: dict[str, tk.Variable] = {}
        self.sonuclar = []
        self.g_son: Girdi | None = None
        self._stil()
        self._ust_cubuk()
        self.defter = ttk.Notebook(self)
        self.defter.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self._genel_sekmeler()
        self._kacis_sekmesi()
        self._merdiven_sekmesi()
        self._sonuc_sekmesi()
        self.defter.insert(1, self.f_kacis)       # Genel → Kullanıcı yükü → Merdiven → Su ... sırası
        self.defter.insert(2, self.f_merdiven)
        self.yukle_girdi(Girdi(tarih=dt.date.today().strftime("%d.%m.%Y")))
        self.durum = ttk.Label(self, text="Hazır. Sekmeleri doldurup 'Hesapla' düğmesine basın.", anchor="w", relief="sunken")
        self.durum.pack(fill="x", side="bottom")

    # ---- görünüm
    def _stil(self):
        s = ttk.Style(self)
        for tema in ("vista", "clam"):
            if tema in s.theme_names():
                s.theme_use(tema)
                break
        s.configure("Treeview", rowheight=24)
        s.configure("Hesapla.TButton", font=("", 10, "bold"))

    def _ust_cubuk(self):
        cubuk = ttk.Frame(self)
        cubuk.pack(fill="x", padx=6, pady=6)
        ttk.Button(cubuk, text="▶ Hesapla", style="Hesapla.TButton", command=self.hesapla).pack(side="left", padx=2)
        ttk.Button(cubuk, text="Excel raporu", command=lambda: self.rapor_kaydet("xlsx")).pack(side="left", padx=2)
        ttk.Button(cubuk, text="Word raporu", command=lambda: self.rapor_kaydet("docx")).pack(side="left", padx=2)
        ttk.Separator(cubuk, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(cubuk, text="Projeyi aç", command=self.proje_ac).pack(side="left", padx=2)
        ttk.Button(cubuk, text="Projeyi kaydet", command=self.proje_kaydet).pack(side="left", padx=2)
        ttk.Separator(cubuk, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(cubuk, text="Boş işveren formu", command=self.bos_form_kaydet).pack(side="left", padx=2)
        ttk.Button(cubuk, text="Formu içe aktar", command=self.form_ice_aktar).pack(side="left", padx=2)
        ttk.Separator(cubuk, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(cubuk, text="Örnek fabrika", command=lambda: self.yukle_girdi(ornek_fabrika())).pack(side="left", padx=2)
        ttk.Button(cubuk, text="Sıfırla", command=lambda: self.yukle_girdi(Girdi(tarih=dt.date.today().strftime("%d.%m.%Y")))).pack(side="left", padx=2)

    # ---- sekmeler
    def _alan_olustur(self, ana, satir, ad, etiket, tur, secenek):
        ttk.Label(ana, text=etiket).grid(row=satir, column=0, sticky="w", padx=6, pady=2)
        if tur == "b":
            v = tk.BooleanVar()
            ttk.Checkbutton(ana, variable=v).grid(row=satir, column=1, sticky="w", padx=6)
        elif tur == "c":
            v = tk.StringVar()
            cb = ttk.Combobox(ana, textvariable=v, values=list(secenek.values()), state="readonly", width=34)
            cb.grid(row=satir, column=1, sticky="w", padx=6)
        elif tur == "tesis":
            v = tk.StringVar()
            degerler = [f"{k} — {a} → {T.TEHLIKE_SINIFLARI[sn]}" for k, a, sn in T.EK1_TESISLER]
            cb = ttk.Combobox(ana, textvariable=v, values=degerler, state="readonly", width=34)
            cb.grid(row=satir, column=1, sticky="w", padx=6)
            cb.bind("<<ComboboxSelected>>", lambda e, d=degerler: self._tesis_secildi(d.index(v.get())))
        else:
            v = tk.StringVar()
            ttk.Entry(ana, textvariable=v, width=36 if tur == "t" else 14).grid(row=satir, column=1, sticky="w", padx=6)
        if not ad.startswith("@"):
            self.vars[ad] = v

    def _tesis_secildi(self, indeks: int):
        kod = T.EK1_TESISLER[indeks][2]
        self.vars["tehlike"].set(T.TEHLIKE_SINIFLARI[kod])

    def _genel_sekmeler(self):
        for baslik, bolumler in SEKMELER:
            kf = KaydirmaCercevesi(self.defter)
            self.defter.add(kf, text=baslik)
            for n, (bolum, alanlar) in enumerate(bolumler):
                lf = ttk.LabelFrame(kf.icerik, text=bolum)
                lf.grid(row=n // 2, column=n % 2, sticky="nsew", padx=8, pady=6)
                for r, (ad, etiket, tur, secenek) in enumerate(alanlar):
                    self._alan_olustur(lf, r, ad, etiket, tur, secenek)

    def _kacis_sekmesi(self):
        f = ttk.Frame(self.defter)
        self.defter.add(f, text="Kullanıcı yükü ve kaçış")
        self.f_kacis = f
        ttk.Label(f, wraplength=1200, justify="left", foreground="#1F3864",
                  text="Önce 'Mahaller' tablosuna her katın mahallerini (alan, Ek-5/A türü) girin; ardından 'Kat kaçış verileri' tablosunda aynı kat adlarıyla çıkış bilgilerini girin. "
                       "Aynı anda kullanılmayan mahaller (tuvalet, soyunma, depo) için 'Sayılır' işaretini kaldırın (Madde 31(6)). Ek-5/A'da ilk satırlar net, diğerleri brüt alan esaslıdır."
                  ).pack(anchor="w", padx=6, pady=4)
        self.t_mahal = TabloDuzenleyici(f, TABLOLAR["mahal"], "Mahaller (kullanıcı yükü)")
        self.t_mahal.pack(fill="both", expand=True, padx=6)
        self.t_kat = TabloDuzenleyici(f, TABLOLAR["kat"], "Kat kaçış verileri",
                                      "Çıkış türü: kontrol edilecek eleman. Genişlik: o türdeki çıkışların toplam temiz genişliği. Mesafeler en uzak noktadan en yakın çıkışadır (Madde 32).")
        self.t_kat.pack(fill="both", expand=True, padx=6)

    def _merdiven_sekmesi(self):
        f = ttk.Frame(self.defter)
        self.defter.add(f, text="Merdiven, kapı, duman, tank")
        self.f_merdiven = f
        self.t_merdiven = TabloDuzenleyici(f, TABLOLAR["merdiven"], "Kaçış merdivenleri (Madde 38–46)")
        self.t_merdiven.pack(fill="both", expand=True, padx=6)
        self.t_kapi = TabloDuzenleyici(f, TABLOLAR["kapi"], "Kaçış yolu kapıları (Madde 47)")
        self.t_kapi.pack(fill="both", expand=True, padx=6)
        self.t_duman = TabloDuzenleyici(f, TABLOLAR["duman"], "Mekanik duman tahliyesi mahalleri (Madde 88(3))",
                                        "Kazan dairesi, kapalı otopark, bodrum depo: alan 2000 m²'yi aşarsa mekanik duman tahliyesi, ≥10 hava değişimi/saat.")
        self.t_duman.pack(fill="both", expand=True, padx=6)
        self.t_tank = TabloDuzenleyici(f, TABLOLAR["tank"], "Yanıcı/parlayıcı sıvı tankları ve kapları (Madde 113–122)",
                                       "Tür: yerustu = açıkta yerüstü tank, yeralti = yeraltı tankı, depo_icinde = depo binası içinde.")
        self.t_tank.pack(fill="both", expand=True, padx=6)

    def _sonuc_sekmesi(self):
        f = ttk.Frame(self.defter)
        self.defter.add(f, text="Sonuçlar")
        self.sonuc_sekmesi = f
        self.ozet_etiket = ttk.Label(f, text="Henüz hesaplanmadı.", font=("", 11, "bold"))
        self.ozet_etiket.pack(anchor="w", padx=8, pady=6)
        sf = ttk.Frame(f)
        sf.pack(fill="x", padx=8)
        ttk.Label(sf, text="Durum filtresi:").pack(side="left")
        self.filtre = tk.StringVar(value="Bilgi hariç hepsi")
        cb = ttk.Combobox(sf, textvariable=self.filtre, state="readonly", width=24,
                          values=["Bilgi hariç hepsi", "Hepsi", UYGUN_DEGIL, GEREKLI, KOSULLU, KONTROL, UYGUN, GEREKMEZ, BILGI])
        cb.pack(side="left", padx=6)
        cb.bind("<<ComboboxSelected>>", lambda e: self._sonuc_goster())
        cerceve = ttk.Frame(f)
        cerceve.pack(fill="both", expand=True, padx=8, pady=6)
        kol = [("bolum", "Bölüm", 230), ("kalem", "Kalem", 330), ("deger", "Değer", 130), ("durum", "Durum", 135), ("madde", "Madde / Ek", 150), ("aciklama", "Açıklama", 700)]
        self.sonuc_agaci = ttk.Treeview(cerceve, columns=[k[0] for k in kol], show="headings")
        for ad, b, w in kol:
            self.sonuc_agaci.heading(ad, text=b)
            self.sonuc_agaci.column(ad, width=w, anchor="w", stretch=False)
        for durum, renk in DURUM_RENK.items():
            self.sonuc_agaci.tag_configure(durum, background=renk)
        dikey = ttk.Scrollbar(cerceve, orient="vertical", command=self.sonuc_agaci.yview)
        yatay = ttk.Scrollbar(cerceve, orient="horizontal", command=self.sonuc_agaci.xview)
        self.sonuc_agaci.configure(yscrollcommand=dikey.set, xscrollcommand=yatay.set)
        self.sonuc_agaci.grid(row=0, column=0, sticky="nsew")
        dikey.grid(row=0, column=1, sticky="ns")
        yatay.grid(row=1, column=0, sticky="ew")
        cerceve.rowconfigure(0, weight=1)
        cerceve.columnconfigure(0, weight=1)
        self.sonuc_agaci.bind("<Double-1>", self._satir_detay)

    # ---- veri aktarımı
    def yukle_girdi(self, g: Girdi):
        for ad, v in self.vars.items():
            deger = getattr(g, ad)
            tur = ALAN_TURU[ad]
            if tur == "b":
                v.set(bool(deger))
            elif tur == "c":
                secenek = self._secenek(ad)
                v.set(secenek.get(deger, next(iter(secenek.values()))))
            elif tur in ("f", "i"):
                v.set(f"{deger:g}" if isinstance(deger, (int, float)) else str(deger))
            else:
                v.set(str(deger))
        self.t_mahal.doldur(self._mahal_satirlari(g))
        self.t_kat.doldur([{"kat": k.ad, "cikis": k.cikis_sayisi, "tur": CIKIS_TURLERI[k.cikis_turu], "genislik": k.mevcut_genislik_cm,
                            "tekil": k.tekil_cikis_genislik_cm, "yon": YONLER[k.yon], "mesafe": k.en_uzak_mesafe_m, "kus": k.kus_ucusu_mesafe_m,
                            "cikmaz": k.cikmaz_mesafe_m, "diyagonal": k.mekan_diyagonal_m, "arasi": k.cikislar_arasi_mesafe_m} for k in g.katlar])
        self.t_merdiven.doldur([{"ad": m.ad, "gen": m.genislik_cm, "riht": m.rihts_mm, "basis": m.basamak_genislik_mm, "sbasamak": m.sahanlik_arasi_basamak,
                                 "skot": m.sahanlik_arasi_kot_cm, "bas": m.bas_yuksekligi_cm, "kat": m.hizmet_verilen_kat, "kapi": m.kapi_dayanim_dk,
                                 "duvar": m.duvar_dayanim_dk, "kullanici": m.kullanici_sayisi_kat, "dengeli": m.dengelenmis} for m in g.merdivenler])
        self.t_kapi.doldur([{"ad": k.ad, "gen": k.temiz_genislik_cm, "yuk": k.yukseklik_cm, "kanat": k.kanat_sayisi, "kisi": k.kisi_yuku,
                             "yone": k.kacis_yonune_aciliyor, "esik": k.esik_var, "kuvvet": k.acma_kuvveti_N} for k in g.kapilar])
        self.t_duman.doldur([{"ad": m.ad, "tur": m.tur, "alan": m.alan_m2, "yuk": m.yukseklik_m} for m in g.duman_mahalleri])
        self.t_tank.doldur([{"ad": t.ad, "sinif": t.sinif, "hacim": t.hacim_L, "tur": t.tur} for t in g.sivi_tanklar])

    @staticmethod
    def _secenek(ad: str) -> dict:
        for _, bolumler in SEKMELER:
            for _, alanlar in bolumler:
                for a, _e, tur, s in alanlar:
                    if a == ad and tur == "c":
                        return s
        raise KeyError(ad)

    @staticmethod
    def _mahal_satirlari(g: Girdi) -> list[dict]:
        out = []
        for k in g.katlar:
            for m in k.mahaller:
                tur = next((a for a, kat, _ in T.EK5A if abs(kat - m.katsayi) < 1e-9 and "Diğer" not in a), "Diğer / özel katsayı (elle gir)")
                out.append({"kat": k.ad, "mahal": m.ad, "tur": tur, "alan": m.alan, "ozel": m.katsayi if tur.startswith("Diğer") else 0,
                            "belirli": m.kisi_belirli or 0, "sayilir": m.sayilir})
        return out

    def topla_girdi(self) -> Girdi:
        veri = {}
        for ad, v in self.vars.items():
            tur = ALAN_TURU[ad]
            if tur == "b":
                veri[ad] = bool(v.get())
            elif tur == "c":
                ters = {b: a for a, b in self._secenek(ad).items()}
                veri[ad] = ters[v.get()]
            elif tur == "f":
                veri[ad] = _f(v.get())
            elif tur == "i":
                veri[ad] = _i(v.get())
            else:
                veri[ad] = v.get()
        g = Girdi(**veri)
        return tablolari_uygula(g, self.t_mahal.satirlar(), self.t_kat.satirlar(), self.t_merdiven.satirlar(),
                                self.t_kapi.satirlar(), self.t_duman.satirlar(), self.t_tank.satirlar())

    # ---- işlemler
    def hesapla(self):
        try:
            g = self.topla_girdi()
            self.sonuclar = H.hesapla(g)
            self.g_son = g
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Hesaplama hatası", f"{type(e).__name__}: {e}")
            return
        oz = H.ozet(self.sonuclar)
        parcalar = [f"{ad}: {oz.get(k, 0)}" for ad, k in (("Uygun", UYGUN), ("Uygun değil", UYGUN_DEGIL), ("Gerekli önlem", GEREKLI),
                                                           ("Koşullu", KOSULLU), ("Veri girilmedi", KONTROL), ("Gerekmez", GEREKMEZ))]
        self.ozet_etiket.config(text="   |   ".join(parcalar), foreground="#C00000" if oz.get(UYGUN_DEGIL) else "#006100")
        self._sonuc_goster()
        self.defter.select(self.sonuc_sekmesi)
        self.durum.config(text=f"{len(self.sonuclar)} satır hesaplandı.")

    def _sonuc_goster(self):
        self.sonuc_agaci.delete(*self.sonuc_agaci.get_children())
        f = self.filtre.get()
        for r in self.sonuclar:
            if f == "Bilgi hariç hepsi" and r.durum == BILGI:
                continue
            if f not in ("Bilgi hariç hepsi", "Hepsi") and r.durum != f:
                continue
            self.sonuc_agaci.insert("", "end", tags=(r.durum,), values=(
                r.bolum, r.kalem, (rapor._fmt(r.deger) + (f" {r.birim}" if r.birim else "")).strip(), r.durum, r.madde, r.aciklama))

    def _satir_detay(self, _e):
        sec = self.sonuc_agaci.selection()
        if sec:
            v = self.sonuc_agaci.item(sec[0], "values")
            messagebox.showinfo(v[1], f"{v[0]}\n\nDeğer: {v[2]}\nDurum: {v[3]}\nDayanak: {v[4]}\n\n{v[5]}")

    def _dosya_adi(self, uzanti):
        ad = (self.vars["proje_adi"].get() or "proje").strip().replace(" ", "_")
        return f"{ad}_yangin_hesabi.{uzanti}"

    def rapor_kaydet(self, tur: str):
        self.hesapla()
        if not self.sonuclar:
            return
        yol = filedialog.asksaveasfilename(defaultextension="." + tur, initialfile=self._dosya_adi(tur),
                                           filetypes=[("Excel" if tur == "xlsx" else "Word", "*." + tur)])
        if not yol:
            return
        try:
            veri = rapor.excel_olustur(self.g_son, self.sonuclar) if tur == "xlsx" else rapor.word_olustur(self.g_son, self.sonuclar)
            with open(yol, "wb") as f:
                f.write(veri)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Rapor oluşturulamadı", str(e))
            return
        self.durum.config(text=f"Kaydedildi: {yol}")
        if messagebox.askyesno("Rapor hazır", f"{os.path.basename(yol)} kaydedildi.\nŞimdi açılsın mı?"):
            try:
                if sys.platform.startswith("win"):
                    os.startfile(yol)  # type: ignore[attr-defined]
                elif sys.platform == "darwin":
                    os.system(f'open "{yol}"')
                else:
                    os.system(f'xdg-open "{yol}" >/dev/null 2>&1 &')
            except Exception:  # noqa: BLE001
                pass

    def bos_form_kaydet(self):
        yol = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile="Isveren_Veri_Toplama_Formu.xlsx", filetypes=[("Excel", "*.xlsx")])
        if yol:
            with open(yol, "wb") as f:
                f.write(FORM.sablon_olustur())
            self.durum.config(text=f"İşveren formu kaydedildi: {yol}")
            messagebox.showinfo("İşveren formu", "Boş form kaydedildi. İşverene gönderin; doldurulmuş hali 'Doldurulmuş formu aktar' ile programa alınır.")

    def form_ice_aktar(self):
        yol = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if not yol:
            return
        try:
            with open(yol, "rb") as f:
                g, uyari, eksik = FORM.formdan_oku(f.read())
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Form okunamadı", f"{type(e).__name__}: {e}")
            return
        self.yukle_girdi(g)
        ozet = f"Form aktarıldı: {os.path.basename(yol)}\n"
        if eksik:
            ozet += f"\nİşverenden istenmesi gereken EKSİK bilgiler ({len(eksik)}):\n- " + "\n- ".join(eksik[:25])
            if len(eksik) > 25:
                ozet += f"\n... ve {len(eksik) - 25} madde daha"
        if uyari:
            ozet += f"\n\nUyarılar ({len(uyari)}):\n- " + "\n- ".join(uyari[:15])
        if not eksik and not uyari:
            ozet += "\nEksik veya hatalı alan yok."
        self.durum.config(text=f"Form aktarıldı; {len(eksik)} eksik, {len(uyari)} uyarı.")
        messagebox.showinfo("Form aktarıldı", ozet + "\n\nBilgileri sekmelerde kontrol edip 'Hesapla'ya basın.")

    def proje_kaydet(self):
        yol = filedialog.asksaveasfilename(defaultextension=".json", initialfile=(self.vars["proje_adi"].get() or "proje") + ".json",
                                           filetypes=[("Proje dosyası", "*.json")])
        if yol:
            with open(yol, "w", encoding="utf-8") as f:
                f.write(self.topla_girdi().to_json())
            self.durum.config(text=f"Proje kaydedildi: {yol}")

    def proje_ac(self):
        yol = filedialog.askopenfilename(filetypes=[("Proje dosyası", "*.json")])
        if yol:
            try:
                with open(yol, encoding="utf-8") as f:
                    self.yukle_girdi(Girdi.from_json(f.read()))
                self.durum.config(text=f"Proje açıldı: {yol}")
            except Exception as e:  # noqa: BLE001
                messagebox.showerror("Dosya açılamadı", str(e))


def kendini_sina() -> int:
    """Arayüzü açmadan hesap ve rapor üretimini dener (derleme sonrası doğrulama için)."""
    import tempfile
    g = ornek_fabrika()
    s = H.hesapla(g)
    with tempfile.TemporaryDirectory() as d:
        for ad, veri in (("r.xlsx", rapor.excel_olustur(g, s)), ("r.docx", rapor.word_olustur(g, s))):
            with open(os.path.join(d, ad), "wb") as f:
                f.write(veri)
            assert os.path.getsize(os.path.join(d, ad)) > 5000, ad
    g2, uyari, _eksik = FORM.formdan_oku(FORM.doldurulmus_form(g))
    assert not uyari and len(H.hesapla(g2)) == len(s), "form gidiş-dönüş"
    assert len(FORM.sablon_olustur()) > 10000
    app = Uygulama()
    app.yukle_girdi(g)
    app.hesapla()
    assert len(app.sonuclar) == len(s)
    app.destroy()
    print(f"KENDINI SINAMA TAMAM: {len(s)} satir, {H.ozet(s)}")
    return 0


def main():
    if "--selftest" in sys.argv:
        sys.exit(kendini_sina())
    Uygulama().mainloop()


if __name__ == "__main__":
    main()
