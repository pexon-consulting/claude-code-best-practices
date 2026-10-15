# Claude Code Memory: Kontext, /compact und Sitzungen steuern

Claude Code startet jede Sitzung mit leerem Kontextfenster und trägt Wissen auf zwei Wegen weiter: über CLAUDE.md-Dateien, die du schreibst, und über die Auto Memory, in der Claude selbst Notizen ablegt (`MEMORY.md`, davon die ersten 200 Zeilen oder 25 KB pro Sitzung). Innerhalb einer Sitzung steuerst du den Kontext mit `/context`, `/compact` und `/clear`, zwischen Sitzungen mit `claude --continue` und `claude --resume`, und Fehler machst du mit Checkpoints und `/rewind` rückgängig. `/compact` nutzt du, wenn eine lange Sitzung weitergehen soll, `/clear`, wenn die nächste Aufgabe nichts mit der bisherigen zu tun hat.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Die Auto Memory ist lokal standardmäßig an und liegt unter `~/.claude/projects/<project>/memory/`, mit `MEMORY.md` als Index.
- Von `MEMORY.md` lädt Claude Code beim Start die ersten 200 Zeilen oder 25 KB, je nachdem, was zuerst erreicht ist; Themendateien liest Claude bei Bedarf.
- `/context` zeigt, was den Kontext belegt und welche CLAUDE.md- und Memory-Dateien geladen sind.
- `/compact` fasst das Gespräch zusammen und gibt Platz frei, `/clear` startet ein neues Gespräch mit leerem Kontext.
- `claude --continue` setzt das letzte Gespräch im Ordner fort, `claude --resume` öffnet eine Auswahl oder eine benannte Sitzung.
- Vor jedem Prompt legt Claude Code einen Checkpoint an; `/rewind` oder zweimal `Esc` stellt Code und Gespräch wieder her, aber keine Änderungen durch Bash-Befehle.

## Wie merkt sich Claude Code Wissen zwischen Sitzungen?

| | CLAUDE.md | Auto Memory |
| --- | --- | --- |
| Wer schreibt | du | Claude |
| Inhalt | Anweisungen und Regeln | Erkenntnisse und Muster |
| Gültigkeit | Projekt, Nutzer oder Organisation | pro Repository, über Worktrees hinweg geteilt |
| Geladen | in jeder Sitzung | in jeder Sitzung (erste 200 Zeilen oder 25 KB) |
| Geeignet für | Coding-Standards, Abläufe, Architektur | deine Vorlieben, Korrekturen, Kontext, der nicht im Code steht |

Beides ist Kontext, keine erzwungene Konfiguration. Was immer passieren muss, gehört in einen [Hook](./claude-code-hooks.md). Wie du die CLAUDE.md aufbaust, steht in der Anleitung [CLAUDE.md](./claude-md.md).

## Auto Memory: was Claude sich selbst notiert

Claude legt vier Arten von Notizen an und schreibt die Art als `type` ins Frontmatter der Datei:

- `user`: deine Rolle, dein Wissen, deine Arbeitsweise
- `feedback`: Korrekturen und bestätigte Vorgehensweisen
- `project`: laufende Arbeit, Fristen, Entscheidungen, die nicht aus Code oder Git hervorgehen
- `reference`: wo Informationen außerhalb des Projekts liegen, etwa Issue-Tracker oder Dashboard

Was Claude aus dem Code ableiten kann oder was schon in einer CLAUDE.md steht, speichert es nicht. Meldungen wie "Saved 2 memories" oder "Recalled 2 memories" zeigen, dass Claude gerade schreibt oder liest.

So sieht der Ordner aus:

```text
~/.claude/projects/<project>/memory/
├── MEMORY.md           # Index, one line per memory, loaded into every session
├── user_role.md        # One memory
├── feedback_testing.md # One memory
└── ...                 # Any other topic files Claude creates
```

Wichtige Eigenschaften:

- Der Ordner `<project>` wird aus dem Git-Repository abgeleitet. Alle Worktrees und Unterordner eines Repos teilen sich eine Auto Memory.
- Die Auto Memory ist maschinenlokal. Sie wird nicht zwischen Rechnern oder in Cloud-Umgebungen geteilt.
- Liegt `MEMORY.md` nahe am Limit, erinnert Claude Code Claude daran zu kürzen. Ist sie darüber, klappt das Schreiben, aber Claude bekommt einen Fehler mit der Aufforderung, den Index neu zu schreiben, denn alles nach dem Limit fällt beim nächsten Laden weg.
- Die Aufräumfrist `cleanupPeriodDays` löscht alte Transkripte, aber nicht die Memory-Dateien.
- Subagents bekommen die Auto Memory des Hauptgesprächs nicht, außer bei einem Fork.

