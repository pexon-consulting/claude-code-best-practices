"""Ausgabe der Befunde als Text, Markdown, JSON oder SARIF (GitHub Code Scanning)."""

from __future__ import annotations

import json

from . import __version__
from .regeln import FEHLER, HINWEIS, REGELN, WARNUNG, Befund

SYMBOL = {FEHLER: "FEHLER ", WARNUNG: "WARNUNG", HINWEIS: "HINWEIS"}
SARIF_STUFE = {FEHLER: "error", WARNUNG: "warning", HINWEIS: "note"}


def zaehle(befunde: list[Befund]) -> dict[str, int]:
    return {s: sum(b.schwere == s for b in befunde) for s in (FEHLER, WARNUNG, HINWEIS)}


def als_text(befunde: list[Befund], pfad: str) -> str:
    if not befunde:
        return f"{pfad}: keine Befunde.\n"
    zeilen = []
    for b in befunde:
        ort = f"{b.datei}:{b.zeile}" if b.zeile else b.datei
        zeilen.append(f"{SYMBOL[b.schwere]} {b.regel} {ort}\n        {b.meldung}")
    z = zaehle(befunde)
    zeilen.append(f"\n{z[FEHLER]} Fehler, {z[WARNUNG]} Warnungen, {z[HINWEIS]} Hinweise.")
    return "\n".join(zeilen) + "\n"


def als_markdown(befunde: list[Befund], pfad: str) -> str:
    z = zaehle(befunde)
    zeilen = [
        f"# Claude-Code-Prüfung: {pfad}",
        "",
        f"{z[FEHLER]} Fehler, {z[WARNUNG]} Warnungen, {z[HINWEIS]} Hinweise. Geprüft mit claude-team {__version__}.",
        "",
    ]
    if not befunde:
        return "\n".join(zeilen + ["Keine Befunde.", ""])
    zeilen += ["| Stufe | Regel | Datei | Befund |", "| --- | --- | --- | --- |"]
    for b in befunde:
        ort = f"`{b.datei}:{b.zeile}`" if b.zeile else f"`{b.datei}`"
        meldung = b.meldung.replace("|", "\\|")
        zeilen.append(f"| {b.schwere} | [{b.regel}]({b.link}) | {ort} | {meldung} |")
    return "\n".join(zeilen) + "\n"


def als_json(befunde: list[Befund], pfad: str) -> str:
    return json.dumps(
        {"werkzeug": "claude-team", "version": __version__, "pfad": pfad, "anzahl": zaehle(befunde), "befunde": [b.als_dict() for b in befunde]},
        ensure_ascii=False, indent=2,
    ) + "\n"


def als_sarif(befunde: list[Befund], pfad: str) -> str:
    benutzt = sorted({b.regel for b in befunde})
    regeln = [
        {
            "id": REGELN[r].id,
            "name": REGELN[r].anker,
            "shortDescription": {"text": REGELN[r].titel},
            "helpUri": REGELN[r].link,
            "defaultConfiguration": {"level": SARIF_STUFE[REGELN[r].schwere]},
        }
        for r in benutzt
    ]
    ergebnisse = []
    for b in befunde:
        ort = {"physicalLocation": {"artifactLocation": {"uri": b.datei}}}
        if b.zeile:
            ort["physicalLocation"]["region"] = {"startLine": b.zeile}
        ergebnisse.append({"ruleId": b.regel, "level": SARIF_STUFE[b.schwere], "message": {"text": b.meldung}, "locations": [ort]})
    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "claude-team", "version": __version__, "informationUri": "https://github.com/pexon-consulting/claude-code-best-practices", "rules": regeln}},
            "results": ergebnisse,
        }],
    }
    return json.dumps(sarif, ensure_ascii=False, indent=2) + "\n"


FORMATE = {"text": als_text, "markdown": als_markdown, "json": als_json, "sarif": als_sarif}
