---
name: claude-code-einrichten
description: "Claude Code für ein Team einrichten: CLAUDE.md mit erkannten Befehlen, .claude/settings.json mit deny-Regeln, sieben getestete Hooks gegen Secrets, deutsche personenbezogene Daten (IBAN, Steuer-ID) und gefährliche Befehle, Subagents, Skills und .gitignore. Überschreibt nie, bestehende Dateien bekommen einen Vorschlag daneben. Nutzen, wenn ein Repo Claude Code neu bekommt oder die Einrichtung für das Team vereinheitlicht werden soll. Englisch: set up Claude Code for a team, add hooks and settings.json."
license: MIT
---

# Claude Code einrichten

Teil von Claude Code Best Practices für Teams.

## Ablauf

1. Probelauf im Projektordner zeigen, nichts wird geschrieben:
   `uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team einrichten . --dry-run`
2. Erkläre die Liste: `angelegt` ist neu, `vorschlag` heißt, die Datei existiert und daneben entsteht `CLAUDE.vorschlag.md` oder `.claude/settings.vorschlag.json`, `bleibt` heißt, eine eigene Version wird nicht angefasst, `ergänzt` gilt für `.gitignore`.
3. Frage, welche Bausteine weg sollen. Möglich mit `--ohne`: `claude-md`, `settings`, `hooks`, `regeln`, `agents`, `skills`, `mcp`, `gitignore`. Für Teams mit strengem Datenschutz `--profil streng` anbieten (sperrt WebFetch, WebSearch, curl, wget, ssh).
4. Nach Zustimmung ohne `--dry-run` ausführen.
5. Gibt es Vorschläge, zeige den Unterschied, z.B. `diff .claude/settings.json .claude/settings.vorschlag.json`, und übernimm Teile nur nach Rückfrage. Danach die Vorschlagsdatei löschen.
6. Platzhalter in `CLAUDE.md` wie `{{EIN_SATZ_WAS_DAS_PROJEKT_TUT}}` gemeinsam füllen. Was du aus dem Code sicher ablesen kannst, schlägst du vor, den Rest fragst du.
7. Wenn es einen Testbefehl gibt, frage, ob der Stop-Hook ihn vor dem Abschluss laufen lassen soll, und trage ihn in `.claude/schutz.json` unter `stopp.befehl` ein.
8. Zum Schluss `claude-team audit .` ausführen und das Ergebnis zeigen.

## Hooks testen

Jeder Hook liest JSON auf stdin. So lässt sich die Wirkung ohne Claude zeigen:

```bash
echo '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | python3 .claude/hooks/secrets_schutz.py
```

Erwartet ist eine Antwort mit `"permissionDecision": "deny"`.

## Grenze

Nichts überschreiben. Keine Werte aus `.env` lesen, um Befehle zu erkennen. Die Hooks brauchen `python3` ab 3.10 auf dem Rechner jeder Person im Team. Ausnahmen für Testdaten gehören in `.claude/schutz.json` unter `pfade_ausnehmen`, nicht in eine abgeschaltete Regel.
