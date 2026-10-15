"""Lesezugriff auf ein Projekt: Dateien, JSON, Frontmatter, Git-Status. Schreibt nie."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from fnmatch import fnmatch
from functools import cached_property
from pathlib import Path

VORLAGE = Path(__file__).resolve().parent / "vorlage"


def lade_muster():
    """Die Erkennung aus den Hooks, damit CLI und Hooks dieselben Regeln nutzen."""
    name = "claude_team._muster"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, VORLAGE / ".claude" / "hooks" / "muster.py")
    modul = importlib.util.module_from_spec(spec)
    sys.modules[name] = modul
    spec.loader.exec_module(modul)
    return modul


@dataclass
class JsonDatei:
    pfad: Path
    daten: object = None
    fehler: str = ""

    @property
    def vorhanden(self) -> bool:
        return self.pfad.is_file()


def lies_json(pfad: Path) -> JsonDatei:
    datei = JsonDatei(pfad)
    if not pfad.is_file():
        return datei
    try:
        datei.daten = json.loads(pfad.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as fehler:
        datei.fehler = str(fehler)
    return datei


def frontmatter(text: str) -> dict[str, str] | None:
    """Einfaches YAML-Frontmatter (key: wert, eine Ebene). None, wenn keins da ist."""
    if not text.startswith("---"):
        return None
    ende = text.find("\n---", 3)
    if ende < 0:
        return None
    werte: dict[str, str] = {}
    schluessel = ""
    for zeile in text[3:ende].splitlines():
        if not zeile.strip() or zeile.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", zeile)
        if m:
            schluessel = m.group(1)
            werte[schluessel] = m.group(2).strip().strip("\"'")
        elif schluessel and zeile.startswith((" ", "\t")):
            werte[schluessel] = (werte[schluessel] + " " + zeile.strip()).strip()
    return werte


@dataclass
class Projekt:
    wurzel: Path
    _ignoriert: dict[str, bool] = field(default_factory=dict)

    def datei(self, relativ: str) -> Path:
        return self.wurzel / relativ

    def text(self, relativ: str) -> str:
        try:
            return self.datei(relativ).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ""

    def json(self, relativ: str) -> JsonDatei:
        return lies_json(self.datei(relativ))

    def suche(self, muster: str) -> list[Path]:
        return sorted(p for p in self.wurzel.glob(muster) if p.is_file())

    def rel(self, pfad: Path) -> str:
        try:
            return pfad.relative_to(self.wurzel).as_posix()
        except ValueError:
            return pfad.as_posix()

    def _git(self, *argumente: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *argumente], cwd=self.wurzel, capture_output=True, text=True, timeout=20, check=False)

    @cached_property
    def ist_git(self) -> bool:
        try:
            return self._git("rev-parse", "--is-inside-work-tree").stdout.strip() == "true"
        except (OSError, subprocess.TimeoutExpired):
            return False

    @cached_property
    def getrackt(self) -> set[str]:
        if not self.ist_git:
            return set()
        return set(self._git("ls-files").stdout.splitlines())

    @cached_property
    def _gitignore_muster(self) -> list[str]:
        zeilen = self.text(".gitignore").splitlines()
        return [z.strip() for z in zeilen if z.strip() and not z.startswith("#")]

    def ist_ignoriert(self, relativ: str) -> bool:
        if relativ in self._ignoriert:
            return self._ignoriert[relativ]
        if self.ist_git:
            ergebnis = self._git("check-ignore", "-q", "--no-index", relativ).returncode == 0
        else:
            name = Path(relativ).name
            ergebnis = any(
                fnmatch(relativ, m.strip("/")) or fnmatch(name, m.strip("/")) or relativ.startswith(m.strip("/") + "/")
                for m in self._gitignore_muster if not m.startswith("!")
            )
        self._ignoriert[relativ] = ergebnis
        return ergebnis
