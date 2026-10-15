#!/usr/bin/env python3
"""PostToolUse-Hook: schreibt ein Protokoll jeder Tool-Nutzung als JSON Lines.

Eine Datei je Tag unter .claude/protokoll/. Gespeichert werden Zeit, Sitzung,
Tool, Datei und der Befehl, aber keine Dateiinhalte. Tokens im Befehl werden
maskiert. Der Ordner gehört in .gitignore.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _hook  # noqa: E402
import muster  # noqa: E402


def maskiere_befehl(befehl: str) -> str:
    for fund in sorted(muster.finde_secrets(befehl), key=lambda f: -f.stelle):
        ende = re.match(r"[^\s'\"`]*", befehl[fund.stelle:]).end() + fund.stelle
        befehl = befehl[: fund.stelle] + f"[{fund.art}]" + befehl[ende:]
    return befehl[:300]


def haupt(eingabe: dict) -> None:
    konfig = _hook.lade_konfig(eingabe)["protokoll"]
    if not konfig.get("aktiv", True):
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
    with open(ordner / f"{jetzt:%Y-%m-%d}.jsonl", "a", encoding="utf-8") as datei:
        datei.write(json.dumps(eintrag, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    _hook.ausfuehren(haupt)
