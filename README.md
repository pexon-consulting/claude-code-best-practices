# Claude Code Best Practices: Vorlagen und Anleitungen für Teams (Deutsch)

Dieses Repo sammelt Claude Code Best Practices auf Deutsch: 35 Anleitungen zu CLAUDE.md, settings.json, Permissions, Hooks, Skills, Subagents, Plugins, MCP, DSGVO, Bedrock und Kosten, dazu fertige Vorlagen und das Werkzeug `claude-team`, das ein Repo in einem Befehl einrichtet und in CI prüft. Es richtet sich an Entwicklerteams und Plattform-Teams, die Claude Code einheitlich und sicher einsetzen wollen. Die mitgelieferten Hooks blockieren Secrets und deutsche personenbezogene Daten (IBAN, Steuer-ID, Sozialversicherungsnummer) mit echter Prüfziffernprüfung, bevor sie im Kontext des Modells landen.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. MIT-Lizenz. [English summary below](#english).

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team einrichten .
```

## Inhalt

- [Was ist Claude Code?](#was-ist-claude-code)
- [Claude Code Best Practices auf einen Blick](#claude-code-best-practices-auf-einen-blick)
- [Schnellstart: Repo in fünf Minuten einrichten](#schnellstart-repo-in-fünf-minuten-einrichten)
- [Claude Code installieren und einrichten](#claude-code-installieren-und-einrichten)
- [CLAUDE.md und AGENTS.md: Projektwissen für den Agenten](#claudemd-und-agentsmd-projektwissen-für-den-agenten)
- [settings.json und Berechtigungen (Permissions)](#settingsjson-und-berechtigungen-permissions)
- [Claude Code Hooks gegen Secrets und personenbezogene Daten](#claude-code-hooks-gegen-secrets-und-personenbezogene-daten)
- [Skills, Subagents und Plugins in Claude Code](#skills-subagents-und-plugins-in-claude-code)
- [MCP-Server in Claude Code einbinden](#mcp-server-in-claude-code-einbinden)
- [Claude Code im Team ausrollen](#claude-code-im-team-ausrollen)
- [Claude Code und DSGVO: Datenschutz im Unternehmen](#claude-code-und-dsgvo-datenschutz-im-unternehmen)
- [Claude Code mit Amazon Bedrock, Google Vertex AI und Microsoft Azure](#claude-code-mit-amazon-bedrock-google-vertex-ai-und-microsoft-azure)
- [Claude Code in CI: GitHub Actions und automatisches Code Review](#claude-code-in-ci-github-actions-und-automatisches-code-review)
- [Claude Code Kosten und Tokens im Griff](#claude-code-kosten-und-tokens-im-griff)
- [Claude Code, Codex und Cursor im Vergleich](#claude-code-codex-und-cursor-im-vergleich)
- [Alle Anleitungen](#alle-anleitungen)
- [Vorlagen](#vorlagen)
- [Das Werkzeug claude-team](#das-werkzeug-claude-team)
- [Häufige Fragen zu Claude Code (FAQ)](#häufige-fragen-zu-claude-code-faq)
- [Claude Code Best Practices in English](#english)
- [Mitmachen und Lizenz](#mitmachen-und-lizenz)

## Was ist Claude Code?

Claude Code ist der Coding-Agent von Anthropic. Er läuft im Terminal, in VS Code, Cursor und JetBrains sowie als Desktop-App, liest den Code eines Projekts, führt Befehle aus, ändert Dateien und erstellt Commits und Pull Requests. Gesteuert wird er über Textdateien im Repo: die CLAUDE.md für Projektwissen, die `.claude/settings.json` für Rechte und Hooks, `.claude/skills/` und `.claude/agents/` für wiederkehrende Aufgaben und die `.mcp.json` für externe Werkzeuge.

Genau diese Dateien entscheiden, ob Claude Code in einem Team gut arbeitet. Fehlen sie, rät der Agent Testbefehle, fragt bei jedem `git status` nach oder liest im schlimmsten Fall eine `.env` mit Produktionszugängen. Dieses Repo zeigt, was in die Dateien gehört, und liefert geprüfte Vorlagen dafür.

## Claude Code Best Practices auf einen Blick

1. **Kurze CLAUDE.md mit Befehlen zuerst.** Build-, Test- und Lint-Befehle oben, unter 200 Zeilen, alles Bereichsspezifische in `.claude/rules/`. ([Anleitung](docs/anleitungen/claude-md.md))
2. **Eine Quelle für alle Agents.** Gemeinsame Regeln in die AGENTS.md, die CLAUDE.md beginnt mit `@AGENTS.md` und ergänzt nur Claude-Spezifisches. ([Anleitung](docs/anleitungen/agents-md.md))
3. **Rechte ausdrücklich festlegen.** `deny` für `.env`, Schlüssel und Cloud-Credentials, `ask` für Push und Deploy, `allow` nur für konkrete Befehle wie `Bash(git status *)`. ([Anleitung](docs/anleitungen/claude-code-permissions.md))
4. **Was zwingend gelten muss, gehört in einen Hook.** Eine Anweisung in der CLAUDE.md ist eine Bitte, ein `PreToolUse`-Hook läuft bei jedem Aufruf. ([Anleitung](docs/anleitungen/claude-code-hooks.md))
5. **Kein `bypassPermissions` im Repo.** `--dangerously-skip-permissions` nur in einem Container ohne Zugangsdaten vom Host. ([Anleitung](docs/anleitungen/claude-code-dangerously-skip-permissions.md))
6. **MCP-Tokens nie im Klartext.** In der `.mcp.json` stehen `${VARIABLEN}`, die Server-Versionen sind gepinnt. ([Anleitung](docs/anleitungen/claude-code-mcp.md))
7. **Erst planen, dann ändern.** Plan Mode für alles, was mehrere Dateien betrifft oder unklar ist. ([Anleitung](docs/anleitungen/claude-code-plan-mode.md))
8. **Kontext sauber halten.** `/clear` zwischen Aufgaben, Subagents für große Ausgaben, Skills statt Dauertext in der CLAUDE.md. ([Anleitung](docs/anleitungen/claude-code-memory.md))
9. **Team-Konfiguration ins Repo, Persönliches daneben.** `.claude/settings.json` und `CLAUDE.md` werden committet, `settings.local.json` und `CLAUDE.local.md` stehen in der `.gitignore`. ([Anleitung](docs/anleitungen/claude-code-settings-json.md))
10. **Konfiguration in CI prüfen.** `claude-team audit` als GitHub Action findet wirkungslose Regeln, kaputte Hook-Pfade und Tokens, bevor sie im Hauptbranch landen. ([Regeln](docs/regeln.md))

## Schnellstart: Repo in fünf Minuten einrichten

Du brauchst Python 3.10 oder neuer. Mit [uv](https://docs.astral.sh/uv/) geht es ohne Installation:

```bash
# Repo prüfen
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team audit .

# erst ansehen, was angelegt würde
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team einrichten . --dry-run

# einrichten
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team einrichten .
```

Oder dauerhaft mit pip:

```bash
pip install git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0
claude-team einrichten .
claude-team audit .
```

`einrichten` überschreibt nichts. Gibt es schon eine CLAUDE.md oder settings.json, entsteht daneben ein Vorschlag (`CLAUDE.vorschlag.md`, `.claude/settings.vorschlag.json`), den du mit `diff` vergleichst. Die `.gitignore` wird nur ergänzt. Die Befehle in der neuen CLAUDE.md erkennt das Werkzeug aus `package.json`, `pyproject.toml`, `uv.lock`, `go.mod`, `Cargo.toml` und ähnlichen Dateien.

Danach liegt im Repo:

```text
CLAUDE.md                      Projektwissen mit erkannten Befehlen
.claude/settings.json          Rechte, Telemetrie aus, Hooks
.claude/schutz.json            Einstellungen der Schutz-Hooks
.claude/hooks/                 sieben Hooks in Python, ohne Abhängigkeiten
.claude/rules/tests.md         Beispiel für eine Bereichsregel
.claude/agents/                code-reviewer, datenschutz-check
.claude/skills/                commit, handoff
.mcp.json.example              MCP-Vorlage mit ${VARIABLEN}
```

Als Plugin für alle eigenen Projekte, ohne Dateien im Repo:

```bash
claude plugin marketplace add pexon-consulting/claude-code-best-practices
claude plugin install team-basis@claude-code-best-practices
```

Das Plugin `team-basis` bringt die Schutz-Hooks für Secrets, personenbezogene Daten und gefährliche Befehle mit, dazu den Sitzungsstart-Hook, die beiden Subagents und die Skills. Protokoll und Formatierung bleiben dem Repo überlassen, weil sie projektabhängig sind.

Die Skills gibt es auch für andere Agents über [skills.sh](https://skills.sh):

```bash
npx skills add pexon-consulting/claude-code-best-practices
```

Die [27 Beispiele](docs/beispiele.md) zeigen jeden Befehl und jeden Hook mit echter Ein- und Ausgabe.

## Claude Code installieren und einrichten

Der native Installer ist der empfohlene Weg:

```bash
# macOS, Linux, WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

Du brauchst ein Pro-, Max-, Team-, Enterprise- oder Console-Konto, der kostenlose Plan reicht nicht. Danach startest du `claude` im Projektordner, meldest dich im Browser an und prüfst die Installation mit `claude doctor`. Unter Windows läuft Claude Code nativ, WSL brauchst du nur für Linux-Toolchains oder die eingebaute Sandbox.

- [Claude Code installieren: Schritt für Schritt für macOS, Linux und Windows](docs/anleitungen/claude-code-installieren.md)
- [Claude Code Windows: Installation mit WSL, Git Bash und PowerShell](docs/anleitungen/claude-code-windows.md)
- [Claude Code VS Code und JetBrains: IDE-Integration einrichten](docs/anleitungen/claude-code-vscode-jetbrains.md)
- [Claude Code Tutorial auf Deutsch: die erste Stunde mit Claude Code](docs/anleitungen/claude-code-tutorial-deutsch.md)

## CLAUDE.md und AGENTS.md: Projektwissen für den Agenten

Die CLAUDE.md liest Claude Code zu Beginn jeder Sitzung. Hinein gehören die Befehle, die Claude sonst rät, der Aufbau des Projekts, Konventionen, die nicht aus dem Code hervorgehen, und feste Regeln. Nicht hinein gehören Dinge, die ein Linter prüft, lange Stilvorgaben und alles, was nur für einen Ordner gilt.

```markdown
# rechnungen

Rechnungsexport für das Buchhaltungssystem, Python 3.12, FastAPI.

## Befehle

uv sync                    # Abhängigkeiten
uv run pytest              # Tests, vor jedem Commit
ruff check . && ruff format --check .

## Regeln

- Beträge immer als Decimal, nie als float.
- Neue Endpunkte brauchen einen Test in tests/api/.
- Kundendaten in Tests nur aus tests/fixtures/, nie echte Daten.
```

Arbeiten im Repo auch Codex oder Cursor, ist die AGENTS.md die gemeinsame Quelle. Claude Code liest sie seit v2.1.277 selbst, aber nur, wenn keine CLAUDE.md existiert. Robust für alle Versionen ist eine CLAUDE.md, die mit `@AGENTS.md` beginnt.

- [CLAUDE.md: Aufbau, Beispiele und Best Practices für Teams](docs/anleitungen/claude-md.md)
- [AGENTS.md und CLAUDE.md: gemeinsame Anweisungen für Claude Code, Codex und Cursor](docs/anleitungen/agents-md.md)
- [Claude Code Rules: modulare Regeln in .claude/rules statt einer riesigen CLAUDE.md](docs/anleitungen/claude-code-rules.md)
- [Claude Code Memory: Kontext, /compact und Sitzungen steuern](docs/anleitungen/claude-code-memory.md)

## settings.json und Berechtigungen (Permissions)

Die `.claude/settings.json` legt fest, was Claude ohne Rückfrage darf. Geprüft wird immer in der Reihenfolge `deny`, dann `ask`, dann `allow`. Ein Ausschnitt aus der Vorlage:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "defaultMode": "default",
    "disableBypassPermissionsMode": "disable",
    "allow": ["Bash(git status *)", "Bash(git diff *)", "Bash(pytest *)"],
    "ask": ["Bash(git push *)", "Bash(terraform apply *)", "WebFetch"],
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(!.env.example)",
      "Read(**/*.pem)",
      "Read(~/.aws/**)",
      "Bash(git push --force *)"
    ]
  },
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1"
  }
}
```

Drei Fallen, die das Audit erkennt:

- `Write(.env)` als deny-Regel wird nie geprüft. Pfadregeln wirken für `Read` und `Edit`, eine Read-Sperre blockiert auch Schreiben ([CC017](docs/regeln.md#cc017)).
- `Bash(git * main)` erlaubt jeden Unterbefehl samt Optionen wie `-c`, weil der Stern vor dem Unterbefehl steht ([CC016](docs/regeln.md#cc016)).
- `defaultMode: bypassPermissions` in der Projektdatei schaltet die Rückfragen für alle ab, die das Repo klonen ([CC012](docs/regeln.md#cc012)). Neuere Versionen ignorieren den Wert aus Projektdateien, ältere nicht.

- [Claude Code settings.json: alle wichtigen Einstellungen mit Vorlage](docs/anleitungen/claude-code-settings-json.md)
- [Claude Code Permissions: Berechtigungen mit allow, ask und deny festlegen](docs/anleitungen/claude-code-permissions.md)
- [Claude Code dangerously-skip-permissions: YOLO-Modus sicher in Sandbox und Container](docs/anleitungen/claude-code-dangerously-skip-permissions.md)
- [Claude Code Plan Mode: erst planen, dann ändern lassen](docs/anleitungen/claude-code-plan-mode.md)
- [Claude Code Sandbox: isoliert arbeiten mit Devcontainer und Docker](docs/anleitungen/claude-code-sandbox.md)

## Claude Code Hooks gegen Secrets und personenbezogene Daten

Deny-Regeln greifen nur, wenn das Muster passt. `cat .env` erkennt Claude Code, `grep DATABASE config/.env.production | head -1` oder `env | sort` nicht zuverlässig. Deshalb liefert die Vorlage sieben Hooks in reinem Python, ohne Abhängigkeiten:

| Hook | Ereignis | Was er tut |
| --- | --- | --- |
| `secrets_schutz.py` | PreToolUse | sperrt `.env`, Schlüssel und Cloud-Credentials für Read, Edit, Grep und jeden Lesebefehl in Bash und PowerShell, blockt `env`, `printenv` und `Get-ChildItem env:`, erkennt im neuen Code Tokens von GitHub, GitLab, AWS, Anthropic, OpenAI, Google, Slack, Stripe und Azure, private Schlüssel, JWTs und URLs mit Passwort |
| `pii_schutz.py` | PreToolUse, UserPromptSubmit | erkennt IBAN, Steuer-ID, Sozialversicherungsnummer, Kreditkarten (Luhn) und USt-IdNr. mit echter Prüfziffernprüfung, lässt die Muster-IBAN der Bundesbank und bekannte Testkarten durch, fragt bei eingefügten Kundenlisten nach |
| `befehle_schutz.py` | PreToolUse | blockt `rm -rf` und `Remove-Item -Recurse` auf Home, Wurzel oder Arbeitsordner, Force-Push und `curl \| sh` oder `irm \| iex`, auch hinter `cd` oder `&&`; fragt bei `sudo` nach und bei Befehlen aus `befehle.fragen_bei` immer |
| `stopp_tests.py` | Stop | lässt Claude erst fertig melden, wenn der Testbefehl grün ist, mit Schleifenschutz |
| `sitzungsstart.py` | SessionStart | gibt Branch, offene Änderungen und letzte Commits als Kontext mit, warnt auf dem Hauptbranch |
| `protokoll.py` | PostToolUse | schreibt eine Zeile je Tool-Aufruf nach `.claude/protokoll/`, ohne Dateiinhalte, Tokens maskiert |
| `format_nach_edit.py` | PostToolUse | formatiert geänderte Dateien mit ruff oder black, prettier, gofmt, rustfmt oder terraform fmt, wenn vorhanden |

So sieht ein Treffer aus. Claude will eine IBAN mit gültiger Prüfziffer in eine Seed-Datei schreiben, der Hook antwortet:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Personenbezogene Daten gefunden: IBAN DE27****************78. Durch Testdaten ersetzen (z.B. die Muster-IBAN DE89 3704 0044 0532 0130 00)."
  }
}
```

