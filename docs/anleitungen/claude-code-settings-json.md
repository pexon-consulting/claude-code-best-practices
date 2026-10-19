# Claude Code settings.json: alle wichtigen Einstellungen mit Vorlage

Claude Code liest Einstellungen aus vier settings.json-Ebenen: Managed Settings der Organisation, `.claude/settings.local.json` (persönlich im Projekt), `.claude/settings.json` (im Team geteilt) und `~/.claude/settings.json` (persönlich für alle Projekte). Bei Konflikten gewinnt die höhere Ebene in dieser Reihenfolge: Managed, dann `--settings` auf der Kommandozeile, dann lokal, dann Projekt, dann Nutzer. Listen wie `permissions.allow` werden dabei nicht ersetzt, sondern über alle Ebenen zusammengeführt.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- Die Team-Datei ist `.claude/settings.json` und gehört ins Repo; persönliche Abweichungen kommen in `.claude/settings.local.json`.
- Managed Settings stehen über allem, auch über `--settings`; nichts darunter kann sie überschreiben.
- Listen werden über die Ebenen zusammengeführt, einzelne Werte gewinnt die höchste Ebene.
- settings.json ist striktes JSON: Ein Kommentar oder ein Komma zu viel führt zu einem Settings Error.
- Die Zeile `"$schema": "https://json.schemastore.org/claude-code-settings.json"` bringt Autovervollständigung im Editor; das Schema hinkt neuen Versionen manchmal hinterher.
- `allow`-Regeln und `additionalDirectories` aus der Projektdatei wirken erst, wenn die Person den Vertrauensdialog für genau diesen Ordner bestätigt hat; `deny` und `ask` gelten sofort.

## Welche settings.json-Ebenen gibt es?

| Ebene | Datei | Gilt für | Typischer Inhalt |
| --- | --- | --- | --- |
| Nutzer | `~/.claude/settings.json` | dich, alle Projekte | Modell, Theme, eigene Regeln |
| Projekt | `.claude/settings.json` | alle im Repo | Team-Permissions, Hooks, Plugins, `env` |
| Lokal | `.claude/settings.local.json` | dich, dieses Projekt | persönliche Ausnahmen, Tests vor dem Teilen |
| Managed | `managed-settings.json`, MDM oder Server-managed | alle Rechner der Organisation | Sicherheitsrichtlinien, Compliance |

Pfade der Managed Settings als Datei:

