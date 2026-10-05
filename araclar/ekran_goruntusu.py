"""Kılavuz için masaüstü arayüzünün ekran görüntülerini alır (Linux + Xvfb + Pillow gerekir).

Kullanım:  xvfb-run -a -s "-screen 0 1400x900x24" python araclar/ekran_goruntusu.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PIL import ImageGrab  # noqa: E402

import masaustu as M  # noqa: E402
from yangin.ornek import ornek_fabrika  # noqa: E402

HEDEF = os.path.join(os.path.dirname(__file__), "..", "belgeler", "ekran")
os.makedirs(HEDEF, exist_ok=True)
app = M.Uygulama()
app.geometry("1280x800+0+0")
app.yukle_girdi(ornek_fabrika())
app.update()


def cek(ad):
    app.update_idletasks()
    app.update()
    ImageGrab.grab(bbox=(0, 0, 1280, 800)).save(os.path.join(HEDEF, ad + ".png"))


sekmeler = {app.defter.tab(i, "text"): i for i in range(app.defter.index("end"))}
for ad, dosya in (("Genel", "01_genel"), ("Su ve söndürme", "02_su"), ("Algılama, duman, aydınlatma", "03_algilama"), ("Kazan ve tehlikeli madde", "04_kazan"),
                  ("Çevre ve ekipler", "05_cevre"), ("Kullanıcı yükü ve kaçış", "06_kacis"), ("Merdiven, kapı, duman, tank", "07_merdiven")):
    app.defter.select(sekmeler[ad])
    cek(dosya)
app.hesapla()
cek("08_sonuclar")
app.filtre.set("Uygun değil")
app._sonuc_goster()
cek("09_uygun_degil")
app.destroy()
print("ekran görüntüleri:", sorted(os.listdir(HEDEF)))
