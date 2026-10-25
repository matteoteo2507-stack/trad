"""Controllo di completezza delle trascrizioni in analysis/intake/yt_fetch.py (dal 2026-10-25).

Caso reale da cui nasce: il 09/10 i sottotitoli manuali di un video erano tronchi (138 parole su
11 minuti) e lo script li aveva presi in silenzio. Tutto senza rete: le tracce sono finte e una
fixture fa fallire qualsiasi connessione.
"""
from __future__ import annotations

import json
import os
import socket
import sys

import pytest

INTAKE = os.path.join(os.path.dirname(__file__), "..", "analysis", "intake")
sys.path.insert(0, os.path.abspath(INTAKE))

import rule_extract  # noqa: E402
import yt_fetch as yf  # noqa: E402
from youtube_transcript_api import NoTranscriptFound  # noqa: E402

UNDICI_MIN = 11 * 60


@pytest.fixture(autouse=True)
def niente_rete(monkeypatch):
    def vietato(*a, **k):
        raise AssertionError("il test ha provato ad aprire una connessione")
    monkeypatch.setattr(socket.socket, "connect", vietato)


class _Seg:
    def __init__(self, text: str):
        self.text = text


class FakeTranscript:
    """Una traccia finta: `n` parole, spezzate in segmenti con a capo come quelli veri."""

    def __init__(self, n: int, generated: bool, lang: str = "en", errore: Exception | None = None):
        self.n = n
        self.is_generated = generated
        self.language_code = lang
        self.errore = errore
        self.chiamate = 0

    def fetch(self):
        self.chiamate += 1
        if self.errore:
            raise self.errore
        parole = [f"w{i}" for i in range(self.n)]
        return [_Seg("\n".join(parole[i:i + 7])) for i in range(0, self.n, 7)]


class FakeList:
    def __init__(self, manuale: FakeTranscript | None, generata: FakeTranscript | None):
        self.manuale = manuale
        self.generata = generata

    def _o_errore(self, t):
        if t is None:
            raise NoTranscriptFound("vid", yf.LINGUE, "")
        return t

    def find_transcript(self, langs):            # come la libreria: prima la manuale
        return self._o_errore(self.manuale or self.generata)

    def find_manually_created_transcript(self, langs):
        return self._o_errore(self.manuale)

    def find_generated_transcript(self, langs):
        return self._o_errore(self.generata)


class FakeApi:
    def __init__(self, tlist: FakeList):
        self.tlist = tlist

    def list(self, vid):
        return self.tlist


def _fetch(manuale, generata, durata=UNDICI_MIN):
    return yf.fetch_transcript("vid", durata, api=FakeApi(FakeList(manuale, generata)))


# --- soglia ---------------------------------------------------------------------------------

def test_soglia_sta_sotto_il_parlato_normale():
    assert 0 < yf.SOGLIA_PAROLE_MIN < 130


def test_confine_della_soglia():
    s = yf.SOGLIA_PAROLE_MIN
    assert yf.completeness(s) == yf.OK
    assert yf.completeness(s - 0.1) == yf.SOTTO
    assert yf.completeness(None) == yf.IGNOTA


def test_parole_al_minuto_caso_09_10():
    assert yf.words_per_minute(138, UNDICI_MIN) == pytest.approx(12.545, abs=1e-3)
    assert yf.words_per_minute(138, 0) is None
    assert yf.words_per_minute(138, None) is None


# --- scelta della traccia -------------------------------------------------------------------

def test_manuale_completa_non_scarica_la_generata():
    man, gen = FakeTranscript(1500, False), FakeTranscript(1600, True)
    tr = _fetch(man, gen)
    assert (tr.traccia, tr.completezza, tr.provate) == ("manuale", yf.OK, ["manuale"])
    assert tr.parole == 1500
    assert gen.chiamate == 0          # nessuna richiesta in piu' nel caso normale


def test_manuale_tronca_passa_alla_generata():
    man, gen = FakeTranscript(138, False), FakeTranscript(1600, True)
    tr = _fetch(man, gen)
    assert tr.traccia == "generata"
    assert tr.completezza == yf.OK
    assert tr.provate == ["manuale", "generata"]
    assert tr.parole == 1600
    assert "\n" not in tr.text


def test_entrambe_tronche_tiene_la_piu_lunga_e_segnala():
    tr = _fetch(FakeTranscript(138, False), FakeTranscript(100, True))
    assert (tr.traccia, tr.parole, tr.completezza) == ("manuale", 138, yf.SOTTO)
    assert tr.provate == ["manuale", "generata"]