| Betriebssystem | Pfad |
| --- | --- |
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` |
| Linux und WSL | `/etc/claude-code/managed-settings.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` |

Daneben gibt es `~/.claude.json`. Diese Datei schreibt Claude Code selbst: Anmeldung, MCP-Konfiguration, Vertrauensentscheidungen pro Projekt und globale Config-Keys. Du musst sie nicht bearbeiten.

Hinweise zur lokalen Datei:

- Claude Code legt `.claude/settings.local.json` an, wenn du bei einer Rückfrage "Yes, and don't ask again" wählst, und speichert dort die `allow`-Regel.
- Beim ersten Schreiben trägt Claude Code `**/.claude/settings.local.json` in deine globale Git-Excludes-Datei ein. Hast du die Datei von Hand angelegt, trägst du sie selbst in `.gitignore` ein.
- Seit v2.1.211 liegt die Datei am Root des Git-Repos, auch wenn du Claude Code in einem Unterordner startest.

## Welche Ebene gewinnt bei Konflikten?

| Rang | Quelle | Bemerkung |
| --- | --- | --- |
| 1 | Managed Settings | nichts darunter überschreibt sie, auch nicht `--settings` |
| 2 | `--settings <datei-oder-json>` | nur für diese Sitzung |
| 3 | `.claude/settings.local.json` | persönlich im Projekt |
| 4 | `.claude/settings.json` | Team |
| 5 | `~/.claude/settings.json` | persönlich, alle Projekte |

Dazu drei Regeln, die oft übersehen werden:

- **Listen werden zusammengeführt.** `permissions.allow`, `deny`, `ask`, `claudeMdExcludes` und andere Arrays aus allen Ebenen gelten gemeinsam. Ausnahmen mit eigenen Regeln sind `fallbackModel`, `modelPicker`, `availableModels` und `modelSettings`.
- **Flags und Umgebungsvariablen sind keine Ebene.** `--model` und `ANTHROPIC_MODEL` schlagen den Key `model` aus jeder Datei. Welches Paar wie wirkt, steht pro Key in der Referenz.
- **Manche Werte wirken nur aus bestimmten Dateien.** `permissions.defaultMode` mit `auto` oder `bypassPermissions` wirkt nicht aus Projekt- oder lokalen Settings. Einige Keys wirken nur aus Nutzer- oder Managed Settings, etwa `useAutoModeDuringPlan` oder `pluginConfigs` für die AGENTS.md-Einstellung.

Für einige Sicherheits-Keys gilt der strengere Wert aus jeder Ebene, auch gegen Managed Settings, zum Beispiel `permissions.blockReadsOutsideWorkingDirectories: true` (ab v2.1.257) oder `disableClaudeAiConnectors: true`.

Welche Dateien geladen wurden, zeigt `/status` in der Zeile `Setting sources`. Verworfene Einträge listet `claude doctor`.

## Die wichtigsten Keys mit Beispiel

| Key | Wofür | Hinweis |
| --- | --- | --- |
| `$schema` | Autovervollständigung im Editor | Schema kann neuen Keys hinterherhinken |
| `permissions` | `allow`, `ask`, `deny`, `defaultMode`, `additionalDirectories`, `disableBypassPermissionsMode` | siehe [Permissions](./claude-code-permissions.md) |
| `env` | Umgebungsvariablen für jede Sitzung | manche Variablen nicht aus Projekt-Settings |
| `hooks` | Befehle bei Ereignissen | werden über Ebenen zusammengeführt |
| `model` | Modell für neue Sitzungen | `--model` und `ANTHROPIC_MODEL` gewinnen |
| `statusLine` | eigene Statuszeile | Objekt mit `type: "command"` |
| `cleanupPeriodDays` | Aufbewahrung lokaler Transkripte in Tagen | Standard 30, mindestens 1 |
| `attribution` | Co-Authored-By-Zeile und PR-Text | ersetzt `includeCoAuthoredBy` |
| `enableAllProjectMcpServers` | alle MCP-Server aus `.mcp.json` ohne Rückfrage | lieber `enabledMcpjsonServers` mit Namen |
| `sandbox` | Bash-Befehle isoliert ausführen | macOS, Linux, WSL2 |

### permissions

```json
{
  "permissions": {
    "allow": ["Bash(npm run *)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"]
  }
}
```

Auswertung immer deny, dann ask, dann allow. Ein `allow` schneidet kein Loch in ein `deny`. Alles Weitere in der Anleitung [Permissions](./claude-code-permissions.md).

### env

```json
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1"
  }
}
```

Ein Wert hier überschreibt die gleiche Variable aus der Shell. Aus Projekt- und lokalen Settings ignoriert Claude Code Variablen, die ein ausgechecktes Repo nicht steuern soll, und protokolliert eine Warnung (sichtbar mit `claude --debug`). Dazu gehören laut Referenz:

- Speicherorte von Claude Code und des Betriebssystems: `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR`, `HOME`, `TMPDIR`, `TMP`, `TEMP` und die `XDG_*`-Familie.
- Windows-Variablen wie `SystemRoot`, `ComSpec`, `ProgramData`, `LOCALAPPDATA`, `PATHEXT`, `PSModulePath` und die `ProgramFiles`-Familie.
- Variablen, die Sitzungsinhalte exportieren: `OTEL_LOG_RAW_API_BODIES`, `ENABLE_BETA_TRACING_DETAILED`, `BETA_TRACING_ENDPOINT`.
- Die OpenTelemetry-Exporter-Variablen, die Telemetrie einschalten oder umleiten, etwa `CLAUDE_CODE_ENABLE_TELEMETRY`, `OTEL_LOGS_EXPORTER`, `OTEL_EXPORTER_OTLP_ENDPOINT` (ab v2.1.282). Werte, die etwas abschalten, etwa `none` für die Exporter, wirken weiter.
- Start- und Sync-Variablen wie `CLAUDE_CODE_PROCESS_WRAPPER`, `CLAUDE_CODE_SYNC_SKILLS`, `CLAUDE_CODE_SYNC_PLUGINS`, `CLAUDE_CODE_PLUGIN_CACHE_DIR`.
- Dialog-Timer `CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS`, `CLAUDE_AFK_TIMEOUT_MS`, `CLAUDE_AFK_COUNTDOWN_MS` sowie `CLAUDE_CODE_DISABLE_ATTACHMENTS` und `CLAUDE_CODE_DISABLE_FILE_MENTIONS`.

`DISABLE_TELEMETRY` gehört nicht zu dieser Liste. Beachte aber: Die Variable schaltet auch das Laden von Feature-Flags ab, und auch `0` oder `false` schalten Telemetrie ab. Zum Wiedereinschalten muss die Variable ganz weg.

### hooks

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PROJECT_DIR}\"/.claude/hooks/block-rm.sh" }
        ]
      }
    ]
  }
}
```

