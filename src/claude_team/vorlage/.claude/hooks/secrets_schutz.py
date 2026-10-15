#!/usr/bin/env python3
"""PreToolUse-Hook: hält Zugangsdaten aus dem Kontext und aus dem Code.

Blockt
- Lesen, Suchen und Schreiben von .env, Schlüsseldateien und Cloud-Credentials,
- Bash- und PowerShell-Befehle, die solche Dateien ausgeben oder die Umgebung auflisten
  (env, printenv, Get-ChildItem env:),
- neuen Code oder Befehle mit echten Tokens (AWS, GitHub, Slack, Anthropic, OpenAI, Stripe, JWT, URL mit Passwort).

Ergänzt die deny-Regeln in .claude/settings.json, ersetzt sie nicht.
"""

from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _hook  # noqa: E402
import muster  # noqa: E402

LESEBEFEHLE = {
    "cat", "less", "more", "head", "tail", "bat", "nl", "grep", "rg", "ag", "awk", "sed", "cut", "sort", "uniq",
    "strings", "xxd", "hexdump", "od", "base64", "cp", "mv", "scp", "rsync", "tar", "zip", "curl", "open",
    "code", "vim", "vi", "nano", "type", "get-content", "gc", "source", ".",
    "select-string", "sls", "copy-item", "cpi", "copy", "import-csv", "notepad",
}
UMGEBUNG = re.compile(
    r"(?i)(?:^|[;&|]\s*)(?:env|printenv|export\s+-p|set)\s*(?:$|[;&|>])"
    r"|(?:^|[;&|]\s*)(?:get-childitem|gci|ls|dir|get-item|gi)\s+env:\\?\*?\s*(?:$|[;&|>])"
    r"|\[(?:system\.)?environment\]::getenvironmentvariables\("
)
TOKEN_BEFEHLE = re.compile(r"\b(?:gh\s+auth\s+token|aws\s+configure\s+get|gcloud\s+auth\s+print-access-token|az\s+account\s+get-access-token|git\s+credential\s+fill)\b")


def woerter(befehl: str, posix: bool = True) -> list[str]:
    """posix=False für PowerShell: Backslashes in Windows-Pfaden bleiben erhalten."""
    try:
        teile = shlex.split(befehl, posix=posix)
    except ValueError:
        teile = befehl.split()
    return teile if posix else [t.strip("'\"") for t in teile]


def pruefe_bash(befehl: str, posix: bool = True) -> str:
    if UMGEBUNG.search(befehl.strip()):
        return "Der Befehl gibt alle Umgebungsvariablen aus, darin stehen oft Tokens. Gezielt eine Variable ohne Wert prüfen, z.B. test -n \"$NAME\"."
    if TOKEN_BEFEHLE.search(befehl):
        return "Der Befehl gibt ein Zugangstoken aus. Tokens gehören nicht in den Verlauf der Sitzung."
    teile = woerter(befehl, posix)
    hat_lesebefehl = any(Path(t.replace("\\", "/")).name.lower() in LESEBEFEHLE for t in teile) or "<" in befehl
    if hat_lesebefehl:
        for teil in teile:
            kandidat = teil.split("=", 1)[-1].lstrip("<")
            if muster.ist_sensibler_pfad(kandidat.replace("~", "home")):
                return f"Der Befehl liest {kandidat}. Darin stehen Zugangsdaten. Mit .env.example arbeiten oder den Nutzer bitten, den Wert selbst zu setzen."
    return ""


def haupt(eingabe: dict) -> None:
    konfig = _hook.lade_konfig(eingabe)["secrets"]
    werkzeug = eingabe.get("tool_name", "")
    tool_input = eingabe.get("tool_input") or {}
    pfad = _hook.dateipfad(tool_input)
    if pfad and _hook.ausgenommen(eingabe, pfad, konfig["pfade_ausnehmen"]):
        return

    if pfad and muster.ist_sensibler_pfad(pfad):
        name = _hook.relativer_pfad(eingabe, pfad)
        return _hook.entscheide(konfig["modus"], f"{name} enthält Zugangsdaten und ist für Claude gesperrt. Für Beispiele .env.example verwenden.")

    if werkzeug in _hook.SHELL_WERKZEUGE:
        grund = pruefe_bash(str(tool_input.get("command", "")), posix=werkzeug == "Bash")
        if grund:
            return _hook.entscheide(konfig["modus"], grund)

    funde = muster.finde_secrets(_hook.neuer_inhalt(tool_input))
    if funde:
        liste = ", ".join(sorted({f"{f.art} ({f.vorschau})" for f in funde}))
        _hook.entscheide(konfig["modus"], f"Im neuen Inhalt steht ein Zugangsschlüssel: {liste}. Wert aus einer Umgebungsvariable lesen, nicht in den Code schreiben.")


if __name__ == "__main__":
    _hook.ausfuehren(haupt)
