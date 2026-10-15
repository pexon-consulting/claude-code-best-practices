# Mitmachen

Verbesserungen sind willkommen: neue Prüfregeln, bessere Erkennung, Korrekturen in den Anleitungen, Übersetzungen.

## Einrichten

```bash
git clone https://github.com/pexon-consulting/claude-code-best-practices
cd claude-code-best-practices
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q
```

## Was in einen Pull Request gehört

- **Neue Regel:** Eintrag in `src/claude_team/regeln.py`, Abschnitt mit Anker in `docs/regeln.md`, Test in `tests/test_regeln.py`. Ein Test schlägt fehl, wenn eins davon fehlt.
- **Hook geändert:** Fall, der greifen soll, und Fall, der durchgehen soll, in `tests/test_hooks.py`.
- **Anleitung:** Jede Aussage über Claude Code mit Link auf die offizielle Doku unter code.claude.com/docs. Ist eine Funktion neu, die Mindestversion nennen. Kopierfertige Beispiele müssen gültiges JSON oder YAML sein.
- **Beispiele:** Ändert sich die Ausgabe der CLI, `python3 scripts/beispiele_bauen.py` laufen lassen und `docs/beispiele.md` mitcommitten.

## Text

Deutsch mit ä, ö, ü und ß, kurze Sätze, Bindestrich statt Gedankenstrich. Keine echten Tokens, IBANs oder Steuer-IDs, auch nicht in Tests. Die Testhelfer in `tests/conftest.py` erzeugen gültige Werte zur Laufzeit.

## Lizenz

Mit einem Pull Request stimmst du zu, dass dein Beitrag unter der MIT-Lizenz des Repos steht.
