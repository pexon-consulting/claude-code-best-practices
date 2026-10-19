# Claude Code Befehle: alle Slash Commands, CLI-Flags und Tastenkürzel erklärt

Claude Code hat eingebaute Slash Commands wie `/clear`, `/compact`, `/model`, `/plan`, `/permissions` und `/mcp`, die du am Anfang einer Nachricht tippst. Eigene Befehle legst du als Skill unter `.claude/skills/<name>/SKILL.md` an, sie erscheinen dann als `/name`. Diese Seite sammelt die wichtigsten Slash Commands, CLI-Flags und Tastenkürzel zum Nachschlagen.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- Ein Slash Command wirkt nur am Anfang der Nachricht. Text dahinter wird zum Argument.
- `/` allein zeigt alle verfügbaren Befehle, Tippen filtert die Liste. Welche erscheinen, hängt von Plattform, Tarif und Umgebung ab.
- Eigene Befehle sind seit v2.1.3 Skills. Dateien in `.claude/commands/` funktionieren weiter.
- Für Skripte und CI startest du Claude Code mit `claude -p "aufgabe"`, das gibt die Antwort aus und beendet sich.
- `Shift+Tab` wechselt den Berechtigungsmodus, `Esc` unterbricht Claude, `Esc Esc` öffnet das Zurückspulen.

## Welche Slash Commands hat Claude Code?

In den Tabellen steht `<arg>` für ein Pflichtargument und `[arg]` für ein optionales. Einige Einträge sind mitgelieferte Skills, sie verhalten sich wie eigene Skills.

### Sitzung und Kontext

| Befehl | Zweck |
| --- | --- |
| `/clear [name]` | neues Gespräch mit leerem Kontext, Projektgedächtnis bleibt |
| `/compact [anweisungen]` | Gespräch zusammenfassen und Kontext freigeben, optional mit Schwerpunkt |
| `/context [all]` | Kontextbelegung als Raster mit Hinweisen |
| `/resume [sitzung]` | frühere Sitzung per ID oder Name fortsetzen |
| `/rename [name]` | Sitzung umbenennen |
| `/branch [name]` | Gespräch an dieser Stelle verzweigen |
| `/fork [prompt]` | Gespräch in eine neue Hintergrundsitzung kopieren |
| `/rewind` | Code und Gespräch auf einen Checkpoint zurücksetzen, Aliase `/checkpoint`, `/undo` |
| `/btw [frage]` | Nebenfrage zur Sitzung, ohne Tools und ohne Eintrag im Verlauf |
| `/export [datei]` | Gespräch als Text exportieren |
| `/copy [N]` | letzte Antwort in die Zwischenablage |
| `/exit` | beenden, Alias `/quit` |

### Modell und Arbeitsweise

| Befehl | Zweck |
| --- | --- |
| `/model [modell]` | Modell wechseln und als Standard speichern |
| `/effort [stufe]` | Effort-Stufe setzen, `low` bis `max` oder `auto` |
| `/fast [on\|off]` | Fast Mode umschalten |
| `/plan [beschreibung]` | direkt in den [Plan Mode](./claude-code-plan-mode.md) wechseln |
| `/output-style [stil]` | Ausgabestil anzeigen oder wechseln |

### Projekt und Konfiguration

| Befehl | Zweck |
| --- | --- |
| `/init` | Start-[CLAUDE.md](./claude-md.md) für das Projekt erzeugen |
| `/memory` | CLAUDE.md bearbeiten, Auto Memory ein- und ausschalten |
| `/config [key=wert]` | Einstellungen öffnen oder direkt setzen |
| `/permissions` | allow-, ask- und deny-Regeln verwalten |
| `/hooks` | Hook-Konfiguration ansehen |
| `/mcp` | MCP-Server verbinden, anmelden, ein- und ausschalten |
| `/plugin [unterbefehl]` | Plugins verwalten |
| `/reload-plugins` | Plugins ohne Neustart neu laden |
| `/skills` | verfügbare Skills auflisten |
| `/reload-skills` | Skill-Ordner neu einlesen |
| `/agents` | Hinweis zum Anlegen von Subagents ausgeben |
| `/statusline` | [Statusline](./claude-code-statusline.md) einrichten |
| `/add-dir <pfad>` | weiteren Arbeitsordner freigeben |
| `/sandbox` | Sandbox-Modus umschalten |
| `/keybindings` | Datei mit Tastenkürzeln öffnen |
| `/terminal-setup` | Shift+Enter für Zeilenumbrüche im Terminal einrichten |
| `/import [codex\|gemini\|cursor]` | Konfiguration aus anderen Coding-Agents übernehmen |

