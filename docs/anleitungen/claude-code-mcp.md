# Claude Code MCP: MCP-Server hinzufügen, konfigurieren und absichern

Einen MCP-Server fügst du in Claude Code mit `claude mcp add` hinzu, zum Beispiel `claude mcp add --transport http sentry https://mcp.sentry.dev/mcp`. Standardmäßig landet der Eintrag nur für dich in `~/.claude.json`. Mit `--scope project` schreibt Claude Code ihn in die Datei `.mcp.json` im Projekt-Root, die du committest und so mit dem Team teilst.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- MCP-Server geben Claude Code zusätzliche Tools, etwa für GitHub, Datenbanken oder Fehlertracking. Jeder Server läuft mit deinen Rechten.
- Es gibt drei Scopes: `local` (Standard, nur du, nur dieses Projekt), `project` (`.mcp.json`, geteilt) und `user` (nur du, alle Projekte).
- Tokens gehören nie in die `.mcp.json`. Schreib stattdessen `${VAR}` oder `${VAR:-standard}`, Claude Code ersetzt das beim Laden.
- Ein Eintrag mit `url` braucht immer `"type": "http"`, sonst wird er als stdio-Server ohne Befehl übersprungen. `sse` ist veraltet.
- Interaktiv fragt Claude Code vor dem ersten Start eines Projekt-Servers nach. In `claude -p`, im Agent SDK und in Cloud-Sitzungen lädt es sie ohne Nachfrage.
- Paketversionen pinnen: `npx -y paket@1.2.3` statt `npx -y paket`.

## Wie füge ich einen MCP-Server hinzu?

```bash
# Remote-Server über HTTP, empfohlen
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# Für das ganze Team, schreibt .mcp.json
claude mcp add --transport http --scope project shared-server https://example.com/mcp

# Lokaler stdio-Server, alles nach -- geht an den Server
claude mcp add --transport stdio --env API_KEY=<dein-token> airtable -- npx -y airtable-mcp-server
```

Bei stdio-Servern trennt `--` die Optionen von Claude Code (`--transport`, `--env`, `--scope`) vom Befehl, der den Server startet. Alles nach `--` geht unverändert an den Server.

| Option | Bedeutung |
| --- | --- |
| `-t`, `--transport` | `stdio` (Standard), `http` oder `sse` |
| `-s`, `--scope` | `local` (Standard), `project` oder `user` |
| `-e`, `--env KEY=wert` | Umgebungsvariable für den Server |
| `-H`, `--header` | HTTP-Header, z.B. für eine Anmeldung |
| `--client-id`, `--client-secret`, `--callback-port` | OAuth-Einstellungen |

Weitere Unterbefehle:

| Befehl | Zweck |
| --- | --- |
| `claude mcp list` | alle Server mit Status |
| `claude mcp get <name>` | Details zu einem Server |
| `claude mcp remove <name>` | Server entfernen |
| `claude mcp add-json <name> '<json>'` | Server als JSON hinzufügen |
| `claude mcp add-from-claude-desktop` | Server aus Claude Desktop übernehmen |
| `claude mcp login <name>` | OAuth-Anmeldung aus der Shell, `--no-browser` für SSH |
| `claude mcp logout <name>` | gespeicherte Anmeldung löschen |
| `claude mcp reset-project-choices` | Freigaben für `.mcp.json`-Server zurücksetzen |
| `claude mcp serve` | Claude Code selbst als MCP-Server starten |

In der Sitzung zeigt `/mcp` alle Server mit Status, dort kannst du dich anmelden, neu verbinden und Server ein- oder ausschalten.

## Wo liegt die .mcp.json und welcher Scope gewinnt?

| Scope | Gilt in | Geteilt | Gespeichert |
| --- | --- | --- | --- |
| `local` | aktuelles Projekt | nein | `~/.claude.json` unter dem Projektpfad |
| `project` | aktuelles Projekt | ja, über Git | `.mcp.json` im Projekt-Root |
| `user` | alle Projekte | nein | `~/.claude.json` |

