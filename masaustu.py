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

from yangin import dokum as DOKUM
from yangin import form as FORM
from yangin import hesaplar as H
from yangin import mevzuat as MEV
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
SARI = "#FFF7A8"          # ipucu penceresi zemin rengi (sarı)
SARI_KENAR = "#B59B00"


class Ipucu:
    """Bir bileşenin üzerine gelince açılan sarı bilgi penceresi (yönetmelik açıklamaları).

    Bölümler: [(stil, metin)]; stil = baslik | govde | not | etiket | mevzuat
    """

    GECIKME_MS = 350
    GENISLIK = 600

    def __init__(self):
        self.pencere = None
        self.zamanlayici = None
        self.pencere_sahibi = None
        self._anahtar = None

    def bagla(self, bilesen, bolum_fn):
        """bolum_fn() -> bölüm listesi (üzerine gelindiğinde hesaplanır)."""
        bilesen.bind("<Enter>", lambda e: self._planla(bilesen, bolum_fn, e.x_root, e.y_root), add="+")
        bilesen.bind("<Leave>", lambda e: self.gizle(), add="+")
        bilesen.bind("<ButtonPress>", lambda e: self.gizle(), add="+")

    def bagla_agac(self, agac, bolum_fn):
        """Treeview için: bolum_fn(x, y) -> (anahtar, bölüm listesi) | None; hücre/sütun değişince yenilenir."""
        def hareket(e):
            sonuc = bolum_fn(e.x, e.y)
            anahtar = sonuc[0] if sonuc else None
            if anahtar == self._anahtar:
                return
            self.gizle()
            self._anahtar = anahtar
            if sonuc:
                self._planla(agac, lambda: sonuc[1], e.x_root, e.y_root, anahtar_koru=True)
        agac.bind("<Motion>", hareket, add="+")
        agac.bind("<Leave>", lambda e: self.gizle(), add="+")
        agac.bind("<ButtonPress>", lambda e: self.gizle(), add="+")

    def _planla(self, bilesen, bolum_fn, x, y, anahtar_koru=False):
        self.gizle(anahtar_koru)
        self.pencere_sahibi = bilesen
        self.zamanlayici = bilesen.after(self.GECIKME_MS, lambda: self._goster(bilesen, bolum_fn, x, y))

    def gizle(self, anahtar_koru=False):
        if not anahtar_koru:
            self._anahtar = None
        if self.zamanlayici is not None:
            try:
                self.pencere_sahibi.after_cancel(self.zamanlayici)
            except Exception:  # noqa: BLE001
                pass
            self.zamanlayici = None
        if self.pencere is not None:
            try:
                self.pencere.destroy()
            except Exception:  # noqa: BLE001
                pass
            self.pencere = None

    def _goster(self, bilesen, bolum_fn, x, y):
        self.zamanlayici = None
        try:
            bolumler = bolum_fn()
        except Exception:  # noqa: BLE001
            return
        if not bolumler:
            return
        self.pencere_sahibi = bilesen
        tw = tk.Toplevel(bilesen)
        tw.wm_overrideredirect(True)
        try:
            tw.attributes("-topmost", True)
        except tk.TclError:
            pass
        cerceve = tk.Frame(tw, background=SARI, highlightbackground=SARI_KENAR, highlightthickness=1, padx=9, pady=7)
        cerceve.pack()
        for stil, metin in bolumler:
            ayar = dict(bg=SARI, fg="#222222", justify="left", anchor="w", wraplength=self.GENISLIK, font=("", 9))
            if stil == "baslik":
                ayar.update(font=("", 10, "bold"), fg="#000000")
            elif stil == "not":
                ayar.update(fg="#5A4A00", font=("", 8))
            elif stil == "etiket":
                ayar.update(fg="#7A5C00", font=("", 8, "bold"))
            elif stil == "mevzuat":
                ayar.update(fg="#1F3864", font=("", 9, "italic"))
            tk.Label(cerceve, text=metin, **ayar).pack(fill="x", anchor="w", pady=(0, 3))
        tw.update_idletasks()
        w, h = tw.winfo_reqwidth(), tw.winfo_reqheight()
        sw, sh = tw.winfo_screenwidth(), tw.winfo_screenheight()
        px = min(x + 16, max(0, sw - w - 8))
        py = y + 22 if y + 22 + h < sh - 8 else max(8, y - h - 12)
        tw.wm_geometry(f"+{px}+{py}")
        self.pencere = tw


IPUCU = Ipucu()


def _norm(metin: str) -> str:
    """Türkçe harf/büyük-küçük farkını yok sayan arama biçimi (ör. 'İPEK' ~ 'ipek' ~ 'IPEK')."""
    t = metin.replace("İ", "i").replace("I", "ı").lower()
    return t.translate(str.maketrans("ıçğöşü", "icgosu"))


