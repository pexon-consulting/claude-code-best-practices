# Claude Code Subagents: eigene Agenten definieren und richtig delegieren

Ein Claude Code Subagent lohnt sich, wenn eine Aufgabe viel Ausgabe erzeugt, die du im Hauptgespräch nicht brauchst, eigene Tool-Grenzen haben soll oder für sich abgeschlossen ist und nur eine Zusammenfassung zurückgeben muss. Du definierst ihn als Markdown-Datei mit Frontmatter unter `.claude/agents/<name>.md` im Projekt oder unter `~/.claude/agents/` für alle eigenen Projekte. Der Text unter dem Frontmatter wird zum System-Prompt des Subagents.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Ein Subagent hat einen eigenen Kontext, eigene Tools und eigenes Modell, er liefert nur sein Ergebnis an das Hauptgespräch zurück.
- Pflichtfelder sind `name` und `description`. Die `description` entscheidet, wann Claude von selbst delegiert.
- Eine `tools`-Liste ist eine Allowlist. Ohne sie bekommt der Subagent alle Tools, deshalb prüft das Audit dieses Repos auf fehlende Listen (Regel [CC044](../regeln.md#cc044)).
- Explizit rufst du einen Subagent mit `@"name (agent)"`, `@agent-name` oder für die ganze Sitzung mit `claude --agent name` auf.
- Seit nach v2.1.197 hat `/agents` keinen Assistenten mehr. Subagents legst du als Datei an oder lässt sie von Claude schreiben.
- Für Rückfragen und kurze Änderungen bleibt das Hauptgespräch besser, für Hintergrundwissen ohne eigenen Kontext ein [Skill](./claude-code-skills.md).

## Wann lohnt sich ein Subagent?

| Hauptgespräch | Subagent |
| --- | --- |
| viel Hin und Her, schrittweise Verfeinerung | Aufgabe mit viel Ausgabe, die du nicht im Kontext brauchst |
| Planung, Umsetzung und Tests teilen viel Kontext | feste Tool-Grenzen sollen gelten, z.B. nur lesen |
| kurze, gezielte Änderung | die Arbeit ist abgeschlossen und kann eine Zusammenfassung liefern |
| Wartezeit spielt eine Rolle | mehrere Recherchen sollen parallel laufen |

Für eine Frage zu dem, was schon im Gespräch steht, nimmst du `/btw`. Das sieht den ganzen Kontext, hat aber keine Tools und landet nicht im Verlauf.

## Wo liegen Subagents und welcher gewinnt?

| Ort | Gilt für | Priorität |
| --- | --- | --- |
| `.claude/agents/` im Managed-Settings-Verzeichnis | ganze Organisation | 1 (höchste) |
| `claude --agents '<json>'` | diese Sitzung | 2 |
| `.claude/agents/` | dieses Projekt, wird committet | 3 |
| `~/.claude/agents/` | alle eigenen Projekte | 4 |
| `<plugin>/agents/` | wo das Plugin aktiv ist | 5 |

Claude Code durchsucht `.claude/agents/` rekursiv und läuft vom Arbeitsordner bis zum Repo-Root nach oben. Die Identität kommt nur aus `name`, nicht aus dem Dateinamen. Doppelte Namen im selben Baum meldet `/doctor`. Änderungen an Agent-Dateien erkennt Claude Code nach wenigen Sekunden. Nur ein neu angelegtes `~/.claude/agents/` braucht einen Neustart.

## Frontmatter-Felder

Die Felder schreiben sich in camelCase, anders als bei Skills. Unbekannte Felder werden still ignoriert.

| Feld | Pflicht | Bedeutung |
| --- | --- | --- |
| `name` | ja | höchstens 256 Zeichen, kein `:`, nicht mit `-` beginnen |
| `description` | ja | wann delegiert werden soll |
| `tools` | nein | Allowlist als Text oder YAML-Liste, fehlt sie, gelten alle Tools |
| `disallowedTools` | nein | Denylist, wird vor `tools` angewendet |
| `model` | nein | `sonnet`, `opus`, `haiku`, `fable`, volle ID wie `claude-opus-5-5` oder `inherit` |
| `permissionMode` | nein | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, `manual` |
| `maxTurns` | nein | Höchstzahl agentischer Turns |
| `skills` | nein | Skills, die beim Start vollständig geladen werden |
| `mcpServers` | nein | Servername oder Inline-Definition |
| `hooks` | nein | Hooks, die nur für diesen Subagent gelten |
| `memory` | nein | `user`, `project` oder `local`, dauerhaftes Gedächtnis |
| `background` | nein | `true`: läuft immer im Hintergrund |
| `effort` | nein | `low` bis `max` |
| `isolation` | nein | `worktree`: eigener temporärer Git-Worktree |
| `omitClaudeMd` | nein | ohne CLAUDE.md starten (ab v2.1.271) |
| `color` | nein | Farbe in der Oberfläche |
| `initialPrompt` | nein | erster Turn, wenn der Agent mit `--agent` die Sitzung führt |

Subagents aus Plugins ignorieren aus Sicherheitsgründen `hooks`, `mcpServers` und `permissionMode`. Das Feld `autoCompactWindow` kommt erst ab v2.1.296 und fehlt deshalb in der hier geprüften Version.

Der Text unter dem Frontmatter ersetzt den System-Prompt von Claude Code. Der Subagent bekommt nur diesen Prompt plus Umgebungsangaben wie den Arbeitsordner. Schreib also alles hinein, was er für seine Aufgabe wissen muss.

## Eingebaute Subagents

| Agent | Tools | Zweck |
| --- | --- | --- |
| Explore | nur lesen | Code durchsuchen, Gründlichkeit quick, medium oder very thorough |
| Plan | nur lesen | Recherche im [Plan Mode](./claude-code-plan-mode.md) |
| general-purpose | alle | mehrschrittige Aufgaben, Modell über `CLAUDE_CODE_SUBAGENT_MODEL` steuerbar |

Explore und Plan starten ohne CLAUDE.md und Git-Status. Mit `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1` schaltest du beide ab. Daneben gibt es Hilfsagenten wie `statusline-setup` und `claude-code-guide`.

## Subagents explizit aufrufen

```text
Use the code-reviewer subagent to look at my recent changes
@"code-reviewer (agent)" schau dir die Änderungen am Login an
@agent-code-reviewer schau dir die Änderungen am Login an
```

Natürliche Sprache überlässt Claude die Entscheidung. Die `@`-Erwähnung erzwingt den Subagent für diese Aufgabe. Plugin-Subagents heißen `@agent-mein-plugin:code-reviewer`. Für eine ganze Sitzung als dieser Agent:

```bash
claude --agent code-reviewer
```

Dauerhaft für ein Projekt geht das über `.claude/settings.json`, das CLI-Flag hat Vorrang:

```json
{ "agent": "code-reviewer" }
```

Damit Claude öfter von selbst delegiert, schreib Wendungen wie "use proactively" oder "nach jeder Änderung einsetzen" in die `description`. Halte die Beschreibungen kurz: Ab 15.000 Tokens für alle Beschreibungen zusammen warnt Claude Code beim Start.

## Subagents sperren

Einzelne Subagents verbietest du mit `Agent(<name>)` in den deny-Regeln. Das Tool hieß früher `Task` und wurde in v2.1.63 in `Agent` umbenannt.

```json
{
  "permissions": {
    "deny": ["Agent(Explore)", "Agent(my-custom-agent)"]
  }
}
```

Für eine einzelne Sitzung: `claude --disallowedTools "Agent(Explore)"`.

## Beispiele

### Beispiel 1: code-reviewer, der nichts ändert

Aus der [Vorlage](../../src/claude_team/vorlage/.claude/agents/code-reviewer.md), gekürzt. `Bash` braucht er für `git diff`, `Edit` und `Write` fehlen absichtlich.

```markdown
---
name: code-reviewer
description: Prüft die aktuellen Änderungen auf Fehler, Sicherheitslücken und fehlende Tests. Nach jeder größeren Änderung und vor jedem Pull Request einsetzen.
tools: Read, Grep, Glob, Bash
model: sonnet
---

Du bist Reviewer in diesem Team. Du änderst keine Dateien, du berichtest.

1. `git diff --stat` und `git diff` lesen. Bei einem Branch: `git diff main...HEAD`.
2. Jede geänderte Datei im Zusammenhang lesen, nicht nur den Diff.
3. Prüfen: Korrektheit, Sicherheit, Tests, Lesbarkeit. Nichts melden, was ein Linter findet.

Antwort als Liste, wichtigstes zuerst, je Punkt Datei und Zeile.
Stufen: **muss** (Fehler, Sicherheit), **sollte** (Tests, Wartbarkeit), **kann** (Stil).
```

### Beispiel 2: datenschutz-check für personenbezogene Daten

Aus der [Vorlage](../../src/claude_team/vorlage/.claude/agents/datenschutz-check.md), gekürzt. Nur Lese-Tools, kein Bash.

```markdown
---
name: datenschutz-check
description: Prüft Code und Änderungen auf personenbezogene Daten nach DSGVO, etwa in Logs, Tests, Fixtures, Analytics und Fehlermeldungen. Einsetzen, wenn Kundendaten, Formulare, Logging oder Exporte betroffen sind.
tools: Read, Grep, Glob
model: sonnet
---

Du prüfst, ob personenbezogene Daten unnötig verarbeitet, gespeichert oder weitergegeben werden. Du änderst nichts.

Suche gezielt nach Logs mit E-Mail, Name, IBAN oder IP-Adresse, nach echt aussehenden Testdaten
(erlaubt sind Adressen unter example.com) und nach Daten, die an Dritte gehen.

Antwort: Liste mit Datei und Zeile, welches Datum, welches Risiko, konkrete Abhilfe.
Keine Rechtsberatung. Wo eine Rechtsfrage offen ist, schreib "mit Datenschutz klären".
```

### Beispiel 3: test-schreiber mit Projektgedächtnis

Darf Dateien schreiben und Tests ausführen. `memory: project` legt Erkenntnisse unter `.claude/agent-memory/test-schreiber/` ab, das Team kann sie committen.

```markdown
---
name: test-schreiber
description: Schreibt fehlende Unit-Tests für geänderten Code und führt sie aus. Einsetzen, wenn neue Funktionen ohne Test entstanden sind oder Tests fehlschlagen.
tools: Read, Grep, Glob, Edit, Write, Bash
model: sonnet
memory: project
maxTurns: 30
---

Du schreibst Tests im Stil der vorhandenen Tests. Lies zuerst deine Notizen in MEMORY.md.

1. Geänderte Dateien mit `git diff --name-only` finden.
2. Für jedes neue Verhalten einen Test schreiben, der den Fehler finden würde.
3. Nur erfundene Testdaten, E-Mails unter example.com.
4. Tests ausführen und bei Fehlern den Test oder den Code korrigieren, nicht den Test abschwächen.

Halte in MEMORY.md fest, welche Testmuster und Fixtures dieses Projekt nutzt.
```

### Beispiel 4: doku-agent im eigenen Worktree

`isolation: worktree` gibt dem Subagent eine eigene Kopie des Repos. Sie zweigt vom Default-Branch ab, nicht von deinem aktuellen Stand, und wird gelöscht, wenn er nichts ändert.

```markdown
---
name: doku-agent
description: Aktualisiert README und docs/ passend zum aktuellen Code. Einsetzen, wenn sich öffentliche Funktionen, CLI-Optionen oder Konfiguration geändert haben.
tools: Read, Grep, Glob, Edit, Write
model: haiku
isolation: worktree
---

Gleiche die Dokumentation mit dem Code ab.

- Jede CLI-Option und jede Konfigurationsvariable muss in docs/ beschrieben sein.
- Beispiele müssen mit dem aktuellen Code laufen.
- Schreibe kurz und sachlich, ohne Werbesprache.

Liefere am Ende eine Liste der geänderten Dateien mit je einem Satz Begründung.
```

### Beispiel 5: migrations-planer, der nur plant

`permissionMode: plan` lässt den Subagent nur lesen und planen, die `tools`-Liste ohne `Edit`, `Write` und `Bash` sichert das zusätzlich ab. Ein stärkeres Modell lohnt sich hier, weil Fehler in Migrationen teuer sind.

```markdown
---
name: migrations-planer
description: Plant Datenbank-Migrationen mit Reihenfolge, Risiken und Rückweg, ohne etwas zu ändern. Einsetzen vor Schemaänderungen an produktiven Tabellen.
tools: Read, Grep, Glob
model: opus
permissionMode: plan
effort: high
---

Erstelle einen Migrationsplan:

1. Betroffene Tabellen, Indizes und Code-Stellen auflisten.
2. Schritte so ordnen, dass jede Version des Codes mit jedem Zwischenstand des Schemas läuft.
3. Für jeden Schritt den Rückweg nennen.
4. Risiken: Sperren auf großen Tabellen, Datenverlust, lange Laufzeiten.

Ändere keine Dateien. Gib den Plan als nummerierte Liste zurück.
```

### Beispiel 6: Subagents nur für eine Sitzung per JSON

Für Skripte und schnelle Tests ohne Datei. Ab v2.1.281 nimmt `-p` statt JSON auch einen Dateipfad an, z.B. `claude -p --agents ./agents.json "Prüfe meine Änderungen"`.

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Prüft Code nach Änderungen. Proaktiv einsetzen.",
    "prompt": "Du bist Reviewer. Achte auf Korrektheit, Sicherheit und Tests.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

## Schritt für Schritt: ersten Subagent anlegen

1. Ordner anlegen: `mkdir -p .claude/agents`.
2. Datei `.claude/agents/code-reviewer.md` mit Frontmatter und Prompt schreiben, oder Claude bitten: "Lege in .claude/agents einen Subagent code-reviewer an, der nur liest".
3. Datei öffnen und prüfen, ob `tools` wirklich nur das enthält, was der Agent braucht.
4. Mit `claude plugin validate .claude/agents` das Frontmatter prüfen (ab v2.1.233).
5. Testen: `@agent-code-reviewer prüfe die letzten Änderungen`.
6. Automatische Delegation testen: eine passende Bitte ohne den Namen formulieren.
7. Mit `claude-team audit .` auf fehlende `name`, `description` oder `tools` prüfen (Regeln [CC040](../regeln.md#cc040) und [CC044](../regeln.md#cc044)).
8. Datei committen, damit das Team sie bekommt.

## Sicherheit

- `permissionMode: bypassPermissions` in einer Agent-Datei ist ein Warnsignal, das Audit meldet es als Regel [CC041](../regeln.md#cc041). Ab v2.1.267 läuft ein Subagent nur dann ohne Rückfragen, wenn auch das Hauptgespräch in diesem Modus ist.
- Läuft das Hauptgespräch in `bypassPermissions`, `acceptEdits` oder Auto-Modus, übernimmt der Subagent diesen Modus und ignoriert sein eigenes `permissionMode`. Ein `plan` im Frontmatter schützt dann nicht, die `tools`-Liste schon.
- Ein Subagent ohne `tools` erbt die Tools des Hauptgesprächs inklusive MCP-Tools. Lege die Liste immer fest.
- Hooks im Frontmatter von Projekt-Subagents laufen erst, wenn du dem Ordner vertraust.
- Subagents können standardmäßig eigene Subagents starten, bis drei Ebenen unter dem Hauptgespräch. Die Grenze setzt `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| `tools` fehlt | Reviewer ändert Dateien | Allowlist ohne `Edit` und `Write` |
| vage `description` | Claude delegiert nie | konkrete Auslöser und "proaktiv einsetzen" |
| Feld in kebab-case (`permission-mode`) | Einstellung greift nicht | camelCase: `permissionMode` |
| `isolation: worktree` für ungespeicherte Arbeit | Subagent sieht deine Änderungen nicht | Worktree zweigt vom Default-Branch ab, vorher committen oder ohne Isolation |
| Plugin-Subagent mit `hooks` | Hooks laufen nicht | Datei nach `.claude/agents/` kopieren |
| `/agents` erwartet Assistenten | nur ein Hinweis erscheint | Datei direkt anlegen oder Claude bitten |

## Häufige Fragen

### Was ist der Unterschied zwischen einem Subagent und einem Skill?

Ein Skill bringt Anweisungen ins Hauptgespräch. Ein Subagent arbeitet in einem eigenen Kontext mit eigenen Tools und gibt nur sein Ergebnis zurück. Wer beides will, setzt im Skill `context: fork`.

### Welches Modell nutzt ein Subagent?

Das im Feld `model` angegebene, sonst das Modell der Sitzung. Für Lese- und Suchaufgaben reicht oft `haiku` oder `sonnet`, für Planung lohnt sich `opus`.

### Sieht ein Subagent meine CLAUDE.md?

Ja. Eigene Subagents laden alle CLAUDE.md-Ebenen, die auch das Hauptgespräch lädt, außer du setzt `omitClaudeMd: true`. Die eingebauten Agents Explore und Plan starten ohne CLAUDE.md. Deinen Gesprächsverlauf sieht ein Subagent nicht, er bekommt nur die Aufgabe, die Claude ihm formuliert.

### Können Subagents parallel laufen?

Ja. Claude kann mehrere Subagents gleichzeitig starten, etwa für parallele Recherchen. Alle laufenden Hintergrund-Subagents stoppst du mit Ctrl+X Ctrl+K (zweimal innerhalb von 3 Sekunden).

### Wie teile ich Subagents im Team?

Über `.claude/agents/` im Repo, über ein [Plugin](./claude-code-plugins.md) oder über Managed Settings für die ganze Organisation.

## Weiterlesen

- [Claude Code Skills](./claude-code-skills.md): wiederverwendbare Anweisungen im Hauptgespräch
- [Claude Code Agent Teams](./claude-code-agent-teams.md): mehrere Sitzungen, die zusammenarbeiten
- [Claude Code Plugins](./claude-code-plugins.md): Subagents versioniert verteilen
- [Claude Code Permissions](./claude-code-permissions.md): was ein Subagent darf
- Vorlagen: [code-reviewer](../../src/claude_team/vorlage/.claude/agents/code-reviewer.md), [datenschutz-check](../../src/claude_team/vorlage/.claude/agents/datenschutz-check.md)
- Offizielle Doku: [Subagents](https://code.claude.com/docs/en/sub-agents)