Bei gleichem Namen gilt local vor project vor user vor Plugin vor claude.ai-Connectors. Die Felder werden nicht zusammengeführt, der Eintrag mit Vorrang gilt ganz. Server aus den Managed Settings (`managedMcpServers`, ab v2.1.259) stehen über allen.

## Das Format der .mcp.json

```json
{
  "mcpServers": {
    "interner-dienst": {
      "type": "stdio",
      "command": "/usr/local/bin/interner-mcp-server",
      "args": ["--config", "${CLAUDE_PROJECT_DIR:-.}/mcp-config.json"],
      "env": { "DIENST_URL": "https://internal.example.com" }
    },
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": { "Authorization": "Bearer ${API_KEY}" }
    }
  }
}
```

| Feld | Für | Bedeutung |
| --- | --- | --- |
| `type` | alle | `stdio`, `http` (Alias `streamable-http`), `sse` (veraltet) oder `ws` |
| `command`, `args` | stdio | Programm und Argumente |
| `env` | stdio | Umgebungsvariablen für den Prozess |
| `url` | http, sse, ws | Adresse des Servers |
| `headers` | http, sse, ws | HTTP-Header |

Variablen wie `${VAR}` und `${VAR:-standard}` werden in `command`, `args`, `env`, `url` und `headers` ersetzt. Den Projektordner bekommst du in `command` und `args` nur mit Standardwert: `${CLAUDE_PROJECT_DIR:-.}`. Ab v2.1.265 fällt `http` automatisch auf SSE zurück, wenn der Server nur SSE kann.

Eine Besonderheit schützt deine Zugangsdaten: `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `AWS_BEARER_TOKEN_BEDROCK` und `NPM_TOKEN` liest Claude Code in `url` und `headers` von Remote-Servern als leer. Eine fremde `.mcp.json` kann sie so nicht an einen beliebigen Server schicken. Für eigene Server legst du deshalb eine eigene Variable an.

## Beispiele für Claude Code MCP

Die Beispiele 1 bis 3 stammen aus der Vorlage [.mcp.json.example](../../src/claude_team/vorlage/.mcp.json.example).

### Beispiel 1: GitHub mit Token aus der Umgebung

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_MCP_TOKEN}" }
    }
  }
}
```

Das Token setzt jede Person in ihrer Shell, etwa mit `export GITHUB_MCP_TOKEN=<dein-token>`. Im Repo steht nur der Variablenname.

### Beispiel 2: Postgres nur lesend

Ein Datenbank-Benutzer mit reinen Leserechten ist die wichtigste Absicherung. Die Verbindungszeichenkette kommt aus der Umgebung, die Paketversion ist fest.

```json
{
  "mcpServers": {
    "postgres-lesend": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres@0.6.2", "${DATABASE_URL_READONLY}"]
    }
  }
}
```

### Beispiel 3: Dateisystem auf einen Ordner begrenzt

Der Server sieht nur `docs/` im Projekt, nicht das ganze Home-Verzeichnis.

```json
{
  "mcpServers": {
    "dateisystem-docs": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem@2025.8.21", "${CLAUDE_PROJECT_DIR:-.}/docs"]
    }
  }
}
```

### Beispiel 4: Sentry mit OAuth-Anmeldung

Remote-Server mit OAuth brauchen kein Token in der Konfiguration. Die Anmeldung läuft im Browser, Claude Code speichert und erneuert die Tokens selbst.

```bash
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp
claude mcp login sentry
```

Alternativ in der Sitzung `/mcp` öffnen und dort anmelden. In `claude -p` gibt es keinen OAuth-Ablauf, dort musst du dich vorher interaktiv anmelden.

### Beispiel 5: eigener stdio-Server im Repo

Ein eigenes Skript im Projekt, das Claude Code als MCP-Server startet. `CLAUDE_PROJECT_DIR` ist im Prozess des Servers gesetzt.

```json
{
  "mcpServers": {
    "team-tools": {
      "type": "stdio",
      "command": "python3",
      "args": ["${CLAUDE_PROJECT_DIR:-.}/tools/mcp_server.py"],
      "env": { "LOG_LEVEL": "${LOG_LEVEL:-info}" }
    }
  }
}
```

### Beispiel 6: Server in der CI gezielt abschalten

