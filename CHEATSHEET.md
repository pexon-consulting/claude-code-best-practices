# Claude Code Cheat Sheet: Befehle, Shortcuts und Konfiguration auf einer Seite

Die wichtigsten Slash Commands, CLI-Flags, Tastenkürzel und Konfigurationsorte von Claude Code zum Nachschlagen. Details stehen in den verlinkten Anleitungen.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](./README.md).

## Slash Commands

| Befehl | Zweck |
| --- | --- |
| `/init` | Start-CLAUDE.md für das Projekt erzeugen |
| `/memory` | CLAUDE.md bearbeiten, Auto Memory steuern |
| `/clear` | neues Gespräch, leerer Kontext |
| `/compact [schwerpunkt]` | Gespräch zusammenfassen, Kontext freigeben |
| `/context` | Kontextbelegung anzeigen |
| `/usage` | Kosten, Limits, Statistik (Aliase `/cost`, `/stats`) |
| `/model [modell]` | Modell wechseln |
| `/effort [stufe]` | Effort-Stufe setzen |
| `/plan [aufgabe]` | Plan Mode starten |
| `/permissions` | allow-, ask- und deny-Regeln verwalten |
| `/hooks` | Hooks ansehen |
| `/mcp` | MCP-Server verbinden und anmelden |
| `/plugin` | Plugins verwalten |
| `/skills` | Skills auflisten |
| `/reload-skills` | neue Skill-Ordner einlesen |
| `/statusline [wunsch]` | Statusline einrichten |
| `/resume [sitzung]` | Sitzung fortsetzen |
| `/rewind` | Code und Gespräch zurücksetzen |
| `/btw [frage]` | Nebenfrage ohne Eintrag im Verlauf |
| `/diff` | Änderungen ansehen |
| `/code-review` | Diff oder Pull Request prüfen (Alias `/review`) |
| `/security-review` | Branch auf Sicherheitslücken prüfen |
| `/doctor` | Einrichtung prüfen |
| `/status` | Version, Modell, Konto |
| `/help` | Hilfe |

Mehr: [Claude Code Befehle](docs/anleitungen/claude-code-befehle.md)

## CLI

| Aufruf | Zweck |
| --- | --- |
| `claude` | interaktive Sitzung |
| `claude "frage"` | Sitzung mit erster Nachricht |
| `claude -p "frage"` | einmal antworten und beenden |
| `cat datei \| claude -p "frage"` | Eingabe per Pipe |
| `claude -c` | letzte Sitzung fortsetzen |
| `claude -r <name>` | bestimmte Sitzung fortsetzen |
| `claude -n <name>` | Sitzung benennen |
| `claude -w <name>` | in eigenem Git-Worktree starten |
| `claude --permission-mode plan` | im Plan Mode starten |
| `claude --model sonnet` | Modell für die Sitzung |
| `claude --agent <name>` | Sitzung als Subagent führen |
| `claude -p ... --output-format json` | Ausgabe als JSON |
| `claude -p ... --max-turns 5` | Turns begrenzen |
| `claude -p ... --max-budget-usd 1` | Kosten begrenzen |
| `claude --bare` | ohne Hooks, Skills, Plugins, MCP, CLAUDE.md |
| `claude --debug` | Debug-Log |
| `claude update` | aktualisieren |
| `claude doctor` | Diagnose ohne Sitzung |

## Tastenkürzel