class FiltreliSecim(ttk.Frame):
    """Yazdıkça süzülen açılır liste: girilen her sözcüğü içeren seçenekler gösterilir.

    Liste penceresi geniştir (uzun seçenekler okunabilir); seçilen metnin tamamı altında ayrıca yazılır.
    Klavye: ↑/↓ gezinir, Enter seçer, Esc kapatır.
    """

    def __init__(self, ana, degerler, degisken: tk.StringVar, genislik=34, komut=None):
        super().__init__(ana)
        self.degerler = list(degerler)
        self.degisken = degisken
        self.komut = komut
        self.pencere = None
        self.liste = None
        self.uygun: list[str] = []
        self._son_gecerli = degisken.get() if degisken.get() in self.degerler else ""
        self.giris = ttk.Entry(self, textvariable=degisken, width=genislik)
        self.giris.grid(row=0, column=0, sticky="ew")
        self.dugme = ttk.Button(self, text="▼", width=3, command=self._tumunu_ac)
        self.dugme.grid(row=0, column=1, padx=(2, 0))
        self.tam_metin = ttk.Label(self, text="", wraplength=520, justify="left", foreground="#1F3864")
        self.tam_metin.grid(row=1, column=0, columnspan=2, sticky="w")
        self.columnconfigure(0, weight=1)
        self.giris.bind("<KeyRelease>", self._yazildi)
        self.giris.bind("<Down>", lambda e: self._gezin(1))
        self.giris.bind("<Up>", lambda e: self._gezin(-1))
        self.giris.bind("<Return>", self._enter)
        self.giris.bind("<Escape>", lambda e: self._kapat())
        self.giris.bind("<FocusOut>", lambda e: self.after(180, self._odak_kontrol))
        self.giris.bind("<Button-1>", lambda e: self.after(10, self._tikla_ac))
        self.degisken.trace_add("write", lambda *_: self._etiketi_yenile())
        self._etiketi_yenile()

    # -- yardımcılar
    def _etiketi_yenile(self):
        v = self.degisken.get()
        self.tam_metin.config(text=("Seçilen: " + v) if v in self.degerler else "")
        if v in self.degerler:
            self._son_gecerli = v

    def sec(self, deger: str):
        self.degisken.set(deger)
        self._son_gecerli = deger
        self._kapat()

    def _filtrele(self, metin: str) -> list[str]:
        sozcukler = [w for w in _norm(metin).split() if w]
        if not sozcukler:
            return list(self.degerler)
        return [d for d in self.degerler if all(w in _norm(d) for w in sozcukler)]

    def _yazildi(self, e):
        if e.keysym in ("Down", "Up", "Return", "Escape", "Tab", "Shift_L", "Shift_R", "Left", "Right"):
            return
        self._ac(self._filtrele(self.degisken.get()))

    def _tumunu_ac(self):
        self._ac(list(self.degerler))
        self.giris.focus_set()

    def _tikla_ac(self):
        if self.pencere is None and self.degisken.get() in ("", None):
            self._ac(list(self.degerler))

    # -- açılır pencere
    def _ac(self, uygun: list[str]):
        self.uygun = uygun
        if self.pencere is None:
            tw = tk.Toplevel(self)
            tw.wm_overrideredirect(True)
            try:
                tw.attributes("-topmost", True)
            except tk.TclError:
                pass
            cerceve = tk.Frame(tw, background="#808080", padx=1, pady=1)
            cerceve.pack()
            self.liste = tk.Listbox(cerceve, activestyle="none", exportselection=False, font=("", 9))
            kay = ttk.Scrollbar(cerceve, orient="vertical", command=self.liste.yview)
            yat = ttk.Scrollbar(cerceve, orient="horizontal", command=self.liste.xview)
            self.liste.configure(yscrollcommand=kay.set, xscrollcommand=yat.set)
            self.liste.grid(row=0, column=0)
            kay.grid(row=0, column=1, sticky="ns")
            yat.grid(row=1, column=0, sticky="ew")
            self.liste.bind("<ButtonRelease-1>", self._liste_tikla)
            self.liste.bind("<Return>", self._enter)
            self.liste.bind("<Escape>", lambda e: self._kapat())
            self.pencere = tw
        self.liste.delete(0, "end")
        if uygun:
            for d in uygun:
                self.liste.insert("end", d)
            en_uzun = max(len(d) for d in uygun)
            self.liste.configure(width=min(max(en_uzun, 40), 150), height=min(len(uygun), 14))
            self.liste.selection_set(0)
            self.liste.activate(0)
        else:
            self.liste.insert("end", "(eşleşen seçenek yok — farklı sözcük deneyin)")
            self.liste.configure(width=46, height=1)
        self.pencere.update_idletasks()
        w, h = self.pencere.winfo_reqwidth(), self.pencere.winfo_reqheight()
        x = self.giris.winfo_rootx()
        y = self.giris.winfo_rooty() + self.giris.winfo_height() + 2
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = max(0, min(x, sw - w - 6))
        if y + h > sh - 40:
            y = max(0, self.giris.winfo_rooty() - h - 2)
        self.pencere.wm_geometry(f"+{x}+{y}")

    def _kapat(self):
        if self.pencere is not None:
            try:
                self.pencere.destroy()
            except Exception:  # noqa: BLE001
                pass
            self.pencere = None
            self.liste = None

    def _gezin(self, yon: int):
        if self.pencere is None:
            self._ac(self._filtrele(self.degisken.get()))
            return "break"
        if not self.uygun:
            return "break"
        sec = self.liste.curselection()
        i = (sec[0] if sec else -1) + yon
        i = max(0, min(len(self.uygun) - 1, i))
        self.liste.selection_clear(0, "end")
        self.liste.selection_set(i)
        self.liste.activate(i)
        self.liste.see(i)
        return "break"

    def _enter(self, _e=None):
        if self.pencere is not None and self.uygun and self.liste is not None:
            sec = self.liste.curselection()
            self._sec_indeks(sec[0] if sec else 0)
        return "break"

    def _liste_tikla(self, e):
        i = self.liste.nearest(e.y)
        if 0 <= i < len(self.uygun):
            self._sec_indeks(i)

    def _sec_indeks(self, i: int):
        deger = self.uygun[i]
        self.sec(deger)
        if self.komut:
            self.komut(self.degerler.index(deger))

    def _odak_kontrol(self):
        # liste penceresine tıklanırken odak kaybı sayılmaz
        try:
            odak = self.focus_get()
        except Exception:  # noqa: BLE001
            odak = None
        if odak is not None and (odak is self.liste or odak is self.giris):
            return
        self._kapat()
        if self.degisken.get() not in self.degerler:          # yarım yazılmış metin: son geçerli seçime dön
            self.degisken.set(self._son_gecerli)


