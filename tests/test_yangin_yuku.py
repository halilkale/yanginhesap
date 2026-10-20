"""Yangın yükü: bölüm bazında q = Σ(m·H)/A ve Ek-4 bölüm alanı kontrolü."""
import pytest

from yangin import dokum as D
from yangin import form as F
from yangin import hesaplar as H
from yangin.modeller import Girdi, YanginYukuBolum, YanginYukuKalem
from araclar.tanyeri_proje import proje


def bul(S, bolum, kalem):
    return next(r for r in S if bolum in r.bolum and kalem in r.kalem)


def test_depo_alt_formul():
    S = H.hesapla(proje())
    r = bul(S, "Depo alt", "Yangın yükü")
    # (300+500)·43 + 250·17,5 = 38 775 MJ ; alan 974,18 m²
    assert r.deger == pytest.approx(38775 / 974.18, abs=0.05)
    assert "38.775 MJ" in r.aciklama.replace(",", ".") or "38,775" in r.aciklama


def test_ek4_depo_siniri_1000():
    S = H.hesapla(proje())
    assert bul(S, "Depo alt", "Ek-4").durum == "UYGUN"          # 974,18 ≤ 1000
    assert bul(S, "Depo üst", "Ek-4").durum == "UYGUN DEĞİL"    # 1403,38 > 1000 (depo, OT-3)
    assert bul(S, "Enjeksiyon", "Ek-4").durum == "UYGUN"        # endüstriyel 6000


def test_kontrol_sistemi_depoyu_sinirsiz_yapar():
    g = proje()
    g.yagmurlama_var = True
    assert bul(H.hesapla(g), "Depo üst", "Ek-4").durum == "KOŞULLU UYGUN"


def test_eksik_veri_uyarilari():
    g = Girdi()
    g.yangin_yuku_bolumleri = [YanginYukuBolum("A", 0)]
    g.yangin_yuku_kalemleri = [YanginYukuKalem("B", "Ahşap (palet, kereste, kontrplak)", 10)]
    S = [r for r in H.yangin_yuku(g)]
    assert any(r.durum == "VERİ GİRİLMEDİ" for r in S) and len(S) >= 2


def test_dokum_ve_form_gidis_donus():
    g = proje()
    b = {x.baslik: x for bo in D.hesap_dokumu(g) for x in bo.bloklar}
    assert any("38.775 MJ" in a for a in b["Yangın yükü — Depo alt"].adimlar)
    g2, uyari, _ = F.formdan_oku(F.doldurulmus_form(g))
    assert len(g2.yangin_yuku_bolumleri) == 6 and len(g2.yangin_yuku_kalemleri) == 13
    assert g2.yangin_yuku_bolumleri[0].kullanim == "depo"
    assert all("Yangın_Yuku" not in u for u in uyari)
