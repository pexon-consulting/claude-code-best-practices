"""Erkennung in muster.py: Prüfziffern, Testwerte, Secrets, sensible Pfade."""

from __future__ import annotations

import pytest

from conftest import anthropic_schluessel, aws_schluessel, github_token, iban, karte, muster, steuer_id, svnr, ust_id


def arten(text: str) -> set[str]:
    return {f.art for f in muster.finde_pii(text)}


def test_iban_mit_pruefziffer():
    wert = iban()
    assert muster.iban_gueltig(wert)
    assert arten(f"Bitte an {wert} überweisen") == {"iban"}


def test_iban_mit_leerzeichen():
    wert = iban()
    gruppiert = " ".join(wert[i:i + 4] for i in range(0, len(wert), 4))
    assert arten(f"IBAN: {gruppiert}.") == {"iban"}


def test_iban_falsche_pruefziffer_zaehlt_nicht():
    wert = iban()
    falsch = wert[:2] + f"{(int(wert[2:4]) + 1) % 100:02d}" + wert[4:]
    assert not muster.iban_gueltig(falsch)
    assert "iban" not in arten(falsch)


def test_iban_falsche_laenge():
    assert not muster.iban_gueltig(iban() + "1")


@pytest.mark.parametrize("wert", ["DE89 3704 0044 0532 0130 00", "DE02120300000000202051"])
def test_muster_iban_ist_testwert(wert):
    assert muster.iban_gueltig(wert)
    assert arten(wert) == set()


def test_steuer_id():
    wert = steuer_id()
    assert muster.steuer_id_gueltig(wert)
    assert arten(f"Steuer-ID {wert}, bitte prüfen") == {"steuer-id"}


def test_steuer_id_mit_leerzeichen():
    wert = steuer_id()
    assert "steuer-id" in arten(f"{wert[:2]} {wert[2:5]} {wert[5:8]} {wert[8:]}")


def test_steuer_id_ziffernregel():
    # alle zehn Ziffern verschieden: verletzt die Regel, auch mit passender Prüfziffer
    basis = "6589471230"
    assert not muster.steuer_id_gueltig(basis + str(muster.mod_11_10(basis)))


def test_steuer_id_nicht_in_laengerer_zahl():
    assert "steuer-id" not in arten("Bestellnummer 9" + steuer_id() + "7")


def test_steuer_id_nicht_als_betrag():
    assert "steuer-id" not in arten("Summe 1." + steuer_id()[:3] + ",50 EUR")


def test_ust_id_ist_weich():
    wert = ust_id()
    assert muster.ust_id_gueltig(wert)
    assert arten(f"USt-IdNr. {wert}") == {"ust-id"}


def test_ust_id_falsche_pruefziffer():
    wert = ust_id()
    assert not muster.ust_id_gueltig(wert[:-1] + str((int(wert[-1]) + 1) % 10))


def test_sozialversicherungsnummer():
    wert = svnr()
    assert arten(f"SV-Nr. {wert}") == {"sozialversicherungsnummer"}


def test_sozialversicherungsnummer_falsche_pruefziffer():
    wert = svnr()
    falsch = wert[:-1] + str((int(wert[-1]) + 1) % 10)
    assert "sozialversicherungsnummer" not in arten(falsch)


def test_sozialversicherungsnummer_ungueltiges_datum():
    assert "sozialversicherungsnummer" not in arten(svnr(datum="451399"))


def test_kreditkarte_luhn():
    wert = karte()
    assert muster.luhn_gueltig(wert)
    assert "kreditkarte" in arten(f"Karte {wert[:4]} {wert[4:8]} {wert[8:12]} {wert[12:]}")


@pytest.mark.parametrize("wert", ["4111 1111 1111 1111", "4242424242424242", "5555555555554444"])
def test_kreditkarte_testnummern(wert):
    assert "kreditkarte" not in arten(wert)


def test_gleiche_ziffern_sind_keine_karte():
    assert not muster.luhn_gueltig("0000000000000000")


def test_normale_zahlen_bleiben_ruhig():
    text = "Version 2.1.294, Port 8080, Zeitstempel 1760550000, Telefon intern 4711, Rechnung 2026-10-15"
    assert muster.finde_pii(text) == []


def test_vorschau_ist_maskiert():
    wert = iban()
    fund = muster.finde_pii(wert)[0]
    assert wert not in fund.vorschau
    assert fund.vorschau.startswith(wert[:4]) and "*" in fund.vorschau


@pytest.mark.parametrize("erzeuger, art", [
    (aws_schluessel, "aws-zugangsschluessel"),
    (github_token, "github-token"),
    (anthropic_schluessel, "anthropic-schluessel"),
])
def test_secrets(erzeuger, art):
    funde = muster.finde_secrets(f"token = '{erzeuger()}'")
    assert art in {f.art for f in funde}


def test_privater_schluessel():
    kopf = "-----BEGIN " + "RSA PRIVATE KEY-----"
    assert {f.art for f in muster.finde_secrets(kopf + "\nMIIE...")} == {"privater-schluessel"}


def test_url_mit_passwort():
    assert "url-mit-passwort" in {f.art for f in muster.finde_secrets("postgres://app:" + "s3cr3tPass" + "@db.intern:5432/app")}


@pytest.mark.parametrize("text", [
    "postgres://user:${DB_PASSWORD}@localhost/app",
    "AKIA" + "IOSFODNN7EXAMPLE",
    "Authorization: Bearer <token>",
    "export GITHUB_TOKEN=${GITHUB_TOKEN}",
])
def test_platzhalter_sind_keine_secrets(text):
    assert muster.finde_secrets(text) == []


@pytest.mark.parametrize("pfad, erwartet", [
    (".env", True),
    ("/repo/.env.production", True),
    ("config/.env.local", True),
    (".env.example", False),
    ("deploy/server.pem", True),
    ("home/.ssh/id_ed25519", True),
    ("home/.ssh/id_ed25519.pub", False),
    ("home/.aws/credentials", True),
    ("infra/terraform.tfstate", True),
    ("secrets/db.yaml", True),
    ("src/environment.ts", False),
    ("docs/secrets-management.md", False),
    ("C:\\Users\\a\\.ssh\\config", True),
])
def test_sensible_pfade(pfad, erwartet):
    assert muster.ist_sensibler_pfad(pfad) is erwartet


def test_kontakte_zaehlen_ohne_harmlose_adressen():
    text = "a@firma.de b@firma.de c@firma.de info@firma.de max@example.com, Tel. +49 30 1234567, mobil 0171 2345678"
    assert muster.zaehle_kontakte(text) == {"email": 3, "telefon": 2}
