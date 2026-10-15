"""Legt die Team-Basis in einem Projekt an. Überschreibt nie eine vorhandene Datei.

Fehlt eine Datei, wird sie angelegt. Gibt es sie schon und weicht sie ab, entsteht
für settings.json und CLAUDE.md ein Vorschlag daneben (settings.vorschlag.json,
CLAUDE.vorschlag.md), alles andere bleibt unverändert. .gitignore wird nur ergänzt.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .projekt import VORLAGE, lies_json

BAUSTEINE = ("claude-md", "settings", "hooks", "regeln", "agents", "skills", "mcp", "gitignore")
PROFILE = ("standard", "streng")
GITIGNORE_ZEILEN = ("CLAUDE.local.md", ".claude/settings.local.json", ".claude/protokoll/", ".env", ".env.*", "!.env.example")
STRENG_DENY = ("WebFetch", "WebSearch", "Bash(curl *)", "Bash(wget *)", "Bash(nc *)", "Bash(scp *)", "Bash(ssh *)")


@dataclass
class Aktion:
    art: str  # angelegt, vorschlag, ergaenzt, unveraendert, uebersprungen
    datei: str
    grund: str = ""


def zusammenfuehren(alt: object, neu: object) -> object:
    """Bestehende Werte bleiben. Listen werden um fehlende Einträge ergänzt, Hooks je Befehl."""
    if isinstance(alt, dict) and isinstance(neu, dict):
        ergebnis = dict(alt)
        for schluessel, wert in neu.items():
            if schluessel == "hooks" and isinstance(wert, dict) and isinstance(alt.get("hooks"), dict):
                ergebnis["hooks"] = _hooks_zusammen(alt["hooks"], wert)
            elif schluessel in alt:
                ergebnis[schluessel] = zusammenfuehren(alt[schluessel], wert)
            else:
                ergebnis[schluessel] = copy.deepcopy(wert)
        return ergebnis
    if isinstance(alt, list) and isinstance(neu, list):
        return alt + [w for w in neu if w not in alt]
    return alt


def _befehle(gruppen: list) -> set[str]:
    return {h.get("command", "") for g in gruppen or [] for h in (g or {}).get("hooks") or []}


def _hooks_zusammen(alt: dict, neu: dict) -> dict:
    ergebnis = copy.deepcopy(alt)
    for ereignis, gruppen in neu.items():
        vorhanden = _befehle(ergebnis.get(ereignis, []))
        fehlend = [g for g in gruppen if not _befehle([g]) <= vorhanden]
        if fehlend:
            ergebnis.setdefault(ereignis, []).extend(copy.deepcopy(fehlend))
    return ergebnis


def erkenne_befehle(ziel: Path) -> dict[str, str]:
    """Install-, Test-, Lint- und Startbefehl aus package.json, pyproject.toml oder Makefile."""
    befehle = {"INSTALL": "", "TEST": "", "LINT": "", "START": ""}
    paket = lies_json(ziel / "package.json").daten
    if isinstance(paket, dict):
        laeufer = "pnpm" if (ziel / "pnpm-lock.yaml").exists() else "yarn" if (ziel / "yarn.lock").exists() else "bun" if (ziel / "bun.lockb").exists() else "npm"
        skripte = paket.get("scripts") or {}
        befehle["INSTALL"] = f"{laeufer} install"
        for platz, namen in (("TEST", ("test",)), ("LINT", ("lint", "format")), ("START", ("dev", "start"))):
            for name in namen:
                if name in skripte:
                    befehle[platz] = f"{laeufer} run {name}" if laeufer != "npm" or name not in ("test", "start") else f"npm {name}"
                    break
    elif (ziel / "pyproject.toml").exists():
        text = (ziel / "pyproject.toml").read_text(encoding="utf-8", errors="replace")
        befehle["INSTALL"] = "uv sync" if (ziel / "uv.lock").exists() else 'pip install -e ".[dev]"'
        befehle["TEST"] = "uv run pytest" if (ziel / "uv.lock").exists() else "pytest"
        befehle["LINT"] = "ruff check . && ruff format --check ." if "ruff" in text else ""
    if (ziel / "Makefile").exists():
        ziele = set(re.findall(r"^([a-zA-Z][\w-]*):", (ziel / "Makefile").read_text(encoding="utf-8", errors="replace"), re.M))
        for platz, name in (("INSTALL", "install"), ("TEST", "test"), ("LINT", "lint"), ("START", "run")):
            if name in ziele and not befehle[platz]:
                befehle[platz] = f"make {name}"
    return befehle


def claude_md_text(ziel: Path) -> str:
    text = (VORLAGE / "CLAUDE.md").read_text(encoding="utf-8")
    befehle = erkenne_befehle(ziel)
    text = text.replace("{{PROJEKT}}", ziel.resolve().name)
    for platz, befehl in befehle.items():
        text = text.replace("{{" + platz + "}}", befehl or "{{" + platz + "}}")
    return text


def settings_daten(profil: str) -> dict:
    daten = json.loads((VORLAGE / ".claude" / "settings.json").read_text(encoding="utf-8"))
    if profil == "streng":
        rechte = daten["permissions"]
        rechte["ask"] = [r for r in rechte["ask"] if r != "WebFetch"]
        rechte["deny"] += [r for r in STRENG_DENY if r not in rechte["deny"]]
        daten["env"]["CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY"] = "1"
        daten["env"]["DISABLE_FEEDBACK_COMMAND"] = "1"
    return daten


def _dateien(baustein: str) -> list[Path]:
    ordner = {"hooks": ".claude/hooks", "regeln": ".claude/rules", "agents": ".claude/agents", "skills": ".claude/skills"}
    if baustein in ordner:
        return sorted(p for p in (VORLAGE / ordner[baustein]).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return [VORLAGE / ".mcp.json.example"] if baustein == "mcp" else []


class Einrichtung:
    def __init__(self, ziel: Path, ohne: set[str], profil: str = "standard", probelauf: bool = False):
        self.ziel = ziel.resolve()
        self.ohne = ohne
        self.profil = profil
        self.probelauf = probelauf
        self.aktionen: list[Aktion] = []

    def _schreibe(self, relativ: str, inhalt: str, art: str, grund: str = "", ausfuehrbar: bool = False) -> None:
        self.aktionen.append(Aktion(art, relativ, grund))
        if self.probelauf:
            return
        pfad = self.ziel / relativ
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(inhalt, encoding="utf-8")
        if ausfuehrbar:
            pfad.chmod(0o755)

    def _datei(self, relativ: str, inhalt: str, vorschlag: str = "", ausfuehrbar: bool = False) -> None:
        pfad = self.ziel / relativ
        if not pfad.exists():
            return self._schreibe(relativ, inhalt, "angelegt", ausfuehrbar=ausfuehrbar)
        if pfad.read_text(encoding="utf-8", errors="replace") == inhalt:
            return self.aktionen.append(Aktion("unveraendert", relativ))
        if vorschlag:
            return self._schreibe(vorschlag, inhalt, "vorschlag", f"{relativ} existiert, Vorschlag zum Abgleich")
        self.aktionen.append(Aktion("uebersprungen", relativ, "existiert mit anderem Inhalt, bleibt"))

    def settings(self) -> None:
        neu = settings_daten(self.profil)
        if "hooks" in self.ohne:
            neu.pop("hooks", None)
        relativ = ".claude/settings.json"
        alt = lies_json(self.ziel / relativ)
        if alt.fehler:
            text = json.dumps(neu, ensure_ascii=False, indent=2) + "\n"
            return self._schreibe(".claude/settings.vorschlag.json", text, "vorschlag", f"{relativ} ist kein gültiges JSON")
        daten = zusammenfuehren(alt.daten, neu) if isinstance(alt.daten, dict) else neu
        rechte = daten.get("permissions")
        if isinstance(rechte, dict) and rechte.get("defaultMode") == "bypassPermissions":
            rechte["defaultMode"] = "default"
        text = json.dumps(daten, ensure_ascii=False, indent=2) + "\n"
        if isinstance(alt.daten, dict) and daten == alt.daten:
            return self.aktionen.append(Aktion("unveraendert", relativ, "enthält die Basis schon"))
        self._datei(relativ, text, vorschlag=".claude/settings.vorschlag.json")

    def gitignore(self) -> None:
        pfad = self.ziel / ".gitignore"
        alt = pfad.read_text(encoding="utf-8") if pfad.exists() else ""
        vorhanden = {z.strip() for z in alt.splitlines()}
        fehlend = [z for z in GITIGNORE_ZEILEN if z not in vorhanden]
        if not fehlend:
            return self.aktionen.append(Aktion("unveraendert", ".gitignore"))
        block = ("\n" if alt and not alt.endswith("\n") else "") + ("\n" if alt else "") + "# Claude Code\n" + "\n".join(fehlend) + "\n"
        self._schreibe(".gitignore", alt + block, "ergaenzt" if alt else "angelegt", ", ".join(fehlend))

    def ausfuehren(self) -> list[Aktion]:
        if "claude-md" not in self.ohne:
            self._datei("CLAUDE.md", claude_md_text(self.ziel), vorschlag="CLAUDE.vorschlag.md")
        if "settings" not in self.ohne:
            self.settings()
        if "hooks" not in self.ohne:
            schutz = json.loads((VORLAGE / ".claude" / "schutz.json").read_text(encoding="utf-8"))
            self._datei(".claude/schutz.json", json.dumps(schutz, ensure_ascii=False, indent=2) + "\n")
        for baustein in ("hooks", "regeln", "agents", "skills", "mcp"):
            if baustein in self.ohne:
                continue
            for quelle in _dateien(baustein):
                relativ = quelle.relative_to(VORLAGE).as_posix()
                self._datei(relativ, quelle.read_text(encoding="utf-8"), ausfuehrbar=quelle.suffix == ".py" and not quelle.name.startswith("_") and quelle.name != "muster.py")
        if "gitignore" not in self.ohne:
            self.gitignore()
        return self.aktionen
