"""Mevzuat ipuçları: madde metinleri doğru alana bağlanıyor mu?"""
import pytest

from yangin import alanlar as A
from yangin import mevzuat as V
from yangin import mevzuat_metin as M


def test_madde_sayisi_ve_basliklar():
    assert len(M.MADDE) >= 170
    assert M.BASLIK["33"] == "Kaçış yolu sayısı ve genişliği"
    assert M.BASLIK["23"] == "Bina taşıyıcı sistemi stabilitesi"


def test_fikra_alintisi():
    a = V.madde_alinti("33", "1")
    assert a.startswith("Madde 33") and "Toplam çıkış genişliği" in a
    assert "120 cm" in V.madde_alinti("33", "2")


def test_tanim_bendi():
    assert "toplam yüksekliğini" in V.madde_alinti("4", "bbb")
    assert "21.50" in V.madde_alinti("4", "ccc")


def test_referans_ayiklama():
    madde, ek = V._ref_ayikla("Madde 33(1)-(2), 52 — açıklama 30,50 m")
    assert ("33", "1") in madde and ("33", "2") in madde and ("52", None) in madde
    assert all(no != "30" for no, _ in madde)         # "30,50" madde sayılmamalı
    _, ek = V._ref_ayikla("Madde 7(4), Ek-5/B dipnotu, Ek-4")
    assert ek == ["Ek-5/B", "Ek-4"]


def test_her_alan_icin_mevzuat_alintisi_var():
    bos = [a.alan for a in A.TUM_ALANLAR if a.alan and a.madde and not V.mevzuat_alintilari(a.madde)]
    assert bos == []


def test_ipucu_icerigi():
    b = V.ipucu_bolumleri("kat_sayisi")
    stiller = [s for s, _ in b]
    assert stiller[0] == "baslik" and "mevzuat" in stiller
    assert any("Ek-4" in m for s, m in b if s == "mevzuat")


@pytest.mark.parametrize("tablo,kolon", [("kat", "genislik"), ("merdiven", "riht"), ("kapi", "kuvvet"), ("duman", "alan"), ("mahal", "tur")])
def test_tablo_ipucu(tablo, kolon):
    b = V.tablo_ipucu_bolumleri(tablo, kolon)
    assert b and any(s == "mevzuat" for s, _ in b)


def test_sonuc_ipucu_ve_duz_metin():
    b = V.sonuc_ipucu_bolumleri("Merdiven", "Madde 41(7)", "En çok 175 mm.")
    assert "175" in V.duz_metin(b)