### Prüfen und Ausliefern

| Befehl | Zweck |
| --- | --- |
| `/diff` | Änderungen im Arbeitsverzeichnis ansehen |
| `/code-review [stufe] [--fix] [pr#]` | aktuellen Diff oder einen Pull Request prüfen, Alias `/review` |
| `/security-review` | Branch auf Sicherheitslücken prüfen |
| `/simplify [ziel]` | geänderten Code aufräumen |
| `/verify` | Änderung durch Bauen und Starten der App prüfen |
| `/install-github-app` | Claude GitHub App für ein Repo einrichten |

### Kosten, Status und Hilfe

| Befehl | Zweck |
| --- | --- |
| `/usage` | Kosten, Limits und Statistiken, Aliase `/cost` und `/stats` |
| `/status` | Version, Modell, Konto, Verbindung |
| `/doctor` | Einrichtung prüfen und Fehler beheben |
| `/debug [beschreibung]` | Debug-Log für die Sitzung einschalten und auswerten |
| `/tasks` | Hintergrundarbeit ansehen, auch fertige Subagents |
| `/help` | Hilfe und Befehlsliste |
| `/release-notes` | Changelog ansehen |
| `/login`, `/logout` | an- und abmelden |

Entfernt wurden unter anderem `/vim` (v2.1.92, jetzt über `/config`), `/pr-comments` (v2.1.91) und `/ultraplan`.

## Welche CLI-Befehle und Flags gibt es?

### Befehle

| Befehl | Zweck |
| --- | --- |
| `claude` | interaktive Sitzung starten |
| `claude "frage"` | Sitzung mit erster Nachricht starten |
| `claude -p "frage"` | einmal antworten und beenden |
| `cat datei \| claude -p "frage"` | Eingabe per Pipe übergeben |
| `claude -c` | letzte Sitzung in diesem Ordner fortsetzen |
| `claude -r "<sitzung>" "frage"` | Sitzung per ID oder Name fortsetzen |
| `claude update` | auf die neueste Version aktualisieren |
| `claude install [version]` | bestimmte Version installieren, z.B. `stable` |
| `claude auth login` / `logout` / `status` | Anmeldung verwalten |
| `claude doctor` | Diagnose ohne Sitzung |
| `claude mcp ...` | [MCP-Server](./claude-code-mcp.md) verwalten |
| `claude plugin ...` | [Plugins](./claude-code-plugins.md) verwalten |
| `claude setup-token` | langlebiges Token für CI erzeugen, erfordert ein Claude-Abo |
| `claude purge [pfad]` | lokale Daten eines Projekts löschen |

### Flags