| Kürzel | Wirkung |
| --- | --- |
| `Esc` | Claude unterbrechen |
| `Esc` `Esc` | Eingabe leeren oder zurückspulen |
| `Shift+Tab` | Berechtigungsmodus wechseln |
| `Ctrl+C` | unterbrechen, zweimal beendet |
| `Ctrl+B` | Befehl oder Agent in den Hintergrund |
| `Ctrl+O` | Transcript mit Tool-Details |
| `Ctrl+R` | Verlauf durchsuchen |
| `Ctrl+G` | Eingabe im Editor bearbeiten |
| `Ctrl+V` | Bild einfügen (`Cmd+V` in iTerm2, `Alt+V` unter Windows) |
| `Option+P` / `Alt+P` | Modell wechseln |
| `\` + `Enter`, `Ctrl+J` | Zeilenumbruch |
| `!` am Anfang | Shell-Befehl direkt ausführen |
| `@` | Datei erwähnen |
| `?` | Hilfe zu Tastenkürzeln |

## Wo liegt was?

| Datei | Zweck | Anleitung |
| --- | --- | --- |
| `CLAUDE.md` oder `.claude/CLAUDE.md` | Projektanweisungen für das Team | [CLAUDE.md](docs/anleitungen/claude-md.md) |
| `CLAUDE.local.md` | eigene Anweisungen, in `.gitignore` | [Memory](docs/anleitungen/claude-code-memory.md) |
| `~/.claude/CLAUDE.md` | eigene Anweisungen für alle Projekte | [Memory](docs/anleitungen/claude-code-memory.md) |
| `.claude/rules/*.md` | Regeln, optional nur für bestimmte Pfade | [Rules](docs/anleitungen/claude-code-rules.md) |
| `.claude/settings.json` | Projekt-Settings, committen | [settings.json](docs/anleitungen/claude-code-settings-json.md) |
| `.claude/settings.local.json` | eigene Settings im Projekt, nicht committen | [settings.json](docs/anleitungen/claude-code-settings-json.md) |
| `~/.claude/settings.json` | eigene Settings für alle Projekte | [settings.json](docs/anleitungen/claude-code-settings-json.md) |
| `.claude/skills/<name>/SKILL.md` | Skills und eigene Befehle | [Skills](docs/anleitungen/claude-code-skills.md) |
| `.claude/agents/<name>.md` | Subagents | [Subagents](docs/anleitungen/claude-code-subagents.md) |
| `.mcp.json` | MCP-Server für das Team | [MCP](docs/anleitungen/claude-code-mcp.md) |
| `.claude-plugin/plugin.json` | Plugin-Manifest | [Plugins](docs/anleitungen/claude-code-plugins.md) |
| `.claude-plugin/marketplace.json` | Plugin-Marketplace | [Plugins](docs/anleitungen/claude-code-plugins.md) |

Vorrang der Settings, höchster zuerst: Managed Settings, `--settings`, `.claude/settings.local.json`, `.claude/settings.json`, `~/.claude/settings.json`. Listen wie `permissions.allow` werden zusammengeführt. Managed Settings liegen unter macOS in `/Library/Application Support/ClaudeCode/managed-settings.json`, unter Linux und WSL in `/etc/claude-code/managed-settings.json`, unter Windows in `C:\Program Files\ClaudeCode\managed-settings.json`.

## Berechtigungen

```json
{
  "permissions": {
    "allow": ["Bash(git status *)", "Bash(git diff *)", "Bash(npm run test *)"],
    "ask": ["Bash(git push *)", "Bash(terraform apply *)"],
    "deny": ["Read(.env)", "Read(.env.*)", "Read(**/*.pem)", "Read(**/*.key)"]
  }
}
```

deny schlägt ask, ask schlägt allow. Eine Regel für `.env` fehlt am häufigsten, das Audit meldet das als [CC013](docs/regeln.md#cc013). Mehr: [Permissions](docs/anleitungen/claude-code-permissions.md)

## Hooks

| Ereignis | Typischer Einsatz |
| --- | --- |
| `PreToolUse` | Secrets und personenbezogene Daten blockieren, gefährliche Befehle stoppen |
| `PostToolUse` | Formatieren nach jeder Änderung |
| `UserPromptSubmit` | Prompts prüfen, Kontext anhängen |
| `SessionStart` | Projektstand in den Kontext legen |
| `Stop` | Tests ausführen, bevor Claude fertig meldet |
| `Notification` | Desktop-Hinweis, wenn Claude wartet |

Exit-Code 2 blockiert und gibt stderr an Claude zurück. Mehr: [Hooks](docs/anleitungen/claude-code-hooks.md)

## MCP

| Befehl | Zweck |
| --- | --- |
| `claude mcp add --transport http <name> <url>` | Remote-Server hinzufügen |
| `claude mcp add --scope project ...` | in `.mcp.json` für das Team |
| `claude mcp add <name> -- npx -y <paket>@<version>` | lokaler stdio-Server |
| `claude mcp list` | Server mit Status |
| `claude mcp login <name>` | OAuth-Anmeldung |

Tokens als `${VAR}` eintragen, nie im Klartext. Mehr: [MCP](docs/anleitungen/claude-code-mcp.md)

## Plugins

```bash
claude plugin marketplace add pexon-consulting/claude-code-best-practices
claude plugin install team-basis@claude-code-best-practices
```

Mehr: [Plugins](docs/anleitungen/claude-code-plugins.md)

## Audit für das eigene Repo

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team audit .
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team einrichten . --dry-run
```

Das Audit prüft CLAUDE.md, Settings, Hooks, MCP, Skills und Subagents gegen die [Prüfregeln](docs/regeln.md). `einrichten` überschreibt nichts, sondern legt Vorschläge als `settings.vorschlag.json` und `CLAUDE.vorschlag.md` an.

## Weiterlesen

- [Claude Code Statusline](docs/anleitungen/claude-code-statusline.md): Modell, Kontext und Kosten in der Statuszeile
- [Claude Code Plan Mode](docs/anleitungen/claude-code-plan-mode.md): erst planen, dann ändern
- [Claude Code Kosten](docs/anleitungen/claude-code-kosten.md): was ein Team ausgibt
- [Claude Code Team-Rollout](docs/anleitungen/claude-code-team-rollout.md): Einführung im Unternehmen
- Offizielle Doku: [Commands](https://code.claude.com/docs/en/commands), [CLI-Referenz](https://code.claude.com/docs/en/cli-reference), [Settings](https://code.claude.com/docs/en/settings)
