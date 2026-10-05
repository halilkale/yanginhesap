"""Yönetmelik ekleri (tablolar) ve sabitler.

Her tablo, Binaların Yangından Korunması Hakkında Yönetmeliğin (RG 19.12.2007/26735,
20.11.2021 tarihli 4825 sayılı CK ile değişik hali) ilgili ekinden alınmıştır.
Değerler PDF'teki tablo görüntüleriyle karşılaştırılarak girilmiştir.
"""

# --------------------------------------------------------------------------
# Tehlike sınıfları (Madde 19, Ek-1)
# --------------------------------------------------------------------------
TEHLIKE_SINIFLARI = {
    "DT": "Düşük Tehlike",
    "OT1": "Orta Tehlike-1",
    "OT2": "Orta Tehlike-2",
    "OT3": "Orta Tehlike-3",
    "OT4": "Orta Tehlike-4",
    "YT1": "Yüksek Tehlike-1",
    "YT2": "Yüksek Tehlike-2",
    "YT3": "Yüksek Tehlike-3",
    "YT4": "Yüksek Tehlike-4",
}
TEHLIKE_SIRASI = list(TEHLIKE_SINIFLARI)


def tehlike_grubu(kod: str) -> str:
    """'dusuk' | 'orta' | 'yuksek'"""
    if kod == "DT":
        return "dusuk"
    return "orta" if kod.startswith("OT") else "yuksek"


def ot3_ve_ustu(kod: str) -> bool:
    """Ek-4 için 'Orta Tehlike-3 ve üstü' mü?"""
    return TEHLIKE_SIRASI.index(kod) >= TEHLIKE_SIRASI.index("OT3")


# Madde 92(3): su deposu hacmi için süre (dakika)
SU_SURESI_DK = {"dusuk": 30, "orta": 60, "yuksek": 90}

# Ek-1/A, Ek-1/B, Ek-1/C  -> (kategori, tesis türü, tehlike sınıfı)
EK1_TESISLER = [
    ("Düşük", "Büro / idari bölüm (126 m²'yi aşmayan, 30 dk dayanımlı bölüm)", "DT"),
    ("Düşük", "Okul / eğitim kurumu (belirli alanlar)", "DT"),
    ("Düşük", "Hapishane", "DT"),
    ("Çimento, metal, gıda", "Çimento işleri", "OT1"),
    ("Çimento, metal, gıda", "Metal levha üretimi", "OT1"),
    ("Çimento, metal, gıda", "Mezbaha, mandıra", "OT1"),
    ("Çeşitli", "Hastane, otel, konut, lokanta, kütüphane (kitap deposu hariç), okul, büro", "OT1"),
    ("Çeşitli", "Bilgisayara veri işleme ofisi (veri saklama odaları hariç)", "OT1"),
    ("Kimyasal / fotoğraf", "Fotoğraf laboratuvarı, fotoğraf film fabrikası", "OT2"),
    ("Mühendislik", "Otomotiv fabrikası, tamirhane", "OT2"),
    ("Yiyecek ve içecek", "Fırın, bisküvi, çikolata, şekerleme imalathanesi, bira fabrikası", "OT2"),
    ("Çeşitli", "Fizik laboratuvarı, çamaşırhane, otopark, müze", "OT2"),
    ("Tekstil", "Deri eşya fabrikası", "OT2"),
    ("Cam", "Cam fabrikası", "OT3"),
    ("Kimyasal", "Boyama işlemleri, sabun fabrikası", "OT3"),
    ("Mühendislik", "Elektronik, buzdolabı ve çamaşır makinesi fabrikası", "OT3"),
    ("Yiyecek ve içecek", "Hayvan yemi, meyve kurutma, kurutulmuş sebze/çorba, şeker imalathanesi, tahıl değirmeni", "OT3"),
    ("Çeşitli", "Radyo-TV yayınevi, tren istasyonu, tesisat odası", "OT3"),
    ("Kâğıt", "Ciltevi, mukavva fabrikası, kâğıt fabrikası, baskı işleri, matbaa", "OT3"),
    ("Lastik ve plastik", "Kablo fabrikası, plastik döküm/eşya (köpük hariç), kauçuk eşya, sentetik lif (akrilik hariç)", "OT3"),
    ("Lastik ve plastik", "Vulkanize fabrikası", "OT3"),
    ("Dükkân ve ofis", "Büyük mağaza, alışveriş merkezi", "OT3"),
    ("Tekstil", "Halı (kauçuk/köpük hariç), kumaş, giysi, fiber levha, ayakkabı, triko, ev tekstili, yatak/şilte, dikim-dokuma, yün atölyesi", "OT3"),
    ("Kereste ve ahşap", "Ahşap işleri, mobilya fabrikası (köpük hariç), mobilya mağazası, koltuk/kanepe imalathanesi", "OT3"),
    ("Kimyasal", "Mum ve balmumu fabrikası, kibrit fabrikası, boyahane", "OT4"),
    ("Yiyecek ve içecek", "Alkol damıtma", "OT4"),
    ("Çeşitli", "Sinema, tiyatro, konser salonu, tütün fabrikası", "OT4"),
    ("Kâğıt", "Atık kâğıt işletmesi", "OT4"),
    ("Lastik ve plastik", "Halat fabrikası", "OT4"),
    ("Dükkân ve ofis", "Sergi salonu", "OT4"),
    ("Tekstil", "Pamuk iplikhanesi, keten ve kenevir hazırlama tesisi", "OT4"),
    ("Kereste ve ahşap", "Odun talaşı, yonga levha, kontrplak fabrikası", "OT4"),
    ("Yüksek tehlike", "Döşemelik kumaş / muşamba fabrikası, kumaş-muşamba yer döşemesi imalatı", "YT1"),
    ("Yüksek tehlike", "Boya, renklendirici, vernik imalatı", "YT1"),
    ("Yüksek tehlike", "Yapay kauçuk, reçine, lamba isi, terebentin imalatı", "YT1"),
    ("Yüksek tehlike", "Talaş fabrikası, odun yünü imalatı", "YT1"),
    ("Yüksek tehlike", "Aydınlatma fişeği fabrikası", "YT2"),
    ("Yüksek tehlike", "Plastik köpük ve sünger imalathanesi, lastik köpük eşya", "YT2"),
    ("Yüksek tehlike", "Katran damıtma", "YT2"),
    ("Yüksek tehlike", "Otobüs ambarı, yüklü kamyon/vagon, otobüs-yüksüz kamyon-vagon deposu", "YT2"),
    ("Yüksek tehlike", "Selüloz nitrat fabrikası", "YT3"),
    ("Yüksek tehlike", "Havai fişek fabrikası", "YT4"),
]

