#!/usr/bin/env python3
"""PreToolUse-Hook für Bash und PowerShell: blockt zerstörerische Befehle, fragt bei riskanten nach.

Permission-Regeln wie "Bash(rm -rf:*)" greifen nur am Anfang eines Befehls.
Dieser Hook prüft jeden Teil einer Kette (&&, ||, ;, |) und erkennt auch
"cd /tmp && rm -rf ~", "git -C . push --force", "git push origin +main",
"curl ... | sh", "bash <(curl ...)", "bash -c '...'" und "Remove-Item ~ -Recurse -Force".
Text in Commit-Nachrichten (-m "...") zählt nicht als Befehl.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _hook  # noqa: E402

# git mit globalen Optionen vor dem Unterbefehl, z.B. "git -C repo -c core.x=y push"
GIT = r"\bgit(?:\s+(?:-[cC]\s+\S+|--[\w-]+(?:=\S+)?|-[pP]))*\s+"
NETZ = r"(?:curl|wget)\b"

SPERREN: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\brm\s+(?:-[a-zA-Z]*\s+)*-[a-zA-Z]*[rR][a-zA-Z]*\s+(?:-[a-zA-Z]+\s+)*(?:/|~|\$HOME|/\*|\.\.?/?|\*)(?:\s|$)"),
     "rm -r auf Wurzel, Home, Arbeitsordner oder * löscht zu viel. Gezielt einzelne Pfade löschen."),
    (re.compile(GIT + r"push\b[^;&|]*(?:\s--force(?!-with-lease|-if-includes)\b|\s-(?!-)[a-zA-Z]*f[a-zA-Z]*\b|\s\+\S+)"),
     "git push --force (auch -f oder +branch) überschreibt fremde Commits. --force-with-lease nutzen oder den Nutzer pushen lassen."),
    (re.compile(GIT + r"(?:commit|push|merge|rebase)\b[^;&|]*\s--no-verify\b"),
     "--no-verify überspringt die Git-Hooks des Teams (Lint, Tests, Secret-Scan). Ursache beheben statt umgehen."),
    (re.compile(r"\b" + NETZ + r"[^|;&]*\|\s*(?:sudo\s+)?(?:ba|z|da)?sh\b"
                r"|\b(?:(?:ba|z|da)?sh|source|eval)\s+(?:-\w+\s+)*[\"']?\$\(\s*" + NETZ +
                r"|(?:\b(?:ba|z|da)?sh|\bsource|(?:^|[;&|]\s*)\.)\s+<\(\s*" + NETZ +
                r"|(?i:\b(?:iwr|irm|invoke-webrequest|invoke-restmethod|curl|wget)\b[^;&]*\|\s*(?:iex|invoke-expression)\b)"
                r"|(?i:\b(?:iex|invoke-expression)\b[^;&|]*\bdownloadstring\b)"),
     "Ein Skript aus dem Netz direkt ausführen ist nicht nachvollziehbar. Erst herunterladen und lesen."),
    (re.compile(r"\bchmod\s+(?:-R\s+)?0?777\b"), "chmod 777 macht Dateien für alle schreibbar. Passende Rechte setzen, z.B. 644 oder 755."),
    (re.compile(r"\b(?:mkfs(?:\.\w+)?|fdisk|diskutil\s+erase\w*)\b|\bdd\b[^;&|]*\bof=/dev/|(?i:\b(?:format-volume|clear-disk|initialize-disk)\b)"),
     "Befehl formatiert oder überschreibt Datenträger."),
    (re.compile(r":\(\)\s*\{\s*:\|:&\s*\};:"), "Fork-Bombe."),
)
NACHFRAGEN: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\brm\s+(?:-[a-zA-Z]*\s+)*-[a-zA-Z]*[rR]"), "rekursives Löschen"),
    (re.compile(r"(?i)\b(?:remove-item|ri|del|rd|rmdir|erase)\b[^;&|]*\s-r(?:ecurse)?\b"), "rekursives Löschen"),
    (re.compile(r"(?i)\bstart-process\b[^;&|]*-verb\s+runas\b"), "Start mit Administratorrechten"),
    (re.compile(GIT + r"reset\s+--hard\b"), "git reset --hard verwirft lokale Änderungen"),
    (re.compile(GIT + r"clean\s+-[a-zA-Z]*f"), "git clean löscht ungetrackte Dateien"),
    (re.compile(GIT + r"(?:checkout|restore)\s+(?:--\s+)?\.(?:\s|$)"), "verwirft alle ungespeicherten Änderungen"),
    (re.compile(GIT + r"branch\s+-D\b"), "löscht einen Branch ohne Merge-Prüfung"),
    (re.compile(GIT + r"push\b[^;&|]*--force-(?:with-lease|if-includes)\b"), "Force-Push"),
    (re.compile(r"\bsudo\b"), "sudo"),
    (re.compile(r"(?i)\b(?:drop\s+(?:database|schema|table)|truncate\s+table)\b"), "löscht Datenbankinhalte"),
    (re.compile(r"\b(?:terraform|tofu)\s+(?:destroy|apply\s+[^;&|]*-auto-approve)\b"), "ändert Infrastruktur ohne Plan-Freigabe"),
)


LOESCHBEFEHLE = {"rm", "remove-item", "ri", "del", "rd", "rmdir", "erase"}
GEFAEHRLICHE_ZIELE = {
    "/", "/*", "~", "~/", "~/*", "~\\", "~\\*", "$home", "$home/", "$home/*", "${home}", "${home}/", "${home}/*",
    "$env:userprofile", "*", ".", "./", "./*", ".\\", "..", "c:", "c:\\", "c:/", "\\",
}
LOESCH_GRUND = "rm -r auf Wurzel, Home, Arbeitsordner oder * löscht zu viel. Gezielt einzelne Pfade löschen."
GIT_OPTIONEN = re.compile(r"^git(?:\s+(?:-[cC]\s+\S+|--[\w-]+(?:=\S+)?|-[pP]))+\s+")
# Inhalt von bash -c "...", sh -c '...', eval "...", $(...) und `...` wird wie ein eigener Befehl geprüft
INNERER_BEFEHL = re.compile(r"""\b(?:(?:ba|z|da)?sh\s+(?:-\w+\s+)*-c|eval)\s+(?:"((?:[^"\\]|\\.)*)"|'([^']*)')|\$\(([^()]*)\)|`([^`]*)`""", re.S)


