"""Yönetmelik PDF'inden madde metinlerini ayıklayıp yangin/mevzuat_metin.py dosyasını üretir.

Kullanım:  python araclar/mevzuat_cikar.py "21.5.2007129).pdf"
(pdftotext komutu gerekir; çıktı depoya işlenir, uygulama çalışırken PDF gerekmez.)
"""
import os
import pprint
import re
import subprocess
import sys

pdf = sys.argv[1] if len(sys.argv) > 1 else "21.5.2007129).pdf"
metin = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout.split("\n")

MADDE_RE = re.compile(r"^\s*(?:MADDE|Madde)\s+(\d+(?:/[A-C])?)\s*[-–]\s*(.*)$")
ETIKET_RE = re.compile(r"\((?:Değişik|Ek|Mülga)[^)]*\)\s*", re.I)
BASLIK_ATLA = re.compile(r"(KISIM|BÖLÜM)\b")

# ek bölümünün başlangıcında dur
son = next(i for i, l in enumerate(metin) if "TARİHLİ VE 2007/12937 SAYILI YÖNETMELİĞE İŞLENEMEYEN" in l)
satirlar = [l.rstrip() for l in metin[:son]]

bloklar: list[tuple[str, list[str]]] = []
for l in satirlar:
    m = MADDE_RE.match(l)
    if m:
        bloklar.append((m.group(1), [m.group(2)]))
    elif bloklar:
        bloklar[-1][1].append(l.strip())

MADDE: dict[str, dict[str, str]] = {}
BASLIK: dict[str, str] = {}
TANIM: dict[str, str] = {}
onceki_baslik = ""
for n, (no, ls) in enumerate(bloklar):
    # dipnot çizgisinden sonrasını at
    kes = next((i for i, l in enumerate(ls) if re.match(r"^[_–—-]{5,}", l)), None)
    if kes is not None:
        # dipnot bölümü sonraki madde başlığına kadar sürer; başlık aranmaz
        ls = ls[:kes]
        sonraki_baslik = ""
    else:
        sonraki_baslik = ""
    # sondaki başlık satırlarını ayır (bir sonraki maddenin başlığı)
    bos_sonrasi = [l for l in ls if l]
    basliklar = []
    while bos_sonrasi and (BASLIK_ATLA.search(bos_sonrasi[-1]) or (len(bos_sonrasi[-1]) < 80 and not re.search(r"[.;:,)]$", bos_sonrasi[-1]) and not re.match(r"^\(?\d+\)", bos_sonrasi[-1]))):
        basliklar.insert(0, bos_sonrasi.pop())
    if no and n + 1 < len(bloklar):
        pass
    govde = [l for l in bos_sonrasi]
    # paragraflara böl
    paragraflar: list[str] = []
    for l in govde:
        l2 = ETIKET_RE.sub("", l).strip()
        if not l2:
            continue
        yeni = re.match(r"^\(\d+\)", l2) or re.match(r"^[a-zçğıöşüA-Z]{1,3}\)\s", l2) or re.match(r"^\d\)\s", l2)
        if yeni or not paragraflar:
            paragraflar.append(l2)
        else:
            paragraflar[-1] += " " + l2
    # fıkralara grupla
    fikralar: dict[str, str] = {}
    mevcut = "_"
    for p in paragraflar:
        m = re.match(r"^\((\d+)\)\s*(.*)$", p)
        if m:
            mevcut = m.group(1)
            fikralar[mevcut] = (fikralar.get(mevcut, "") + " " + m.group(2)).strip().rstrip(",;")
        else:
            fikralar[mevcut] = (fikralar.get(mevcut, "") + "\n" + p).strip()
    if no == "4":
        for p in paragraflar:
            m = re.match(r"^([a-zçğıöşü]{1,3})\)\s*(.*)$", p)
            if m:
                TANIM[m.group(1)] = re.sub(r"[,;]?\s+[a-zçğıöşü]{1,3}\)$", "", m.group(2)).strip()
    MADDE[no] = fikralar
    # bu bloğun sonundaki başlık, bir sonraki maddenin başlığıdır
    if basliklar and n + 1 < len(bloklar):
        saf = [b for b in basliklar if not BASLIK_ATLA.search(b)]
        if saf:
            BASLIK[bloklar[n + 1][0]] = ETIKET_RE.sub("", saf[-1]).strip()      # bölüm adı değil, madde başlığı (son satır)

# 1. maddenin başlığı için ilk satırlardan al
hedef = os.path.join(os.path.dirname(__file__), "..", "yangin", "mevzuat_metin.py")
with open(hedef, "w", encoding="utf-8") as f:
    f.write('"""Yönetmelik madde metinleri (otomatik üretilmiştir: araclar/mevzuat_cikar.py).\n\n'
            'Binaların Yangından Korunması Hakkında Yönetmelik, RG 19.12.2007/26735 (4825 sayılı CK ile değişik).\n'
            'MADDE[no][fıkra] = metin;  BASLIK[no] = madde başlığı;  TANIM[harf] = Madde 4 tanımı.\n"""\n\n')
    f.write("MADDE = " + pprint.pformat(MADDE, width=140, sort_dicts=False) + "\n\n")
    f.write("BASLIK = " + pprint.pformat(BASLIK, width=140, sort_dicts=False) + "\n\n")
    f.write("TANIM = " + pprint.pformat(TANIM, width=140, sort_dicts=False) + "\n")
print("madde:", len(MADDE), "başlık:", len(BASLIK), "tanım:", len(TANIM))