**Etwas merken lassen:** "remember that the API tests require a local Redis instance" landet in der Auto Memory. Soll es in die CLAUDE.md, sagst du "add this to CLAUDE.md" oder bearbeitest die Datei über `/memory`.

**Ansehen und bearbeiten:** `/memory` listet CLAUDE.md, CLAUDE.local.md und die Memory-Orte, öffnet Dateien im Editor, hat einen Schalter für die Auto Memory und öffnet auf Wunsch den Memory-Ordner. Alle Dateien sind normales Markdown.

**Abschalten:** über den Schalter in `/memory` (schreibt `autoMemoryEnabled` in `~/.claude/settings.json`), pro Projekt mit `"autoMemoryEnabled": false` in den Projekt-Settings oder mit der Variable `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

## Kontext in der Sitzung steuern

| Befehl | Was er tut | Wann |
| --- | --- | --- |
| `/context` | zeigt die Belegung als Raster mit Hinweisen, welche Tools, Memory-Dateien oder Kapazitäten auffallen; `/context all` klappt alles aus | wenn Antworten schlechter werden oder vor einer großen Aufgabe |
| `/compact [anweisungen]` | fasst das bisherige Gespräch zusammen, optional mit Fokus | lange Sitzung, gleiche Aufgabe geht weiter |
| `/clear [name]` | neues Gespräch mit leerem Kontext; Aliase `/reset`, `/new` | Wechsel zu einer unabhängigen Aufgabe |
| `/autocompact [auto\|<tokens>]` | legt fest, ab welcher Füllung automatisch komprimiert wird (ab v2.1.221) | wenn die automatische Komprimierung zu spät kommt |
| `/btw [frage]` | Seitenfrage zur Sitzung, ohne das Gespräch zu verlängern | kurze Rückfrage zwischendurch |
| `/memory` | CLAUDE.md und Auto Memory öffnen und bearbeiten | Notizen prüfen oder korrigieren |

Claude Code komprimiert automatisch, wenn das Kontextfenster voll wird, eine volle Sitzung endet also nicht. Ein gezieltes `/compact` mit Fokus ist trotzdem oft besser, weil du bestimmst, was die Zusammenfassung behält. Die Doku nennt außerdem: große Lese-Aufgaben an einen [Subagent](./claude-code-subagents.md) geben, damit die Dateiinhalte in dessen Kontext bleiben.

### Was überlebt /compact?

| Inhalt | Nach der Komprimierung |
| --- | --- |
| CLAUDE.md im Projekt-Root und Regeln ohne `paths` | neu von der Platte eingelesen |
| Auto Memory | neu von der Platte eingelesen |
| Plan aus dem Plan Mode | neu von der Platte eingelesen |
| Regeln mit `paths` und CLAUDE.md in Unterordnern | laden erst wieder, wenn Claude passende Dateien anfasst |
| Gelesene oder bearbeitete Dateien | bis zu fünf, die zuletzt geänderten zuerst, werden neu gelesen |
| Aufgerufene Skills | wieder eingefügt, je Skill bis 5.000 Tokens, zusammen bis 25.000 |
| Nur im Gespräch gegebene Anweisungen | nur noch als Teil der Zusammenfassung |

Geht nach `/compact` eine Anweisung verloren, stand sie meist nur im Chat. Dann gehört sie in die CLAUDE.md.

## Sitzungen fortsetzen: --continue und --resume

| Aufruf | Wirkung |
| --- | --- |
| `claude -c` oder `claude --continue` | lädt das letzte Gespräch im aktuellen Ordner; Sitzungen aus `claude -p` und dem Agent SDK werden übersprungen |
| `claude -r` oder `claude --resume` | öffnet eine Auswahl der Sitzungen |
| `claude --resume <id-oder-name>` | setzt eine bestimmte Sitzung fort |
| `claude -r "auth-refactor" "Finish this PR"` | setzt fort und schickt gleich einen Prompt |
| `claude --resume <id> --fork-session` | setzt fort, aber mit neuer Sitzungs-ID, das Original bleibt unverändert |
| `claude -n "mein-feature"` | gibt der Sitzung beim Start einen Namen für `/resume` |

In der Sitzung selbst gibt es `/resume` (Alias `/continue`), `/rename` zum Umbenennen und `/branch`, um an der aktuellen Stelle eine Abzweigung des Gesprächs anzulegen und hineinzuwechseln; das Original bleibt über `/resume` erreichbar.

Transkripte liegen lokal im Klartext unter `~/.claude/projects/` und werden nach `cleanupPeriodDays` gelöscht (Standard 30 Tage). Danach taucht eine Sitzung nicht mehr in der Auswahl auf.

## Checkpoints und /rewind

Vor jedem Prompt, der einen Turn startet, sichert Claude Code den Stand der Dateien, die Claude mit seinen Datei-Tools bearbeitet. Pro Sitzung bleiben die Snapshots der letzten 100 Checkpoints. Checkpoints werden mit dem Gespräch gespeichert, `/rewind` funktioniert also auch nach dem Fortsetzen einer Sitzung.

`/rewind` (Aliase `/checkpoint`, `/undo`) oder zweimal `Esc` bei leerer Eingabe öffnet das Menü. Dort wählst du einen früheren Prompt und dann:

| Aktion | Wirkung |
| --- | --- |
| Restore code and conversation | Code und Gespräch auf diesen Punkt zurück |
| Restore conversation | Gespräch zurück, Code bleibt |
| Restore code | Dateien zurück, Gespräch bleibt |
| Summarize from here | ab hier zusammenfassen, frühere Anweisungen bleiben vollständig |
| Summarize up to here | bis hier zusammenfassen, spätere Nachrichten bleiben |

Grenzen laut Doku:

- Änderungen durch Bash-Befehle (`rm`, `mv`, `cp`) werden nicht erfasst.
- Änderungen außerhalb von Claude Code und aus parallelen Sitzungen werden normalerweise nicht erfasst.
- Bearbeitungen von Subagents werden meist nicht zurückgesetzt, außer bei einem Skill mit `context: fork` im Vordergrund.
- Symlinks und Hardlinks werden beim Wiederherstellen übersprungen.
- Checkpoints ersetzen keine Versionskontrolle. Für dauerhafte Stände bleibt Git zuständig.

Abschalten lässt sich das mit `"fileCheckpointingEnabled": false` oder für eine Sitzung mit `CLAUDE_CODE_DISABLE_FILE_CHECKPOINTING`.

## Wann nutze ich was?

| Situation | Werkzeug |
| --- | --- |
| Eine Regel soll in jeder Sitzung für alle gelten | CLAUDE.md |
| Claude soll sich eine persönliche Vorliebe merken | "remember ..." (Auto Memory) |
| Kontext wird voll, die Aufgabe geht weiter | `/compact` mit Fokus |
| Nur der Anfang einer langen Debug-Sitzung ist noch wichtig | `/rewind` und "Summarize from here" |
| Neue, unabhängige Aufgabe | `/clear` |
| Gestern abgebrochen, heute weiter | `claude --continue` |
| Alternative ausprobieren, ohne das Original zu verlieren | `/branch` oder `claude --continue --fork-session` |
| Claude hat gerade Mist gebaut | zweimal `Esc`, "Restore code and conversation" |
| Kurze Frage nebenbei | `/btw` |

## Beispiele

### Beispiel 1: Komprimieren mit Fokus

Vor einer neuen Teilaufgabe in einer langen Sitzung. Die Zusammenfassung behält, was du vorgibst.

```text
/compact Behalte die Entscheidungen zum Datenmodell und die offene Fehlerliste, verwirf die Debug-Ausgaben
```

### Beispiel 2: Benannte Sitzung starten und später fortsetzen

Für Aufgaben über mehrere Tage.

```bash
claude -n "export-refactor"
# am nächsten Tag:
claude --resume export-refactor
```

### Beispiel 3: Alternative ausprobieren, ohne das Original zu ändern

Die letzte Sitzung wird mit neuer ID fortgesetzt. Die ursprüngliche Sitzung bleibt, wie sie war.

```bash
claude --continue --fork-session
```

### Beispiel 4: Auto Memory für ein Projekt abschalten

Etwa in Kundenprojekten, in denen keine Notizen auf dem Rechner bleiben sollen. Gehört in `.claude/settings.json` oder `.claude/settings.local.json`.

```json
{
  "autoMemoryEnabled": false
}
```

### Beispiel 5: Auto Memory an einem anderen Ort speichern

Der Pfad muss absolut sein oder mit `~/` beginnen.

```json
{
  "autoMemoryDirectory": "~/claude-memory"
}
```

### Beispiel 6: Kontext nach jeder Komprimierung neu einspielen

Ein SessionStart-Hook mit dem Matcher `compact` läuft nach jeder Komprimierung. Klartext auf stdout wird bei SessionStart zu Kontext für Claude.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          { "type": "command", "command": "cat \"${CLAUDE_PROJECT_DIR}/docs/aktueller-stand.md\"" }
        ]
      }
    ]
  }
}
```

