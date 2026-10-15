# AGENTS.md und CLAUDE.md: gemeinsame Anweisungen für Claude Code, Codex und Cursor

Claude Code liest eine AGENTS.md seit v2.1.277 selbst, aber standardmäßig nur dann, wenn im Arbeitsverzeichnis und darüber keine CLAUDE.md, keine `.claude/CLAUDE.md` und keine CLAUDE.local.md liegt. Sobald eine CLAUDE.md existiert, ignoriert Claude Code die AGENTS.md. Die robuste, versionsunabhängige Lösung für Repos, in denen mehrere Coding-Agents arbeiten, ist deshalb eine CLAUDE.md, die mit `@AGENTS.md` beginnt und darunter nur Claude-spezifische Ergänzungen enthält.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- AGENTS.md ist das Anweisungsformat, das viele andere Coding-Agents nutzen; Claude Code liest es ab v2.1.277 nativ.
- Liegt eine CLAUDE.md oder CLAUDE.local.md im Arbeitsverzeichnis oder darüber, liest Claude Code nur diese und nicht die AGENTS.md.
- `~/.claude/CLAUDE.md`, die Managed-CLAUDE.md und `.claude/rules/` blockieren das Lesen der AGENTS.md nicht.
- Eine Zeile `@AGENTS.md` am Anfang der CLAUDE.md funktioniert in jeder Version und in jeder Sitzungsart.
- Über die Einstellung **Project instructions** in `/config` lässt sich das Verhalten umschalten, zum Beispiel auf "beide Dateien lesen".
- Das Prüf-CLI dieses Repos meldet mit [CC006](../regeln.md#cc006), wenn eine AGENTS.md neben einer CLAUDE.md liegt und nicht importiert wird.

## Liest Claude Code die AGENTS.md?

Ja, ab v2.1.277, mit einer wichtigen Einschränkung. Die Doku beschreibt das Standardverhalten so:

| Das Repo enthält | Claude Code liest (Standard `claude-md-or-agents-md`) |
| --- | --- |
| AGENTS.md, aber keine CLAUDE.md, `.claude/CLAUDE.md` oder CLAUDE.local.md im Arbeitsverzeichnis oder darüber | die AGENTS.md (auch `.claude/AGENTS.md`) |
| AGENTS.md und eine CLAUDE.md oder CLAUDE.local.md | nur die CLAUDE.md |
| CLAUDE.md mit der Zeile `@AGENTS.md` | die CLAUDE.md samt importierter AGENTS.md |

Was beim Prüfen zählt und was nicht:

- **Zählt als Blocker:** eine `CLAUDE.md`, `.claude/CLAUDE.md` oder `CLAUDE.local.md` im Arbeitsverzeichnis oder in einem Ordner darüber.
- **Zählt nicht:** die eigene `~/.claude/CLAUDE.md`, die Managed-CLAUDE.md der Organisation und Dateien in `.claude/rules/`. Sie laden zusätzlich zur AGENTS.md.
- **Achtung:** Auch eine persönliche `CLAUDE.local.md` blockiert die AGENTS.md. Wer in einem AGENTS.md-Repo eigene Notizen anlegt, schaltet damit für sich die AGENTS.md ab.
- **Nie gelesen:** `AGENTS.local.md`, `AGENTS.override.md` und alles unter einem `.agents/`-Ordner.

Liest Claude Code die AGENTS.md direkt, zeigt eine interaktive Sitzung eine Zeile wie `no CLAUDE.md found; AGENTS.md loaded: /home/you/repo/AGENTS.md`. In Unterordnern lädt Claude Code eine dortige AGENTS.md, sobald Claude eine Datei in diesem Ordner mit dem Read-Tool öffnet und der Ordner keine eigene CLAUDE.md hat.

## Wann liest Claude Code die AGENTS.md nicht?

In diesen Fällen liest Claude Code nur CLAUDE.md-Dateien, und **Project instructions** fehlt in `/config`:

- Claude Code ist älter als v2.1.277.
- Das eingebaute Plugin, das AGENTS.md liest, wurde über `/plugin` abgeschaltet.
- Manchmal in der ersten Sitzung nach einem Update von v2.1.276 oder älter; ab der nächsten Sitzung klappt es.
- Vor v2.1.281 lasen manche Sitzungen, etwa auf Amazon Bedrock oder mit abgeschalteter Telemetrie, gar keine AGENTS.md.

Genau deshalb ist der Import die robusteste Lösung: Er hängt weder von der Version noch von einer Einstellung ab.

## AGENTS.md und CLAUDE.md synchron halten

Es gibt drei Wege. Die Doku empfiehlt für Repos mit Claude-spezifischem Inhalt den Import.

| Weg | Vorteil | Nachteil |
| --- | --- | --- |
| CLAUDE.md mit `@AGENTS.md` | funktioniert in jeder Version, Claude-Ergänzungen möglich | zwei Dateien im Repo |
| Symlink `CLAUDE.md` auf `AGENTS.md` | eine einzige Quelle | unter Windows problematisch, Edit-Tool schreibt nicht durch Symlinks |
| Nur AGENTS.md, keine CLAUDE.md | eine Datei | erst ab v2.1.277, eine CLAUDE.local.md schaltet sie ab |

Zum Symlink nennt die Doku zwei Einschränkungen:

- Die Edit- und Write-Tools schreiben nicht durch einen Symlink. Claude wird dann angewiesen, das Ziel `AGENTS.md` zu bearbeiten.
- Unter Windows braucht ein Symlink Administratorrechte oder den Entwicklermodus, und Git checkt einen committeten Symlink ohne `core.symlinks` als Textdatei aus. Dann steht in der CLAUDE.md nur eine Zeile statt der Anweisungen. Wer Windows-Nutzer im Team hat, nimmt den Import.

## Project instructions umschalten

In einer Sitzung `/config` aufrufen und **Project instructions** auf einen dieser Werte stellen:

| Wert | Was Claude Code liest |
| --- | --- |
| `claude-md-or-agents-md` | CLAUDE.md, oder AGENTS.md, wenn keine CLAUDE.md und keine CLAUDE.local.md da ist (Standard) |
| `claude-md-and-agents-md` | beide; je Ordner zuerst CLAUDE.md, dann AGENTS.md; eine bereits importierte AGENTS.md wird nicht doppelt geladen |
| `claude-md` | nur CLAUDE.md |
| `managed-only` | beim Start nur die Managed-CLAUDE.md und die Auto Memory; Unterordner-Dateien und Rules mit `paths` laden weiter bei Bedarf |

Die Einstellung lässt sich auch in eine Settings-Datei schreiben, und zwar unter `pluginConfigs` mit der Plugin-ID `cc-plugin-agents-md@builtin`. Claude Code liest diesen Eintrag nur aus `~/.claude/settings.json`, aus einer `--settings`-Datei oder aus Managed Settings, nicht aus `.claude/settings.json` im Projekt. Vor v2.1.285 hieß die ID `agents-md@builtin`; ab v2.1.285 werden beide IDs gelesen.

## Unterschiede zwischen AGENTS.md und CLAUDE.md

Eine AGENTS.md, die Claude Code über **Project instructions** liest, verhält sich in drei Punkten anders als eine CLAUDE.md:

| Punkt | CLAUDE.md | AGENTS.md über die Einstellung |
| --- | --- | --- |
| `InstructionsLoaded`-Hooks | feuern | feuern nicht (aber bei importierter AGENTS.md) |
| Ordner aus `--add-dir` mit `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | deren CLAUDE.md lädt | deren AGENTS.md lädt nicht |
| `@`-Import außerhalb des Arbeitsverzeichnisses | Freigabedialog | lädt nur, wenn externe Imports schon freigegeben sind |

`@`-Imports und `claudeMdExcludes` funktionieren in einer AGENTS.md genauso wie in einer CLAUDE.md.

## Beispiele

### Beispiel 1: CLAUDE.md, die AGENTS.md importiert

Die Standardlösung für Repos, in denen Claude Code und andere Agents arbeiten. Claude liest zuerst die importierte Datei, dann den Rest.

```markdown
@AGENTS.md

## Claude Code

- Für Änderungen unter `src/billing/` den Plan Mode nutzen.
- Subagent `code-reviewer` nach jeder größeren Änderung aufrufen.
```

### Beispiel 2: Eine AGENTS.md, die für alle Agents taugt

Werkzeugneutral formuliert, ohne Claude-spezifische Begriffe wie Skills oder Hooks.

````markdown
# Projekt-Anweisungen für Coding-Agents

Rechnungsdienst in Go 1.23 mit PostgreSQL.

## Befehle

```bash
go build ./...
go test ./... -race
golangci-lint run
```

## Konventionen

- Fehler mit `fmt.Errorf("...: %w", err)` umhüllen, nie verschlucken.
- Ein Paket pro Fachbereich unter `internal/`.
- Tabellengetriebene Tests, Dateiname `*_test.go` neben dem Code.

## Grenzen

- Keine echten Kundendaten in Tests, Mails nur an `@example.com`.
- Migrationen unter `migrations/` nur als neue Datei.
````

### Beispiel 3: Symlink statt zweiter Datei

Nur sinnvoll, wenn es keine Claude-spezifischen Inhalte gibt und niemand im Team unter Windows arbeitet.

```bash
ln -s AGENTS.md CLAUDE.md
git add CLAUDE.md
```

Der Befehl gibt bei Erfolg nichts aus. Danach in einer neuen Sitzung `/context` aufrufen und prüfen, ob CLAUDE.md unter **Memory files** steht.

### Beispiel 4: Immer beide Dateien lesen

Für alle, die eine CLAUDE.local.md behalten und trotzdem die AGENTS.md geladen haben wollen. Gehört in `~/.claude/settings.json`.

```json
{
  "pluginConfigs": {
    "cc-plugin-agents-md@builtin": {
      "options": { "instructionFiles": "claude-md-and-agents-md" }
    }
  }
}
```

### Beispiel 5: Gleiche Einstellung für ältere Versionen

Liest auch eine Claude-Code-Version vor v2.1.285 dieselbe Datei, nutzt du die alte Plugin-ID. Neuere Versionen lesen beide.

```json
{
  "pluginConfigs": {
    "agents-md@builtin": {
      "options": { "instructionFiles": "claude-md-and-agents-md" }
    }
  }
}
```

### Beispiel 6: In der CI prüfen, ob die AGENTS.md importiert wird

Ein einfacher Check für die Pipeline, falls das Prüf-CLI nicht genutzt wird.

```bash
if [ -f AGENTS.md ] && [ -f CLAUDE.md ] && ! grep -q '^@AGENTS.md' CLAUDE.md; then
  echo "CLAUDE.md importiert AGENTS.md nicht" >&2
  exit 1
fi
```

Mit dem CLI aus diesem Repo geht es kürzer, die Regel [CC006](../regeln.md#cc006) prüft genau diesen Fall:

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team audit . --schwelle hinweis
```

### Beispiel 7: Anweisungen aus anderen Tools übernehmen

Wer von Codex, Gemini CLI oder Cursor kommt, kann deren Konfiguration einmalig übernehmen. `/import` gibt es ab v2.1.213, den Import aus Cursor ab v2.1.265.

```text
/import codex --dry-run
/import cursor
```

`/import` hängt eine einmalige Kopie von Anweisungsdateien wie AGENTS.md an die passende CLAUDE.md an und übernimmt MCP-Server, Commands, Subagents und Skills. Es ist auf Bedrock, Vertex AI, Foundry und Claude Platform on AWS nicht verfügbar. Ohne gleich zu importieren, liest auch `/init` Cursor-Regeln aus `.cursor/rules/` oder `.cursorrules` sowie `.github/copilot-instructions.md` mit ein.

## Schritt für Schritt: ein Repo für mehrere Agents einrichten

1. Gemeinsame Regeln in die `AGENTS.md` schreiben: Befehle, Aufbau, Konventionen, Grenzen. Keine Claude-spezifischen Begriffe.
2. Eine `CLAUDE.md` anlegen, deren erste Zeile `@AGENTS.md` ist.
3. Darunter nur ergänzen, was Claude Code zusätzlich braucht, etwa Plan Mode für heikle Ordner oder Subagents.
4. Bereichsregeln für Claude Code in `.claude/rules/` ablegen. Sie blockieren die AGENTS.md nicht.
5. Harte Verbote als `deny`-Regel in `.claude/settings.json` eintragen, denn weder AGENTS.md noch CLAUDE.md erzwingen etwas.
6. Neue Sitzung starten und `/memory` oder `/context` aufrufen. Die AGENTS.md muss dort auftauchen.
7. `claude-team audit .` in die CI aufnehmen, damit [CC006](../regeln.md#cc006) einen fehlenden Import meldet.

## Alte Behelfslösungen aufräumen

Viele Teams haben Claude Code schon vor v2.1.277 an die AGENTS.md angebunden. Die Doku sagt, was mit jeder Variante passiert:

| Bisherige Lösung | Was tun |
| --- | --- |
| CLAUDE.md mit `@AGENTS.md` | darf bleiben, die AGENTS.md wird nie doppelt gelesen |
| CLAUDE.md mit dem Satz "lies die AGENTS.md" | ersetzen durch `@AGENTS.md` oder CLAUDE.md löschen; der Satz wirkt nur, wenn Claude die Datei von sich aus öffnet |
| CLAUDE.md als Symlink auf AGENTS.md | nichts tun oder Symlink löschen, der Inhalt wird einmal gelesen |
| SessionStart-Hook, der die AGENTS.md ausgibt | entfernen, sonst steht der Inhalt doppelt im Kontext |

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| CLAUDE.md und AGENTS.md ohne Import | Claude kennt die AGENTS.md-Regeln nicht | `@AGENTS.md` in die CLAUDE.md |
| Persönliche CLAUDE.local.md im AGENTS.md-Repo | AGENTS.md wird für dich nicht mehr gelesen | Import nutzen oder `claude-md-and-agents-md` einstellen |
| `pluginConfigs` in `.claude/settings.json` | Einstellung wirkt nicht | in `~/.claude/settings.json` oder Managed Settings eintragen |
| Symlink im Repo mit Windows-Nutzern | CLAUDE.md enthält nur den Pfad als Text | Import statt Symlink |
| `@AGENTS.md` in Backticks | Import wird nicht ausgeführt | Backticks entfernen |
| Anweisungen in `AGENTS.override.md` | werden nie gelesen | in AGENTS.md oder CLAUDE.md verschieben |

## Häufige Fragen

### Liest Claude Code die AGENTS.md automatisch?

Ja, ab v2.1.277, aber nur, wenn im Arbeitsverzeichnis und darüber keine CLAUDE.md und keine CLAUDE.local.md liegt. Sonst liest es nur die CLAUDE.md, außer **Project instructions** steht auf `claude-md-and-agents-md`.

### AGENTS.md oder CLAUDE.md: welche Datei sollte ich anlegen?

Arbeitet das Team nur mit Claude Code, reicht eine CLAUDE.md. Nutzen mehrere Agents dasselbe Repo, gehören die gemeinsamen Regeln in die AGENTS.md und eine kurze CLAUDE.md importiert sie mit `@AGENTS.md`.

### Wird die AGENTS.md doppelt geladen, wenn ich sie importiere und beide Dateien lesen lasse?

Nein. Laut Doku überspringt Claude Code eine AGENTS.md, die es schon geladen hat, auch wenn die CLAUDE.md sie importiert oder per Symlink darauf zeigt.

### Wie prüfe ich, ob Claude Code meine AGENTS.md geladen hat?

Mit `/memory`: Dort muss der Pfad der AGENTS.md stehen. Vor v2.1.280 zeigten `/memory` und `/context` eine direkt gelesene AGENTS.md nicht an; auf diesen Versionen fragst du Claude nach dem Inhalt der Projekt-Anweisungen.

### Gilt die AGENTS.md auch für Subagents?

Subagents, die ohne Projekt-Anweisungen starten, bekommen auch die AGENTS.md nicht. Das betrifft laut Doku zum Beispiel die eingebauten Subagents Explore und Plan, die ohne CLAUDE.md starten.

## Weiterlesen

- [CLAUDE.md: Aufbau, Beispiele und Best Practices](./claude-md.md)
- [Claude Code Rules in .claude/rules](./claude-code-rules.md)
- [Claude Code Memory und Sitzungen](./claude-code-memory.md)
- [Claude Code vs. Codex und Cursor](./claude-code-vs-codex-cursor.md)
- [Claude Code Subagents](./claude-code-subagents.md)
- Prüfregel [CC006](../regeln.md#cc006), Vorlage [CLAUDE.md](../../src/claude_team/vorlage/CLAUDE.md)
- Offizielle Doku: [AGENTS.md in Claude Code](https://code.claude.com/docs/en/memory)
