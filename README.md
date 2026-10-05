# Yangın Koruma Hesap Uygulaması

**Binaların Yangından Korunması Hakkında Yönetmelik** (RG 19.12.2007/26735; 20.11.2021 tarihli 4825 sayılı Cumhurbaşkanı Kararı ile değişik) ve **Yönetmelik Kılavuzu (Aralık 2024)** esas alınarak, özellikle **fabrika / endüstriyel yapılar** için yönetmelikteki sayısal hesapları ve kontrolleri yapan, sonucu **Excel (.xlsx)** ve **Word (.docx)** raporu olarak veren uygulama.

Her satır, dayandığı **madde / ek numarasıyla** raporlanır ve bir durum alır:
`UYGUN`, `UYGUN DEĞİL`, `GEREKLİ` (yapılması zorunlu önlem), `KOŞULLU UYGUN`, `VERİ GİRİLMEDİ`, `GEREKMEZ`, `BİLGİ`.

## Windows .exe (kurulum gerektirmez)

Masaüstü arayüzlü sürüm `masaustu.py` dosyasıdır. GitHub Actions her güncellemede Windows için `YanginHesap.exe` derler ve
**Releases → "YanginHesap.exe (Windows)"** sayfasında yayınlar. İndirip çift tıklamanız yeterlidir (Python gerekmez).
Windows "bilinmeyen yayıncı" uyarısı verirse *Ek bilgi → Yine de çalıştır* seçin (exe dijital olarak imzalı değildir).

