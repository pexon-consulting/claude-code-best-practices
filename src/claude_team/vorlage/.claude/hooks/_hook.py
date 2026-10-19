"""Gemeinsame Basis für alle Hooks: Eingabe lesen, Konfiguration laden, Entscheidung ausgeben.

Claude Code schickt je Ereignis ein JSON-Objekt auf stdin. Ein Hook antwortet mit
Exit 0 und JSON auf stdout. Läuft ein Hook selbst auf einen Fehler, lässt er die
Aktion durch (Exit 0 ohne Ausgabe), damit ein kaputter Hook niemanden aussperrt.
"""

from __future__ import annotations

import json
import os
import re
import sys
from fnmatch import fnmatch
from pathlib import Path

STANDARD = {
    "secrets": {"modus": "deny", "pfade_ausnehmen": []},
    "pii": {"modus": "deny", "kontakte_ab": 5, "pfade_ausnehmen": []},
    "befehle": {"modus": "deny", "fragen_bei": ["git push", "npm publish", "terraform apply", "kubectl delete"]},
    "protokoll": {"aktiv": False, "ordner": ".claude/protokoll", "aufbewahrung_tage": 30},
    "stopp": {"befehl": ""},
}
SHELL_WERKZEUGE = ("Bash", "PowerShell")
DATEIFELDER = ("file_path", "notebook_path", "path")
INHALTSFELDER = ("content", "new_string", "new_source", "command", "prompt")
# Commit- und Tag-Nachrichten: der Text ist kein Befehl, z.B. git commit -m "fix: rm -rf / verhindern"
NACHRICHT = re.compile(r"""(\s(?:-m|--message)(?:\s+|=))("(?:[^"\\]|\\.)*"|'[^']*')""", re.S)
# "$(cat <<'EOF' ... EOF)" ist wörtlicher Text; andere $(...) und `...` führt die Shell aus
HEREDOC_TEXT = re.compile(r"""^"\$\(cat\s+<<-?\s*'(\w+)'\n.*\n\1\s*\)"$""", re.S)


def ohne_nachrichten(befehl: str) -> str:
    """Ersetzt wörtliche Nachrichten nach -m oder --message durch "". Nachrichten mit $(...) bleiben."""
    def ersetze(m: re.Match[str]) -> str:
        text = m.group(2)
        woertlich = text.startswith("'") or not ("$(" in text or "`" in text) or HEREDOC_TEXT.match(text)
        return m.group(1) + '""' if woertlich else m.group(0)
    return NACHRICHT.sub(ersetze, befehl)


def lies_eingabe() -> dict:
    try:
        daten = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}
    return daten if isinstance(daten, dict) else {}


def projektordner(eingabe: dict) -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or eingabe.get("cwd") or os.getcwd())


def lade_konfig(eingabe: dict) -> dict:
    """Standard plus .claude/schutz.json des Projekts. Fehlerhafte Datei: Standard bleibt."""
    konfig = {k: dict(v) for k, v in STANDARD.items()}
    datei = projektordner(eingabe) / ".claude" / "schutz.json"
    try:
        eigen = json.loads(datei.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return konfig
    for bereich, werte in eigen.items():
        if bereich in konfig and isinstance(werte, dict):
            konfig[bereich].update(werte)
    return konfig


def relativer_pfad(eingabe: dict, pfad: str) -> str:
    if not pfad:
        return ""
    try:
        return Path(pfad).resolve().relative_to(projektordner(eingabe).resolve()).as_posix()
    except (ValueError, OSError):
        return Path(pfad).as_posix()


def ausgenommen(eingabe: dict, pfad: str, muster: list[str]) -> bool:
    rel = relativer_pfad(eingabe, pfad)
    return bool(rel) and any(fnmatch(rel, m) for m in muster)


def dateipfad(tool_input: dict) -> str:
    for feld in DATEIFELDER:
        wert = tool_input.get(feld)
        if isinstance(wert, str) and wert:
            return wert
    return ""


def neuer_inhalt(tool_input: dict) -> str:
    """Alles, was ein Tool neu schreiben oder ausführen würde. Alter Text (old_string) zählt nicht."""
    teile = [tool_input[f] for f in INHALTSFELDER if isinstance(tool_input.get(f), str)]
    for edit in tool_input.get("edits") or []:
        if isinstance(edit, dict) and isinstance(edit.get("new_string"), str):
            teile.append(edit["new_string"])
    return "\n".join(teile)


def entscheide(modus: str, grund: str, ereignis: str = "PreToolUse") -> None:
    """PreToolUse: deny oder ask. Andere Ereignisse: block. Modus 'aus' gibt nichts aus."""
    if modus not in ("deny", "ask"):
        return
    if ereignis == "PreToolUse":
        antwort = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": modus, "permissionDecisionReason": grund}}
    else:
        antwort = {"decision": "block", "reason": grund}
    print(json.dumps(antwort, ensure_ascii=False))


def kontext(ereignis: str, text: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": ereignis, "additionalContext": text[:9000]}}, ensure_ascii=False))


def ausfuehren(haupt) -> None:
    """Startet einen Hook. Unerwartete Fehler gehen nach stderr, die Aktion läuft weiter."""
    try:
        haupt(lies_eingabe())
    except Exception as fehler:  # noqa: BLE001
        print(f"Hook-Fehler ({Path(sys.argv[0]).name}): {fehler}", file=sys.stderr)
    sys.exit(0)
