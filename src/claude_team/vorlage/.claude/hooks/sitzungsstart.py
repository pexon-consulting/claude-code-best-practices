#!/usr/bin/env python3
"""SessionStart-Hook: gibt Claude den Git-Stand mit, bevor die erste Frage kommt.

Branch, Zahl der offenen Änderungen, die letzten Commits. Auf main oder master
kommt der Hinweis, für Änderungen einen Branch anzulegen.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _hook  # noqa: E402


def git(projekt: Path, *argumente: str) -> str:
    ergebnis = subprocess.run(["git", *argumente], cwd=projekt, capture_output=True, text=True, timeout=5, check=False)
    return ergebnis.stdout.strip() if ergebnis.returncode == 0 else ""


def haupt(eingabe: dict) -> None:
    projekt = _hook.projektordner(eingabe)
    branch = git(projekt, "branch", "--show-current")
    if not branch and not git(projekt, "rev-parse", "--git-dir"):
        return
    offen = [z for z in git(projekt, "status", "--porcelain").splitlines() if z.strip()]
    commits = git(projekt, "log", "-3", "--format=%h %s")
    zeilen = [f"Git-Branch: {branch or '(detached HEAD)'}", f"Offene Änderungen: {len(offen)} {'Datei' if len(offen) == 1 else 'Dateien'}"]
    if commits:
        zeilen.append("Letzte Commits:\n" + commits)
    if branch in ("main", "master"):
        zeilen.append("Hinweis: Du bist auf dem Hauptbranch. Vor Änderungen einen Feature-Branch anlegen.")
    _hook.kontext("SessionStart", "\n".join(zeilen))


if __name__ == "__main__":
    _hook.ausfuehren(haupt)