Kendiniz derlemek isterseniz (Windows'ta): `pip install -r requirements-exe.txt` ardından
`pyinstaller --noconfirm --onefile --windowed --name YanginHesap --collect-data docx --collect-data openpyxl masaustu.py`

## İşveren veri toplama formu ve kullanım kılavuzu

* `belgeler/Isveren_Veri_Toplama_Formu.xlsx` — işverene gönderilecek Excel formu (102 soru, açılır listeler, "kim doldurur" etiketi, belge kontrol listesi, 6 tablo). Programdaki **Boş işveren formu** düğmesi de aynısını üretir.
* `belgeler/Ornek_Doldurulmus_Form.xlsx` — örnek fabrikayla doldurulmuş form (nasıl doldurulacağını gösterir).
* `belgeler/Kullanim_Kilavuzu.docx` — ayrıntılı kullanım kılavuzu (kurulum, form, alan alan açıklama, sonuçların okunması, formüller, çözümlü örnek, SSS).
* Doldurulmuş form, programda **Formu içe aktar** ile tek tıkla alınır; eksik zorunlu bilgiler ve hatalı değerler listelenir.
* Belgeler `python araclar/belge_uret.py` ile yeniden üretilir (alan tanımları `yangin/alanlar.py` içindedir; form, aktarma ve kılavuz aynı kaynaktan beslenir).

## Kurulum ve çalıştırma (web arayüzü)

| Sistem | Yol |
|---|---|
| Windows | `calistir.bat` dosyasına çift tıklayın (Python kurulu olmalı: <https://www.python.org/downloads/>, kurulumda *Add Python to PATH* seçin). |
| Linux / macOS | `./calistir.sh` |
| Elle | `pip install -r requirements.txt` ardından `streamlit run app.py` |

Tarayıcıda otomatik açılır (genellikle <http://localhost:8501>).

**Kullanım:** soldaki *Örnek fabrika yükle* ile örneği inceleyin → sekmeleri doldurun → *8 Sonuçlar ve Rapor* sekmesinden Excel/Word raporunu indirin. *Projeyi kaydet (.json)* ile girdileri saklayıp sonra yeniden açabilirsiniz.

## Hesaplanan / kontrol edilen konular

| # | Konu | Dayanak |
|---|---|---|
| 1 | Kullanım sınıfı, tehlike sınıfı (Ek-1/A-B-C listesinden öneri), yüksek bina, tahliye projesi, orman alanı kapsamı | Md 4, 7, 8, 14, 17–19 |
| 2 | Yangın dayanım süreleri (kullanım sınıfı × yağmurlama × yükseklik × bodrum derinliği), çelik yalıtım, beton paspayı, ahşap kalan kesit, cephe/çatı, yapı elemanları tablosu | Md 23–28, Ek-3/B, Ek-3/C |
| 3 | En fazla kompartıman alanı ve dipnot kuralları (kontrol sistemi, tek katlı), gerekli kompartıman sayısı | Md 24, Ek-4 |
| 4 | Kullanıcı yükü, gerekli çıkış genişliği (kapı/merdiven/koridor), asgari tekil genişlik, çıkış sayısı, tek çıkış istisnası, kaçış uzaklığı (tek/iki yön, kuş uçuşu, çıkmaz koridor, çıkışlar arası mesafe) | Md 31–33, 39, 52, Ek-5/A, Ek-5/B, Ek-14 |
| 5 | Kaçış merdiveni (rıht, basış, sahanlık, baş yüksekliği, kapı/duvar dayanımı), kapılar | Md 38–47 |
| 6 | Yağmurlama zorunluluğu, tasarım yoğunluğu × koruma alanı = debi, yaklaşık başlık adedi, yedek başlık | Md 96, Ek-8/B |
| 7 | Yangın suyu deposu (Md 92(5) usulü ve Ek-8/A tablosu), toplam debi, pompa debisi/basma yüksekliği (Hy), pompa karakteristik kontrolleri, yedek pompa | Md 92–93, Ek-8/A-B-C |
| 8 | Yangın dolabı zorunluluğu/adedi/tipi, itfaiye su alma ağzı ve su verme bağlantısı, dış hidrant zorunluluğu/adedi, taşınabilir söndürücü adedi | Md 94–97, 99 |
| 9 | Otomatik algılama, yangın butonu adedi, acil aydınlatma süresi/seviyeleri, yönlendirme işareti görülebilirlik uzaklığı ve adedi | Md 70–75, 81, Ek-7 |
| 10 | Mekanik duman tahliyesi (10 hava değişimi/saat → m³/h), kaçış merdiveni basınçlandırma zorunluluğu ve asgari hava debisi | Md 85–89 |
| 11 | Kazan dairesi çıkış sayısı, yakıt depolama limitleri ve havuzlama, trafo/jeneratör odası | Md 54–56, 65–66 |
| 12 | LPG emniyet uzaklıkları (tüp, dökme tank, duvar/yalıtım azaltması), yanıcı sıvı: IA eşdeğeri, bildirim/izin, depo içi limitler, tank mesafeleri, havuzlama | Md 106–122, Ek-9…Ek-12 |
| 13 | İtfaiye erişimi (45 m, yol genişlik/yarıçap/eğim/yükseklik/taşıma yükü), orman alanında dış yangın bölgesi (eğime göre) | Md 21–22 |
| 14 | Acil durum ekipleri ve asgari personel, tatbikat | Md 124–129 |

## Doğrulama

* Tablolar (Ek-1, 3/C, 4, 5/A, 5/B, 7, 8, 9–12) PDF'teki tablo görüntüleriyle karşılaştırılarak girilmiştir. Metin çıkarımında satırı kaydıran tablolar (ör. Ek-3/C Büro satırı, Ek-8/A birleşik hücreler) görselden düzeltilmiştir.
* `tests/` altındaki testler Kılavuzdaki çözümlü örnekleri üretir: yangın suyu deposu **79,2 m³** (43,2 + 12 + 24), pompa **79,2 m³/h**, Hy ≈ **96 mSS**; büro katı çıkış genişliği **168,87 cm** (merdiven) ve **101,32 cm** (koridor).

```
pip install -r requirements-dev.txt
python -m pytest -q
```

## Sınırlar ve bilinmesi gerekenler

* Uygulama yönetmeliğin **sayısal kriterlerini** ve **zorunluluk koşullarını** hesaplar. Boru çapı/hidrolik hesabı, yapısal yangın analizi, duman tahliye hacim hesabı (yönetmelik sayısal debi vermez, standartlara atıf yapar), sızıntı alanlarından basınçlandırma debisi gibi **standart tabanlı detay tasarımlar kapsam dışıdır**; ilgili satırlarda bu açıkça belirtilir.
* **Ön hesap niteliğindeki** değerler: yaklaşık başlık, dolap, hidrant, buton ve söndürücü adetleri. Bunlar yönetmelikteki azami uzaklık/alan kriterlerinden ızgara kapsamasıyla türetilir; kesin yerleşim proje çizimiyle yapılır.
* **Yönetmelikte olmayıp varsayım gerektiren** girdiler uygulamada ayrı gösterilir: hidrant bölge riski (Md 95(3) tehlike sınıfıyla eşleştirme vermez), OT-2 ve üzeri için başlık başına koruma alanı (TS EN 12845: 12 m² / 9 m²), eş zamanlı dolap sayısı (Kılavuz örneği 2).
* **Ek-7** tablosunun endüstriyel, ticaret, kurum ve toplanma amaçlı yapılara ilişkin kısımları Danıştay kararıyla iptal edilmiştir (E.2019/261, K.2021/5537; İDDK onama 22/2/2023). Uygulama bu hali esas alır; fabrikalar için algılama zorunluluğu Ek-7'den değil, tehlikeli madde varlığı (Md 81), kompartıman dipnotları (Ek-4) ve itfaiye görüşünden doğar.
* **Mevcut yapılar** (Onuncu Kısım, Md 138–167) için yalnızca Ek-14 kaçış uzaklığı çarpanı uygulanır; mevcut yapı uyum hükümleri ayrıca değerlendirilmelidir.
* Rapor, projenin onayı veya itfaiye görüşünün yerine geçmez. Kılavuzda belirtildiği gibi mevzuatla çelişme halinde **yürürlükteki mevzuat geçerlidir**; yönetmelik değiştikçe `yangin/tablolar.py` güncellenmelidir.

## Dosya yapısı

```
app.py                  Streamlit (web) arayüzü
masaustu.py             Tkinter masaüstü arayüzü (.exe bundan derlenir)
yangin/tablolar.py      Yönetmelik ekleri (tablolar)
yangin/modeller.py      Girdi ve sonuç modelleri
yangin/hesaplar.py      Hesap modülleri (her biri madde numarasına bağlı)
yangin/rapor.py         Excel ve Word rapor üreticileri
yangin/ornek.py         Örnek fabrika projesi
yangin/alanlar.py       Form/kılavuz alan tanımları (işveren dilinde açıklamalar)
yangin/form.py          İşveren formu üretimi ve içe aktarma
yangin/kilavuz.py       Kullanım kılavuzu üretimi
araclar/                Belge ve ekran görüntüsü üreten betikler
belgeler/               Hazır form ve kılavuz
tests/                  Kılavuz örnekleriyle doğrulama testleri
```