def test_generata_tronca_senza_manuale():
    tr = _fetch(None, FakeTranscript(138, True))
    assert (tr.traccia, tr.completezza, tr.provate) == ("generata", yf.SOTTO, ["generata"])


@pytest.mark.parametrize("durata", [0, None])
def test_durata_ignota_segnala_e_non_blocca(durata):
    gen = FakeTranscript(1600, True)
    tr = _fetch(FakeTranscript(138, False), gen, durata=durata)
    assert tr.completezza == yf.IGNOTA
    assert tr.parole_min is None
    assert gen.chiamate == 0          # senza durata non si puo' dire che sia tronca


def test_errore_sulla_seconda_traccia_risale():
    """Un blocco IP durante il secondo tentativo deve arrivare al backoff di main()."""
    gen = FakeTranscript(1600, True, errore=RuntimeError("HTTP 429"))
    with pytest.raises(RuntimeError, match="429"):
        _fetch(FakeTranscript(138, False), gen)


# --- file grezzo e stato --------------------------------------------------------------------

def test_file_grezzo_sotto_soglia(tmp_path, monkeypatch):
    monkeypatch.setattr(yf, "RAW", str(tmp_path))
    meta = {"id": "abc123", "title": "Video tronco", "duration": UNDICI_MIN}
    tr = _fetch(FakeTranscript(138, False), None)
    path, name = yf.write_raw(meta, "Canale", tr)
    t = open(path, encoding="utf-8").read()
    assert "- completezza: SOTTO SOGLIA (12.5 parole/min)" in t
    assert "- traccia: manuale (en)" in t
    assert "- parole: 138 (al minuto: 12.5)" in t
    assert "- durata: 11 min" in t
    assert not os.path.exists(path + ".tmp")
    assert rule_extract.body(path).split() == tr.text.split()


def test_file_grezzo_completo_e_durata_ignota(tmp_path, monkeypatch):
    monkeypatch.setattr(yf, "RAW", str(tmp_path))
    ok = _fetch(FakeTranscript(1500, False), None)
    t = open(yf.write_raw({"id": "a", "title": "ok", "duration": UNDICI_MIN}, "C", ok)[0],
             encoding="utf-8").read()
    assert f"- completezza: ok (soglia {yf.SOGLIA_PAROLE_MIN} parole/min)" in t
    ign = _fetch(FakeTranscript(1500, True), None, durata=0)
    t = open(yf.write_raw({"id": "b", "title": "ign", "duration": 0}, "C", ign)[0],
             encoding="utf-8").read()
    assert "- durata: ignota" in t
    assert "- traccia: generata (en)" in t
    assert "- completezza: durata ignota" in t


def test_intestazione_lunga_resta_saltabile_da_rule_extract(tmp_path, monkeypatch):
    """rule_extract.body() salta l'intestazione solo se il '---' cade entro 700 caratteri."""
    monkeypatch.setattr(yf, "RAW", str(tmp_path))
    meta = {"id": "x" * 11, "title": "T" * 100, "duration": 3 * 3600}   # 100 = massimo YouTube
    tr = _fetch(FakeTranscript(138, False), FakeTranscript(100, True), durata=3 * 3600)
    path, _ = yf.write_raw(meta, "C" * 80, tr)
    head = yf.raw_header(meta, "C" * 80, tr)
    assert len(head) < 700
    assert rule_extract.body(path).split() == tr.text.split()


def test_stato_registra_la_completezza(tmp_path, monkeypatch):
    monkeypatch.setattr(yf, "STATE", str(tmp_path / "_state.json"))
    tr = _fetch(FakeTranscript(138, False), None)
    meta = {"id": "abc123", "title": "Video tronco", "duration": UNDICI_MIN}
    st = {"Canale": {"abc123": yf.state_entry(meta, "f.md", tr)}}
    yf.save_state(st)
    e = json.load(open(tmp_path / "_state.json", encoding="utf-8"))["Canale"]["abc123"]
    assert (e["completezza"], e["parole_min"], e["traccia"], e["words"]) == (
        "SOTTO SOGLIA", 12.5, "manuale", 138)
    assert "SOTTO SOGLIA (12.5 parole/min" in yf.outcome_label(tr)


def test_save_state_non_svuota_il_file_se_la_serializzazione_fallisce(tmp_path, monkeypatch):
    p = tmp_path / "_state.json"
    monkeypatch.setattr(yf, "STATE", str(p))
    yf.save_state({"a": 1})
    with pytest.raises(TypeError):
        yf.save_state({"a": object()})
    assert json.load(open(p, encoding="utf-8")) == {"a": 1}
