"""Durchsucht Dateien oder stdin nach Secrets und deutschen personenbezogenen Daten.

Gleiche Erkennung wie die Hooks. Gedacht für pre-commit und CI, damit auch Code,
den kein Agent geschrieben hat, geprüft wird.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .projekt import lade_muster

BINAER = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".gz", ".xlsx", ".docx", ".woff", ".woff2", ".ico", ".lock"}


@dataclass(frozen=True)
class Treffer:
    datei: str
    zeile: int
    art: str
    klasse: str
    vorschau: str


def scanne_text(text: str, datei: str, kontakte_ab: int = 5) -> list[Treffer]:
    muster = lade_muster()
    treffer = [
        Treffer(datei, text.count("\n", 0, f.stelle) + 1, f.art, f.klasse, f.vorschau)
        for f in muster.finde_secrets(text) + muster.finde_pii(text)
    ]
    for art, anzahl in muster.zaehle_kontakte(text).items():
        if anzahl >= kontakte_ab:
            treffer.append(Treffer(datei, 0, f"viele-{art}", "pii", f"{anzahl} verschiedene"))
    return sorted(treffer, key=lambda t: (t.datei, t.zeile, t.art))


def dateien(pfade: list[Path], nur_git: bool) -> list[Path]:
    ergebnis: list[Path] = []
    for pfad in pfade:
        if pfad.is_file():
            ergebnis.append(pfad)
        elif pfad.is_dir():
            if nur_git:
                ausgabe = subprocess.run(["git", "ls-files", "-z"], cwd=pfad, capture_output=True, text=True, check=False).stdout
                ergebnis += [pfad / n for n in ausgabe.split("\0") if n]
            else:
                ergebnis += [p for p in pfad.rglob("*") if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts]
    return [p for p in ergebnis if p.suffix.lower() not in BINAER]


def scanne(pfade: list[Path], nur_git: bool = True, kontakte_ab: int = 5) -> list[Treffer]:
    treffer: list[Treffer] = []
    for pfad in dateien(pfade, nur_git):
        try:
            text = pfad.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        treffer += scanne_text(text, pfad.as_posix(), kontakte_ab)
    return treffer
