"""Veri toplama formu, form aktarımı ve kullanım kılavuzu için tek kaynak: alan tanımları.

Her alan `Girdi` modelindeki bir alana karşılık gelir. `kim` sütunu bilginin kimden isteneceğini söyler:
  Z = işveren (mutlaka doldurmalı)    V = işveren (biliyorsa / varsa)    M = proje müellifi, montaj-bakım firması veya mühendis
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import etiketler as E
from . import tablolar as T


@dataclass
class Alan:
    alan: str | None          # Girdi alan adı (None: yalnızca form bilgisi, programa aktarılmaz)
    baslik: str               # İşverenin göreceği soru
    tip: str                  # metin | sayi | tam | evet | secim | tesis | bilgi
    aciklama: str             # Nasıl doldurulur / ne demek
    birim: str = ""
    kaynak: str = ""          # Bilgi hangi belgeden/kişiden bulunur
    kim: str = "Z"
    madde: str = ""           # Programda neye etki ediyor (yönetmelik dayanağı)
    secenek: dict | None = None
    ornek: str = ""


@dataclass
class Sayfa:
    ad: str                   # Excel sekme adı
    baslik: str
    giris: str
    alanlar: list[Alan] = field(default_factory=list)
    program_sekmesi: str = ""


EVET_HAYIR = {True: "Evet", False: "Hayır"}
KULLANIM = T.KULLANIM_SINIFLARI
TEHLIKE = T.TEHLIKE_SINIFLARI
TESIS_ETIKET = [f"{k} — {a} → {T.TEHLIKE_SINIFLARI[sn]}" for k, a, sn in T.EK1_TESISLER]

SAYFALAR: list[Sayfa] = [
    Sayfa("1_Genel", "1. Genel bilgiler ve faaliyet", "Tesisin kimliği, ne üretildiği ve binanın genel özellikleri.", program_sekmesi="Genel", alanlar=[
        Alan(None, "Formu dolduran kişi ve görevi", "bilgi", "Sorularımız olursa kime ulaşacağımızı yazın.", kaynak="—", ornek="Ahmet Yılmaz — İSG uzmanı"),
        Alan(None, "Telefon / e-posta", "bilgi", "Formu dolduran kişinin iletişim bilgisi.", kaynak="—"),
        Alan("proje_adi", "Proje / bina adı", "metin", "Raporun başlığında görünecek ad.", kaynak="Ruhsat veya işletme belgesi", ornek="Örnek Mobilya Fabrikası - A Blok"),
        Alan("tesis_adi", "Firma unvanı", "metin", "Ticaret sicilindeki tam unvan.", kaynak="Vergi levhası / ticaret sicil gazetesi", ornek="Örnek Sanayi A.Ş."),
        Alan("adres", "Tesis adresi", "metin", "Açık adres, ada/parsel varsa yazın.", kaynak="Tapu / ruhsat"),
        Alan("tarih", "Rapor tarihi", "metin", "Boş bırakırsanız bugünün tarihi yazılır.", kim="V"),
        Alan("hazirlayan", "Raporu hazırlayan (mühendis)", "metin", "Bu alanı işveren boş bırakır; raporu hazırlayan mühendis yazar.", kim="M"),
        Alan("kullanim", "Binanın ana kullanım amacı", "secim", "Binanın asıl işlevini seçin. Fabrika ve imalathane için 'Endüstriyel yapı', ambar/depo için 'Depolama amaçlı tesis'.",
             kaynak="Yapı ruhsatı / iskân belgesi", madde="Madde 8, 14, 16 — tüm tablolar bu seçime göre okunur", secenek=KULLANIM, ornek="Endüstriyel yapı (fabrika, imalathane)"),
        Alan("@tesis", "Ana üretim / faaliyet türü", "tesis", "Listeden üretiminize en yakın faaliyeti seçin. Program tehlike sınıfını buna göre önerir. Birden fazla faaliyet varsa en tehlikeli olanı seçin ve Notlar bölümüne diğerlerini yazın.",
             kaynak="Üretim akışı, kapasite raporu", madde="Madde 19, Ek-1/A-B-C", ornek="Ahşap işleri, mobilya fabrikası ... → Orta Tehlike-3"),
        Alan("tehlike", "Tehlike sınıfı (mühendis kararı)", "secim", "Boş bırakılabilir; faaliyet türünden otomatik belirlenir. Mühendis farklı sınıf belirlerse buraya yazar.",
             kim="M", madde="Madde 19 — su deposu, sprinkler, kompartıman, dayanım süreleri", secenek=TEHLIKE),
        Alan("mevcut_yapi", "Bina daha önce yapılmış ve işletmede mi?", "evet", "Evet: mevcut işletme / Hayır: yeni yapılacak veya yeni ruhsat alacak proje.",
             kaynak="Yapı kullanma izin belgesi tarihi", madde="Onuncu Kısım (Madde 138-167), Ek-14 kaçış mesafesi"),
        Alan("karisik_kullanim", "Aynı binada farklı işlevler var ve yangın duvarıyla ayrılmamış mı?", "evet",
             "Örn. fabrika içinde ofis, yemekhane, depo bölümleri var ama bunlar yangına dayanıklı duvar/kapıyla ayrılmamışsa 'Evet'.",
             kaynak="Mimari kat planları", madde="Madde 18 — daha sıkı kurallar tüm binaya uygulanır"),
        Alan("tasiyici", "Taşıyıcı sistem türü", "secim", "Binanın kolon-kiriş sistemi neyden yapılmış?", kaynak="Statik proje, ruhsat eki", madde="Madde 23 — çelikte yalıtım, betonarmede paspayı", secenek=E.TASIYICI),
        Alan("kolay_alevlenici", "Üretimde veya depoda kolay alevlenen / parlayan madde var mı?", "evet",
             "Boya, tiner, solvent, vernik, yapıştırıcı, LPG, doğalgaz kullanan proses, akaryakıt, ahşap/toz talaşı, köpük, plastik hammaddesi, ambalaj stokları vb.",
             kaynak="Üretim akışı, MSDS (güvenlik bilgi formları)", madde="Madde 52, 96(2)e, Ek-5/B dipnotu — sprinkler zorunluluğu ve kaçış mesafesi"),
        Alan("yanmaz_malzeme_yapim", "Yapı yanmaz malzemelerle mi yapılmış?", "evet", "Çelik, betonarme, kâgir (tuğla/briket/gazbeton) yanmaz sayılır. Ahşap veya sandviç panel (yanıcı dolgulu) varsa 'Hayır'.",
             kaynak="Mimari/statik proje", madde="Madde 52(ç) — tek çıkış istisnası"),
    ]),
    Sayfa("2_Bina_Olculeri", "2. Bina ölçüleri ve çalışan sayısı", "Mimari projenizden alınacak ölçüler. Metre ve metrekare olarak, sayı yazın.", program_sekmesi="Genel — Geometri", alanlar=[
        Alan("yapi_yuksekligi", "Yapı yüksekliği", "sayi", "Bodrum katlar, asma katlar ve çatı arası dahil, yapının tüm katlarının toplam yüksekliği.", "m", "Mimari kesit", madde="Madde 4(bbb); 30,50 m üstü yüksek bina, sprinkler", ornek="12"),
        Alan("bina_yuksekligi", "Bina yüksekliği", "sayi", "Bina yaklaşma kotundan (zemin) çatı saçağına kadar olan yükseklik.", "m", "Mimari kesit / cephe", madde="Madde 4(h); 21,50 m üstü yüksek bina; Ek-3/C sütunu", ornek="10"),
        Alan("kat_sayisi", "Zemin üstü kat sayısı", "tam", "Zemin kat dahil, bodrumlar hariç. Tek katlı fabrika hali için 1 yazın. Asma katları ayrı kat saymayın, mimar belirler.", "adet", "Mimari plan", madde="Ek-4 (tek katlı sınırsız), Madde 75", ornek="2"),
        Alan("bodrum_kat_sayisi", "Bodrum kat sayısı", "tam", "Bodrum yoksa 0.", "adet", "Mimari plan", madde="Madde 89(2), Ek-3/C", ornek="0"),
        Alan("bodrum_derinligi", "Bodrum derinliği", "sayi", "En alt bodrum döşemesi ile zemin kat döşemesi arasındaki mesafe. Bodrum yoksa 0.", "m", "Mimari kesit", madde="Ek-3/C"),
        Alan("taban_alani", "Bu binanın taban (oturum) alanı", "sayi", "Binanın zemine oturduğu alan.", "m²", "Mimari vaziyet planı", madde="Madde 95(7), 97", ornek="6000"),
        Alan("tesis_toplam_taban_alani", "Parseldeki tüm binaların taban alanı toplamı", "sayi", "Tesiste birden fazla bina varsa hepsinin toplamı. Tek bina ise boş bırakın.", "m²", "Vaziyet planı", kim="V", madde="Madde 95(7): 5000 m² üstü dış hidrant"),
        Alan("toplam_kapali_alan", "Toplam kapalı kullanım alanı", "sayi", "Tüm katlar (bodrumlar dahil) kapalı alanlarının toplamı.", "m²", "Yapı ruhsatı alan tablosu", madde="Madde 7(4), 7(12), 94, 96, 99 ve Ek-7 eşikleri", ornek="9000"),
        Alan("en_buyuk_kat_alani", "En büyük kat alanı", "sayi", "Katlar arasında alanı en büyük olanın brüt alanı.", "m²", "Mimari plan", madde="Ek-4, Madde 75(2)", ornek="6000"),
        Alan("kompartiman_alani", "Yangın duvarıyla ayrılmış en büyük bölümün alanı", "sayi", "Yangına dayanıklı duvar ve döşemelerle (en az 60 dk) bölünmüş bölümlerden en büyüğünün alanı. Hiç bölme yoksa boş bırakın (kat alanı kabul edilir).",
             "m²", "Yangın projesi / mimari plan", kim="V", madde="Ek-4 en fazla kompartıman alanı"),
        Alan("otopark_alani", "Bina içindeki kapalı otopark alanı", "sayi", "Bina içinde kapalı otopark yoksa 0.", "m²", "Mimari plan", kim="V", madde="Madde 94 (600 m²), 96(2)c"),
        Alan("bina_boyu", "Bina boyu (uzun kenar)", "sayi", "Dikdörtgen yaklaşık plan ölçüsü.", "m", "Mimari plan", madde="Dolap, hidrant, buton, söndürücü adedi hesabı", ornek="120"),
        Alan("bina_eni", "Bina eni (kısa kenar)", "sayi", "Dikdörtgen yaklaşık plan ölçüsü.", "m", "Mimari plan", madde="Dolap, hidrant, buton, söndürücü adedi hesabı", ornek="50"),
        Alan("cephe_genisligi", "Ana cephe genişliği", "sayi", "En uzun cephenin uzunluğu.", "m", "Mimari cephe", madde="Madde 97: 75 m üstü itfaiye su verme bağlantısı", ornek="120"),
        Alan("calisan_sayisi", "Aynı anda binada bulunan en yüksek çalışan sayısı", "sayi", "En kalabalık vardiyadaki çalışan + sürekli bulunan ziyaretçi/taşeron sayısı.", "kişi", "İK / vardiya listesi",
             madde="Madde 126: 50 kişiyi aşan işyerlerinde acil durum ekipleri", ornek="180"),
    ]),
    Sayfa("3_Mevcut_Sistemler", "3. Mevcut yangın sistemleri ve su kaynağı", "Tesiste halihazırda bulunan veya projelendirilen yangın sistemleri. Teknik hidrolik değerleri (M) montaj/proje firmasından alınır.",
          program_sekmesi="Genel — Aktif sistemler; Su ve söndürme", alanlar=[
        Alan("yagmurlama_var", "Otomatik yağmurlama (sprinkler) sistemi var mı?", "evet", "Tavanda su püskürten başlıklar.", kaynak="Sprinkler projesi / sistem bakım sözleşmesi", madde="Ek-3/C, Ek-4, Ek-5/B — birçok sınır sprinklerle değişir", ornek="Evet"),
        Alan("yagmurlama_tipi", "Sprinkler tipi", "secim", "Hatlar su ile dolu ise ıslak, hava ile dolu ise kuru.", kim="M", kaynak="Sprinkler projesi", madde="Ek-8/A, 8/B", secenek=E.YAGMURLAMA, ornek="Islak / ön etkili"),
        Alan("algilama_var", "Otomatik yangın algılama (duman/ısı dedektörü) ve alarm var mı?", "evet", "Yangın alarm paneli, dedektörler, sirenler.", kaynak="Yangın alarm projesi", madde="Madde 74-77"),
        Alan("duman_tahliye_var", "Duman tahliye sistemi var mı?", "evet", "Çatı duman tahliye bacaları/lüverleri veya mekanik duman egzoz fanları.", kaynak="Duman tahliye projesi", madde="Ek-4 dipnotları — kompartıman sınırı"),
        Alan("hidrant_var", "Bina çevresinde yangın hidrantı (dış hidrant) var mı?", "evet", "Bina etrafında yer üstü yangın hidrantları.", kaynak="Vaziyet planı / yangın projesi", madde="Madde 95"),
        Alan("dolap_var", "Bina içinde yangın dolabı var mı?", "evet", "Duvarda hortumlu kırmızı yangın dolapları.", kaynak="Yangın tesisat projesi", madde="Madde 94"),
        Alan("yangin_butonu_adedi", "Yangın uyarı butonu (el ile alarm) adedi", "tam", "Duvardaki kırmızı alarm butonlarının toplam sayısı.", "adet", "Yangın alarm projesi / yerinde sayım", kim="V", madde="Madde 75(2)"),
        Alan("mevcut_su_deposu_m3", "Yangın suyu deposu hacmi", "sayi", "Yalnızca yangına ayrılmış rezerv hacmi. Yoksa 0.", "m³", "Yangın tesisat projesi / depo etiketi", kim="V", madde="Madde 92", ornek="200"),
        Alan("pompa_adedi", "Asıl yangın pompası adedi", "tam", "Elektrik veya dizel; yedek pompalar hariç.", "adet", "Pompa odası / proje", kim="M", madde="Madde 93(2)", ornek="1"),
        Alan("yedek_pompa_adedi", "Yedek yangın pompası adedi", "tam", "Dizel yedek pompa dahil.", "adet", "Pompa odası / proje", kim="M", madde="Madde 93(2)", ornek="1"),
        Alan("pompa_anma_debi_m3h", "Yangın pompası anma debisi", "sayi", "Pompa etiketindeki / karakteristik eğrisindeki nominal debi.", "m³/h", "Pompa etiketi, karakteristik eğri", kim="M", madde="Madde 93", ornek="150"),
        Alan("pompa_anma_basma_mSS", "Pompa anma basma yüksekliği", "sayi", "Nominal debideki basma yüksekliği.", "mSS", "Pompa karakteristik eğrisi", kim="M", madde="Madde 93(1)", ornek="100"),
        Alan("pompa_kapali_vana_basma_mSS", "Pompa kapalı vana (sıfır debi) basma yüksekliği", "sayi", "Eğrinin sıfır debideki değeri.", "mSS", "Pompa karakteristik eğrisi", kim="M", madde="Madde 93(1): en çok %140", ornek="130"),
        Alan("pompa_150_debi_basma_mSS", "Pompa %150 debide basma yüksekliği", "sayi", "Nominal debinin 1,5 katındaki basma yüksekliği.", "mSS", "Pompa karakteristik eğrisi", kim="M", madde="Madde 93(1): en az %65", ornek="70"),
        Alan("statik_yukseklik_mSS", "Pompadan en yüksek çıkışa statik yükseklik", "sayi", "Pompa ekseni ile en yüksek/uzak sprinkler başlığı veya hidrant arasındaki kot farkı.", "mSS (≈ m)", "Hidrolik hesap", kim="M", madde="Madde 93 — pompa Hy hesabı", ornek="14"),
        Alan("boru_kaybi_mSS", "Kritik hattaki toplam boru basınç kaybı", "sayi", "Hidrolik hesaptaki toplam kayıp.", "mSS", "Hidrolik hesap raporu", kim="M", madde="Madde 93 — pompa Hy hesabı", ornek="18"),
        Alan("akma_basinci_mSS", "Çıkışta gereken akma basıncı", "sayi", "Hidrant için 700 kPa ≈ 70 mSS (yönetmelik değeri); farklı ise mühendis yazar.", "mSS", "Yönetmelik Madde 95(2)", kim="M", madde="Madde 95(2)", ornek="70"),
        Alan("spr_yukseklik_h", "En alt ve en üst sprinkler başlığı arasındaki yükseklik", "sayi", "Tek katlı hallerde çatı altı ile en alt başlık arası. Raf depolarda raf içi başlıklar dahil.", "m", "Sprinkler projesi", kim="M", madde="Ek-8/A su deposu tablosu", ornek="10"),
        Alan("spr_baslik_alani_m2", "Sprinkler başlığı başına koruma alanı", "sayi", "Boş bırakılırsa program yönetmelik/standart değerini kullanır.", "m²", "Sprinkler projesi", kim="M", madde="Madde 96(5)"),
        Alan("spr_koruma_alani_m2", "Sprinkler tasarım (hidrolik) koruma alanı", "sayi", "Hidrolik hesapla belirlenmişse. Boş bırakılırsa Ek-8/B değeri kullanılır.", "m²", "Hidrolik hesap", kim="M", madde="Ek-8/B"),
        Alan("es_zamanli_dolap", "Yangın anında aynı anda çalışacak dolap sayısı", "tam", "Tasarım kabulü. Kılavuz örneğinde 2 alınmıştır.", "adet", "Proje müellifi", kim="M", madde="Madde 92(5), Ek-8/C", ornek="2"),
        Alan("dolap_tipi", "Yangın dolabı hortum tipi", "secim", "Yarı-sert hortum (Ø25, en yaygın) veya yassı hortum (DN50, eğitimli ekip gerektirir).", kim="M", kaynak="Dolap etiketi", madde="Madde 94(b)", secenek=E.DOLAP),
        Alan("hidrant_risk", "Hidrant bölge riski", "secim", "Hidrantlar arası azami uzaklığı belirler. Yönetmelik tehlike sınıfı ile eşleştirme vermez; mühendis seçer.", kim="M", madde="Madde 95(3)", secenek=E.HIDRANT),
        Alan("sadece_hidrant", "Tesiste yalnızca dış hidrant sistemi var (sprinkler/dolap yok)", "evet", "Böyle ise en az 1900 l/dk × 90 dk su gerekir.", kim="V", madde="Madde 92(7)"),
        Alan("sadece_dolap", "Tesiste yalnızca yangın dolabı sistemi var", "evet", "Sprinkler yok, sadece dolaplar.", kim="V", madde="Madde 92(6)"),
    ]),
    Sayfa("4_Aydinlatma_Duman", "4. Acil aydınlatma, yönlendirme, duman ve basınçlandırma", "Acil durum aydınlatma/yönlendirme ölçümleri ve merdiven basınçlandırması.", program_sekmesi="Algılama, duman, aydınlatma", alanlar=[
        Alan("kacis_yolu_uzunlugu_m", "En uzun kaçış yolu uzunluğu", "sayi", "Binanın en uzak noktasından dışarı çıkışa kadar izlenen yolun uzunluğu.", "m", "Yangın tahliye planı", madde="Madde 73(4) — yönlendirme işareti adedi", ornek="120"),
        Alan("isaret_yuksekligi_cm", "Acil çıkış yönlendirme levhasının yüksekliği", "sayi", "Yeşil 'ÇIKIŞ' levhasının boyu. En az 15 cm olmalıdır.", "cm", "Levha / yerinde ölçüm", madde="Madde 73(4)", ornek="20"),
        Alan("isaret_aydinlatma", "Yönlendirme levhası aydınlatma tipi", "secim", "Levha kendi içinden ışık veriyorsa 'İçeriden'; dışarıdan bir lamba aydınlatıyorsa 'Dışarıdan'.", kaynak="Armatür kataloğu", madde="Madde 73(4)", secenek=E.ISARET),
        Alan("acil_aydinlatma_sure_dk", "Acil aydınlatma bataryasının çalışma süresi", "sayi", "Şebeke kesilince armatürlerin yanık kalma süresi (test/katalog).", "dk", "Armatür kataloğu / test raporu", kim="V", madde="Madde 72(3): 60 dk, 200+ kişide 120 dk"),
        Alan("acil_aydinlatma_lux_baslangic", "Ölçülen acil aydınlık düzeyi (başlangıç)", "sayi", "Kaçış yolu merkez hattında luksmetre ile ölçülen en düşük değer.", "lux", "Ölçüm raporu", kim="V", madde="Madde 72(4): en az 1 lux"),
        Alan("acil_aydinlatma_lux_bitis", "Ölçülen acil aydınlık düzeyi (süre sonunda)", "sayi", "Batarya süresinin sonunda ölçülen değer.", "lux", "Ölçüm raporu", kim="V", madde="Madde 72(4): en az 0,5 lux"),
        Alan("acil_aydinlatma_max_min_orani", "Kaçış yolunda en yüksek / en düşük aydınlık oranı", "sayi", "Ölçüm raporundaki oran.", "", "Ölçüm raporu", kim="V", madde="Madde 72(4): en çok 40"),
        Alan("merdiven_kovasi_yuksekligi", "Kaçış merdiveni kovası yüksekliği", "sayi", "Merdiven en alt ile en üst kat arası yükseklik. Merdiven yoksa boş bırakın.", "m", "Mimari kesit", kim="V", madde="Madde 89: 30,50 m üstü basınçlandırma"),
        Alan("basinc_kapi_alani_m2", "Basınçlandırılan merdiven kapılarının alanı", "sayi", "Tek kapı alanı (genişlik × yükseklik). Tipik 0,9 × 2,1 = 1,9 m².", "m²", "Mimari proje", kim="M", madde="Madde 89(8) — asgari hava debisi", ornek="2,1"),
        Alan("basinc_sizinti_debisi_m3s", "Basınçlandırma sızıntı debisi", "sayi", "Kapalı kapı aralıklarından kaçan hava, mühendislik hesabıyla.", "m³/s", "Basınçlandırma projesi", kim="M", madde="Madde 89(10)"),
    ]),
    Sayfa("5_Kazan_Yakit_LPG", "5. Kazan dairesi, yakıt, trafo, LPG ve yanıcı sıvılar", "Isıtma/buhar kazanları, yakıt tankları, LPG ve yanıcı sıvı depoları. Yoksa 'Hayır' veya 0 yazın.", program_sekmesi="Kazan ve tehlikeli madde", alanlar=[
        Alan("kazan_var", "Kazan dairesi / buhar kazanı var mı?", "evet", "Isıtma veya proses kazanı olan ayrı oda.", kaynak="Mekanik proje", madde="Madde 54-55"),
        Alan("kazan_kw", "Kazanların toplam ısıl kapasitesi", "sayi", "Etiketteki kW değerleri toplamı (1 kcal/h = 0,001163 kW).", "kW", "Kazan etiketi", kim="V", madde="Madde 54(5), 94: 350 kW üstü", ornek="600"),
        Alan("kazan_alani_m2", "Kazan dairesi döşeme alanı", "sayi", "", "m²", "Mimari plan", kim="V", madde="Madde 54(5): 100 m² üstü 2 kapı; 88(3): 2000 m²", ornek="60"),
        Alan("kazan_kapi_sayisi", "Kazan dairesi çıkış kapısı sayısı", "tam", "Dışarı veya ortak koridora açılan kapılar.", "adet", "Mimari plan", kim="V", madde="Madde 54(5)", ornek="2"),
        Alan("kazan_sivi_yakit", "Kazan sıvı yakıtla (fuel-oil, motorin) mi çalışıyor?", "evet", "Doğalgaz/elektrik ise 'Hayır'.", kim="V", madde="Madde 54(7): pis su çukuru"),
        Alan("yakit_tank_L", "Kalorifer / proses yakıt deposu toplam hacmi", "sayi", "Yoksa 0.", "litre", "Tank etiketi", kim="V", madde="Madde 56(3): depolama sınırları", ornek="0"),
        Alan("yakit_yeri", "Yakıt deposu nerede?", "secim", "Tank bulunduğu yeri seçin. Tank yoksa boş bırakın.", kim="V", madde="Madde 56(3)", secenek=E.YAKIT),
        Alan("yakit_havuz_L", "Yakıt tankı havuzlama (taşma) hacmi", "sayi", "Tank çevresindeki sızıntı havuzunun alacağı hacim.", "litre", "Mimari/mekanik proje", kim="V", madde="Madde 56(1): en az tank hacminin 1/3'ü"),
        Alan("yagli_trafo_var", "Yağlı tip trafo var mı?", "evet", "Kuru tip trafo ise 'Hayır'.", kim="V", kaynak="Elektrik projesi", madde="Madde 65"),
        Alan("jenerator_var", "Jeneratör var mı?", "evet", "", kim="V", kaynak="Elektrik projesi", madde="Madde 66"),
        Alan("lpg_tup_kg", "LPG tüp deposu toplam miktarı (bina dışı)", "sayi", "Depolanan tüplerdeki toplam LPG kütlesi. Yoksa 0.", "kg", "LPG depo ruhsatı", kim="V", madde="Madde 106-107, Ek-9"),
        Alan("lpg_tank_m3", "Dökme LPG tankı beher tank su hacmi", "sayi", "Tank etiketindeki su hacmi. Yoksa 0.", "m³", "Tank etiketi/ruhsat", kim="V", madde="Ek-10"),
        Alan("lpg_tank_tur", "LPG tankı türü", "secim", "Yerüstü veya gömülü.", kim="V", madde="Ek-10", secenek=E.LPG_TUR),
        Alan("lpg_duvar_4saat", "Tank ile komşu arsa arasında ≥1,5 m yüksekliğinde, 4 saat yangına dayanıklı duvar var mı?", "evet", "", kim="V", madde="Ek-10 not (c): mesafeler 1/3 azalır"),
        Alan("lpg_alt_yalitim_2saat", "Tankın alt yüzeyi 2 saat yangına dayanıklı yalıtımlı mı?", "evet", "", kim="V", madde="Ek-10 not (d)"),
        Alan("sivi_depolama_yeri", "Yanıcı sıvı depolama yeri", "secim", "Bina içi zemin/üstü depo hacmi mi, açıkta mı?", kim="V", madde="Madde 114, Ek-11", secenek=E.SIVI_YER),
        Alan("sivi_depo_alani_m2", "Fabrika içindeki tecrit edilmiş yanıcı sıvı deposunun alanı", "sayi", "Üretim alanından yangına dayanıklı duvarla ayrılmış depo odası. Yoksa 0.", "m²", "Mimari plan", kim="V", madde="Madde 118(3), Ek-12/B"),
        Alan("sivi_depo_dayanim_dk", "Bu depo odasının yangın dayanımı", "sayi", "Duvar/döşeme dayanım süresi (60 veya 120 dk).", "dk", "Yangın projesi", kim="V", madde="Ek-12/B"),
        Alan("sivi_depo_yangin_korunum", "Bu depoda yangın korunumu (sprinkler, CO₂, kuru kimyevi toz) var mı?", "evet", "", kim="V", madde="Ek-12/B"),
        Alan("sivi_depo_orijinal_kap", "Yanıcı sıvılar orijinal ambalajında mı depolanıyor?", "evet", "Hayır: taşınabilir tanklar (IBC vb.).", kim="V", madde="Ek-12/A"),
    ]),
    Sayfa("6_Cevre_Erisim", "6. Çevre, itfaiye erişimi ve orman", "Tesisin çevresi ve itfaiyenin ulaşımı. Ölçümler vaziyet planından alınır.", program_sekmesi="Çevre ve ekipler", alanlar=[
        Alan("itfaiye_son_nokta_mesafe_m", "İtfaiye aracının girebildiği son noktadan binanın en uzak cephesine yatay mesafe", "sayi", "", "m", "Vaziyet planı", madde="Madde 22(2): en çok 45 m", ornek="30"),
        Alan("ic_yol_genislik_m", "Tesis içi itfaiye yolu genişliği", "sayi", "", "m", "Vaziyet planı", madde="Madde 22(3): en az 4 m (çıkmazda 8 m)", ornek="6"),
        Alan("ic_yol_cikmaz", "Yol çıkmaz mı?", "evet", "Araç dönüş yapmadan geri çıkmak zorunda kalıyorsa 'Evet'.", madde="Madde 22(3)"),
        Alan("ic_yol_ic_yaricap_m", "Yol dönemecinin iç yarıçapı", "sayi", "", "m", "Vaziyet planı", kim="V", madde="Madde 22(3): en az 11 m", ornek="12"),
        Alan("ic_yol_dis_yaricap_m", "Yol dönemecinin dış yarıçapı", "sayi", "", "m", "Vaziyet planı", kim="V", madde="Madde 22(3): en az 15 m", ornek="16"),
        Alan("ic_yol_egim_yuzde", "Yolun en büyük boyuna eğimi", "sayi", "", "%", "Vaziyet planı / aplikasyon", kim="V", madde="Madde 22(3): en çok %6", ornek="4"),
        Alan("ic_yol_serbest_yukseklik_m", "Yol üzerindeki en düşük serbest yükseklik", "sayi", "Kapı, kanopi, boru köprüsü altı.", "m", "Yerinde ölçüm", kim="V", madde="Madde 22(3): en az 4 m", ornek="4,5"),
        Alan("ic_yol_tasima_yuku_ton", "Yolun taşıma yükü", "sayi", "İtfaiye aracı için dayanım.", "ton", "Zemin/kaplama projesi", kim="V", madde="Madde 22(3): en az 15 ton", ornek="20"),
        Alan("orman_yakin", "Tesis orman alanı içinde veya bitişiğinde mi?", "evet", "Orman bölge müdürlüğü sınırına yakınlık (yaklaşık 300 m içinde).", kaynak="İmar durumu / orman sınır haritası", madde="Madde 7(12), 21(5), 22(5), 27(4), 92(7), 95(7)"),
        Alan("arazi_egimi_yuzde", "Arazi eğimi", "sayi", "Orman alanına yakınsa binaya göre ortalama arazi eğimi.", "%", "Topoğrafik harita", kim="V", madde="Madde 21(5): eğimle dış yangın bölgesi mesafesi"),
    ]),
    Sayfa("7_Yapi_Elemanlari", "7. Taşıyıcı eleman detayları (isteğe bağlı)", "Yalnızca statik projede bulunuyorsa doldurun. Mühendis kontrol amaçlı kullanır.", program_sekmesi="Genel — Betonarme / ahşap", alanlar=[
        Alan("net_beton_kolon_mm", "Kolon net beton paspayı", "sayi", "En dış donatı yüzü ile beton yüzeyi arası.", "mm", "Statik proje / kalıp-donatı planı", kim="M", madde="Madde 23(5): 120 dk için en az 35 mm"),
        Alan("net_beton_kiris_mm", "Kiriş net beton paspayı", "sayi", "", "mm", "Statik proje", kim="M", madde="Madde 23(5): en az 25 mm"),
        Alan("net_beton_doseme_mm", "Döşeme net beton paspayı", "sayi", "", "mm", "Statik proje", kim="M", madde="Madde 23(5): en az 20 mm"),
        Alan("ahsap_b_mm", "Ahşap taşıyıcı elemanın genişliği (b)", "sayi", "Ahşap kolon/kiriş varsa.", "mm", "Statik proje", kim="M", madde="Madde 23(6)"),
        Alan("ahsap_h_mm", "Ahşap taşıyıcı elemanın yüksekliği (h)", "sayi", "", "mm", "Statik proje", kim="M", madde="Madde 23(6)"),
        Alan("ahsap_yanma_hizi", "Ahşap yanma (kömürleşme) hızı", "sayi", "Yönetmelik: 0,6 – 0,8 mm/dk. Boşsa 0,7.", "mm/dk", "Yönetmelik Madde 23(6)", kim="M", madde="Madde 23(6)"),
        Alan("ahsap_yuzey", "Yangına maruz yüzey sayısı", "tam", "Kolon için 4, üstü kapalı kiriş için 3.", "adet", "Statik proje", kim="M", madde="Madde 23(6)"),
    ]),
]

# ---------------------------------------------------------------------------
# Tablo sayfaları
# ---------------------------------------------------------------------------
@dataclass
class TabloSayfa:
    ad: str
    baslik: str
    giris: str
    anahtar: str                       # etiketler.TABLOLAR anahtarı
    aciklamalar: dict[str, str]
    ornek: dict
    program_sekmesi: str = ""
    kim: str = "Z"
    kaynak: str = ""
    satir: int = 40


TABLO_SAYFALARI: list[TabloSayfa] = [
    TabloSayfa("T1_Mahaller", "Tablo 1 — Mahaller (kullanıcı yükü)",
               "Her katın bölümlerini (üretim holü, depo, ofis, yemekhane ...) ayrı satıra yazın. Program bu alanlardan binadaki kişi sayısını ve gerekli çıkış genişliğini hesaplar.",
               "mahal", {
                   "kat": "Katın adı. Tablo 2'deki kat adıyla AYNI yazın (Zemin kat, 1. kat gibi).",
                   "mahal": "Bölümün adı.",
                   "tur": "Bölümün işlevine en yakın türü açılır listeden seçin (kullanıcı yükü katsayısını belirler).",
                   "alan": "Bölümün alanı (m²). Yemekhane, toplantı salonu, sergi gibi türlerde NET alan; diğerlerinde BRÜT alan yazın.",
                   "ozel": "Listede uygun tür yoksa 'Diğer / özel katsayı' seçin ve m²/kişi değerini buraya yazın. Aksi halde boş bırakın.",
                   "belirli": "Bölümde aynı anda bulunan kişi sayısı kesin biliniyorsa (ör. hat başında 40 kişi) yazın. Hesaplanan değerden az olamaz.",
                   "sayilir": "Bölümde bulunanlar aynı anda kullanılmıyorsa (tuvalet, soyunma, aynı katta bakım odası) 'Hayır' yazın.",
               },
               {"kat": "Zemin kat", "mahal": "Üretim holü", "tur": E.EK5A_AD[0], "alan": 4800, "ozel": "", "belirli": "", "sayilir": "Evet"},
               program_sekmesi="Kullanıcı yükü ve kaçış → Mahaller", kaynak="Mimari kat planları, yerleşim (layout) planı"),
    TabloSayfa("T2_Katlar", "Tablo 2 — Katlardaki çıkışlar ve kaçış mesafeleri",
               "Her kat için bir satır. Çıkış kapıları ve merdivenleri, en uzak noktadan çıkışa mesafe gibi ölçümler. Ölçümleri yangın tahliye planı üzerinden yapın.",
               "kat", {
                   "kat": "Katın adı. Tablo 1'deki kat adıyla AYNI yazın.",
                   "cikis": "O kattaki toplam kaçış çıkışı sayısı (dışarı açılan kapılar veya kaçış merdivenleri).",
                   "tur": "Kontrol etmek istediğiniz çıkış türü: zemin/tek katlı hallerde 'Dışarı çıkış kapısı', üst katlarda 'Kaçış merdiveni'.",
                   "genislik": "Seçtiğiniz türdeki çıkışların TOPLAM temiz genişliği (cm). Temiz genişlik: kapı kanadı 90° açıkken kullanılabilir boşluk.",
                   "tekil": "O türdeki en dar tekil çıkışın temiz genişliği (cm).",
                   "yon": "Çalışan bir yönde mi (tek yön) yoksa iki farklı yönde kaçabiliyor mu (iki yön)?",
                   "mesafe": "Katın en uzak noktasından en yakın çıkışa yürüme mesafesi (m). Duvarlardan 40 cm içeride, kaçış yolu boyunca ölçülür.",
                   "kus": "Aynı noktadan en yakın çıkışa kuş uçuşu (düz çizgi) mesafe (m). Bilmiyorsanız boş bırakın.",
                   "cikmaz": "Varsa çıkmaz koridorun uzunluğu (m).",
                   "diyagonal": "İki çıkışlı büyük tek mekânda mekânın köşegen uzunluğu (m). Bilmiyorsanız boş bırakın.",
                   "arasi": "Aynı mekândaki iki çıkış arasındaki mesafe (m).",
               },
               {"kat": "Zemin kat", "cikis": 4, "tur": E.CIKIS_TURLERI["dis_kapi"], "genislik": 480, "tekil": 120, "yon": E.YONLER["iki"], "mesafe": 70, "kus": "", "cikmaz": 12, "diyagonal": 130, "arasi": 60},
               program_sekmesi="Kullanıcı yükü ve kaçış → Kat kaçış verileri", kaynak="Yangın tahliye planı, mimari plan, yerinde ölçüm"),
    TabloSayfa("T3_Merdivenler", "Tablo 3 — Kaçış merdivenleri",
               "Her kaçış (yangın) merdiveni için bir satır. Merdiven yoksa (tek katlı fabrika) boş bırakın.", "merdiven", {
                   "ad": "Merdivenin adı (KM-1, KM-2 ...).", "gen": "Merdivenin temiz genişliği (cm).", "riht": "Basamak yüksekliği (rıht), mm. En çok 175.",
                   "basis": "Basamak genişliği (basış), mm. En az 250.", "sbasamak": "İki sahanlık arasındaki basamak sayısı (4–17).", "skot": "İki sahanlık arasındaki kot farkı (cm). En çok 300.",
                   "bas": "Basamak üzerinden tavana baş yüksekliği (cm). En az 210.", "kat": "Merdivenin hizmet verdiği kat sayısı (bodrum dahil).",
                   "kapi": "Merdiven kapısının yangın dayanım süresi (dk) — kapı etiketi/test belgesi.", "duvar": "Merdiven yuvası duvarlarının yangın dayanımı (dk).",
                   "kullanici": "O katta merdivenin hizmet verdiği kullanıcı sayısı.", "dengeli": "Kova hattı dar basamaklı (dengelenmiş) merdiven mi?",
               },
               {"ad": "KM-1", "gen": 150, "riht": 170, "basis": 280, "sbasamak": 10, "skot": 260, "bas": 230, "kat": 2, "kapi": 60, "duvar": 120, "kullanici": 100, "dengeli": "Hayır"},
               program_sekmesi="Merdiven, kapı, duman, tank → Kaçış merdivenleri", kaynak="Mimari proje, yerinde ölçüm, kapı etiketi"),
    TabloSayfa("T4_Kapilar", "Tablo 4 — Kaçış yolu kapıları",
               "Başlıca çıkış kapıları için bir satır (özellikle çok kişinin kullandığı çıkışlar).", "kapi", {
                   "ad": "Kapının adı/numarası.", "gen": "Temiz genişlik (cm): kanat 90° açıkken. Tek kanatlı 80–120 cm.", "yuk": "Kapı yüksekliği (cm). En az 200.",
                   "kanat": "Kanat sayısı (1 veya 2).", "kisi": "Kapının hizmet verdiği mekândaki toplam kişi sayısı.", "yone": "Kapı kaçış yönüne (dışarı) açılıyor mu? 50 kişiden fazla mekânlarda zorunlu.",
                   "esik": "Kapıda eşik (basamak/çıta) var mı?", "kuvvet": "Kapıyı açmak için gereken kuvvet (N). En çok 110 N. Bilmiyorsanız boş bırakın.",
               },
               {"ad": "Ana çıkış", "gen": 200, "yuk": 210, "kanat": 2, "kisi": 300, "yone": "Evet", "esik": "Hayır", "kuvvet": ""},
               program_sekmesi="Merdiven, kapı, duman, tank → Kapılar", kaynak="Yerinde ölçüm"),
    TabloSayfa("T5_Duman_Mahalleri", "Tablo 5 — Mekanik duman tahliyesi gereken mahaller",
               "Kazan dairesi, kapalı otopark ve bodrum depolar için. Yoksa boş bırakın.", "duman", {
                   "ad": "Mahalin adı.", "tur": "kazan, otopark, bodrum_depo veya diger.", "alan": "Mahalin alanı (m²). 2000 m²'yi aşarsa mekanik duman tahliyesi gerekir.", "yuk": "Tavan yüksekliği (m).",
               },
               {"ad": "Kapalı otopark", "tur": "otopark", "alan": 2200, "yuk": 3},
               program_sekmesi="Merdiven, kapı, duman, tank → Mekanik duman tahliyesi", kim="V", kaynak="Mimari plan"),
    TabloSayfa("T6_Yanici_Sivi", "Tablo 6 — Yanıcı / parlayıcı sıvı tankları ve depolama",
               "Tiner, solvent, boya, akaryakıt, kimyasal vb. sıvıların tankları veya depo bölümleri. Yoksa boş bırakın. Sınıfı bilmiyorsanız parlama noktasını (MSDS 9. bölüm) yazıp mühendise danışın.", "tank", {
                   "ad": "Tank veya depo adı.",
                   "sinif": "Parlama noktasına göre sınıf: IA (<22,8 °C ve kaynama <37,8 °C), IB (<22,8 °C), IC (22,8–37,8 °C), II (37,8–60 °C), IIIA (60–93 °C), IIIB (>93 °C).",
                   "hacim": "Toplam hacim (litre).",
                   "tur": "yerustu = açıkta yer üstü tank, yeralti = gömülü tank, depo_icinde = depo binası/odası içinde.",
               },
               {"ad": "Tiner tankı", "sinif": "IB", "hacim": 2000, "tur": "yerustu"},
               program_sekmesi="Merdiven, kapı, duman, tank → Yanıcı sıvı tankları", kim="V", kaynak="MSDS, tank etiketi, depo ruhsatı"),
]

# ---------------------------------------------------------------------------
# Belge listesi (işverenden istenecek dokümanlar)
# ---------------------------------------------------------------------------
BELGELER: list[tuple[str, str, str, str]] = [
    ("Yapı ruhsatı ve yapı kullanma izin belgesi (iskân)", "Kullanım sınıfı, kat sayısı, alanlar, yapının yeni/mevcut olduğu", "Belediye / işveren", "Zorunlu"),
    ("Mimari proje (vaziyet planı, kat planları, kesitler, cepheler)", "Tüm ölçüler, çıkışlar, kaçış yolları, mahal alanları, bina ve yol ölçüleri", "Proje müellifi / işveren", "Zorunlu"),
    ("Yangın tahliye planı", "Kaçış yolları, çıkışlar, yangın dolapları, butonlar, söndürücüler, toplanma yeri", "İSG / işveren", "Zorunlu"),
    ("Üretim akışı ve kullanılan/depolanan maddelerin listesi (kapasite, miktarlar)", "Tehlike sınıfı, yanıcı madde varlığı", "İşveren / üretim müdürü", "Zorunlu"),
    ("Güvenlik bilgi formları (MSDS/SDS) — yanıcı, parlayıcı, patlayıcı maddeler", "Parlama noktası, sıvı sınıfı, depolama miktar ve koşulları", "Tedarikçi / işveren", "Varsa"),
    ("Statik proje ve taşıyıcı sistem bilgisi (beton paspayı, çelik koruma)", "Yapı elemanlarının yangın dayanımı kontrolü", "Statik proje müellifi", "Varsa"),
    ("Sprinkler (yağmurlama) projesi ve hidrolik hesap raporu", "Tasarım yoğunluğu, koruma alanı, kritik hat kaybı, su ihtiyacı", "Mekanik taahhüt/montaj firması", "Varsa"),
    ("Yangın pompası etiketi ve karakteristik eğrisi, pompa odası projesi", "Anma debi/basma, kapalı vana, %150 debi kontrolleri; yedek pompa", "Pompa üreticisi / montaj firması", "Varsa"),
    ("Yangın suyu deposu bilgisi (hacim, yalnız yangına ayrılmış rezerv)", "Gerekli su deposu hacmiyle karşılaştırma", "Mekanik proje", "Varsa"),
    ("Yangın alarm / algılama sistemi projesi ve bakım raporları", "Algılama, buton ve alarm sistemi varlığı ve kapsamı", "Elektrik taahhüt/bakım firması", "Varsa"),
    ("Duman tahliye projesi / hesabı", "Kompartıman sınırlarının değerlendirilmesi", "Mekanik proje", "Varsa"),
    ("Acil aydınlatma ve yönlendirme projesi, aydınlık ölçüm (lux) raporu", "Süre, aydınlık seviyesi ve oran kontrolleri", "Elektrik proje / ölçüm firması", "Varsa"),
    ("Kazan dairesi, yakıt tankı, trafo, jeneratör bilgileri / projesi", "Kazan, yakıt ve enerji odası kontrolleri", "Mekanik/elektrik proje", "Varsa"),
    ("LPG tank/tüp depo ruhsatı ve yerleşimi; yanıcı sıvı depo/tank bilgileri", "Emniyet mesafeleri, miktar eşikleri, havuzlama", "İşveren / ruhsat veren kurum", "Varsa"),
    ("İtfaiye raporları / önceki denetim tutanakları", "Mevcut uygunsuzluklar, itfaiye görüşü", "Belediye itfaiyesi / işveren", "Varsa"),
    ("Orman sınırına yakınlık bilgisi (imar durumu, orman bölge müdürlüğü yazısı)", "Orman alanındaki endüstriyel tesis ilave tedbirleri", "Belediye / orman işletme", "Varsa"),
    ("Vardiya çizelgesi ve çalışan sayıları", "Kullanıcı yükü, acil durum ekipleri", "İnsan kaynakları", "Zorunlu"),
]

TUM_ALANLAR: list[Alan] = [a for s in SAYFALAR for a in s.alanlar]


def kapsam_kontrol() -> list[str]:
    """Girdi'deki tüm basit alanların formda bulunduğunu doğrular; eksik alan adlarını döndürür."""
    import dataclasses
    from .modeller import Girdi
    liste = {"katlar", "merdivenler", "kapilar", "duman_mahalleri", "sivi_tanklar"}
    formda = {a.alan for a in TUM_ALANLAR if a.alan}
    return [f.name for f in dataclasses.fields(Girdi) if f.name not in liste and f.name not in formda]