Die Prüfziffer macht den Unterschied: Eine zufällige 22-stellige Zahl mit `DE` davor löst nichts aus, eine echte IBAN schon. Das hält die Fehlalarme niedrig. Einstellbar ist alles in `.claude/schutz.json`, zum Beispiel `"modus": "ask"` statt `"deny"` oder Ausnahmen für `tests/fixtures/**`. Bei kaputter Eingabe lassen die Hooks durch, statt die Sitzung zu blockieren.

Hooks testest du ohne Claude, indem du das JSON per Pipe übergibst:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"cd /tmp && rm -rf ~"}}' | python3 .claude/hooks/befehle_schutz.py
```

- [Claude Code Hooks: Secrets und personenbezogene Daten automatisch blockieren](docs/anleitungen/claude-code-hooks.md)
- [Alle Hook-Beispiele mit Ein- und Ausgabe](docs/beispiele.md#beispiel-12)
- [Claude Code Security: Sicherheitsregeln für Teams und Unternehmen](docs/anleitungen/claude-code-sicherheit.md)

## Skills, Subagents und Plugins in Claude Code

Die drei Bausteine lösen verschiedene Probleme:

| Baustein | Datei | Wofür |
| --- | --- | --- |
| Skill | `.claude/skills/<name>/SKILL.md` | wiederkehrende Aufgabe mit Anleitung, per `/name` oder automatisch geladen, teilt den Kontext mit der Sitzung |
| Subagent | `.claude/agents/<name>.md` | abgeschlossene Aufgabe mit eigenem Kontext und eigenen Tool-Grenzen, gibt nur eine Zusammenfassung zurück |
| Plugin | `.claude-plugin/plugin.json` | Paket aus Skills, Subagents, Hooks und MCP-Servern, über einen Marketplace verteilt |

Ein Skill reicht für "so committen wir" oder "so schreiben wir eine Migration". Ein Subagent lohnt sich, wenn eine Aufgabe viel Ausgabe erzeugt, etwa ein Review über 40 Dateien. Ein Plugin ist der Weg, Skills und Hooks über viele Repos hinweg aktuell zu halten.

Dieses Repo ist selbst ein Plugin-Marketplace und enthält vier Skills: `claude-code-audit`, `claude-code-einrichten`, `claude-md-schreiben` und `hook-schreiben`.

- [Claude Code Skills: eigene Skills erstellen, testen und im Team teilen](docs/anleitungen/claude-code-skills.md)
- [Claude Code Subagents: eigene Agenten definieren und richtig delegieren](docs/anleitungen/claude-code-subagents.md)
- [Claude Code Plugins: Marketplace einrichten und Plugins im Team verteilen](docs/anleitungen/claude-code-plugins.md)
- [Claude Code Agent Teams: mehrere Agenten parallel koordinieren](docs/anleitungen/claude-code-agent-teams.md)
- [Claude Code Befehle: Slash Commands, CLI-Flags und Shortcuts als Cheat Sheet](docs/anleitungen/claude-code-befehle.md)
- [Claude Code Statusline: Modell, Kontext und Kosten in der Statuszeile anzeigen](docs/anleitungen/claude-code-statusline.md)

## MCP-Server in Claude Code einbinden

MCP-Server geben Claude Zugriff auf Werkzeuge wie GitHub, Sentry oder eine Datenbank. Hinzufügen geht per Befehl:

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
claude mcp add --scope project --transport http github https://api.githubcopilot.com/mcp/
```

