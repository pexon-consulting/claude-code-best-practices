#!/usr/bin/env python3
"""PreToolUse- und UserPromptSubmit-Hook: hält personenbezogene Daten aus Code und Prompts (DSGVO).

Hart (nur mit gültiger Prüfziffer): IBAN, Steuer-ID, Sozialversicherungsnummer, Kreditkarte.
Weich: viele verschiedene E-Mail-Adressen oder Telefonnummern in einem Schreibvorgang,
typisch für einen eingefügten Kundenexport. Dann fragt der Hook nach.

Beim Prompt blockt der Hook, bevor der Text an das Modell geht. Testdaten-Ordner
lassen sich in .claude/schutz.json unter pii.pfade_ausnehmen freigeben.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _hook  # noqa: E402
import muster  # noqa: E402

NAMEN = {
    "iban": "IBAN", "steuer-id": "Steuer-ID", "sozialversicherungsnummer": "Sozialversicherungsnummer",
    "kreditkarte": "Kreditkartennummer", "ust-id": "USt-IdNr.",
}
WEICH = {"ust-id"}  # Firmen-USt-IdNrn sind öffentlich, bei Einzelunternehmern aber personenbezogen


def bewerte(text: str, kontakte_ab: int) -> tuple[str, str]:
    """Gibt (stufe, grund) zurück. stufe ist 'hart', 'weich' oder ''."""
    funde = muster.finde_pii(text)
    harte = [f for f in funde if f.art not in WEICH]
    if harte:
        arten = ", ".join(sorted({f"{NAMEN[f.art]} {f.vorschau}" for f in harte}))
        return "hart", f"Personenbezogene Daten gefunden: {arten}. Durch Testdaten ersetzen (z.B. die verbreitete Beispiel-IBAN DE89 3704 0044 0532 0130 00)."
    hinweise = sorted({f"{NAMEN[f.art]} {f.vorschau}" for f in funde})
    zaehlung = muster.zaehle_kontakte(text)
    hinweise += [f"{n} {art}" for art, n in (("E-Mail-Adressen", zaehlung["email"]), ("Telefonnummern", zaehlung["telefon"])) if n >= kontakte_ab]
    if hinweise:
        return "weich", f"Der Inhalt enthält {', '.join(hinweise)}. Kann auf echte Personen- oder Kundendaten hindeuten. Bitte bestätigen oder pseudonymisieren."
    return "", ""


def haupt(eingabe: dict) -> None:
    konfig = _hook.lade_konfig(eingabe)["pii"]
    if konfig["modus"] == "aus":
        return
    ereignis = eingabe.get("hook_event_name", "PreToolUse")

    if ereignis == "UserPromptSubmit":
        stufe, grund = bewerte(str(eingabe.get("prompt", "")), int(konfig["kontakte_ab"]))
        if stufe == "hart":
            _hook.entscheide("deny", grund + " Der Prompt wurde nicht gesendet.", ereignis)
        elif stufe == "weich":
            _hook.kontext(ereignis, "Hinweis vom PII-Hook: " + grund + " Keine dieser Daten in Dateien, Commits oder Logs übernehmen.")
        return

    tool_input = eingabe.get("tool_input") or {}
    pfad = _hook.dateipfad(tool_input)
    if pfad and _hook.ausgenommen(eingabe, pfad, konfig["pfade_ausnehmen"]):
        return
    stufe, grund = bewerte(_hook.neuer_inhalt(tool_input), int(konfig["kontakte_ab"]))
    if stufe == "hart":
        _hook.entscheide(konfig["modus"], grund)
    elif stufe == "weich":
        _hook.entscheide("ask", grund)


if __name__ == "__main__":
    _hook.ausfuehren(haupt)