### Beispiel 7: Transkripte kürzer aufbewahren

Lokale Transkripte enthalten Prompts und gelesenen Code im Klartext. Für Teams mit Datenschutzvorgaben kann eine kürzere Frist sinnvoll sein; der Mindestwert ist 1, `0` ist ungültig. Bedenke: Mit den Transkripten verschwinden auch die Checkpoints und die Sitzungen in `/resume`.

```json
{
  "cleanupPeriodDays": 14
}
```

### Beispiel 8: Zusätzliche Ordner samt CLAUDE.md laden

Ordner aus `--add-dir` liefern ihre CLAUDE.md nur mit dieser Variable.

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

## Schritt für Schritt: eine lange Sitzung sauber halten

1. Zu Beginn kurz `/context` aufrufen und prüfen, ob die richtigen CLAUDE.md-Dateien geladen sind.
2. Große Recherchen ("finde alle Stellen, die X nutzen") an einen Subagent geben.
3. Nach einem abgeschlossenen Teilschritt `/compact` mit einem Satz zum Fokus aufrufen.
4. Wenn ein Weg in die Sackgasse führt: zweimal `Esc`, den Prompt vor dem Fehlversuch wählen, "Restore code and conversation".
5. Wichtige Erkenntnisse, die auch morgen gelten, mit "add this to CLAUDE.md" festhalten.
6. Bei einer neuen, unabhängigen Aufgabe `/clear` statt weiterzumachen.
7. Am Ende der Arbeit die Sitzung mit `/rename` benennen, damit sie sich morgen mit `claude --resume <name>` wiederfinden lässt.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Wichtige Regel nur im Chat gesagt | nach `/compact` vergessen | in die CLAUDE.md schreiben |
| Nie `/clear` zwischen Aufgaben | Antworten werden ungenauer, Tokens steigen | bei Themenwechsel `/clear` |
| `MEMORY.md` wächst unkontrolliert | Notizen nach Zeile 200 fehlen | über `/memory` prüfen, Einträge zusammenfassen |
| Auf `/rewind` nach `rm` per Bash verlassen | Datei bleibt gelöscht | Git nutzen, Bash-Änderungen werden nicht erfasst |
| `cleanupPeriodDays` auf `0` gesetzt | Settings-Fehler | Wert ab 1 wählen |
| `--continue` erwartet einen `claude -p`-Lauf | eine ältere interaktive Sitzung wird geladen | `claude --resume <id>` mit der Sitzungs-ID |