# --------------------------------------------------------------------------
# Kullanım sınıfları (Madde 8) ve ilişkili tablo anahtarları
# --------------------------------------------------------------------------
# anahtar -> (ad, ek3c_satir, ek5b_satir)
KULLANIM_SINIFLARI = {
    "endustriyel": "Endüstriyel yapı (fabrika, imalathane)",
    "depo": "Depolama amaçlı tesis (depo)",
    "buro": "Büro binası",
    "ticaret": "Ticaret amaçlı bina",
    "toplanma": "Toplanma amaçlı bina",
    "konaklama": "Konaklama amaçlı bina",
    "kurumsal": "Kurumsal bina (eğitim, sağlık)",
    "apartman": "Konut - apartman",
    "otopark": "Kapalı otopark",
    "yuksek_tehlikeli": "Yüksek tehlikeli yer (Madde 17)",
}

# --------------------------------------------------------------------------
# Ek-3/C  Yangına dayanım süreleri (dk)
# sütunlar: bodrum(>10 m), bodrum(<10 m), bodrum(<5 m), üst kat (<21.50), (<30.50), (>30.50)
# None -> "---", "IY" -> "İzin verilmez"
# --------------------------------------------------------------------------
IY = "İzin verilmez"
EK3C = {
    # (sınıf, yağmurlama_var) : (b>10, b<10, b<5, h<21.5, h<30.5, h>30.5)
    ("apartman", False): (90, 60, 30, 60, 90, 120),
    ("apartman", True): (90, 60, 30, 60, 90, 120),
    ("konaklama", False): (90, 60, 60, 60, 90, IY),
    ("konaklama", True): (60, 60, 30, 60, 60, 120),
    ("kurumsal", False): (90, 60, 60, 60, 90, IY),
    ("kurumsal", True): (90, 60, 30, 60, 90, 120),
    ("buro", False): (90, 60, 30, 60, 90, IY),
    ("buro", True): (60, 60, 30, 30, 60, 120),
    ("ticaret", False): (90, 60, 60, 60, 90, IY),
    ("ticaret", True): (60, 60, 30, 30, 60, 120),
    ("endustriyel", False): (120, 90, 60, 90, 120, IY),
    ("endustriyel", True): (90, 60, 30, 60, 90, 120),
    ("toplanma", False): (90, 60, 60, 60, 90, IY),
    ("toplanma", True): (60, 60, 30, 60, 60, 120),
    ("depo", False): (120, 90, 60, 90, 120, IY),
    ("depo", True): (90, 60, 30, 60, 90, 120),
    ("otopark", False): (90, 60, 30, 60, 90, IY),
    ("otopark", True): (90, 60, 30, 60, 90, 120),
    # Yüksek tehlikeli yerlerde Ek-3/C'de ayrı satır yoktur; endüstriyel satırı esas alınır.
    ("yuksek_tehlikeli", False): (120, 90, 60, 90, 120, IY),
    ("yuksek_tehlikeli", True): (90, 60, 30, 60, 90, 120),
}
EK3C_SUTUNLAR = [
    "Bodrum (derinlik > 10 m)",
    "Bodrum (derinlik < 10 m)",
    "Bodrum (derinlik < 5 m)",
    "Üst katlar (bina yüksekliği < 21,50 m)",
    "Üst katlar (bina yüksekliği < 30,50 m)",
    "Üst katlar (bina yüksekliği > 30,50 m)",
]

