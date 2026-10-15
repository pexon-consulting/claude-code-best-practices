"""Gemeinsame Helfer. Gültige Nummern und Schlüssel entstehen erst zur Laufzeit,
damit im Repo nichts steht, das wie ein echter Wert aussieht."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from claude_team.projekt import VORLAGE, lade_muster

HOOKS = VORLAGE / ".claude" / "hooks"
muster = lade_muster()


# --- Testwerte mit gültiger Prüfziffer ----------------------------------------

def iban(blz: str = "10020030", konto: str = "0012345678", land: str = "DE") -> str:
    zahl = "".join(str(int(z, 36)) for z in blz + konto + land + "00")
    return f"{land}{98 - int(zahl) % 97:02d}{blz}{konto}"


def steuer_id(basis: str = "6589471236") -> str:
    """basis: 10 Ziffern, erste nicht 0, genau eine Ziffer doppelt."""
    return basis + str(muster.mod_11_10(basis))


def ust_id(basis: str = "81234567") -> str:
    return "DE" + basis + str(muster.mod_11_10(basis))


def svnr(bereich: str = "65", datum: str = "170839", buchstabe: str = "J", serie: str = "00") -> str:
    ziffern = bereich + datum + f"{ord(buchstabe) - 64:02d}" + serie
    gewichte = (2, 1, 2, 5, 7, 1, 2, 1, 2, 1, 2, 1)
    summe = sum(sum(int(q) for q in str(int(z) * g)) for z, g in zip(ziffern, gewichte))
    return f"{bereich}{datum}{buchstabe}{serie}{summe % 10}"


def karte(anfang: str = "4920193847561") -> str:
    """Luhn-gültige Nummer mit 16 Stellen."""
    roh = (anfang + "000000000000000")[:15]
    for pruef in "0123456789":
        if muster.luhn_gueltig(roh + pruef):
            return roh + pruef
    raise AssertionError("keine Prüfziffer gefunden")


def aws_schluessel() -> str:
    return "AK" + "IA" + "QWERTZUIOPLKJHGF"


def github_token() -> str:
    return "gh" + "p_" + "a1B2c3D4e5F6g7H8i9J0" * 2


def anthropic_schluessel() -> str:
    return "sk-" + "ant-" + "api03-" + "Zq7Wm2Lp9Rt4Vb8Nc6Xk" * 2


# --- Hooks als Subprozess -----------------------------------------------------

def hook(name: str, eingabe: dict | str, projekt: Path) -> tuple[int, dict | None, str]:
    """Startet einen Hook wie Claude Code: JSON auf stdin, Projektordner in der Umgebung."""
    text = eingabe if isinstance(eingabe, str) else json.dumps(eingabe)
    umgebung = {**os.environ, "CLAUDE_PROJECT_DIR": str(projekt)}
    lauf = subprocess.run([sys.executable, str(HOOKS / name)], input=text, capture_output=True, text=True, env=umgebung, timeout=60, check=False)
    ausgabe = json.loads(lauf.stdout) if lauf.stdout.strip() else None
    return lauf.returncode, ausgabe, lauf.stderr


def werkzeug(name: str, projekt: Path, **tool_input) -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": name, "tool_input": tool_input, "cwd": str(projekt), "session_id": "abcdef123456"}


def entscheidung(ausgabe: dict | None) -> str:
    """deny, ask, block oder '' (keine Ausgabe)."""
    if not ausgabe:
        return ""
    if "hookSpecificOutput" in ausgabe and "permissionDecision" in ausgabe["hookSpecificOutput"]:
        return ausgabe["hookSpecificOutput"]["permissionDecision"]
    return ausgabe.get("decision", "")


def git(ordner: Path, *argumente: str) -> None:
    subprocess.run(["git", *argumente], cwd=ordner, capture_output=True, check=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"})


def schreibe(ordner: Path, relativ: str, inhalt: str | dict) -> Path:
    pfad = ordner / relativ
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(inhalt if isinstance(inhalt, str) else json.dumps(inhalt, indent=2), encoding="utf-8")
    return pfad


@pytest.fixture
def projekt(tmp_path: Path) -> Path:
    """Leeres Git-Repo."""
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "core.excludesFile", os.devnull)
    return tmp_path