Hooks aus allen Ebenen laufen gemeinsam. Interaktiv erscheint in einem neuen Ordner zuerst der Vertrauensdialog; `claude -p` zeigt keinen Dialog und führt Hooks aus der Projektdatei trotzdem aus. Details in der Anleitung [Hooks](./claude-code-hooks.md).

### model

```json
{
  "model": "opusplan"
}
```

`opusplan` nutzt Opus im Plan Mode und Sonnet bei der Umsetzung. Vorrang für eine Sitzung: `--model` vor `ANTHROPIC_MODEL` vor dem Key.

### statusLine

```json
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'",
    "padding": 2
  }
}
```

Das Beispiel braucht `jq`. Mehr in der Anleitung [Statusline](./claude-code-statusline.md).

### cleanupPeriodDays

```json
{
  "cleanupPeriodDays": 30
}
```

Löscht lokale Transkripte und Checkpoint-Snapshots nach der Frist. `0` ist ungültig; für lange Aufbewahrung einen großen Wert wie `3650` wählen.

### attribution statt includeCoAuthoredBy

`includeCoAuthoredBy` ist seit v2.0.62 veraltet. Der Nachfolger `attribution` steuert Commit-Trailer, PR-Text und Sitzungslink getrennt:

```json
{
  "attribution": {
    "commit": "",
    "pr": "",
    "sessionUrl": false
  }
}
```

`"attribution": false` blendet alles aus, funktioniert aber erst ab v2.1.281. Ältere Versionen verwerfen dann die ganze Datei. Für gemischte Versionen im Team deshalb die Form mit leeren Strings nutzen.

### enableAllProjectMcpServers

```json
{
  "enabledMcpjsonServers": ["github", "sentry"]
}
```