# Ek-3/B  Yapı elemanlarının yangına dayanım süreleri (sabit olanlar)
EK3B_SABIT = [
    ("Taşıyıcı sistem (çerçeve, kiriş, kolon)", "R — Ek-3/C'ye göre", "Ek-3/B-1"),
    ("Yük taşıyıcı duvar", "R — Ek-3/C'ye göre", "Ek-3/B-2"),
    ("Kat döşemeleri (kompartıman döşemeleri dâhil)", "REI — Ek-3/C'ye göre (alt yüzeyden)", "Ek-3/B-3c"),
    ("Bodrum kat ile zemin kat arası döşeme", "REI 90 veya Ek-3/C (hangisi büyükse)", "Ek-3/B-3d"),
    ("Kaçış yolu teşkil eden çatı bölümü", "REI 30", "Ek-3/B-4a"),
    ("Parsel sınırına 2 m'den yakın dış duvar", "REI — Ek-3/C'ye göre (her yüzey)", "Ek-3/B-5a"),
    ("Bina içi farklı kullanımları ayıran kompartıman duvarı", "REI 60 veya Ek-3/C (hangisi büyükse)", "Ek-3/B-6"),
    ("Diğer kompartıman duvarları", "REI — Ek-3/C'ye göre", "Ek-3/B-7"),
    ("Korunumlu şaftlar", "REI 120", "Ek-3/B-8"),
    ("Kaçış merdiveni yuvası / acil durum asansör kuyusu / güvenlik holü (binadan ayıran duvar)", "REI 120", "Ek-3/B-9a"),
    ("Merdiven yuvası, asansör kuyusu ve güvenlik holünü birbirinden ayıran duvar", "REI 60", "Ek-3/B-9b"),
    ("Yangın kesici", "EI 30", "Ek-3/B-10"),
    ("Asma tavan", "EI 30", "Ek-3/B-11"),
    ("Asansör kat kapıları (yapı yüksekliği > 51,50 m)", "E 60", "Ek-3/B-12a"),
    ("Asansör kat kapıları (yapı yüksekliği < 51,50 m)", "E 30", "Ek-3/B-12b"),
    ("Yangın duvarı (bitişik nizam)", "en az 90 dk", "Madde 25"),
    ("Kazan dairesi / yakıt deposu bölmesi", "en az 120 dk", "Madde 54, 56"),
    ("Trafo ve jeneratör odası", "en az 120 dk", "Madde 65, 66"),
]

