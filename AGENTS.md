# Claude Code Best Practices für Teams

Vorlagen, Anleitungen und eine Prüf-CLI für Teams, die Claude Code einsetzen. Python 3.10 oder neuer, keine Abhängigkeiten außer der Standardbibliothek.

## Befehle

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q                          # alle Tests
.venv/bin/pytest -q tests/test_hooks.py      # nur die Hooks
.venv/bin/claude-team audit .                # das Repo selbst prüfen
python3 scripts/sync_skills.py --check       # Skill-Spiegel aktuell?
python3 scripts/beispiele_bauen.py --check   # docs/beispiele.md aktuell?
```

## Aufbau

- `src/claude_team/` die CLI: `regeln.py` (Prüfregeln CC001 bis CC051), `einrichten.py`, `scannen.py`, `bericht.py` (Text, Markdown, JSON, SARIF), `cli.py`.
- `src/claude_team/vorlage/` was `claude-team einrichten` in ein Projekt kopiert. Die Hooks unter `vorlage/.claude/hooks/` sind dieselben, die das Plugin `team-basis` über `hooks/hooks.json` lädt.
- `vorlage/.claude/hooks/muster.py` ist die einzige Stelle für die Erkennung von Secrets und personenbezogenen Daten. CLI und Hooks nutzen sie beide.
- `skills/` die kanonischen Skills. `.claude/skills/` und `.agents/skills/` sind Kopien, erzeugt mit `python3 scripts/sync_skills.py`.
- `docs/anleitungen/` die Anleitungen, `docs/rollout/` die Freigabe-Unterlagen, `docs/regeln.md` die Regeln mit Ankern.

## Regeln

- Neue Prüfregel: in `regeln.py` mit `regel(...)` anlegen, Abschnitt mit `<a id="ccxxx"></a>` und Tabellenzeile in `docs/regeln.md`, Test `test_ccxxx_...` in `tests/test_regeln.py`. Ein Test prüft, dass alle drei da sind.
- Die Hooks bleiben bei der Standardbibliothek und lassen bei eigenen Fehlern die Aktion durch (Exit 0 ohne Ausgabe).
- Keine echt aussehenden Schlüssel oder Nummern mit gültiger Prüfziffer in Dateien. Tests erzeugen sie zur Laufzeit (`tests/conftest.py`). Erlaubt sind die Testwerte in `muster.TESTWERTE`.
- Fakten über Claude Code nur mit Quelle aus der offiziellen Doku unter code.claude.com/docs und mit Versionsangabe, wenn eine Funktion neu ist.
- Deutsche Texte mit ä, ö, ü, ß und ohne Gedankenstrich.
