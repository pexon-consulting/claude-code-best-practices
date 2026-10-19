#!/usr/bin/env python3
"""PreToolUse-Hook: hält Zugangsdaten aus dem Kontext und aus dem Code.

Blockt
- Lesen, Suchen und Schreiben von .env, Schlüsseldateien und Cloud-Credentials,
- Bash- und PowerShell-Befehle, die solche Dateien nennen, auch in Interpreter-Code
  (python -c "open('.env')"), über Platzhalter (cat .e*v) oder per grep -r über einen
  Ordner, in dem solche Dateien liegen,
- Befehle, die die Umgebung auflisten (env, printenv, export, declare -x, Get-ChildItem env:),
- neuen Code oder Befehle mit echten Tokens (AWS, GitHub, Slack, Anthropic, OpenAI, Stripe, JWT, URL mit Passwort).

Nicht erkannt werden Pfade, die erst zur Laufzeit entstehen (cat $(echo .e""nv),
Variablen, Base64), und Programme, die selbst Dateien öffnen. Ergänzt die deny-Regeln
in .claude/settings.json, ersetzt sie nicht.
"""

from __future__ import annotations

import glob
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _hook  # noqa: E402
import muster  # noqa: E402

UMGEBUNG = re.compile(
    r"(?i)(?:^|[;&|]\s*)(?:(?:/usr)?/bin/env|env|printenv|export(?:\s+-p)?|declare\s+-[a-z]*[xp][a-z]*|typeset\s+-[a-z]*x[a-z]*|set)\s*(?:$|[;&|>])"
    r"|(?:^|[;&|]\s*)(?:get-childitem|gci|ls|dir|get-item|gi)\s+env:\\?\*?\s*(?:$|[;&|>])"
    r"|\[(?:system\.)?environment\]::getenvironmentvariables\("
)
TOKEN_BEFEHLE = re.compile(r"\b(?:gh\s+auth\s+token|aws\s+configure\s+get|gcloud\s+auth\s+print-access-token|az\s+account\s+get-access-token|git\s+credential\s+fill)\b")
# Pfadkandidaten auch in Anführungszeichen, Klammern und Interpreter-Code: open('.env'), readFileSync(".env")
KANDIDAT = re.compile(r"""[^\s'"`()<>,;|&={}\[\]]+""")
# Befehle, die nur prüfen, ob eine Datei da ist, und nichts ausgeben
NUR_METADATEN = {"ls", "test", "[", "[[", "stat", "touch"}
GREP_REKURSIV = re.compile(r"(?:^|[;&|]\s*|\s)(?:grep|egrep|fgrep)\s+(?:[^;&|]*\s)?(?:-[a-zA-Z]*[rR][a-zA-Z]*|--recursive|--dereference-recursive)\b")
# --exclude='.env*' nennt eine Datei, um sie gerade nicht zu lesen
FILTER_OPTIONEN = re.compile(r"""--(?:exclude|exclude-dir|include|glob|iglob)(?:=|\s+)(?:'[^']*'|"[^"]*"|\S+)|\s-g\s+(?:'[^']*'|"[^"]*"|\S+)""")
ORDNER_AUSLASSEN = {".git", "node_modules", ".venv", "venv", "__pycache__", ".tox", "dist", "build"}
MAX_DATEIEN = 20000


def _ist_sensibel(kandidat: str) -> bool:
    return muster.ist_sensibler_pfad(kandidat.lstrip("<").replace("~", "home"))


def _ketten(befehl: str) -> list[str]:
    return [t for t in re.split(r"&&|\|\||;|\||\n", befehl) if t.split()]


def _befehlsteile(befehl: str) -> list[list[str]]:
    return [t.split() for t in _ketten(befehl)]


def _nur_metadaten(teil: str) -> bool:
    """ls .env oder test -f .env geben keinen Inhalt aus. $(...) und `...` können es doch."""
    return Path(teil.split()[0]).name.lower() in NUR_METADATEN and "$(" not in teil and "`" not in teil and "<" not in teil