Mit `--scope project` landet der Eintrag in der `.mcp.json` im Projekt und gilt für alle. Dann darf dort kein Token stehen:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres@0.6.2", "${DATABASE_URL}"]
    }
  }
}
```

Das Audit meldet Tokens im Klartext ([CC032](docs/regeln.md#cc032)), Server ohne feste Version ([CC033](docs/regeln.md#cc033)) und HTTP-Server ohne `"type"`, die Claude Code beim Start mit einer Warnung überspringt ([CC034](docs/regeln.md#cc034)).

- [Claude Code MCP: MCP-Server hinzufügen, konfigurieren und absichern](docs/anleitungen/claude-code-mcp.md)

## Claude Code im Team ausrollen

Ein Rollout hat drei Ebenen: das Repo (CLAUDE.md, settings.json, Hooks), den Rechner (Plugin, persönliche Einstellungen) und die Organisation (Managed Settings, Verträge, Budgets). Managed Settings liegen im Systemverzeichnis jedes Rechners oder kommen per MDM und gelten über allen anderen Ebenen. Damit sperrst du den Bypass-Modus, legst deny-Regeln und Telemetrie fest und erlaubst Plugins nur aus freigegebenen Marketplaces.

Für den Weg durch IT-Sicherheit, Datenschutz und Betriebsrat liegen unter [`docs/rollout/`](docs/rollout/README.md) ausfüllbare Vorlagen:

| Vorlage | Für wen |
| --- | --- |
| [Pilotplan](docs/rollout/pilotplan.md) | Teamleitung: sechs Wochen Pilot mit Messgrößen und Abbruchkriterien |
| [Freigabe-Paket](docs/rollout/freigabe-paket.md) | IT-Sicherheit: Datenflüsse, Einstellungen, Restrisiken |
| [TOM-Vorlage](docs/rollout/tom-vorlage.md) | Datenschutz: technische und organisatorische Maßnahmen |
| [DSFA-Vorlage](docs/rollout/dsfa-vorlage.md) | Datenschutz: Datenschutz-Folgenabschätzung |
| [Infoblatt für den Betriebsrat](docs/rollout/betriebsrat-infoblatt.md) | Betriebsrat: was protokolliert wird und was nicht |
| [Kostenrichtlinie](docs/rollout/kostenrichtlinie.md) | Controlling: Budgets, Modelle, Limits |
| [managed-settings.json](vorlagen/managed-settings.json) | Plattform-Team: Ausgangsfassung für die zentrale Verteilung |

- [Claude Code im Team: Rollout, Onboarding und gemeinsame Konfiguration](docs/anleitungen/claude-code-team-rollout.md)
- [Claude Code Enterprise: Managed Settings, SSO und zentrale Richtlinien](docs/anleitungen/claude-code-enterprise.md)
- [Claude Code Workflow: Erkunden, Planen, Umsetzen, Committen](docs/anleitungen/claude-code-workflow.md)

## Claude Code und DSGVO: Datenschutz im Unternehmen

Claude Code lässt sich DSGVO-konform einsetzen, wenn drei Dinge zusammenkommen: ein kommerzieller Vertrag (Team, Enterprise, API oder ein Cloud-Anbieter wie Amazon Bedrock) mit Auftragsverarbeitungsvertrag, eine bewusst gewählte Region und Einstellungen, die Telemetrie, Feedback-Uploads und personenbezogene Daten im Prompt begrenzen. Alles, was Claude liest oder du eingibst, geht als Prompt an das Modell. Die Betriebsvariante entscheidet, wer die Daten verarbeitet und wie lange sie gespeichert werden.

Technisch hilft dieses Repo an drei Stellen: `DISABLE_TELEMETRY` und `DISABLE_ERROR_REPORTING` im `env`-Block, `cleanupPeriodDays` für lokale Verläufe und der PII-Hook, der IBAN, Steuer-ID und Sozialversicherungsnummer stoppt, bevor sie im Prompt landen. Die rechtliche Bewertung bleibt Sache deines Datenschutzbeauftragten. Die Anleitung ist keine Rechtsberatung.

- [Claude Code DSGVO: datenschutzkonform im Unternehmen einsetzen](docs/anleitungen/claude-code-dsgvo.md)
- [Datenschutzhinweis zu diesem Repo und dem Werkzeug](PRIVACY.md)

## Claude Code mit Amazon Bedrock, Google Vertex AI und Microsoft Azure

Claude Code läuft auch über die Konten der großen Cloud-Anbieter. Abgerechnet wird dann über die Cloud-Rechnung, und die Region legst du selbst fest.

```bash
# Amazon Bedrock in Frankfurt
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=eu-central-1

