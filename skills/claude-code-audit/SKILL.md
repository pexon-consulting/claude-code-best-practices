---
name: claude-code-audit
description: "Claude-Code-Konfiguration eines Repos prüfen: CLAUDE.md, .claude/settings.json, Permissions, Hooks, .mcp.json, Subagents, Skills und .gitignore gegen 36 Regeln (CC001 bis CC051), mit Fundstelle und Lösung. Nutzen, wenn jemand fragt, ob die Claude-Code-Einrichtung sicher und vollständig ist, vor einem Team-Rollout oder in einem Review. Englisch: audit Claude Code settings, check permissions, find leaked tokens in .mcp.json."
license: MIT
---

# Claude-Code-Konfiguration prüfen

Teil von Claude Code Best Practices für Teams. Das Audit läuft lokal, liest nur Dateien und schreibt nichts.

## Ablauf

1. Führe im Projektordner aus:
   `uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team audit . --format json`
2. Lies `anzahl` und `befunde`. Jeder Befund hat `regel`, `schwere` (fehler, warnung, hinweis), `datei`, `zeile`, `meldung` und `link`.
3. Fasse zusammen: zuerst alle Fehler mit Datei und Lösung aus `meldung`, dann Warnungen, Hinweise nur als Zahl. Verlinke je Regel auf `link`.
4. Biete an, die Fehler zu beheben. Ändere eine Datei erst nach Zustimmung. Bei CC030 (Schlüssel in einer Datei) und CC050 (.env in Git) sag klar, dass der Schlüssel widerrufen werden muss. Entfernen allein reicht nicht.
5. Nach jeder Korrektur das Audit erneut ausführen und zeigen, dass der Befund weg ist.

## Häufige Korrekturen

- CC013 oder CC014: deny-Regeln in `.claude/settings.json` ergänzen, z.B. `"Read(.env)"`, `"Read(.env.*)"`, `"Read(!.env.example)"`, `"Read(**/*.pem)"`.
- CC012: `"disableBypassPermissionsMode": "disable"` unter `permissions`.
- CC017: `Write(...)` wird zu `Edit(...)`, `Glob(...)` zu `Read(...)`.
- CC023: Hook-Befehle mit `"${CLAUDE_PROJECT_DIR}/..."` beginnen.
- CC032: Klartext-Token durch `${NAME}` ersetzen und den Wert in der Shell setzen.

Fehlt die halbe Einrichtung, schlage den Skill `claude-code-einrichten` vor.

## Grenze

Nur lesen. Keine Datei ändern, ohne zu fragen. Keine Werte aus `.env` oder Schlüsseldateien öffnen, um einen Befund zu bestätigen. Die Meldungen zeigen Schlüssel nur maskiert, gib nie den vollen Wert aus. Regeln mit Begründung: https://github.com/pexon-consulting/claude-code-best-practices/blob/v0.2.0/docs/regeln.md