`"enableAllProjectMcpServers": true` gibt jeden Server aus `.mcp.json` ohne Rückfrage frei, auch Server, die später jemand ergänzt. Sicherer ist eine Liste mit Namen wie oben. `disabledMcpjsonServers` gewinnt immer. In einem nicht vertrauten Ordner ignoriert Claude Code diese Freigaben aus der Projektdatei. Das Prüf-CLI meldet den Freibrief als [CC018](../regeln.md#cc018).

### sandbox

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": { "allowWrite": ["/tmp/build"] },
    "network": { "allowedDomains": ["registry.npmjs.org", "*.example.com"] }
  }
}
```

Die Sandbox isoliert nur Shell-Befehle, nicht Read, Edit oder WebFetch. Kann sie nicht starten, läuft der Befehl ohne Sandbox, außer `failIfUnavailable` ist gesetzt. Mehr in der Anleitung [Sandbox](./claude-code-sandbox.md).

## Die Team-Vorlage aus diesem Repo erklärt

Die Datei [`.claude/settings.json`](../../src/claude_team/vorlage/.claude/settings.json) ist die Basis, die `claude-team einrichten` anlegt. Die Teile im Überblick:

| Teil | Inhalt | Warum |
| --- | --- | --- |
| `$schema` | schemastore-URL | Autovervollständigung und Prüfung im Editor |
| `permissions.defaultMode` | `"default"` | alle starten im Manual-Modus; ab v2.1.283 wäre ohne diesen Key Auto Mode der eingebaute Start |
| `permissions.disableBypassPermissionsMode` | `"disable"` | `--dangerously-skip-permissions` wird abgelehnt |
| `permissions.allow` | `git status`, `git diff`, `git log`, `git show`, `ls`, `pwd`, Test-, Lint- und Build-Befehle | Routinebefehle ohne Rückfrage, jeweils mit festem Unterbefehl |
| `permissions.ask` | `git push`, `git reset`, `git rebase`, `npm publish`, `docker push`, `terraform apply`, `kubectl apply`, `kubectl delete`, `WebFetch` | alles mit Wirkung nach außen fragt nach |
| `permissions.deny` | `.env`, Schlüsseldateien, `*.tfstate`, Cloud-Zugangsdaten unter `~/`, `.git/**` bearbeiten, `sudo`, `curl ... \| sh`, Force-Push, `rm -rf /`, `printenv`, `env` | Zugangsdaten bleiben aus dem Kontext, gefährliche Befehle sind gesperrt |
| `env` | `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING` | Telemetrie und Fehlerberichte aus |
| `cleanupPeriodDays` | `30` | Transkripte nicht länger als nötig |
| `hooks` | SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop | Schutz-Hooks für Secrets, personenbezogene Daten und Befehle, Formatierung, Protokoll, Tests |

Die Hooks der Vorlage starten mit `python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/<name>.py"`:

| Ereignis | Hook | Aufgabe |
| --- | --- | --- |
| SessionStart | `sitzungsstart.py` | Branch, offene Änderungen und letzte Commits als Kontext |
| UserPromptSubmit | `pii_schutz.py` | blockt IBAN, Steuer-ID und ähnliche Daten, bevor der Prompt ans Modell geht |
| PreToolUse | `secrets_schutz.py`, `pii_schutz.py`, `befehle_schutz.py` | sperrt Secrets, personenbezogene Daten in Befehlen und neuem Code sowie gefährliche Befehle; gelesene Dateiinhalte prüft kein Hook |
| PostToolUse | `format_nach_edit.py`, `protokoll.py` | formatiert nach Edits; das Protokoll ohne Dateiinhalte ist standardmäßig aus |
| Stop | `stopp_tests.py` | führt den Testbefehl aus `.claude/schutz.json` aus |

Die `deny`-Regeln sind die erste Schutzschicht. Die Hooks sind die zweite und lassen eine Aktion durch, wenn sie selbst abstürzen, damit ein kaputter Hook niemanden aussperrt.

## Beispiele für die settings.json

### Beispiel 1: Persönliche Datei für alle Projekte

Für `~/.claude/settings.json`: Modell, eigene Freigaben und Sprache.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "sonnet",
  "language": "german",
  "permissions": {
    "allow": ["Bash(npm run lint)", "Bash(npm run test *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  }
}
```

`language` wird laut Referenz nicht geprüft; ein Wert wie `"german"` wird als Text übernommen.

### Beispiel 2: Minimale Team-Datei

Für `.claude/settings.json`, wenn die volle Vorlage zu viel ist.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "allow": ["Bash(git status *)", "Bash(git diff *)", "Bash(ruff check *)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(.env)", "Read(.env.*)", "Read(**/*.pem)", "Read(**/*.key)", "Bash(git diff *--output*)"]
  },
  "env": { "DISABLE_TELEMETRY": "1" }
}
```

Testbefehle wie `pytest` stehen bewusst nicht in `allow`, weil sie Code aus dem Repo ausführen. Wann sie trotzdem passen, steht in [Claude Code Permissions](./claude-code-permissions.md#beispiel-2-python-projekt).

### Beispiel 3: Persönliche Ausnahme im Projekt

Für `.claude/settings.local.json`: Das Team nutzt Sonnet, du willst in diesem Projekt Opus.

```json
{
  "model": "claude-opus-5-5"
}
```

### Beispiel 4: Einstellung nur für eine Sitzung

Probiert einen Wert aus, ohne eine Datei zu ändern.

```bash
claude --settings '{"model": "claude-opus-5-5"}'
```

### Beispiel 5: Managed Settings für die Organisation

Eine Kombination dokumentierter Keys für `managed-settings.json`. Eine ausführlichere Vorlage liegt unter [vorlagen/managed-settings.json](../../vorlagen/managed-settings.json).

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"]
  },
  "allowManagedHooksOnly": true,
  "allowManagedPermissionRulesOnly": true,
  "forceLoginMethod": "claudeai",
  "sandbox": { "enabled": true, "allowUnsandboxedCommands": false },
  "companyAnnouncements": ["Bitte die Coding-Guidelines unter docs.example.com beachten"]
}
```

`allowManagedHooksOnly` und `allowManagedPermissionRulesOnly` wirken nur aus Managed Settings und schalten alle anderen Hooks bzw. Regeln ab. Das ist streng; erst im Pilot testen.

## Schritt für Schritt: Team-Settings einführen

1. Vorschau ansehen: `uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team einrichten . --dry-run`.
2. Einrichten ohne `--dry-run`. Gibt es schon eine `.claude/settings.json`, entsteht `.claude/settings.vorschlag.json` mit den zusammengeführten Werten.
3. Die `allow`-Liste an die echten Befehle des Projekts anpassen: Testbefehl, Linter, Build.
4. Prüfen, dass die Datei gültiges JSON ist: `python3 -m json.tool .claude/settings.json > /dev/null`.
5. `.claude/settings.local.json` in `.gitignore` eintragen, falls sie fehlt.
6. Committen. Jede Person bestätigt beim nächsten Start den Vertrauensdialog, erst dann wirken die `allow`-Regeln. In `claude -p` ohne Vertrauen bleiben sie wirkungslos, und Claude Code warnt mit `this workspace has not been trusted`.
7. In einer Sitzung `/status` aufrufen und die Zeile `Setting sources` prüfen.
8. `claude-team audit .` in die CI aufnehmen.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Kommentar oder Komma zu viel | Settings Error beim Start, Datei wird übersprungen | striktes JSON, mit `python3 -m json.tool` prüfen |
| `defaultMode: "auto"` in der Projektdatei | Sitzung startet nicht im Auto Mode | in `~/.claude/settings.json` setzen |
| `includeCoAuthoredBy` statt `attribution` | wird ignoriert, sobald `attribution.commit` oder `attribution.pr` gesetzt ist | auf `attribution` umstellen |
| `"attribution": false` bei älteren Versionen | ganze Datei wird verworfen | leere Strings und `sessionUrl: false` |
| Telemetrie-Exporter in der Projektdatei | Collector bekommt keine Daten | in Nutzer- oder Managed Settings setzen |
| `settings.local.json` committet | persönliche Freigaben gelten für alle ([CC011](../regeln.md#cc011)) | aus Git nehmen, in `.gitignore` |
| `allow`-Regeln wirken nicht | Rückfragen trotz Regel | Vertrauensdialog bestätigen, `/permissions` prüfen |

## Häufige Fragen

### Wo liegt die settings.json von Claude Code?

Persönlich unter `~/.claude/settings.json`, im Projekt unter `.claude/settings.json` für das Team und `.claude/settings.local.json` für dich. Managed Settings liegen je nach System unter `/Library/Application Support/ClaudeCode/`, `/etc/claude-code/` oder `C:\Program Files\ClaudeCode\`.

### Welche Einstellung gewinnt bei Konflikten?

Managed Settings, dann `--settings`, dann `.claude/settings.local.json`, dann `.claude/settings.json`, dann `~/.claude/settings.json`. Listen wie `permissions.allow` werden über alle Ebenen zusammengeführt.

### Muss ich Claude Code nach einer Änderung neu starten?

Meist nicht. Claude Code beobachtet die Dateien und übernimmt die meisten Änderungen sofort, auch an `permissions` und `hooks`. Ausnahmen wie `model` und `effortLevel` liest es nur beim Start; dafür gibt es `/model` und `/effort`.

### Gibt es noch den Befehl claude config?

Nein, der Unterbefehl `claude config` wurde zugunsten der settings.json abgeschafft. In der Sitzung öffnet `/config` die Einstellungen, und `/config key=value` setzt einzelne Werte direkt, zum Beispiel `/config thinking=false`; `/config --help` listet die Kurzschlüssel.

### Darf ich Kommentare in die settings.json schreiben?

Nein. Die Dateien sind striktes JSON, ein `//`-Kommentar ist ein Syntaxfehler. Notizen gehören in eine README oder in die Commit-Nachricht.

### Wie prüfe ich, welche Settings wirklich geladen sind?

`/status` zeigt in der Zeile `Setting sources` jede geladene Datei. `/permissions` zeigt alle Regeln mit ihrer Herkunftsdatei, und `claude doctor` listet verworfene Einträge.

## Weiterlesen

- [Claude Code Permissions: allow, ask und deny](./claude-code-permissions.md)
- [Claude Code Hooks](./claude-code-hooks.md)
- [Claude Code Sandbox](./claude-code-sandbox.md)
- [Claude Code Statusline](./claude-code-statusline.md)
- [Claude Code Enterprise](./claude-code-enterprise.md)
- Vorlagen: [.claude/settings.json](../../src/claude_team/vorlage/.claude/settings.json), [managed-settings.json](../../vorlagen/managed-settings.json), Prüfregeln [CC010 bis CC019](../regeln.md#cc010)
- Offizielle Doku: [Settings](https://code.claude.com/docs/en/settings), [Settings reference](https://code.claude.com/docs/en/settings-reference)
