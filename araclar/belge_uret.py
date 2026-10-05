"""Teslim belgelerini üretir: işveren formu, örnek doldurulmuş form, kullanım kılavuzu.

Kullanım:  python araclar/belge_uret.py
"""
import os
import sys

KOK = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, KOK)
from yangin import form, kilavuz  # noqa: E402
from yangin.ornek import ornek_fabrika  # noqa: E402

HEDEF = os.path.join(KOK, "belgeler")
os.makedirs(HEDEF, exist_ok=True)
for ad, veri in (
    ("Isveren_Veri_Toplama_Formu.xlsx", form.sablon_olustur()),
    ("Ornek_Doldurulmus_Form.xlsx", form.doldurulmus_form(ornek_fabrika())),
    ("Kullanim_Kilavuzu.docx", kilavuz.kilavuz_olustur(os.path.join(HEDEF, "ekran"))),
):
    with open(os.path.join(HEDEF, ad), "wb") as f:
        f.write(veri)
    print("yazıldı:", ad, len(veri) // 1024, "KB")