# --------------------------------------------------------------------------
# Ek-4  En fazla kompartıman alanı (m²)
# --------------------------------------------------------------------------
# anahtar -> (alan, not no)   not: 1 -> kontrol sistemi varsa 2 kat; 2 -> sınırsız;
#                                  3 -> tek katlı sınırsız / kontrol sistemi varsa sınırsız
def ek4_limit(kullanim: str, tehlike: str):
    """(limit_m2 | None, not_no, aciklama). None = sınırlama yok."""
    if kullanim == "endustriyel" or kullanim == "yuksek_tehlikeli":
        if ot3_ve_ustu(tehlike):
            return 6000, 2, "Endüstriyel yapı — Orta Tehlike-3 ve üstü"
        return 15000, 3, "Endüstriyel yapı — Orta Tehlike-1 ve 2"
    if kullanim == "depo":
        if ot3_ve_ustu(tehlike):
            return 1000, 2, "Depo — Orta Tehlike-3 ve üstü"
        return 5000, 3, "Depo — Orta Tehlike-1 ve 2"
    if kullanim == "otopark":
        return None, 0, "Kapalı otopark — sınırlama yok"
    if kullanim == "apartman":
        return None, 0, "Konut — sınırsız"
    if kullanim == "konaklama":
        return 4000, 1, "Konaklama"
    if kullanim == "kurumsal":
        return 6000, 2, "Kurumsal — eğitim tesisi (sağlık için 1500 m², not 1)"
    if kullanim == "buro":
        return 8000, 1, "Büro binası"
    if kullanim == "ticaret":
        return 2000, 2, "Ticaret amaçlı bina"
    if kullanim == "toplanma":
        return 6000, 2, "Diğer toplanma amaçlı bina (yeme-içme, eğlence, müze için 4000 m²)"
    raise KeyError(kullanim)


# --------------------------------------------------------------------------
# Ek-5/A  Kullanıcı yükü katsayıları (m²/kişi)  — (ad, katsayı, alan_türü)
# alan_türü: "net" (1-4. satırlar) | "brüt" (diğerleri)
# --------------------------------------------------------------------------
EK5A = [
    ("Fabrika üretim alanı / paketleme yeri", 10.0, "brüt"),
    ("Depo, ambar, makine dairesi", 30.0, "brüt"),
    ("Atölye / sanat galerisi / müze", 5.0, "brüt"),
    ("Mutfak, çamaşırhane", 10.0, "brüt"),
    ("Ofis, dernek merkezi, halk kütüphanesi", 10.0, "brüt"),
    ("Yemekhane / kantin / lokanta (net alan)", 1.5, "net"),
    ("Toplantı, konferans, çok amaçlı salon (net alan)", 1.5, "net"),
    ("Derslik, bilgisayar odası, seminer salonu", 1.5, "brüt"),
    ("Resepsiyon, bekleme alanı, atrium zemini", 3.0, "brüt"),
    ("Süpermarket, mağaza, dükkân", 5.0, "brüt"),
    ("Sanat galerisi, müze", 5.0, "brüt"),
    ("Sergi alanı, stüdyo (net alan)", 1.5, "net"),
    ("Terminal bekleme salonu (net alan)", 3.0, "net"),
    ("Çok amaçlı spor tesisi", 3.0, "brüt"),
    ("Fitness, aerobik, okuma salonu", 5.0, "brüt"),
    ("Muayenehane, öğrenci laboratuvarı", 5.0, "brüt"),
    ("Otopark", 30.0, "brüt"),
    ("Öğrenci yatak odası", 10.0, "brüt"),
    ("Otel yatak odası", 20.0, "brüt"),
    ("Hastane yatak odası, hemşire odası", 20.0, "brüt"),
    ("Hastane laboratuvarı, eczane", 20.0, "brüt"),
    ("Dans salonu, bar, gece kulübü — oturulan kısım (net)", 1.0, "net"),
    ("Dans salonu, bar, gece kulübü — ayakta durulan kısım (net)", 0.5, "net"),
    ("Diğer / özel katsayı (elle gir)", 0.0, "brüt"),
]