def teile(befehl: str) -> list[str]:
    return re.split(r"&&|\|\||;|\||\n", befehl)


def loescht_zu_viel(befehl: str) -> bool:
    """Rekursives Löschen mit gefährlichem Ziel, egal in welcher Reihenfolge Optionen und Ziel stehen."""
    for teil in teile(befehl):
        woerter = teil.split()
        if woerter and woerter[0].lower() == "sudo":
            woerter = woerter[1:]
        if not woerter or woerter[0].lower() not in LOESCHBEFEHLE:
            continue
        optionen = [w.lower() for w in woerter[1:] if w.startswith("-")]
        if woerter[0].lower() == "rm":
            # Kurzoptionen wie -rf oder -fR; in PowerShell ist rm ein Alias, dort steht -Recurse
            rekursiv = any(o == "--recursive" or (not o.startswith("--") and "r" in o[1:]) for o in optionen)
        else:
            rekursiv = any(o.startswith("-r") for o in optionen)
        ziele = {w.strip("'\"").lower() for w in woerter[1:] if not w.startswith("-")}
        if rekursiv and ziele & GEFAEHRLICHE_ZIELE:
            return True
    return False


def pruefe(befehl: str, fragen_bei: list[str], tiefe: int = 0) -> tuple[str, str]:
    befehl = _hook.ohne_nachrichten(befehl)
    if tiefe < 3:
        for m in INNERER_BEFEHL.finditer(befehl):
            innen = next(g for g in m.groups() if g is not None)
            stufe, grund = pruefe(innen, fragen_bei, tiefe + 1)
            if stufe == "deny":
                return stufe, grund
    if loescht_zu_viel(befehl):
        return "deny", LOESCH_GRUND
    for muster, grund in SPERREN:
        if muster.search(befehl):
            return "deny", grund
    for muster, grund in NACHFRAGEN:
        if muster.search(befehl):
            return "ask", f"Riskanter Befehl ({grund}). Bitte bestätigen."
    for teil in teile(befehl):
        teil = GIT_OPTIONEN.sub("git ", teil.strip())
        for praefix in fragen_bei:
            if teil == praefix or teil.startswith(praefix + " "):
                return "ask", f"'{praefix}' ist im Team freigabepflichtig (.claude/schutz.json, befehle.fragen_bei)."
    return "", ""


def haupt(eingabe: dict) -> None:
    if eingabe.get("tool_name") not in _hook.SHELL_WERKZEUGE:
        return
    konfig = _hook.lade_konfig(eingabe)["befehle"]
    befehl = str((eingabe.get("tool_input") or {}).get("command", ""))
    stufe, grund = pruefe(befehl, list(konfig.get("fragen_bei") or []))
    if stufe == "deny":
        _hook.entscheide(konfig["modus"], grund)
    elif stufe == "ask" and konfig["modus"] != "aus":
        _hook.entscheide("ask", grund)


if __name__ == "__main__":
    _hook.ausfuehren(haupt)