In `claude -p` startet Claude Code alle Projekt-Server ohne Nachfrage. Mit `--strict-mcp-config` nutzt der Lauf nur die Server aus `--mcp-config`:

```bash
claude -p --strict-mcp-config --mcp-config ./ci-mcp.json "Prüfe die Änderungen im Pull Request"
```

Alternativ einzelne Server in der Projekt-Konfiguration sperren:

```json
{
  "disabledMcpjsonServers": ["postgres-lesend", "dateisystem-docs"]
}
```

### Beispiel 7: MCP-Tools in den Berechtigungen

Tool-Namen haben das Format `mcp__<server>__<tool>`. In `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["mcp__github__get_issue", "mcp__postgres-lesend__*"],
    "ask": ["mcp__github__*"]
  }
}
```

`mcp__github` oder `mcp__github__*` trifft alle Tools eines Servers. Das allgemeine `"mcp__*"` wirkt nur in `deny` und `ask`, in `allow` ignoriert Claude Code es (Regel [CC017](../regeln.md#cc017)). Tools aus Plugin-Servern heißen `mcp__plugin_<plugin>_<server>__<tool>`.

## Projekt-Server freigeben

Interaktiv fragt Claude Code vor dem ersten Start eines Servers aus `.mcp.json` nach. Dauerhaft steuerst du das in den Settings:

| Einstellung | Wirkung |
| --- | --- |
| `enabledMcpjsonServers: ["github"]` | gibt genau diese Server frei |
| `disabledMcpjsonServers: ["postgres-lesend"]` | sperrt diese Server, gewinnt immer |
| `enableAllProjectMcpServers: true` | gibt alle frei, auch künftige |

Von `enableAllProjectMcpServers` rät das Audit ab (Regel [CC018](../regeln.md#cc018)): Ein Pull Request, der einen neuen Server einträgt, liefe sonst beim nächsten Start auf jedem Rechner. In einem Ordner, dem du nicht vertraust, ignoriert Claude Code Freigaben aus der committeten `.claude/settings.json`, der Server bleibt auf "Pending approval".

## MCP im Unternehmen steuern

Für die ganze Organisation gibt es zwei Wege:

- **`managed-mcp.json`** legt die Server fest und schließt alle anderen aus. Format wie `.mcp.json`. Pfade: macOS `/Library/Application Support/ClaudeCode/managed-mcp.json`, Linux und WSL `/etc/claude-code/managed-mcp.json`, Windows `C:\Program Files\ClaudeCode\managed-mcp.json`.
- **`allowedMcpServers` und `deniedMcpServers`** in den Managed Settings erlauben oder sperren Server nach Name, Befehl oder URL. Die Sperrliste gilt immer. Mit `allowManagedMcpServersOnly: true` wird die Allowlist hart. Ein `serverName` ist nur das Etikett, das jemand vergibt, und deshalb keine Sicherheitsgrenze. Verlässlich sind `serverCommand` und `serverUrl`.

```json
{
  "allowedMcpServers": [
    { "serverUrl": "https://mcp.sentry.dev/*" },
    { "serverCommand": ["npx", "-y", "@modelcontextprotocol/server-filesystem@2025.8.21", "."] }
  ],
  "deniedMcpServers": [
    { "serverUrl": "https://mcp.example.com/*" }
  ]
}
```

## Grenzen und Zeitlimits

| Wert | Standard | Ändern mit |
| --- | --- | --- |
| Warnung bei großer Tool-Ausgabe | ab 10.000 Tokens | - |
| Höchstgröße einer Tool-Ausgabe | 25.000 Tokens | `MAX_MCP_OUTPUT_TOKENS=50000` |
| Textergebnis wird als Datei abgelegt | über 50.000 Zeichen | - |
| Startzeit eines Servers | 30.000 ms | `MCP_TIMEOUT` |
| Länge eines Tool-Namens | 128 Zeichen, längere werden nicht gesendet | kürzere Servernamen |

## Schritt für Schritt: MCP-Server sicher ins Team-Repo bringen

1. Server lokal testen: `claude mcp add --transport http <name> <url>`, dann `/mcp` in der Sitzung.
2. Eintrag in `.mcp.json` übernehmen, mit `"type"` und ohne Tokens. Zugangsdaten als `${VAR}`.
3. Bei `npx` und `uvx` eine feste Version angeben (Regel [CC033](../regeln.md#cc033)).
4. Datenbank-Server nur mit Lese-Benutzer, Dateisystem-Server nur auf einen Ordner.
5. In `.claude/settings.json` die Server namentlich mit `enabledMcpjsonServers` freigeben.
6. Berechtigungen für schreibende Tools auf `ask` setzen.
7. `claude-team audit .` ausführen, es prüft `.mcp.json` auf die Regeln [CC031 bis CC036](../regeln.md#cc031).
8. Im README dokumentieren, welche Variablen jede Person setzen muss.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| `url` ohne `type` | Server fehlt, Meldung `has a "url" but no "type"` ([CC034](../regeln.md#cc034)) | `"type": "http"` ergänzen |
| Token im Klartext | Secret im Git-Verlauf ([CC032](../regeln.md#cc032)) | `${VAR}` nutzen, Token widerrufen |
| `npx -y paket` ohne Version | jedes Update läuft ungeprüft ([CC033](../regeln.md#cc033)) | Version pinnen |
| `"type": "sse"` | Hinweis im Audit ([CC035](../regeln.md#cc035)) | auf `http` wechseln |
| `${ANTHROPIC_API_KEY}` im Header | Anmeldung ohne Token ([CC036](../regeln.md#cc036)) | eigene Variable anlegen |
| kaputtes JSON | kein Projekt-Server lädt ([CC031](../regeln.md#cc031)) | mit `python3 -m json.tool .mcp.json` prüfen |
| stdio-Befehl ohne `--` | Claude Code liest `-y` als eigene Option | Server-Befehl komplett nach `--` |

## Häufige Fragen

### Wo liegt die .mcp.json?

Im Root des Projekts, neben `CLAUDE.md`. Claude Code legt sie an, wenn du `claude mcp add --scope project` nutzt. Server mit Scope `local` oder `user` stehen in `~/.claude.json`.

### Ist es sicher, die .mcp.json zu committen?

Ja, solange keine Tokens darin stehen. Zugangsdaten gehören als `${VAR}` in die Datei und als Variable in die Umgebung jeder Person.

### Warum startet mein MCP-Server nicht?

Prüfe in `/mcp` den Status. Häufige Gründe: fehlendes `type` bei `url`, nicht freigegebener Projekt-Server, fehlende Umgebungsvariable oder ein Start, der länger als `MCP_TIMEOUT` dauert. `claude --debug` zeigt Details.

### Kann ich MCP-Server in Skills oder Subagents nutzen?

Ja. Subagents haben ein Feld `mcpServers`, Skills und Subagents können MCP-Tools in `allowed-tools` bzw. `tools` nennen. Plugins können eine eigene `.mcp.json` mitbringen.

### Was ist der Unterschied zwischen http und stdio?

`stdio` startet ein Programm auf deinem Rechner und spricht über Ein- und Ausgabe mit ihm. `http` verbindet sich mit einem Server über das Netz, oft mit OAuth-Anmeldung.

### Wie groß darf eine MCP-Antwort sein?

Standardmäßig 25.000 Tokens. Mit `MAX_MCP_OUTPUT_TOKENS` hebst du die Grenze an, das kostet aber Kontext.

## Weiterlesen

- [Claude Code Permissions](./claude-code-permissions.md): MCP-Tools erlauben, nachfragen oder sperren
- [Claude Code Plugins](./claude-code-plugins.md): MCP-Server im Paket verteilen
- [Claude Code Sicherheit](./claude-code-sicherheit.md): Risiken durch fremde Server
- [Claude Code Enterprise](./claude-code-enterprise.md): Managed Settings für die Organisation
- Prüfregeln: [CC031 bis CC036](../regeln.md#cc031), [CC018](../regeln.md#cc018)
- Vorlage: [.mcp.json.example](../../src/claude_team/vorlage/.mcp.json.example)
- Offizielle Doku: [MCP](https://code.claude.com/docs/en/mcp), [Managed MCP](https://code.claude.com/docs/en/managed-mcp)