# Google Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_PROJECT_ID=mein-projekt
export CLOUD_ML_REGION=europe-west1

# Microsoft Foundry
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=meine-ressource
```

In jedem Fall gilt: Modellversionen pinnen und die Variablen zentral über Managed Settings verteilen, nicht über persönliche Shell-Profile.

- [Claude Code Bedrock: Claude Code über Amazon Bedrock in der EU betreiben](docs/anleitungen/claude-code-bedrock.md)
- [Claude Code Vertex AI: Claude Code über Google Cloud betreiben](docs/anleitungen/claude-code-vertex-ai.md)
- [Claude Code Azure: Claude Code über Microsoft Foundry nutzen](docs/anleitungen/claude-code-azure-foundry.md)
- [Claude Code Proxy und LLM-Gateway: LiteLLM, OpenRouter und Firmen-Gateways](docs/anleitungen/claude-code-llm-gateway.md)

## Claude Code in CI: GitHub Actions und automatisches Code Review

Zwei Dinge gehören in die Pipeline: Claude als Reviewer für Pull Requests und eine Prüfung der Claude-Konfiguration selbst. Für das Review gibt es die offizielle Action `anthropics/claude-code-action@v1`. Für die Konfiguration bringt dieses Repo eine eigene Action mit, die Befunde als SARIF in GitHub Code Scanning hochlädt:

```yaml
name: claude-code-audit
on: [pull_request]
permissions:
  contents: read
  security-events: write
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pexon-consulting/claude-code-best-practices@v0.1.0
        with:
          schwelle: warnung
          sarif: true