# --------------------------------------------------------------------------
# Ek-5/B  Kaçış uzaklıkları ve birim genişlik (50 cm başına kişi)
# alanlar: tek_yon (ysiz, ysli), iki_yon (ysiz, ysli), birim: dis_kapi, diger_kapi,
#          merdiven, rampa_koridor, cikmaz (ysiz, ysli)
# --------------------------------------------------------------------------
EK5B = {
    "yuksek_tehlikeli": dict(tek=(10, 20), iki=(20, 35), dis_kapi=50, diger_kapi=40, merdiven=30, koridor=50, cikmaz=(10, 20)),
    "endustriyel": dict(tek=(15, 25), iki=(30, 60), dis_kapi=100, diger_kapi=80, merdiven=60, koridor=100, cikmaz=(15, 20)),
    "yurt": dict(tek=(15, 30), iki=(45, 75), dis_kapi=50, diger_kapi=40, merdiven=30, koridor=50, cikmaz=(15, 20)),
    "ticaret": dict(tek=(15, 25), iki=(45, 60), dis_kapi=100, diger_kapi=80, merdiven=60, koridor=100, cikmaz=(15, 20)),
    "buro": dict(tek=(15, 30), iki=(45, 75), dis_kapi=100, diger_kapi=80, merdiven=60, koridor=100, cikmaz=(15, 20)),
    "depo": dict(tek=(15, 25), iki=(45, 60), dis_kapi=100, diger_kapi=80, merdiven=60, koridor=100, cikmaz=(15, 20)),
    "otopark": dict(tek=(15, 25), iki=(45, 60), dis_kapi=100, diger_kapi=80, merdiven=60, koridor=100, cikmaz=(15, 20)),
    "okul": dict(tek=(15, 30), iki=(45, 75), dis_kapi=100, diger_kapi=80, merdiven=60, koridor=100, cikmaz=(15, 20)),
    "toplanma": dict(tek=(15, 25), iki=(45, 60), dis_kapi=100, diger_kapi=80, merdiven=60, koridor=100, cikmaz=(15, 20)),
    "hastane": dict(tek=(15, 25), iki=(30, 45), dis_kapi=30, diger_kapi=30, merdiven=30, koridor=30, cikmaz=(15, 20)),
    "otel": dict(tek=(15, 20), iki=(30, 45), dis_kapi=50, diger_kapi=40, merdiven=30, koridor=50, cikmaz=(15, 20)),
    "apartman": dict(tek=(15, 30), iki=(30, 75), dis_kapi=50, diger_kapi=40, merdiven=30, koridor=50, cikmaz=(15, 20)),
}
# Madde 8 kullanım sınıfı -> Ek-5/B satırı
KULLANIM_EK5B = {
    "endustriyel": "endustriyel",
    "depo": "depo",
    "buro": "buro",
    "ticaret": "ticaret",
    "toplanma": "toplanma",
    "konaklama": "otel",
    "kurumsal": "okul",
    "apartman": "apartman",
    "otopark": "otopark",
    "yuksek_tehlikeli": "yuksek_tehlikeli",
}

# Ek-14 (mevcut yapılar) — tek yön / iki yön en çok kaçış uzaklıkları
EK14_ENDUSTRIYEL = dict(tek=(15, 25), iki=(30, 60))

# --------------------------------------------------------------------------
# Ek-7  Otomatik algılama gereken binalar  (yapı yüksekliği > m, toplam kapalı alan > m²)
# Endüstriyel yapılar satırı Danıştay kararıyla iptal edilmiştir.
# --------------------------------------------------------------------------
EK7 = {
    "apartman": (51.50, None),
    "konaklama": (6.50, 1000),
    "buro": (30.50, 5000),
    "depo": (6.50, 5000),
    "yuksek_tehlikeli": (6.50, 1000),
}

# --------------------------------------------------------------------------
# Ek-8/A  Su deposu en az hacmi (m³) — h<=15, 15<h<=30, 30<h<=45
# --------------------------------------------------------------------------
EK8A = {
    ("DT", "islak"): (9, 10, 11),
    ("OT1", "islak"): (55, 70, 80),
    ("OT1", "kuru"): (105, 125, 140),
    ("OT2", "islak"): (105, 125, 140),
    ("OT2", "kuru"): (135, 160, 185),
    ("OT3", "islak"): (135, 160, 185),
    ("OT3", "kuru"): (160, 185, 200),
    ("OT4", "islak"): (160, 185, 200),
    # OT-4 kuru ve Yüksek Tehlike: hidrolik hesap kullanılır
}

# Ek-8/B  Yağmurlama tasarım yoğunluğu (mm/dk), koruma alanı (m²) ıslak / kuru
EK8B = {
    "DT": (2.25, 84, None),   # kuru: Orta Tehlike-1 kullanılır
    "OT1": (5.0, 72, 90),
    "OT2": (5.0, 144, 180),
    "OT3": (5.0, 216, 270),
    "OT4": (5.0, 360, None),  # kuru: Yüksek Tehlike-1 kullanılır
    "YT1": (7.7, 260, 325),
    "YT2": (10.0, 260, 325),
    "YT3": (12.5, 260, 325),
    "YT4": (None, None, None),  # yoğun su
}