def _glob_treffer(kandidat: str, basis: Path) -> str:
    if not any(z in kandidat for z in "*?[") or kandidat.startswith(("/", "~")):
        return ""
    try:
        treffer = glob.glob(kandidat, root_dir=basis)
    except (OSError, ValueError):
        return ""
    return next((t for t in treffer[:500] if _ist_sensibel(t)), "")


def _sensible_datei_unter(ordner: Path) -> str:
    """Erste Datei mit Zugangsdaten unter ordner, ohne .git, node_modules und virtuelle Umgebungen."""
    gezaehlt = 0
    for wurzel, ordner_namen, dateien in os.walk(ordner):
        ordner_namen[:] = [o for o in ordner_namen if o not in ORDNER_AUSLASSEN]
        for name in dateien:
            pfad = Path(wurzel, name)
            if muster.ist_sensibler_pfad(pfad.relative_to(ordner).as_posix()):
                return pfad.relative_to(ordner).as_posix()
            gezaehlt += 1
            if gezaehlt > MAX_DATEIEN:
                return ""
    return ""


def _grep_ziele(befehl: str, basis: Path) -> list[Path]:
    """Ordner, die ein rekursives grep durchsucht. Ohne Pfadangabe ist es der Arbeitsordner."""
    ziele = []
    for woerter in _befehlsteile(befehl):
        if Path(woerter[0]).name not in ("grep", "egrep", "fgrep"):
            continue
        argumente = [w.strip("'\"") for w in woerter[1:]]
        positionen = [a for a in argumente if not a.startswith("-")]
        hat_muster_option = any(a in ("-e", "-f") or a.startswith(("--regexp", "--file")) for a in argumente)
        pfade = positionen if hat_muster_option else positionen[1:]
        ziele += [basis / p.replace("~", str(Path.home()), 1) for p in pfade] or [basis]
    return [z for z in ziele if z.is_dir()]


def pruefe_bash(befehl: str, posix: bool = True, basis: Path | None = None) -> str:
    basis = basis or Path.cwd()
    if UMGEBUNG.search(befehl.strip()):
        return "Der Befehl gibt alle Umgebungsvariablen aus, darin stehen oft Tokens. Gezielt eine Variable ohne Wert prüfen, z.B. test -n \"$NAME\"."
    if TOKEN_BEFEHLE.search(befehl):
        return "Der Befehl gibt ein Zugangstoken aus. Tokens gehören nicht in den Verlauf der Sitzung."
    text = _hook.ohne_nachrichten(befehl.replace("\\\n", " ") if posix else befehl)
    for teil in _ketten(FILTER_OPTIONEN.sub(" ", text)):
        if _nur_metadaten(teil):
            continue
        for kandidat in KANDIDAT.findall(teil):
            if _ist_sensibel(kandidat):
                return f"Der Befehl liest {kandidat}. Darin stehen Zugangsdaten. Mit .env.example arbeiten oder den Nutzer bitten, den Wert selbst zu setzen."
            treffer = _glob_treffer(kandidat, basis)
            if treffer:
                return f"Der Platzhalter {kandidat} trifft {treffer}. Darin stehen Zugangsdaten. Datei ausdrücklich ausschließen."
    if GREP_REKURSIV.search(text) and not re.search(r"--exclude[=\s]", text):
        for ordner in _grep_ziele(text, basis):
            datei = _sensible_datei_unter(ordner)
            if datei:
                return (f"grep -r liest auch {datei}. --exclude='.env*' und --exclude-dir=secrets setzen "
                        "oder rg nutzen, das .gitignore und versteckte Dateien standardmäßig auslässt.")
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
        basis = Path(eingabe.get("cwd") or _hook.projektordner(eingabe))
        grund = pruefe_bash(str(tool_input.get("command", "")), posix=werkzeug == "Bash", basis=basis)
        if grund:
            return _hook.entscheide(konfig["modus"], grund)

    funde = muster.finde_secrets(_hook.neuer_inhalt(tool_input))
    if funde:
        liste = ", ".join(sorted({f"{f.art} ({f.vorschau})" for f in funde}))
        _hook.entscheide(konfig["modus"], f"Im neuen Inhalt steht ein Zugangsschlüssel: {liste}. Wert aus einer Umgebungsvariable lesen, nicht in den Code schreiben.")


if __name__ == "__main__":
    _hook.ausfuehren(haupt)