class UyariPenceresi(tk.Toplevel):
    """Eksik bilgi uyarısı: 'Geri dön' / 'Yine de devam et'. devam: True/False."""

    def __init__(self, ana, baslik: str, ust_metin: str, maddeler: list[str], devam_metni="Yine de devam et"):
        super().__init__(ana)
        self.title(baslik)
        self.transient(ana)
        self.grab_set()
        self.devam = False
        self.resizable(False, False)
        ttk.Label(self, text="⚠ " + ust_metin, font=("", 10, "bold"), wraplength=560, justify="left").pack(anchor="w", padx=12, pady=(12, 4))
        cerceve = ttk.Frame(self)
        cerceve.pack(fill="both", expand=True, padx=12)
        kutu = tk.Listbox(cerceve, width=84, height=min(max(len(maddeler), 3), 14), activestyle="none", bg="#FFF7A8", relief="flat", font=("", 9))
        kay = ttk.Scrollbar(cerceve, orient="vertical", command=kutu.yview)
        kutu.configure(yscrollcommand=kay.set)
        for m in maddeler:
            kutu.insert("end", "•  " + m)
        kutu.pack(side="left", fill="both", expand=True)
        kay.pack(side="right", fill="y")
        alt = ttk.Frame(self)
        alt.pack(pady=12)
        geri = ttk.Button(alt, text="Geri dön ve doldur", command=self.destroy)
        geri.pack(side="left", padx=6)
        ttk.Button(alt, text=devam_metni, command=self._devam).pack(side="left", padx=6)
        geri.focus_set()
        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        x = ana.winfo_rootx() + max(0, (ana.winfo_width() - self.winfo_reqwidth()) // 2)
        y = ana.winfo_rooty() + max(0, (ana.winfo_height() - self.winfo_reqheight()) // 3)
        self.geometry(f"+{x}+{y}")
        self.wait_window()

    def _devam(self):
        self.devam = True
        self.destroy()


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

    def __init__(self, ana, kolonlar, degerler: dict, tablo: str | None = None):
        super().__init__(ana)
        self.title("Satır")
        self.transient(ana)
        self.grab_set()
        self.sonuc = None
        self.vars = {}
        for r, (anahtar, baslik, tur, secenek, _g) in enumerate(kolonlar):
            etiket = ttk.Label(self, text=baslik)
            etiket.grid(row=r, column=0, sticky="w", padx=8, pady=3)
            v = tk.StringVar(value=str(degerler.get(anahtar, "")))
            if tur == "b":
                v = tk.BooleanVar(value=_bool(degerler.get(anahtar, False)))
                giris = ttk.Checkbutton(self, variable=v)
                giris.grid(row=r, column=1, sticky="w", padx=8)
            elif tur == "c" and len(secenek) > 8:
                giris = FiltreliSecim(self, secenek, v, genislik=46)
                giris.grid(row=r, column=1, padx=8, pady=3, sticky="w")
            elif tur == "c":
                giris = ttk.Combobox(self, textvariable=v, values=secenek, state="readonly", width=44)
                giris.grid(row=r, column=1, padx=8, pady=3)
            else:
                giris = ttk.Entry(self, textvariable=v, width=46)
                giris.grid(row=r, column=1, padx=8, pady=3)
            if tablo:
                for b in (etiket, giris, getattr(giris, "giris", giris)):
                    IPUCU.bagla(b, lambda k=anahtar: MEV.tablo_ipucu_bolumleri(tablo, k))
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
    # yeni satırda varsayılan değerler: (tablo, sütun) -> değer
    VARSAYILAN = {("kapi", "kanat"): 1, ("kapi", "yone"): True, ("mahal", "sayilir"): True, ("kat", "cikis"): 2, ("merdiven", "kat"): 1,
                  ("duman", "yuk"): 3, ("merdiven", "sbasamak"): 0}

    def __init__(self, ana, kolonlar, baslik, aciklama="", anahtar=None, degisti=None):
        super().__init__(ana)
        self.kolonlar = kolonlar
        self.tablo_anahtar = anahtar
        self.degisti = degisti
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
        if anahtar:
            IPUCU.bagla_agac(self.agac, self._sutun_ipucu)

    def _sutun_ipucu(self, x, y):
        """Fare altındaki sütun için (anahtar, ipucu bölümleri)."""
        if self.agac.identify_region(x, y) not in ("heading", "cell"):
            return None
        sutun = self.agac.identify_column(x)           # '#1', '#2' ...
        try:
            kolon = self.kolonlar[int(sutun[1:]) - 1][0]
        except (ValueError, IndexError):
            return None
        return (self.tablo_anahtar, kolon), MEV.tablo_ipucu_bolumleri(self.tablo_anahtar, kolon)

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

    def _degisti(self):
        if self.degisti:
            self.degisti()

    def satir_ekle(self, d: dict):
        self.agac.insert("", "end", values=self._goster(d))

    def ekle(self):
        varsayilan = {k: ("" if t not in ("b",) else False) for k, _b, t, _s, _g in self.kolonlar}
        for k, _b, t, s, _g in self.kolonlar:
            if t == "c":
                varsayilan[k] = s[0]
            elif t in ("f", "i"):
                varsayilan[k] = 0
            if (self.tablo_anahtar, k) in self.VARSAYILAN:
                varsayilan[k] = self.VARSAYILAN[(self.tablo_anahtar, k)]
        d = SatirDialogu(self.winfo_toplevel(), self.kolonlar, varsayilan, self.tablo_anahtar)
        if d.sonuc is not None:
            self.agac.insert("", "end", values=self._goster(d.sonuc))
            self._degisti()

    def duzenle(self):
        sec = self.agac.selection()
        if not sec:
            return
        deger = {}
        for (k, _b, t, _s, _g), v in zip(self.kolonlar, self.agac.item(sec[0], "values")):
            deger[k] = (v == "✔") if t == "b" else v
        d = SatirDialogu(self.winfo_toplevel(), self.kolonlar, deger, self.tablo_anahtar)
        if d.sonuc is not None:
            self.agac.item(sec[0], values=self._goster(d.sonuc))
            self._degisti()

    def sil(self):
        for iid in self.agac.selection():
            self.agac.delete(iid)
        self._degisti()

    def kopyala(self):
        for iid in self.agac.selection():
            self.agac.insert("", "end", values=self.agac.item(iid, "values"))
        self._degisti()


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
        self.tehlike_belirlendi = False      # kullanıcı tehlike sınıfını seçti / proje yüklendi
        self._sessiz = False                 # programatik sekme geçişlerinde uyarı verme
        self._onceki_sekme = None
        self._gecildi: dict[str, frozenset] = {}
        self._stil()
        self._ust_cubuk()
        self.defter = ttk.Notebook(self)
        self.defter.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self._genel_sekmeler()
        self._kacis_sekmesi()
        self._merdiven_sekmesi()
        self._yuk_sekmesi()
        self._sonuc_sekmesi()
        self._dokum_sekmesi()
        self.defter.insert(1, self.f_kacis)       # Genel → Kullanıcı yükü → Merdiven → Su ... sırası
        self.defter.insert(2, self.f_merdiven)
        self.yukle_girdi(Girdi(tarih=dt.date.today().strftime("%d.%m.%Y")))
        self.tehlike_belirlendi = False
        self._onceki_sekme = self.defter.select()
        self.defter.bind("<<NotebookTabChanged>>", self._sekme_degisti)
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
        ttk.Button(cubuk, text="▶ Hesapla", style="Hesapla.TButton", command=lambda: self.hesapla(sor=True)).pack(side="left", padx=2)
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
        ttk.Button(cubuk, text="Sıfırla", command=self.sifirla).pack(side="left", padx=2)

    def sifirla(self):
        self.yukle_girdi(Girdi(tarih=dt.date.today().strftime("%d.%m.%Y")))
        self.tehlike_belirlendi = False
        self._gecildi.clear()

    # ---- sekmeler
    def _alan_olustur(self, ana, satir, ad, etiket, tur, secenek):
        lbl = ttk.Label(ana, text=etiket)
        lbl.grid(row=satir, column=0, sticky="w", padx=6, pady=2)
        if tur == "b":
            v = tk.BooleanVar()
            giris = ttk.Checkbutton(ana, variable=v)
            giris.grid(row=satir, column=1, sticky="w", padx=6)
        elif tur == "c":
            v = tk.StringVar()
            giris = ttk.Combobox(ana, textvariable=v, values=list(secenek.values()), state="readonly", width=34)
            giris.grid(row=satir, column=1, sticky="w", padx=6)
        elif tur == "tesis":
            v = tk.StringVar()
            degerler = [f"{k} — {a} → {T.TEHLIKE_SINIFLARI[sn]}" for k, a, sn in T.EK1_TESISLER]
            giris = FiltreliSecim(ana, degerler, v, genislik=40, komut=self._tesis_secildi)
            giris.grid(row=satir, column=1, sticky="w", padx=6)
            self.tesis_secim = giris
        else:
            v = tk.StringVar()
            giris = ttk.Entry(ana, textvariable=v, width=36 if tur == "t" else 14)
            giris.grid(row=satir, column=1, sticky="w", padx=6)
        if ad == "tehlike":
            giris.bind("<<ComboboxSelected>>", lambda e: setattr(self, "tehlike_belirlendi", True), add="+")
        for b in (lbl, giris, getattr(giris, "giris", giris)):          # etiketin veya kutunun üzerine gelince sarı mevzuat ipucu
            IPUCU.bagla(b, lambda a=ad: MEV.ipucu_bolumleri(a))
        if not ad.startswith("@"):
            self.vars[ad] = v

    def _tesis_secildi(self, indeks: int):
        kod = T.EK1_TESISLER[indeks][2]
        self.vars["tehlike"].set(T.TEHLIKE_SINIFLARI[kod])
        self.tehlike_belirlendi = True

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
        self.t_mahal = TabloDuzenleyici(f, TABLOLAR["mahal"], anahtar="mahal", degisti=self.kat_senkron, baslik="Mahaller (kullanıcı yükü)")
        self.t_mahal.pack(fill="both", expand=True, padx=6)
        self.t_kat = TabloDuzenleyici(f, TABLOLAR["kat"], anahtar="kat", baslik="Kat kaçış verileri",
                                      aciklama="Çıkış türü: kontrol edilecek eleman. Genişlik: o türdeki çıkışların toplam temiz genişliği. Mesafeler en uzak noktadan en yakın çıkışadır (Madde 32).")
        self.t_kat.pack(fill="both", expand=True, padx=6)

    def _merdiven_sekmesi(self):
        f = ttk.Frame(self.defter)
        self.defter.add(f, text="Merdiven, kapı, duman, tank")
        self.f_merdiven = f
        self.t_merdiven = TabloDuzenleyici(f, TABLOLAR["merdiven"], anahtar="merdiven", baslik="Kaçış merdivenleri (Madde 38–46)")
        self.t_merdiven.pack(fill="both", expand=True, padx=6)
        self.t_kapi = TabloDuzenleyici(f, TABLOLAR["kapi"], anahtar="kapi", baslik="Kaçış yolu kapıları (Madde 47)")
        self.t_kapi.pack(fill="both", expand=True, padx=6)
        self.t_duman = TabloDuzenleyici(f, TABLOLAR["duman"], anahtar="duman", baslik="Mekanik duman tahliyesi mahalleri (Madde 88(3))",
                                        aciklama="Kazan dairesi, kapalı otopark, bodrum depo: alan 2000 m²'yi aşarsa mekanik duman tahliyesi, ≥10 hava değişimi/saat.")
        self.t_duman.pack(fill="both", expand=True, padx=6)
        self.t_tank = TabloDuzenleyici(f, TABLOLAR["tank"], anahtar="tank", baslik="Yanıcı/parlayıcı sıvı tankları ve kapları (Madde 113–122)",
                                       aciklama="Tür: yerustu = açıkta yerüstü tank, yeralti = yeraltı tankı, depo_icinde = depo binası içinde.")
        self.t_tank.pack(fill="both", expand=True, padx=6)

    def _yuk_sekmesi(self):
        f = ttk.Frame(self.defter)
        self.defter.add(f, text="Yangın yükü")
        ttk.Label(f, wraplength=1200, justify="left", foreground="#1F3864",
                  text="Yangın duvarlarıyla ayrılmış her bölümü (kompartıman) 'Bölümler' tablosuna alanıyla girin; her bölümde bulunan yanıcı malzemeleri 'Malzemeler' tablosuna miktarıyla (kg) girin. "
                       "Yangın yükü q = Σ(kütle × alt ısıl değer) ÷ alan [MJ/m²] hesaplanır ve bölüm alanı Ek-4 sınırıyla karşılaştırılır. Isıl değerler yaygın literatür ortalamasıdır; "
                       "MSDS/laboratuvar değeri biliniyorsa kalem satırına yazın. Malzemeler tablosuna yeni bir bölüm adı yazarsanız Bölümler tablosuna otomatik eklenir (alanını girin)."
                  ).pack(anchor="w", padx=6, pady=4)
        self.t_yyb = TabloDuzenleyici(f, TABLOLAR["yyb"], anahtar="yyb", baslik="Bölümler (kompartımanlar)")
        self.t_yyb.pack(fill="both", expand=True, padx=6)
        self.t_yyk = TabloDuzenleyici(f, TABLOLAR["yyk"], anahtar="yyk", degisti=self.yuk_senkron, baslik="Malzemeler")
        self.t_yyk.pack(fill="both", expand=True, padx=6)

    def yuk_senkron(self):
        """Malzemeler tablosunda geçen bölüm adı Bölümler tablosunda yoksa otomatik eklenir."""
        mevcut = {str(r["bolum"]).strip() for r in self.t_yyb.satirlar()}
        eklenen = []
        for r in self.t_yyk.satirlar():
            ad = str(r["bolum"] or "").strip()
            if ad and ad not in mevcut:
                self.t_yyb.satir_ekle({"bolum": ad, "alan": 0, "kat": "", "tur": "Depo" if "depo" in ad.lower() else "Endüstriyel (üretim)"})
                mevcut.add(ad)
                eklenen.append(ad)
        if eklenen:
            self.durum.config(text="Otomatik: " + ", ".join(repr(a) for a in eklenen) + " bölümü 'Bölümler' tablosuna eklendi — alanını girmeyi unutmayın.")

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
        IPUCU.bagla_agac(self.sonuc_agaci, self._sonuc_ipucu)

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
        self.t_yyb.doldur([{"bolum": b.ad, "alan": b.alan_m2, "kat": b.kat, "tur": "Depo" if b.kullanim == "depo" else "Endüstriyel (üretim)"} for b in g.yangin_yuku_bolumleri])
        self.t_yyk.doldur([{"bolum": k.bolum, "malzeme": k.malzeme, "kg": k.kg, "isil": k.isil_MJkg} for k in g.yangin_yuku_kalemleri])
        self.tehlike_belirlendi = True           # yüklenen projede tehlike sınıfı belirlenmiştir
        self._gecildi.clear()
        if hasattr(self, "tesis_secim"):
            self.tesis_secim.degisken.set("")

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
                                self.t_kapi.satirlar(), self.t_duman.satirlar(), self.t_tank.satirlar(),
                                self.t_yyb.satirlar(), self.t_yyk.satirlar())

    # ---- zorunlu alan denetimi, otomatik kat ekleme
    SEKME_ALANLARI = {
        "Genel": [("yapi_yuksekligi", "Yapı yüksekliği (m)"), ("bina_yuksekligi", "Bina yüksekliği (m)"), ("kat_sayisi", "Zemin üstü kat sayısı"),
                  ("taban_alani", "Bina taban alanı (m²)"), ("toplam_kapali_alan", "Toplam kapalı alan (m²)"), ("en_buyuk_kat_alani", "En büyük kat alanı (m²)"),
                  ("bina_boyu", "Bina boyu (m)"), ("bina_eni", "Bina eni (m)"), ("cephe_genisligi", "Cephe genişliği (m)")],
    }

    def zorunlu_eksikler(self, sekme: str, g: Girdi | None = None) -> list[str]:
        """Bir sekmede, hesabın yapılabilmesi/kontrol edilebilmesi için doldurulması gereken ama boş bırakılan alanlar."""
        g = g or self.topla_girdi()
        e: list[str] = []
        if sekme == "Genel":
            tesis_ok = hasattr(self, "tesis_secim") and self.tesis_secim.degisken.get() in self.tesis_secim.degerler
            if not (self.tehlike_belirlendi or tesis_ok):
                e.append("Üretim/tesis türü seçilmedi (tehlike sınıfı buna göre belirlenir; ya da tehlike sınıfını elle seçin)")
            for alan, ad in self.SEKME_ALANLARI["Genel"]:
                if getattr(g, alan) <= 0:
                    e.append(f"{ad} girilmedi")
        elif sekme == "Kullanıcı yükü ve kaçış":
            if not g.katlar or not any(m.alan > 0 for k in g.katlar for m in k.mahaller):
                e.append("Mahaller tablosuna en az bir mahal (alanıyla) girilmedi — kullanıcı yükü hesaplanamaz")
            for k in g.katlar:
                for m in k.mahaller:
                    if m.alan <= 0:
                        e.append(f"'{k.ad}' katı, '{m.ad}' mahalinin alanı girilmedi")
                if not k.mahaller:
                    e.append(f"'{k.ad}' katı için mahal girilmedi")
                if k.cikis_sayisi <= 0:
                    e.append(f"'{k.ad}': çıkış sayısı girilmedi")
                if k.mevcut_genislik_cm <= 0:
                    e.append(f"'{k.ad}': mevcut toplam çıkış genişliği girilmedi")
                if k.en_uzak_mesafe_m <= 0:
                    e.append(f"'{k.ad}': en uzak kaçış mesafesi girilmedi")
        elif sekme == "Merdiven, kapı, duman, tank":
            if (g.kat_sayisi > 1 or g.bodrum_kat_sayisi > 0) and not g.merdivenler:
                e.append("Çok katlı binada en az bir kaçış merdiveni girilmedi")
            for m in g.merdivenler:
                if m.genislik_cm <= 0:
                    e.append(f"Merdiven '{m.ad}': genişlik girilmedi")
        elif sekme == "Su ve söndürme":
            if g.yagmurlama_var and g.spr_yukseklik_h <= 0:
                e.append("Sprinkler var: en alt-en üst başlık arası yükseklik h girilmedi (Ek-8/A)")
            if g.dolap_var and g.es_zamanli_dolap <= 0:
                e.append("Yangın dolabı var: eş zamanlı çalışan dolap sayısı girilmedi")
        elif sekme == "Algılama, duman, aydınlatma":
            if g.kacis_yolu_uzunlugu_m <= 0:
                e.append("En uzun kaçış yolu uzunluğu girilmedi (yönlendirme işareti adedi için)")
        elif sekme == "Kazan ve tehlikeli madde":
            if g.kazan_var:
                if g.kazan_kw <= 0:
                    e.append("Kazan dairesi var: ısıl kapasite (kW) girilmedi")
                if g.kazan_alani_m2 <= 0:
                    e.append("Kazan dairesi var: döşeme alanı girilmedi")
        elif sekme == "Yangın yükü":
            adlar = {b.ad.strip() for b in g.yangin_yuku_bolumleri}
            for b in g.yangin_yuku_bolumleri:
                if b.alan_m2 <= 0:
                    e.append(f"'{b.ad}' bölümünün alanı girilmedi")
            for k in g.yangin_yuku_kalemleri:
                if k.bolum.strip() not in adlar:
                    e.append(f"'{k.malzeme}' kalemi için '{k.bolum}' bölümü tanımlı değil")
                if k.kg <= 0:
                    e.append(f"'{k.bolum}' / '{k.malzeme}': miktar (kg) girilmedi")
        elif sekme == "Çevre ve ekipler":
            if g.itfaiye_son_nokta_mesafe_m <= 0:
                e.append("İtfaiye aracının son yaklaşma noktasından cepheye mesafe girilmedi (Madde 22)")
            if g.ic_yol_genislik_m <= 0:
                e.append("İç ulaşım yolu genişliği girilmedi (Madde 22)")
        return e

    def _sekme_degisti(self, _e=None):
        simdiki = self.defter.select()
        onceki = self._onceki_sekme
        if self._sessiz or onceki is None or onceki == simdiki:
            self._onceki_sekme = simdiki
            return
        try:
            ad = self.defter.tab(onceki, "text")
            eksik = self.zorunlu_eksikler(ad)
        except Exception:  # noqa: BLE001
            self._onceki_sekme = simdiki
            return
        if eksik and self._gecildi.get(ad) != frozenset(eksik):
            devam = UyariPenceresi(self, "Eksik bilgi",
                                   f"'{ad}' sekmesinde hesap için gerekli {len(eksik)} bilgi eksik. Doldurmadan devam edilsin mi?", eksik).devam
            if not devam:
                self._sessiz = True
                try:
                    self.defter.select(onceki)
                finally:
                    self._sessiz = False
                return
            self._gecildi[ad] = frozenset(eksik)
        self._onceki_sekme = simdiki

    def sekme_sec(self, sekme_widget):
        """Uyarı vermeden sekme değiştirir."""
        self._sessiz = True
        try:
            self.defter.select(sekme_widget)
        finally:
            self._sessiz = False
        self._onceki_sekme = self.defter.select()

    def kat_senkron(self):
        """Mahaller tablosuna eklenen kat, 'Kat kaçış verileri' tablosunda yoksa otomatik eklenir (ve kat sayıları güncellenir)."""
        mevcut = {str(r["kat"]).strip() for r in self.t_kat.satirlar()}
        eklenen = []
        for r in self.t_mahal.satirlar():
            ad = str(r["kat"] or "").strip()
            if ad and ad not in mevcut:
                zemin = "zemin" in ad.lower()
                self.t_kat.satir_ekle({"kat": ad, "cikis": 2, "tur": CIKIS_TURLERI["dis_kapi" if zemin else "merdiven"], "genislik": 0, "tekil": 0,
                                       "yon": YONLER["iki"], "mesafe": 0, "kus": 0, "cikmaz": 0, "diyagonal": 0, "arasi": 0})
                mevcut.add(ad)
                eklenen.append(ad)
        adlar = {str(r["kat"]).strip() for r in self.t_kat.satirlar() if str(r["kat"]).strip()}
        bodrum = sum(1 for a in adlar if "bodrum" in a.lower())
        ust = len(adlar) - bodrum
        notlar = []
        try:
            if ust > _i(self.vars["kat_sayisi"].get(), 0):
                self.vars["kat_sayisi"].set(str(ust))
                notlar.append(f"zemin üstü kat sayısı {ust} yapıldı")
            if bodrum > _i(self.vars["bodrum_kat_sayisi"].get(), 0):
                self.vars["bodrum_kat_sayisi"].set(str(bodrum))
                notlar.append(f"bodrum kat sayısı {bodrum} yapıldı")
        except KeyError:
            pass
        if eklenen or notlar:
            self.durum.config(text="Otomatik: " + (f"{', '.join(repr(a) for a in eklenen)} katı 'Kat kaçış verileri' tablosuna eklendi" if eklenen else "")
                              + ("; " if eklenen and notlar else "") + "; ".join(notlar) + ". Çıkış bilgilerini girmeyi unutmayın.")

    # ---- işlemler
    def hesapla(self, sor: bool = False):
        """sor=True: eksik zorunlu bilgi varsa kullanıcıya sorar ('Yine de devam et' ile sürer). Hesaplandıysa True döner."""
        try:
            g = self.topla_girdi()
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Hesaplama hatası", f"{type(e).__name__}: {e}")
            return False
        if sor:
            hepsi = []
            for i in range(self.defter.index("end")):
                ad = self.defter.tab(i, "text")
                hepsi.extend(f"{ad}: {m}" for m in self.zorunlu_eksikler(ad, g))
            if hepsi and not UyariPenceresi(self, "Eksik bilgi", f"Hesap için gerekli {len(hepsi)} bilgi eksik. Yine de hesaplansın mı?", hepsi,
                                            devam_metni="Yine de hesapla").devam:
                return False
        try:
            self.sonuclar = H.hesapla(g)
            self.g_son = g
            self.dokum_goster(DOKUM.hesap_dokumu(g))
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Hesaplama hatası", f"{type(e).__name__}: {e}")
            return False
        oz = H.ozet(self.sonuclar)
        parcalar = [f"{ad}: {oz.get(k, 0)}" for ad, k in (("Uygun", UYGUN), ("Uygun değil", UYGUN_DEGIL), ("Gerekli önlem", GEREKLI),
                                                           ("Koşullu", KOSULLU), ("Veri girilmedi", KONTROL), ("Gerekmez", GEREKMEZ))]
        self.ozet_etiket.config(text="   |   ".join(parcalar), foreground="#C00000" if oz.get(UYGUN_DEGIL) else "#006100")
        self._sonuc_goster()
        self.sekme_sec(self.sonuc_sekmesi)
        self.durum.config(text=f"{len(self.sonuclar)} satır hesaplandı; ayrıntılı hesaplar 'Hesap dökümü' sekmesinde.")
        return True

    # ---- hesap dökümü sekmesi
    def _dokum_sekmesi(self):
        f = ttk.Frame(self.defter)
        self.defter.add(f, text="Hesap dökümü")
        self.dokum_sekmesi = f
        ust = ttk.Frame(f)
        ust.pack(fill="x", padx=8, pady=6)
        ttk.Label(ust, text="Tüm hesapların formülü, yerine konan sayılar ve sonuçları (önce 'Hesapla' düğmesine basın).", font=("", 10, "bold")).pack(side="left")
        ttk.Button(ust, text="Metni kaydet (.txt)", command=self.dokum_kaydet).pack(side="right", padx=2)
        ttk.Button(ust, text="Kopyala", command=self.dokum_kopyala).pack(side="right", padx=2)
        cerceve = ttk.Frame(f)
        cerceve.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.dokum_metni = tk.Text(cerceve, wrap="word", font=("Courier New", 10) if sys.platform.startswith("win") else ("DejaVu Sans Mono", 9), padx=8, pady=6, undo=False)
        kay = ttk.Scrollbar(cerceve, orient="vertical", command=self.dokum_metni.yview)
        self.dokum_metni.configure(yscrollcommand=kay.set)
        self.dokum_metni.pack(side="left", fill="both", expand=True)
        kay.pack(side="right", fill="y")
        t = self.dokum_metni
        t.tag_configure("bolum", background="#1F3864", foreground="#FFFFFF", font=("", 11, "bold"), spacing1=10, spacing3=4)
        t.tag_configure("blok", font=("", 10, "bold"), foreground="#1F3864", spacing1=8)
        t.tag_configure("madde", foreground="#7F7F7F", font=("", 8))
        t.tag_configure("adim", lmargin1=18, lmargin2=34)
        t.tag_configure("sonuc", font=("", 10, "bold"), lmargin1=18, lmargin2=34, foreground="#222222", spacing3=2)
        t.tag_configure("uygun", foreground="#006100", font=("", 10, "bold"), lmargin1=18, lmargin2=34)
        t.tag_configure("uygunsuz", foreground="#C00000", font=("", 10, "bold"), lmargin1=18, lmargin2=34)
        t.tag_configure("kosullu", foreground="#9C5700", font=("", 10, "bold"), lmargin1=18, lmargin2=34)
        t.insert("1.0", "Henüz hesaplanmadı. 'Hesapla' düğmesine basın.")
        t.configure(state="disabled")

    def dokum_goster(self, bolumler):
        t = self.dokum_metni
        t.configure(state="normal")
        t.delete("1.0", "end")
        for bo in bolumler:
            t.insert("end", bo.ad + "\n", "bolum")
            for bl in bo.bloklar:
                t.insert("end", "▌ " + bl.baslik, "blok")
                if bl.madde:
                    t.insert("end", "   [" + bl.madde + "]", "madde")
                t.insert("end", "\n")
                for a in bl.adimlar:
                    t.insert("end", "• " + a + "\n", "adim")
                etiket = {"UYGUN": "uygun", "UYGUN DEĞİL": "uygunsuz", "KOŞULLU UYGUN": "kosullu"}.get(bl.durum, "sonuc")
                t.insert("end", "► Sonuç: " + bl.sonuc + (f"   —  {bl.durum}" if bl.durum else "") + "\n", etiket)
        t.configure(state="disabled")
        self._dokum_duz = DOKUM.dokum_duz_metin(bolumler)

    def dokum_kopyala(self):
        self.clipboard_clear()
        self.clipboard_append(getattr(self, "_dokum_duz", ""))
        self.durum.config(text="Hesap dökümü panoya kopyalandı.")

    def dokum_kaydet(self):
        if not getattr(self, "_dokum_duz", ""):
            messagebox.showinfo("Hesap dökümü", "Önce 'Hesapla' düğmesine basın.")
            return
        yol = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=self._dosya_adi("txt").replace("_yangin_hesabi", "_hesap_dokumu"), filetypes=[("Metin", "*.txt")])
        if yol:
            with open(yol, "w", encoding="utf-8") as f:
                f.write(self._dokum_duz)
            self.durum.config(text=f"Hesap dökümü kaydedildi: {yol}")

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

    def _sonuc_ipucu(self, x, y):
        """Sonuç satırının üzerine gelince dayanak madde metnini gösterir."""
        iid = self.sonuc_agaci.identify_row(y)
        if not iid or self.sonuc_agaci.identify_region(x, y) != "cell":
            return None
        v = self.sonuc_agaci.item(iid, "values")
        return iid, MEV.sonuc_ipucu_bolumleri(v[1], v[4], v[5])

    def _satir_detay(self, _e):
        sec = self.sonuc_agaci.selection()
        if sec:
            v = self.sonuc_agaci.item(sec[0], "values")
            messagebox.showinfo(v[1], f"{v[0]}\n\nDeğer: {v[2]}\nDurum: {v[3]}\nDayanak: {v[4]}\n\n{v[5]}")

    def _dosya_adi(self, uzanti):
        ad = (self.vars["proje_adi"].get() or "proje").strip().replace(" ", "_")
        return f"{ad}_yangin_hesabi.{uzanti}"

    def rapor_kaydet(self, tur: str):
        if not self.hesapla(sor=True):
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
    assert any(st == "mevzuat" for st, _ in MEV.ipucu_bolumleri("kat_sayisi")), "mevzuat ipucu"
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
