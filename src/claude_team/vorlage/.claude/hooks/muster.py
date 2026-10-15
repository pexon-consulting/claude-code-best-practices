"""Erkennung von Secrets und deutschen personenbezogenen Daten. Nur Standardbibliothek.

Zahlen zählen nur mit gültiger Prüfziffer: IBAN (ISO 13616, Mod 97), Steuer-ID
(ISO 7064 Mod 11,10 plus Ziffernregel), Sozialversicherungsnummer (Verfahren der
Deutschen Rentenversicherung), Kreditkarte (Luhn). So bleiben Fehlalarme selten.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import PurePosixPath


@dataclass(frozen=True)
class Fund:
    art: str  # z.B. "iban", "aws-zugangsschluessel"
    klasse: str  # "secret" oder "pii"
    stelle: int  # Zeichenposition im Text
    vorschau: str  # maskiert, nie der volle Wert


def maskiere(wert: str) -> str:
    wert = wert.strip()
    if len(wert) <= 8:
        return "*" * len(wert)
    return f"{wert[:4]}{'*' * (len(wert) - 6)}{wert[-2:]}"


# --- Secrets ---------------------------------------------------------------

SECRET_MUSTER: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("privater-schluessel", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("aws-zugangsschluessel", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b")),
    ("gitlab-token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b")),
    ("anthropic-schluessel", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("openai-schluessel", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b")),
    ("google-api-schluessel", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("stripe-schluessel", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{20,}\b")),
    ("azure-speicherschluessel", re.compile(r"AccountKey=[A-Za-z0-9+/=]{40,}")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("url-mit-passwort", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s:/@]+:[^\s@/]{3,}@[^\s/]+")),
)

# Platzhalter, die in Vorlagen und Doku stehen dürfen.
_PLATZHALTER = re.compile(r"(?i)(example|beispiel|xxxx|changeme|dummy|placeholder|\$\{|<[a-z_-]+>)")


def finde_secrets(text: str) -> list[Fund]:
    funde = []
    for art, muster in SECRET_MUSTER:
        for m in muster.finditer(text):
            wert = m.group(0)
            if art == "url-mit-passwort" and _PLATZHALTER.search(wert):
                continue
            if art not in ("privater-schluessel",) and _PLATZHALTER.search(wert):
                continue
            funde.append(Fund(art, "secret", m.start(), maskiere(wert)))
    return funde


# --- Sensible Pfade --------------------------------------------------------

SENSIBLE_DATEIEN = (
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "*.jks", "*.keystore",
    "id_rsa", "id_rsa.*", "id_ed25519", "id_ed25519.*", "id_ecdsa", "id_ecdsa.*",
    ".netrc", ".npmrc", ".pypirc", "credentials", "credentials.json", "*.tfstate", "*.tfstate.*",
    "secrets.*", "*.secrets.*",
)
SENSIBLE_ORDNER = ("secrets", ".aws", ".ssh", ".gnupg", ".kube", ".azure", ".config/gcloud", ".docker")
ERLAUBTE_DATEIEN = (".env.example", ".env.sample", ".env.template", ".env.dist", "*.pub")


def ist_sensibler_pfad(pfad: str) -> bool:
    """True für Dateien mit Zugangsdaten: .env, Schlüssel, Cloud-Credentials. Vorlagen wie .env.example sind erlaubt."""
    if not pfad:
        return False
    p = PurePosixPath(pfad.replace("\\", "/"))
    name = p.name
    if any(fnmatch(name, m) for m in ERLAUBTE_DATEIEN):
        return False
    if any(fnmatch(name, m) for m in SENSIBLE_DATEIEN):
        return True
    teile = "/" + "/".join(p.parts) + "/"
    return any(f"/{o}/" in teile for o in SENSIBLE_ORDNER)


# --- Personenbezogene Daten -------------------------------------------------

_IBAN = re.compile(r"\b([A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){2,7}(?: ?[A-Z0-9]{1,4})?)\b")
_IBAN_LAENGE = {"DE": 22, "AT": 20, "CH": 21, "LI": 21, "LU": 20, "NL": 18, "BE": 16, "FR": 27, "IT": 27, "ES": 24, "PL": 28, "DK": 18}
_ELF_ZIFFERN = re.compile(r"(?<!\d)(?<!\d[.,])(\d{2} ?\d{3} ?\d{3} ?\d{3})(?!\d|[.,]\d)")
_UST_ID = re.compile(r"\b(DE ?\d{3} ?\d{3} ?\d{3})\b")
_SVNR = re.compile(r"\b(\d{2}) ?(\d{6}) ?([A-Z]) ?(\d{2}) ?(\d)\b")
_KARTE = re.compile(r"(?<!\d)(\d(?:[ -]?\d){12,18})(?!\d)")
_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_TELEFON = re.compile(r"(?<![\w+])(?:\+49|0049|0)[ /-]?(?:\(0\))?[ /-]?[1-9]\d{1,4}[ /-]?\d{3,8}(?:[ -]?\d{1,5})?(?!\d)")
_EMAIL_HARMLOS = re.compile(r"(?i)@(example\.(com|org|net|de)|beispiel\.de|test\.de|localhost|users\.noreply\.github\.com)$|^(noreply|no-reply|info|kontakt|support|hello|team)@")


# Öffentlich dokumentierte Testwerte (Bundesbank-Beispiel, Kartennetz-Testnummern). Dürfen in Tests stehen.
TESTWERTE = frozenset({
    "DE89370400440532013000", "DE02120300000000202051", "DE02500105170137075030", "DE75512108001245126199",
    "4111111111111111", "4242424242424242", "5555555555554444", "5105105105105100", "378282246310005", "4000056655665556",
})


def ist_testwert(text: str) -> bool:
    return re.sub(r"[ -]", "", text).upper() in TESTWERTE


def iban_gueltig(text: str) -> bool:
    s = text.replace(" ", "").upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", s):
        return False
    laenge = _IBAN_LAENGE.get(s[:2])
    if laenge and len(s) != laenge:
        return False
    umgestellt = s[4:] + s[:4]
    zahl = "".join(str(int(z, 36)) for z in umgestellt)
    return int(zahl) % 97 == 1


def steuer_id_gueltig(text: str) -> bool:
    s = text.replace(" ", "")
    if not re.fullmatch(r"[1-9]\d{10}", s):
        return False
    zaehler = {z: s[:10].count(z) for z in set(s[:10])}
    mehrfach = [z for z, n in zaehler.items() if n > 1]
    if len(mehrfach) != 1 or zaehler[mehrfach[0]] not in (2, 3):
        return False
    return mod_11_10(s[:10]) == int(s[10])


def mod_11_10(ziffern: str) -> int:
    """Prüfziffer nach ISO 7064 MOD 11,10 (Steuer-ID, USt-IdNr.)."""
    produkt = 10
    for ziffer in ziffern:
        summe = (int(ziffer) + produkt) % 10 or 10
        produkt = (summe * 2) % 11
    pruef = 11 - produkt
    return 0 if pruef == 10 else pruef


def ust_id_gueltig(text: str) -> bool:
    s = text.replace(" ", "").upper()
    return bool(re.fullmatch(r"DE[1-9]\d{8}", s)) and mod_11_10(s[2:10]) == int(s[10])


def svnr_gueltig(bereich: str, datum: str, buchstabe: str, serie: str, pruef: str) -> bool:
    tag, monat = int(datum[:2]), int(datum[2:4])
    if not (1 <= tag <= 31 or 51 <= tag <= 81) or not 1 <= monat <= 12:
        return False
    ziffern = bereich + datum + f"{ord(buchstabe) - 64:02d}" + serie
    gewichte = (2, 1, 2, 5, 7, 1, 2, 1, 2, 1, 2, 1)
    summe = sum(sum(int(q) for q in str(int(z) * g)) for z, g in zip(ziffern, gewichte))
    return summe % 10 == int(pruef)


def luhn_gueltig(text: str) -> bool:
    s = re.sub(r"[ -]", "", text)
    if not 13 <= len(s) <= 19 or len(set(s)) == 1:
        return False
    summe = 0
    for i, z in enumerate(reversed(s)):
        n = int(z) * (2 if i % 2 else 1)
        summe += n - 9 if n > 9 else n
    return summe % 10 == 0 and s[0] in "3456"


def finde_pii(text: str) -> list[Fund]:
    """IBAN, Steuer-ID, USt-IdNr., Sozialversicherungsnummer, Kreditkarte. Bekannte Testwerte zählen nicht."""
    pruefungen = (
        ("iban", _IBAN, lambda m: iban_gueltig(m.group(1))),
        ("steuer-id", _ELF_ZIFFERN, lambda m: steuer_id_gueltig(m.group(1))),
        ("ust-id", _UST_ID, lambda m: ust_id_gueltig(m.group(1))),
        ("sozialversicherungsnummer", _SVNR, lambda m: svnr_gueltig(*m.groups())),
        ("kreditkarte", _KARTE, lambda m: luhn_gueltig(m.group(1))),
    )
    funde = []
    for art, regex, gueltig in pruefungen:
        for m in regex.finditer(text):
            if gueltig(m) and not ist_testwert(m.group(0)):
                funde.append(Fund(art, "pii", m.start(), maskiere(m.group(0))))
    return funde


def zaehle_kontakte(text: str) -> dict[str, int]:
    """Wie viele verschiedene E-Mail-Adressen und Telefonnummern stehen im Text."""
    mails = {m.group(0).lower() for m in _EMAIL.finditer(text) if not _EMAIL_HARMLOS.search(m.group(0))}
    telefone = {re.sub(r"\D", "", m.group(0)) for m in _TELEFON.finditer(text)}
    telefone = {t for t in telefone if 8 <= len(t) <= 15}
    return {"email": len(mails), "telefon": len(telefone)}
