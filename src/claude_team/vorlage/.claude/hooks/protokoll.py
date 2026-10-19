#!/usr/bin/env python3
"""PostToolUse-Hook: schreibt ein Protokoll jeder Tool-Nutzung als JSON Lines.

Standardmäßig aus. Einschalten mit "protokoll": {"aktiv": true} in .claude/schutz.json,
im Team erst nach Absprache mit Betriebsrat und Datenschutz: das Protokoll zeichnet
Befehle je Person auf.

Eine Datei je Tag unter .claude/protokoll/. Gespeichert werden Zeit, Sitzung,
Tool, Datei und der Befehl, aber keine Dateiinhalte. Tokens, IBAN, Steuer-ID,
Sozialversicherungsnummer, Kartennummern und E-Mail-Adressen im Befehl werden
maskiert, Heredoc-Inhalte (alles ab <<) nicht gespeichert. Dateien, die älter als
aufbewahrung_tage sind (Standard 30), löscht der Hook beim nächsten Schreiben.
Der Ordner gehört in .gitignore.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _hook  # noqa: E402
import muster  # noqa: E402

TAGESDATEI = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.jsonl$")


def maskiere_befehl(befehl: str) -> str:
    heredoc = befehl.find("<<")
    if heredoc >= 0:
        befehl = befehl[:heredoc] + "<< [Heredoc nicht protokolliert]"
    bereiche: list[list] = []
    for fund in sorted(muster.finde_secrets(befehl) + muster.finde_pii(befehl), key=lambda f: f.stelle):
        ende = fund.stelle + fund.laenge
        if fund.klasse == "secret":
            ende = max(ende, re.match(r"[^\s'\"`]*", befehl[fund.stelle:]).end() + fund.stelle)
        if bereiche and fund.stelle < bereiche[-1][1]:
            bereiche[-1][1] = max(bereiche[-1][1], ende)
        else:
            bereiche.append([fund.stelle, ende, fund.art])
    for anfang, ende, art in reversed(bereiche):
        befehl = befehl[:anfang] + f"[{art}]" + befehl[ende:]
    befehl = muster._EMAIL.sub("[email]", befehl)
    return befehl[:300]


def alte_loeschen(ordner: Path, tage: int, heute: date) -> None:
    grenze = heute - timedelta(days=tage)
    for datei in ordner.glob("*.jsonl"):
        m = TAGESDATEI.match(datei.name)
        if not m:
            continue
        try:
            tag = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        if tag < grenze:
            datei.unlink(missing_ok=True)


def haupt(eingabe: dict) -> None:
    konfig = _hook.lade_konfig(eingabe)["protokoll"]
    if not konfig.get("aktiv", False):
        return
    tool_input = eingabe.get("tool_input") or {}
    jetzt = datetime.now(timezone.utc)
    eintrag = {
        "zeit": jetzt.isoformat(timespec="seconds"),
        "sitzung": str(eingabe.get("session_id", ""))[:8],
        "ereignis": eingabe.get("hook_event_name", ""),
        "tool": eingabe.get("tool_name", ""),
        "modus": eingabe.get("permission_mode", ""),
    }
    pfad = _hook.dateipfad(tool_input)
    if pfad:
        eintrag["datei"] = _hook.relativer_pfad(eingabe, pfad)
    if isinstance(tool_input.get("command"), str):
        eintrag["befehl"] = maskiere_befehl(tool_input["command"])
    if "duration_ms" in eingabe:
        eintrag["dauer_ms"] = eingabe["duration_ms"]
    ordner = _hook.projektordner(eingabe) / konfig.get("ordner", ".claude/protokoll")
    ordner.mkdir(parents=True, exist_ok=True)
    alte_loeschen(ordner, max(1, int(konfig.get("aufbewahrung_tage", 30))), jetzt.date())
    with open(ordner / f"{jetzt:%Y-%m-%d}.jsonl", "a", encoding="utf-8") as datei:
        datei.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    _hook.ausfuehren(haupt)
