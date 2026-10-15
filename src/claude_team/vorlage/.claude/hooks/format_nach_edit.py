#!/usr/bin/env python3
"""PostToolUse-Hook für Edit und Write: formatiert die geänderte Datei.

Nutzt nur Formatter, die im Projekt oder auf dem PATH schon vorhanden sind:
ruff oder black (Python), prettier aus node_modules (JS, TS, JSON, CSS, Markdown),
gofmt, rustfmt, terraform fmt. Fehlt ein Formatter, passiert nichts.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _hook  # noqa: E402

PRETTIER = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".css", ".scss", ".md", ".yaml", ".yml", ".html", ".vue", ".svelte"}


def befehl_fuer(datei: Path, projekt: Path) -> list[str] | None:
    endung = datei.suffix.lower()
    if endung == ".py":
        if shutil.which("ruff"):
            return ["ruff", "format", "--quiet", str(datei)]
        if shutil.which("black"):
            return ["black", "--quiet", str(datei)]
    if endung in PRETTIER:
        prettier = projekt / "node_modules" / ".bin" / "prettier"
        if prettier.exists():
            return [str(prettier), "--write", "--log-level", "warn", str(datei)]
    if endung == ".go" and shutil.which("gofmt"):
        return ["gofmt", "-w", str(datei)]
    if endung == ".rs" and shutil.which("rustfmt"):
        return ["rustfmt", str(datei)]
    if endung in (".tf", ".tfvars") and shutil.which("terraform"):
        return ["terraform", "fmt", str(datei)]
    return None


def haupt(eingabe: dict) -> None:
    pfad = _hook.dateipfad(eingabe.get("tool_input") or {})
    if not pfad or not Path(pfad).is_file():
        return
    projekt = _hook.projektordner(eingabe)
    befehl = befehl_fuer(Path(pfad), projekt)
    if befehl:
        subprocess.run(befehl, cwd=projekt, capture_output=True, timeout=30, check=False)


if __name__ == "__main__":
    _hook.ausfuehren(haupt)