| Flag | Zweck |
| --- | --- |
| `-p`, `--print` | ohne interaktiven Modus antworten |
| `-c`, `--continue` | letzte Sitzung fortsetzen |
| `-r`, `--resume` | bestimmte Sitzung fortsetzen |
| `-n`, `--name` | Sitzung benennen |
| `--model` | Modell, z.B. `sonnet`, `opus`, `haiku` oder volle ID |
| `--effort` | Effort-Stufe für die Sitzung |
| `--permission-mode` | Startmodus: `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `--allowedTools` | Tools ohne Rückfrage |
| `--disallowedTools` | Tools sperren |
| `--add-dir` | weitere Ordner freigeben |
| `--agent <name>` | Sitzung als dieser [Subagent](./claude-code-subagents.md) führen |
| `--agents '<json>'` | Subagents nur für diese Sitzung |
| `--append-system-prompt` | Text an den System-Prompt anhängen |
| `--output-format` | `text`, `json` oder `stream-json`, nur mit `-p` |
| `--max-turns` | Höchstzahl agentischer Turns, nur mit `-p` |
| `--max-budget-usd` | Kostengrenze für den Lauf, nur mit `-p` |
| `--mcp-config` | MCP-Server aus Datei oder JSON laden |
| `--strict-mcp-config` | nur Server aus `--mcp-config` nutzen |
| `--settings` | zusätzliche Settings-Datei oder JSON |
| `--setting-sources` | nur bestimmte Quellen laden: `user`, `project`, `local` |
| `--bare` | ohne Hooks, Skills, Plugins, MCP und CLAUDE.md starten |
| `--plugin-dir` | Plugin für diese Sitzung laden |
| `-w`, `--worktree` | in einem eigenen Git-Worktree starten |
| `--debug` | Debug-Modus, Filter mit `--debug='mcp,startup'` |
| `--dangerously-skip-permissions` | alle Rückfragen überspringen, siehe [eigene Anleitung](./claude-code-dangerously-skip-permissions.md) |
| `-v`, `--version` | Version ausgeben |

## Tastenkürzel

### Steuerung

| Kürzel | Wirkung |
| --- | --- |
| `Esc` | Claude unterbrechen, die bisherige Arbeit bleibt |
| `Esc` `Esc` | Eingabe leeren, bei leerer Eingabe Zurückspulen öffnen |
| `Shift+Tab` | Berechtigungsmodus wechseln, unter Windows teils `Alt+M` |
| `Ctrl+C` | unterbrechen oder Eingabe leeren, zweimal beendet |
| `Ctrl+D` | beenden, zweimal innerhalb von 800 ms |
| `Ctrl+B` | laufende Befehle und Agents in den Hintergrund |
| `Ctrl+X Ctrl+K` | alle Hintergrund-Subagents stoppen |
| `Ctrl+O` | Transcript mit Tool-Details ein- und ausblenden |
| `Ctrl+T` | Aufgabenliste von Claude ein- und ausblenden |
| `Ctrl+R` | Verlauf rückwärts durchsuchen |
| `Ctrl+G` oder `Ctrl+X Ctrl+E` | Eingabe im Editor bearbeiten |
| `Ctrl+S` | Eingabe parken und wiederherstellen |
| `Ctrl+V`, `Cmd+V` (iTerm2), `Alt+V` (Windows) | Bild einfügen |
| `Ctrl+L` | Bildschirm neu zeichnen |
| `Option+P` / `Alt+P` | Modell wechseln |
| `Option+T` / `Alt+T` | Extended Thinking umschalten, ohne Wirkung bei Opus, Sonnet und Haiku 5.5 sowie Fable |
| `Option+O` / `Alt+O` | Fast Mode umschalten |

### Eingabe

| Kürzel | Wirkung |
| --- | --- |
| `/` am Anfang | Befehl oder Skill |
| `!` am Anfang | Shell-Modus: Befehl direkt ausführen, Ausgabe kommt in die Sitzung |
| `@` | Datei erwähnen, mit Autovervollständigung |
| `?` bei leerer Eingabe | Hilfe zu Tastenkürzeln |
| `\` + `Enter`, `Ctrl+J` | Zeilenumbruch in jedem Terminal |
| `Shift+Enter` | Zeilenumbruch in iTerm2, WezTerm, Ghostty, Kitty, Warp, Apple Terminal und Windows Terminal |
| `Ctrl+A` / `Ctrl+E` | Zeilenanfang und Zeilenende |
| `Ctrl+K` / `Ctrl+U` | bis Zeilenende oder Zeilenanfang löschen |
| `Ctrl+W` | bis zum letzten Leerzeichen löschen |
| `Ctrl+Y` | Gelöschtes wieder einfügen |

Auf macOS brauchen die `Alt`-Kürzel die Einstellung "Option as Meta" im Terminal.

## Beispiele für Claude Code Befehle

### Beispiel 1: eigener Befehl /fix-issue

Ein Skill, der eine Issue-Nummer als Argument nimmt. Datei: `.claude/skills/fix-issue/SKILL.md`.

```markdown
---
name: fix-issue
description: Behebt ein GitHub-Issue nach unseren Coding-Standards
disable-model-invocation: true
argument-hint: "[issue-nummer]"
---

Behebe GitHub-Issue $ARGUMENTS nach unseren Coding-Standards.

1. Issue lesen und Anforderungen verstehen.
2. Fix umsetzen.
3. Tests schreiben und ausführen.
4. Commit anlegen, nicht pushen.
```

Aufruf: `/fix-issue 123`. Mehr dazu in der Anleitung zu [Claude Code Skills](./claude-code-skills.md).

### Beispiel 2: Kontext gezielt verdichten

Wenn das Gespräch lang wird, behält `/compact` mit Schwerpunkt das Wichtige:

```text
/compact Behalte die Entscheidungen zur Datenbank und die offenen Testfehler, der Rest kann weg
```

Für eine neue Aufgabe ist `/clear` besser. Vorher hilft der Skill `/handoff` aus der [Vorlage](../../src/claude_team/vorlage/.claude/skills/handoff/SKILL.md), den Stand festzuhalten.

### Beispiel 3: Claude Code im Skript

Ein Lauf ohne Dialog, mit JSON-Ausgabe und Grenzen für Turns und Kosten:

```bash
claude -p "Fasse die Änderungen seit gestern für das Team zusammen" \
  --output-format json \
  --max-turns 5 \
  --max-budget-usd 1
