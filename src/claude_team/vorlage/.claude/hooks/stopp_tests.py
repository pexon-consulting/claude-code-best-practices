#!/usr/bin/env python3
"""Stop-Hook: lässt Claude erst fertig sein, wenn die Tests grün sind.

Der Befehl steht in .claude/schutz.json unter stopp.befehl, z.B. "pytest -q" oder
"npm test". Leer heißt aus. Läuft nur, wenn Git offene Änderungen zeigt, und nur
einmal je Stopp (stop_hook_active), damit keine Endlosschleife entsteht.
"""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _hook  # noqa: E402


def haupt(eingabe: dict) -> None:
    befehl = str(_hook.lade_konfig(eingabe)["stopp"].get("befehl") or "").strip()
    if not befehl or eingabe.get("stop_hook_active"):
        return
    projekt = _hook.projektordner(eingabe)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=projekt, capture_output=True, text=True, timeout=10, check=False)
    if status.returncode == 0 and not status.stdout.strip():
        return
    lauf = subprocess.run(shlex.split(befehl), cwd=projekt, capture_output=True, text=True, timeout=600, check=False)
    if lauf.returncode != 0:
        ausgabe = "\n".join((lauf.stdout + "\n" + lauf.stderr).strip().splitlines()[-40:])
        _hook.entscheide("deny", f"'{befehl}' schlägt fehl (Exit {lauf.returncode}). Bitte beheben, bevor du fertig meldest.\n\n{ausgabe}", "Stop")


if __name__ == "__main__":
    _hook.ausfuehren(haupt)