```

Die Action schreibt den Bericht in die Step Summary und schlägt fehl, wenn ein Befund die Schwelle erreicht. Ohne Action geht dasselbe mit `claude-team audit . --schwelle warnung --format markdown`.

- [Claude Code Review: automatische Reviews mit GitHub Actions](docs/anleitungen/claude-code-review-github-actions.md)
- [Claude Agent SDK: eigene Agenten auf Basis von Claude Code bauen](docs/anleitungen/claude-agent-sdk.md)

## Claude Code Kosten und Tokens im Griff

Laut offizieller Kosten-Doku liegen die Kosten in Unternehmen im Schnitt bei etwa 13 US-Dollar pro Entwickler und aktivem Tag und 150-250 US-Dollar im Monat. Abgerechnet wird über ein Abo mit Kontingent pro Sitz oder nach Tokens über die API, Bedrock, Vertex AI oder Foundry. Was eine Sitzung verbraucht, zeigt `/usage`, was den Kontext füllt, zeigt `/context`.

Am meisten sparen: `/clear` zwischen Aufgaben, eine kurze CLAUDE.md, Skills statt Dauertext, Subagents für große Ausgaben und das passende Modell. Für automatisierte Läufe begrenzt `--max-budget-usd` die Ausgaben.

- [Claude Code Kosten: Abo oder API, Budgets und Limits im Team](docs/anleitungen/claude-code-kosten.md)
- [Claude Code Usage: Token-Verbrauch messen und senken](docs/anleitungen/claude-code-usage-tokens.md)

## Claude Code, Codex und Cursor im Vergleich

Claude Code ist ein Agent, der im Terminal, in IDE-Erweiterungen und als Desktop-App läuft. Codex ist der Coding-Agent von OpenAI, Cursor ist ein Editor mit eingebauten KI-Funktionen. Für Teams zählen neben dem Modell die Konfigurationsdateien, Hooks, Skills, MCP und der Betrieb über eigene Cloud-Konten. Viele Teams nutzen mehrere Werkzeuge parallel. Eine gemeinsame AGENTS.md hält die Regeln dann an einer Stelle, und die Claude-Code-Erweiterung läuft auch in Cursor.

- [Claude Code vs Codex und Cursor: Unterschiede für Teams](docs/anleitungen/claude-code-vs-codex-cursor.md)

## Alle Anleitungen

Jede Anleitung beginnt mit einer direkten Antwort, dann folgen Vorlagen, Schritte, häufige Fehler mit Fehlermeldung und Lösung sowie Links zu den Nachbarthemen.

| Anleitung | Beantwortet | Stufe |
| --- | --- | --- |
| **Einstieg** | | |
| [Claude Code installieren](docs/anleitungen/claude-code-installieren.md) | Wie installiere ich Claude Code und was brauche ich dafür? | Einstieg |
| [Claude Code unter Windows](docs/anleitungen/claude-code-windows.md) | Läuft Claude Code nativ unter Windows oder brauche ich WSL? | Einstieg |
| [Claude Code Tutorial auf Deutsch](docs/anleitungen/claude-code-tutorial-deutsch.md) | Wie fange ich mit Claude Code an? | Einstieg |
| [VS Code und JetBrains](docs/anleitungen/claude-code-vscode-jetbrains.md) | Wie verbinde ich Claude Code mit VS Code oder IntelliJ? | Einstieg |
| [Befehle und Shortcuts](docs/anleitungen/claude-code-befehle.md) | Welche Slash Commands und CLI-Flags gibt es? | Einstieg |
| [Workflow](docs/anleitungen/claude-code-workflow.md) | Welcher Ablauf liefert die besten Ergebnisse? | Einstieg |
| [Plan Mode](docs/anleitungen/claude-code-plan-mode.md) | Wie aktiviere ich den Plan Mode und wann lohnt er sich? | Einstieg |
| **Projekt-Konfiguration** | | |
| [CLAUDE.md](docs/anleitungen/claude-md.md) | Was gehört in eine CLAUDE.md und wie lang darf sie sein? | Grundlagen |
| [AGENTS.md](docs/anleitungen/agents-md.md) | Liest Claude Code die AGENTS.md und wie halte ich beide synchron? | Grundlagen |
| [Rules](docs/anleitungen/claude-code-rules.md) | Wie teile ich Regeln auf mehrere Dateien auf? | Grundlagen |
| [Memory und Kontext](docs/anleitungen/claude-code-memory.md) | Wie merkt sich Claude Wissen und wann nutze ich /compact? | Grundlagen |
| [settings.json](docs/anleitungen/claude-code-settings-json.md) | Welche Ebenen gibt es und welche gewinnt? | Grundlagen |
| [Permissions](docs/anleitungen/claude-code-permissions.md) | Wie erlaube ich Befehle dauerhaft und verbiete andere? | Grundlagen |
| [Statusline](docs/anleitungen/claude-code-statusline.md) | Wie zeige ich Modell, Kontext und Kosten in der Statuszeile? | Grundlagen |
| **Erweitern** | | |
| [Hooks](docs/anleitungen/claude-code-hooks.md) | Wie blockiere ich .env-Zugriffe und personenbezogene Daten? | Fortgeschritten |
| [Skills](docs/anleitungen/claude-code-skills.md) | Wie erstelle ich einen Skill und wo liegt die SKILL.md? | Fortgeschritten |
| [Subagents](docs/anleitungen/claude-code-subagents.md) | Wann lohnt sich ein Subagent und wie definiere ich ihn? | Fortgeschritten |
| [Agent Teams](docs/anleitungen/claude-code-agent-teams.md) | Wann lohnen sich mehrere Agenten parallel? | Fortgeschritten |
| [Plugins](docs/anleitungen/claude-code-plugins.md) | Wie installiere ich Plugins und betreibe einen Team-Marketplace? | Fortgeschritten |
| [MCP](docs/anleitungen/claude-code-mcp.md) | Wie füge ich einen MCP-Server hinzu und sichere ihn ab? | Fortgeschritten |
| [Claude Agent SDK](docs/anleitungen/claude-agent-sdk.md) | Was unterscheidet das SDK von Claude Code? | Fortgeschritten |
| **Sicherheit und Betrieb** | | |
| [Sicherheit](docs/anleitungen/claude-code-sicherheit.md) | Welche Risiken gibt es und wie begrenzt man sie? | Team |
| [dangerously-skip-permissions](docs/anleitungen/claude-code-dangerously-skip-permissions.md) | Wann ist der YOLO-Modus vertretbar? | Team |
| [Sandbox und Devcontainer](docs/anleitungen/claude-code-sandbox.md) | Wie starte ich Claude Code isoliert? | Team |
| [DSGVO](docs/anleitungen/claude-code-dsgvo.md) | Ist Claude Code DSGVO-konform nutzbar? | Team |
| [Team-Rollout](docs/anleitungen/claude-code-team-rollout.md) | Wie rolle ich Claude Code einheitlich aus? | Team |
| [Enterprise und Managed Settings](docs/anleitungen/claude-code-enterprise.md) | Wie erzwinge ich Einstellungen für alle? | Team |
| [Code Review mit GitHub Actions](docs/anleitungen/claude-code-review-github-actions.md) | Wie prüft Claude Pull Requests automatisch? | Team |
| **Cloud und Kosten** | | |
| [Amazon Bedrock](docs/anleitungen/claude-code-bedrock.md) | Wie betreibe ich Claude Code über Bedrock in der EU? | Team |
| [Google Vertex AI](docs/anleitungen/claude-code-vertex-ai.md) | Welche Variablen braucht Claude Code für Vertex AI? | Team |
| [Microsoft Foundry](docs/anleitungen/claude-code-azure-foundry.md) | Kann ich Claude Code über Azure betreiben? | Team |
| [LLM-Gateway und Proxy](docs/anleitungen/claude-code-llm-gateway.md) | Wie leite ich Claude Code über ein Firmen-Gateway? | Team |
| [Kosten](docs/anleitungen/claude-code-kosten.md) | Was kostet Claude Code pro Entwickler? | Team |
| [Usage und Tokens](docs/anleitungen/claude-code-usage-tokens.md) | Wie messe und senke ich den Token-Verbrauch? | Team |
| [Claude Code vs Codex und Cursor](docs/anleitungen/claude-code-vs-codex-cursor.md) | Wann ist welches Werkzeug die bessere Wahl? | Team |

Zum Nachschlagen: das [Cheat Sheet](CHEATSHEET.md) mit Befehlen, Shortcuts und Dateipfaden auf einer Seite.

## Vorlagen

Alle Vorlagen liegen unter [`src/claude_team/vorlage/`](src/claude_team/vorlage/) und werden von `claude-team einrichten` ins Repo kopiert. Du kannst sie auch direkt übernehmen.

| Datei | Inhalt |
| --- | --- |
| [CLAUDE.md](src/claude_team/vorlage/CLAUDE.md) | Gerüst mit Befehlen, Aufbau, Arbeitsweise und Regeln |
| [.claude/settings.json](src/claude_team/vorlage/.claude/settings.json) | Rechte, Telemetrie aus, alle Hooks registriert |
| [.claude/schutz.json](src/claude_team/vorlage/.claude/schutz.json) | Modus, Ausnahmen und freigabepflichtige Befehle für die Hooks |
| [.claude/hooks/](src/claude_team/vorlage/.claude/hooks/) | sieben Hooks in reinem Python, ohne Abhängigkeiten |
| [.claude/agents/code-reviewer.md](src/claude_team/vorlage/.claude/agents/code-reviewer.md) | Review-Subagent: liest Diff und Umfeld, ändert nichts, meldet nach Dringlichkeit |
| [.claude/agents/datenschutz-check.md](src/claude_team/vorlage/.claude/agents/datenschutz-check.md) | prüft Änderungen auf personenbezogene Daten |
| [.claude/skills/commit/](src/claude_team/vorlage/.claude/skills/commit/SKILL.md) | Commit nach Conventional Commits, nur auf Wunsch |
| [.claude/skills/handoff/](src/claude_team/vorlage/.claude/skills/handoff/SKILL.md) | Übergabe-Notiz am Ende einer Sitzung |
| [.mcp.json.example](src/claude_team/vorlage/.mcp.json.example) | MCP-Server mit `${VARIABLEN}` und gepinnten Versionen |
| [vorlagen/managed-settings.json](vorlagen/managed-settings.json) | Managed Settings für die zentrale Verteilung |

Mit `--profil streng` sperrt die settings.json zusätzlich `WebFetch`, `WebSearch` und Netzwerkbefehle wie `curl`, `wget`, `ssh`, `scp` und `nc`, etwa für Repos mit Kundendaten.

## Das Werkzeug claude-team

| Befehl | Was er tut |
| --- | --- |
| `claude-team audit [pfad]` | prüft CLAUDE.md, Settings, Hooks, MCP, Subagents, Skills und Git gegen 35 Regeln |
| `claude-team einrichten [pfad]` | legt die Vorlagen an, ohne zu überschreiben |
| `claude-team scannen [pfad\|-]` | durchsucht alle Dateien, die Git kennt, oder stdin nach Secrets und personenbezogenen Daten |
| `claude-team regeln` | listet alle Regeln mit Schwere |

Wichtige Optionen:

```bash
claude-team audit . --schwelle warnung          # Exit 1 ab Warnung, Standard ist fehler
claude-team audit . --format markdown           # für PR-Kommentar und Step Summary
claude-team audit . --format json               # für eigene Auswertungen
claude-team audit . --format sarif              # für GitHub Code Scanning
claude-team audit . --ignorieren CC003,CC019    # Regeln auslassen
claude-team einrichten . --ohne agents,skills   # Bausteine auslassen
claude-team einrichten . --profil streng        # zusätzlich Web und Netz sperren
echo "Text" | claude-team scannen -             # stdin prüfen, z.B. im pre-commit-Hook
```

Die 35 Regeln (16 Fehler, 12 Warnungen, 7 Hinweise) sind in [docs/regeln.md](docs/regeln.md) einzeln erklärt, jede mit Begründung, Beispiel und Lösung. Ein typischer Bericht:

```text
FEHLER  CC012 .claude/settings.json
        defaultMode bypassPermissions schaltet alle Rückfragen ab, für jedes Teammitglied.