```

### Beispiel 4: Logdatei per Pipe auswerten

```bash
tail -200 app.log | claude -p "Welche Fehler treten am häufigsten auf und wo im Code entstehen sie?"
```

### Beispiel 5: benannte Sitzung später fortsetzen

```bash
claude -n auth-umbau
# später
claude -r auth-umbau "Mach mit den offenen Tests weiter"
```

### Beispiel 6: erst planen, dann umsetzen

```bash
claude --permission-mode plan "Plane die Umstellung der Konfiguration auf Umgebungsvariablen"
```

In einer laufenden Sitzung geht dasselbe mit `/plan` oder `Shift+Tab`.

### Beispiel 7: parallel in einem eigenen Worktree

```bash
claude -w feature-export
```

Claude Code legt den Worktree unter `<repo>/.claude/worktrees/feature-export` an. So kann eine zweite Sitzung arbeiten, ohne die erste zu stören.

## Eigene Befehle anlegen

1. Ordner `.claude/skills/<name>/` anlegen, für persönliche Befehle `~/.claude/skills/<name>/`.
2. `SKILL.md` mit Frontmatter (`description`, bei Nebenwirkungen `disable-model-invocation: true`) und Anweisungen schreiben.
3. In der Sitzung `/reload-skills` ausführen, wenn der Ordner neu ist.
4. Mit `/name` aufrufen, Argumente kommen über `$ARGUMENTS` oder `$0`, `$1` in den Text.
5. Committen, damit das Team den Befehl bekommt.

Bestehende Dateien in `.claude/commands/` funktionieren weiter. Aus `.claude/commands/frontend/component.md` wird `/frontend:component`.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Befehl mitten im Text | nichts passiert | Befehl an den Anfang der Nachricht |
| `/vim` getippt | Befehl unbekannt | Editor-Modus über `/config` |
| `--max-turns` ohne `-p` | keine Wirkung | nur im Print-Modus verfügbar |
| neuer Skill-Ordner | `/name` unbekannt | `/reload-skills` |
| `Alt`-Kürzel auf dem Mac | Sonderzeichen statt Aktion | "Option as Meta" im Terminal einschalten |
| `Shift+Enter` sendet ab | kein Zeilenumbruch | `/terminal-setup` oder `\` + `Enter` |

## Häufige Fragen

### Wie sehe ich alle verfügbaren Befehle?

Tippe `/` in der Sitzung. Die Liste zeigt eingebaute Befehle, mitgelieferte Skills und deine eigenen Skills. `/help` zeigt eine Übersicht.

### Wie lege ich einen eigenen Slash Command an?

Als Skill: Ordner `.claude/skills/<name>/` mit einer `SKILL.md`. Der Ordnername wird zum Befehl. Die Anleitung zu [Claude Code Skills](./claude-code-skills.md) erklärt alle Felder.

### Was ist der Unterschied zwischen /clear und /compact?

`/clear` startet ein neues Gespräch mit leerem Kontext. `/compact` fasst das laufende Gespräch zusammen und arbeitet damit weiter.

### Wie wechsle ich zwischen den Berechtigungsmodi?

Mit `Shift+Tab` in der Sitzung oder beim Start mit `--permission-mode`. Was die Modi bedeuten, erklärt die Anleitung zu [Claude Code Permissions](./claude-code-permissions.md).

### Kann ich Tastenkürzel ändern?

Ja, `/keybindings` öffnet die Datei mit deinen Tastenkürzeln.

## Weiterlesen

- [Claude Code Cheat Sheet](../../CHEATSHEET.md): alles Wichtige auf einer Seite
- [Claude Code Skills](./claude-code-skills.md): eigene Befehle schreiben
- [Claude Code Workflow](./claude-code-workflow.md): Befehle im Arbeitsalltag
- [Claude Code Usage und Tokens](./claude-code-usage-tokens.md): `/usage` und `/context` richtig lesen
- Offizielle Doku: [Commands](https://code.claude.com/docs/en/commands), [CLI-Referenz](https://code.claude.com/docs/en/cli-reference), [Interaktiver Modus](https://code.claude.com/docs/en/interactive-mode)