## Häufige Fragen

### Wann sollte ich /compact nutzen und wann /clear?

`/compact` nutzt du, wenn die aktuelle Aufgabe weitergeht und der Kontext voll wird; das Gespräch wird zusammengefasst. `/clear` nutzt du beim Wechsel zu einer unabhängigen Aufgabe, denn alter Verlauf verdrängt sonst die Dateien, die du als Nächstes brauchst, und kostet bei jeder Nachricht Tokens.

### Wo speichert Claude Code die Auto Memory?

Unter `~/.claude/projects/<project>/memory/`, mit `MEMORY.md` als Index und einer Datei pro Notiz. Den Ort änderst du mit `autoMemoryDirectory`, und alle Worktrees eines Repos teilen sich denselben Ordner.

### Kann ich die Auto Memory abschalten?

Ja, über den Schalter in `/memory`, mit `"autoMemoryEnabled": false` in den Settings oder mit der Umgebungsvariable `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

### Wie setze ich eine frühere Sitzung fort?

Mit `claude --continue` für das letzte Gespräch im aktuellen Ordner oder mit `claude --resume` für eine Auswahl. Benannte Sitzungen öffnest du direkt mit `claude --resume <name>`.

### Macht /rewind auch Änderungen durch Bash-Befehle rückgängig?

Nein. Checkpoints erfassen nur Änderungen, die Claude mit seinen Datei-Tools macht. Was über `rm`, `mv` oder `cp` per Bash passiert, stellst du mit Git wieder her.

### Werden meine Gespräche lokal gespeichert?

Ja, als Klartext unter `~/.claude/projects/`, standardmäßig 30 Tage lang (`cleanupPeriodDays`). Was an Anthropic geht, beschreibt die Anleitung zu [Claude Code und DSGVO](./claude-code-dsgvo.md).

## Weiterlesen

- [CLAUDE.md: Aufbau, Beispiele und Best Practices](./claude-md.md)
- [Claude Code Rules in .claude/rules](./claude-code-rules.md)
- [Claude Code Befehle](./claude-code-befehle.md)
- [Claude Code Usage und Tokens](./claude-code-usage-tokens.md)
- [Claude Code Subagents](./claude-code-subagents.md)
- [Claude Code Hooks](./claude-code-hooks.md)
- Offizielle Doku: [Memory](https://code.claude.com/docs/en/memory), [Checkpointing](https://code.claude.com/docs/en/checkpointing), [Context window](https://code.claude.com/docs/en/context-window)