FEHLER  CC032 .mcp.json
        github.Authorization steht im Klartext. "Bearer ${GITHUB_TOKEN}" verwenden, Wert in der Shell setzen.
WARNUNG CC016 .claude/settings.json
        "Bash(git * main)": Der Stern steht vor dem Unterbefehl und erlaubt damit jeden Unterbefehl samt Optionen wie -c.
WARNUNG CC023 .claude/settings.json
        ".claude/hooks/check.py" ist relativ zum Arbeitsordner und bricht, wenn Claude in einen Unterordner wechselt. "${CLAUDE_PROJECT_DIR}" voranstellen.
```

Das Werkzeug sendet nichts ins Netz, liest keine Inhalte aus `~/.claude` und gibt gefundene Werte nur maskiert aus. Details in [PRIVACY.md](PRIVACY.md).

## Häufige Fragen zu Claude Code (FAQ)

### Was sind Claude Code Best Practices?

Claude Code Best Practices sind die Regeln, mit denen ein Team Claude Code verlässlich und sicher nutzt: eine kurze CLAUDE.md mit Befehlen, ausdrückliche Rechte in der settings.json, Hooks für alles, was zwingend gelten muss, MCP-Tokens nur über Variablen und eine Prüfung der Konfiguration in CI. Die [zehn wichtigsten](#claude-code-best-practices-auf-einen-blick) stehen oben, jede mit Anleitung.

### Was gehört in eine CLAUDE.md?

In eine CLAUDE.md gehören die Build-, Test- und Lint-Befehle, der Aufbau des Projekts, Konventionen, die nicht aus dem Code hervorgehen, und feste Regeln. Sie sollte unter 200 Zeilen bleiben. Bereichsregeln kommen nach `.claude/rules/`, zwingende Regeln in einen Hook. Siehe [CLAUDE.md-Anleitung](docs/anleitungen/claude-md.md).

### Was ist der Unterschied zwischen AGENTS.md und CLAUDE.md?

Die AGENTS.md ist ein werkzeugübergreifendes Format, das Codex, Cursor und andere Agents lesen, die CLAUDE.md ist die Datei von Claude Code. Claude Code liest die AGENTS.md seit v2.1.277 nur, wenn keine CLAUDE.md existiert. Am robustesten ist eine CLAUDE.md, die mit `@AGENTS.md` beginnt. Siehe [AGENTS.md-Anleitung](docs/anleitungen/agents-md.md).

### Wie installiere ich Claude Code unter Windows?

Unter Windows installierst du Claude Code nativ mit `irm https://claude.ai/install.ps1 | iex` in PowerShell, ohne Administratorrechte und ohne WSL. Git for Windows ist optional und liefert Git Bash für das Bash-Tool. WSL 2 brauchst du nur für Linux-Toolchains oder die eingebaute Sandbox. Siehe [Windows-Anleitung](docs/anleitungen/claude-code-windows.md).