# Ek-8/C  İlave yangın dolabı debisi (l/dk), hidrant debisi (l/dk), süre (dk)
EK8C = {
    "dusuk": (100, 400, 30),
    "OT12": (100, 400, 60),
    "OT34": (100, 1000, 60),
    "yuksek": (200, 1500, 90),
}


def ek8c_anahtar(tehlike: str) -> str:
    if tehlike == "DT":
        return "dusuk"
    if tehlike in ("OT1", "OT2"):
        return "OT12"
    if tehlike in ("OT3", "OT4"):
        return "OT34"
    return "yuksek"


# --------------------------------------------------------------------------
# Tehlikeli madde tabloları (Ek-9, Ek-10, Ek-12)
# --------------------------------------------------------------------------
# Ek-9: LPG tüp deposu (bina dışı) — üst kg sınırı, bina/komşu arsa sınırı (m), cadde-okul vb. (m)
EK9 = [(1250, 0, 3), (2700, 3, 6), (4500, 6, 12), (float("inf"), 8, 15)]

# Ek-10: dökme LPG tankı — üst su hacmi (m³), yeraltı (m), yerüstü (m), tanklar arası (m | "D/4")
EK10 = [
    (0.5, 3, 3, 0.0),
    (3.0, 3, 3, 1.0),
    (10, 5, 7.5, 1.0),
    (50, 7.5, 10, 1.0),
    (120, 10, 15, 1.5),
    (250, 15, 23, "D/4"),
    (600, 15, 38, "D/4"),
    (1200, 15, 61, "D/4"),
    (5000, 15, 91, "D/4"),
    (float("inf"), 15, 122, "D/4"),
]

# Ek-12/A: depo binasında depolama (litre) — sınıf: (orijinal kap, taşınabilir tank)
EK12A = {
    "IA": (2500, None),
    "IB": (5000, 7500),
    "IC": (10000, 5000),
    "II": (30000, 40000),
    "IIIA": (100000, 150000),
    "IIIB": (200000, 300000),
}

# Ek-12/B: bina içi depolama — (en çok alan m², izin verilen L/m², dayanım dk, korunum var mı)
EK12B = [
    (15, 70, 60, False),
    (15, 175, 60, True),
    (50, 140, 120, False),
    (50, 350, 120, True),
]

# Ek-12/C: açıkta yerüstü tankı — (üst hacim L, arsa sınırı/yol m, idari bina m, tanklar arası m | "D/4")
EK12C = [
    (1000, 1.5, 1.5, 0.0),
    (3000, 3.0, 1.5, 1.0),
    (45000, 5.0, 1.5, 1.0),
    (115000, 7.0, 1.5, 1.5),
    (190000, 10.0, 3.0, 1.5),
    (375000, 15.0, 5.0, 1.5),
    (1900000, 25.0, 7.5, "D/4"),
    (3750000, 30.0, 10.0, "D/4"),
    (7550000, 40.0, 15.0, "D/4"),
    (11375000, 50.0, 17.5, "D/4"),
    (float("inf"), 55.0, 20.0, "D/4"),
]

# Ek-12/Ç: yeraltı tankı — (üst hacim L, arsa sınırı/yol m, tanklar arası m | "D/4")
EK12C2 = [
    (500, 0.0, 0.0),
    (3000, 3.0, 1.0),
    (10000, 5.0, 1.0),
    (50000, 7.5, 1.0),
    (120000, 10.0, 1.5),
    (250000, 15.0, "D/4"),
    (600000, 15.0, "D/4"),
    (1200000, 15.0, "D/4"),
    (5000000, 15.0, "D/4"),
    (float("inf"), 15.0, "D/4"),
]

# Ek-11: yanıcı/parlayıcı sıvı depolama miktarları (litre) — (alt sınır = bildirim, üst sınır = itfaiye izni)
# Madde 114: değerleri aşan miktarlarda bildirim; üst sınırı aşarsa ayrıca itfaiye izni.
EK11 = {
    "zemin_ustu": {"IA": (20, 60), "IB_IC_II": (100, 300)},
    "acikta": {"IA": (20, 200), "IB_IC_II": (40, 600)},
}

# Madde 118(2): karışık depolamada Sınıf IA cinsinden eşdeğerlik bölenleri
IA_ESDEGER_BOLEN = {"IA": 1, "IB": 2, "IC": 4, "II": 12, "IIIA": 40, "IIIB": 80}
