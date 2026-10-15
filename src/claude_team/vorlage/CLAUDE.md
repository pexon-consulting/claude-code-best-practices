# {{PROJEKT}}

{{EIN_SATZ_WAS_DAS_PROJEKT_TUT}}

## Befehle

```bash
{{INSTALL}}      # Abhängigkeiten installieren
{{TEST}}         # Tests, vor jedem Commit
{{LINT}}         # Lint und Format
{{START}}        # lokal starten
```

## Aufbau

- `src/` Anwendungscode
- `tests/` Tests, gleiche Ordnerstruktur wie `src/`
- `docs/` Entscheidungen und Architektur

## Arbeitsweise

- Vor größeren Änderungen erst einen Plan zeigen und auf Freigabe warten.
- Kleine Commits, Nachricht im Imperativ: `fix: leere Liste im Export abfangen`.
- Neue Funktion heißt neuer Test. Ein Bugfix bekommt zuerst einen Test, der den Fehler zeigt.
- Nie auf `main` committen. Branch: `feat/...`, `fix/...`.
- Keine neuen Abhängigkeiten ohne Rückfrage.

## Grenzen

- Keine echten Kundendaten in Code, Tests oder Prompts. Testdaten erfinden.
- `.env` und Schlüsseldateien nicht lesen. Neue Variablen in `.env.example` eintragen.
- Datenbank-Migrationen nur als neue Datei, nie eine bestehende ändern.

## Fallen

- {{BEKANNTE_FALLE_1}}
- {{BEKANNTE_FALLE_2}}