### Was sind Claude Code Skills und wie erstelle ich einen?

Ein Skill ist ein Ordner mit einer `SKILL.md`, die Anweisungen für eine wiederkehrende Aufgabe enthält und per `/name` oder automatisch geladen wird. Du legst ihn unter `.claude/skills/<name>/SKILL.md` an, mit einem Frontmatter, das mindestens `description` enthält. Siehe [Skills-Anleitung](docs/anleitungen/claude-code-skills.md).

### Wie füge ich in Claude Code einen MCP-Server hinzu?

Mit `claude mcp add`, zum Beispiel `claude mcp add --transport http sentry https://mcp.sentry.dev/mcp`. Ohne Option (Scope `local`) gilt der Server nur für dich und nur in diesem Projekt, mit `--scope project` landet er in der `.mcp.json` des Projekts. Tokens gehören dort als `${VARIABLE}` hinein, nie im Klartext. Siehe [MCP-Anleitung](docs/anleitungen/claude-code-mcp.md).

### Wie verhindere ich, dass Claude Code .env-Dateien und Secrets liest?

Mit zwei Schichten: deny-Regeln wie `Read(.env)` und `Read(.env.*)` in der `.claude/settings.json` und einem `PreToolUse`-Hook, der auch Umwege wie `grep` in einer Bash-Kette oder `printenv` blockt. Beides legt `claude-team einrichten .` an. Siehe [Hooks-Anleitung](docs/anleitungen/claude-code-hooks.md) und [Beispiele](docs/beispiele.md#beispiel-13).

### Ist Claude DSGVO-konform nutzbar?

Ja, wenn ein kommerzieller Vertrag mit Auftragsverarbeitungsvertrag besteht, die Region bewusst gewählt ist und Telemetrie sowie personenbezogene Daten im Prompt technisch begrenzt sind. Die kostenlosen Verbraucher-Pläne sind für Unternehmensdaten nicht gedacht. Die Bewertung im Einzelfall trifft dein Datenschutzbeauftragter. Siehe [DSGVO-Anleitung](docs/anleitungen/claude-code-dsgvo.md).

### Was macht --dangerously-skip-permissions?

`--dangerously-skip-permissions` startet Claude Code im Modus `bypassPermissions`: Jeder Werkzeugaufruf läuft ohne Rückfrage. Vertretbar ist das nur in einem Container oder einer VM ohne Zugangsdaten vom Host, als normaler Nutzer und mit begrenztem Netz. Für weniger Rückfragen auf dem eigenen Rechner ist Auto Mode gedacht. Siehe [Anleitung](docs/anleitungen/claude-code-dangerously-skip-permissions.md).

### Was kostet Claude Code und wie spare ich Tokens?

Laut offizieller Doku im Schnitt etwa 13 US-Dollar pro Entwickler und aktivem Tag, 150-250 US-Dollar im Monat, abhängig von Modell, Codebasis und Arbeitsweise. Tokens sparst du mit `/clear` zwischen Aufgaben, einer kurzen CLAUDE.md, Subagents für große Ausgaben und dem passenden Modell. Siehe [Kosten](docs/anleitungen/claude-code-kosten.md) und [Usage](docs/anleitungen/claude-code-usage-tokens.md).

### Kann ich Claude Code über Amazon Bedrock oder Google Vertex AI nutzen?

Ja. Für Bedrock setzt du `CLAUDE_CODE_USE_BEDROCK=1` und eine Region wie `AWS_REGION=eu-central-1`, für Vertex AI `CLAUDE_CODE_USE_VERTEX=1`, `ANTHROPIC_VERTEX_PROJECT_ID` und `CLOUD_ML_REGION`. Über Microsoft Foundry geht es mit `CLAUDE_CODE_USE_FOUNDRY=1`. Siehe [Bedrock](docs/anleitungen/claude-code-bedrock.md), [Vertex AI](docs/anleitungen/claude-code-vertex-ai.md) und [Foundry](docs/anleitungen/claude-code-azure-foundry.md).

### Was ist der Unterschied zwischen Subagents, Skills und Plugins?

Ein Skill ist eine Anleitung, die im Kontext der laufenden Sitzung arbeitet. Ein Subagent arbeitet in einem eigenen Kontext mit eigenen Tool-Grenzen und gibt nur ein Ergebnis zurück. Ein Plugin ist ein Paket, das Skills, Subagents, Hooks und MCP-Server über einen Marketplace verteilt. Siehe [die Übersicht oben](#skills-subagents-und-plugins-in-claude-code).

<a id="english"></a>
## Claude Code Best Practices in English

This repository collects Claude Code best practices for teams, written in German, with ready-to-use templates and a CLI. It covers CLAUDE.md, AGENTS.md, settings.json and permissions, hooks, skills, subagents, plugins, MCP servers, GitHub Actions code review, Amazon Bedrock, Google Vertex AI, Microsoft Foundry, GDPR, costs and token usage.

What makes it different from other Claude Code best practice collections:

- **Hooks that block secrets and German personal data.** `PreToolUse` and `UserPromptSubmit` hooks detect IBANs, German tax IDs, social security numbers, VAT IDs and credit cards with real checksum validation, plus tokens from GitHub, AWS, Anthropic, OpenAI, Slack and Stripe. They also catch indirect reads like `grep KEY config/.env.production | head` and `env | sort`, which permission rules miss.
- **A linter for Claude Code configuration.** `claude-team audit` checks 35 rules, for example deny rules that never fire (`Write(.env)`), wildcards that allow any subcommand (`Bash(git * main)`), relative hook paths, plaintext MCP tokens, unpinned MCP servers and HTTP servers missing `"type"`. Output as text, Markdown, JSON or SARIF.
- **A GitHub Action** that uploads findings to GitHub Code Scanning.
- **A Claude Code plugin** (`team-basis`) and skills for skills.sh.
- **Rollout templates** for security approval, GDPR documentation (TOM, DPIA), works council and cost policy, plus a managed-settings.json.

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team audit .
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team einrichten .

claude plugin marketplace add pexon-consulting/claude-code-best-practices
claude plugin install team-basis@claude-code-best-practices
```

The commands are German (`einrichten` = set up, `scannen` = scan, `regeln` = rules), the output is German. Every rule is documented in [docs/regeln.md](docs/regeln.md), every command and hook is shown with real input and output in [docs/beispiele.md](docs/beispiele.md).

## Mitmachen und Lizenz

Fehler in einer Anleitung, eine Regel, die zu viel oder zu wenig meldet, eine neue Claude-Code-Version mit geänderten Feldern: Issues und Pull Requests sind willkommen. Wie du Tests startest und neue Regeln anlegst, steht in [CONTRIBUTING.md](CONTRIBUTING.md). Sicherheitslücken bitte nicht als Issue, sondern wie in [SECURITY.md](SECURITY.md) beschrieben melden.

```bash
git clone https://github.com/pexon-consulting/claude-code-best-practices
cd claude-code-best-practices
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q
```

Lizenz: [MIT](LICENSE). Zitieren: [CITATION.cff](CITATION.cff). Änderungen: [CHANGELOG.md](CHANGELOG.md).

Claude und Claude Code sind Marken von Anthropic. Dieses Repo ist ein unabhängiges Community-Projekt und nicht mit Anthropic verbunden.

Gepflegt von Pexon Consulting. Wer Claude Code im Team einführt, findet bei uns eine [Claude-Code-Schulung zu Agentic Coding](https://pexon-consulting.de/schulungen/claude-code-schulung-agentic-coding).
