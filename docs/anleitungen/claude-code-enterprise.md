# Claude Code Enterprise: Managed Settings, SSO und zentrale Richtlinien

Claude Code Enterprise-Richtlinien erzwingst du über Managed Settings: eine `managed-settings.json` im Systemverzeichnis jedes Rechners, ein MDM-Profil oder Server-managed Settings aus der claude.ai-Admin-Konsole. Claude Code wendet diese Werte über allen anderen Ebenen an, so dass weder Nutzer- noch Projektdateien noch `--settings` sie überschreiben. Damit sperrst du den Bypass-Modus, legst deny-Regeln, Telemetrie, Login-Organisation, MCP-Allowlist und zulässige Plugin-Marketplaces für alle Entwickler fest.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Managed Settings haben dieselbe JSON-Form wie settings.json und stehen über allen anderen Ebenen.
- Die Datei liegt unter `/Library/Application Support/ClaudeCode/` (macOS), `/etc/claude-code/` (Linux, WSL) oder `C:\Program Files\ClaudeCode\` (Windows).
- Einige Keys wirken nur aus Managed Settings, etwa `allowManagedPermissionRulesOnly`, `allowManagedHooksOnly`, `strictKnownMarketplaces` und `claudeMd`.
- Ist eine Managed-Datei kein gültiges JSON, startet Claude Code nicht; prüfe sie vor der Verteilung.
- `/status` zeigt in der Zeile `Setting sources`, ob und aus welcher Quelle die Managed Settings gelten; `claude doctor` listet verworfene Einträge.
- Managed Settings binden nur Claude Code: Wer lokale Admin-Rechte hat, kann die Datei ändern, und andere Werkzeuge sind nicht erfasst.

## Wie verteile ich Managed Settings?

Es gibt vier Wege, die alle dieselben Keys tragen ([Managed settings](https://code.claude.com/docs/en/managed-settings)):

| Weg | Wo die Richtlinie liegt | Wann Claude Code sie liest | Passt, wenn |
| --- | --- | --- | --- |
| Server-managed Settings | claude.ai-Admin-Konsole oder selbst gehostetes Claude apps gateway | beim Start, dann stündlich | eine Stelle für die ganze claude.ai-Organisation reicht |
| MDM oder OS-Richtlinie | macOS-Profil in der Domain `com.anthropic.claudecode`, Windows-Registry `HKLM\SOFTWARE\Policies\ClaudeCode` (Wert `Settings`) | beim Start, alle 30 Minuten auf Änderung geprüft | Geräte über Jamf, Intune oder Gruppenrichtlinien verwaltet werden |
| Datei | `managed-settings.json` plus optional `managed-settings.d/*.json` im Systemverzeichnis | beim Start und bei Dateiänderung | Linux-Hosts, eigene Images, Rechner ohne MDM |
| HKCU-Registry (Windows, WSL) | `HKCU\SOFTWARE\Policies\ClaudeCode` | wie MDM, nur ohne Admin-Quelle darüber | kein Schreibrecht auf `HKLM` besteht; nutzerbeschreibbar |

Systemverzeichnisse für die Datei:

| Betriebssystem | managed-settings.json | managed-mcp.json | Managed CLAUDE.md |
| --- | --- | --- | --- |
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` | `/Library/Application Support/ClaudeCode/managed-mcp.json` | `/Library/Application Support/ClaudeCode/CLAUDE.md` |
| Linux und WSL | `/etc/claude-code/managed-settings.json` | `/etc/claude-code/managed-mcp.json` | `/etc/claude-code/CLAUDE.md` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` | `C:\Program Files\ClaudeCode\managed-mcp.json` | `C:\Program Files\ClaudeCode\CLAUDE.md` |

Den alten Windows-Pfad `C:\ProgramData\ClaudeCode\managed-settings.json` liest Claude Code nicht mehr. Vorlagen für Jamf, Iru, Intune und Gruppenrichtlinien liegen im [MDM-Beispielordner](https://github.com/anthropics/claude-code/tree/main/examples/mdm) von Anthropic.

## Welche Quelle gewinnt?

Für die Einstellungen insgesamt gilt: Managed vor `--settings` vor `.claude/settings.local.json` vor `.claude/settings.json` vor `~/.claude/settings.json`. Listen wie `permissions.allow` werden zusammengeführt. Einige sicherheitsrelevante Keys lassen strengere Werte aus unteren Ebenen weiter gelten.

Innerhalb der Managed-Ebene prüft Claude Code die Quellen in dieser Reihenfolge:

1. Server-managed Settings (claude.ai oder Gateway), nur wenn die Sitzung sich direkt bei der Anthropic-API mit einer berechtigten Anmeldung oder per `/login` an einem Gateway anmeldet.
2. MDM oder OS-Richtlinie (macOS-Profil, `HKLM`).
3. Dateien: `managed-settings.json` und `managed-settings.d/*.json`, zusammengeführt.
4. `HKCU`, nur wenn keine Admin-Quelle darüber vorhanden ist.

Standardmäßig (`managedSourcesBehavior: "first-wins"`) gilt nur die höchste Quelle mit mindestens einem Policy-Key, die anderen werden ignoriert. Ausnahmen liest Claude Code aus jeder Admin-Quelle, darunter `env` (je Variable zusammengeführt, ab v2.1.223), `deniedMcpServers` und die Sandbox-Sperren. Mit `"merge"` (ab v2.1.242) kombiniert Claude Code alle Admin-Quellen; das nur einschalten, wenn jede untere Quelle unter Admin-Kontrolle steht.

In `managed-settings.d/` werden Dateien alphabetisch nach `managed-settings.json` zusammengeführt. Einzelwerte ersetzt die spätere Datei, Listen werden vereinigt, Blöcke wie `env` je Key zusammengeführt. Benenne die Dateien mit Präfix, etwa `10-telemetrie.json` und `20-sicherheit.json`, damit Teams getrennte Teile pflegen.

## Welche Keys sind für Unternehmen wichtig?

Alle Keys unten stehen in der [Settings-Referenz](https://code.claude.com/docs/en/settings-reference). "Nur managed" heißt: In Nutzer- oder Projektdateien wirkt der Key nicht.

| Key | Wirkung | Nur managed | Ab Version |
| --- | --- | --- | --- |
| `permissions.deny` | sperrt Tools, Dateien und Befehle in jedem Modus | nein | - |
| `permissions.disableBypassPermissionsMode: "disable"` | sperrt `bypassPermissions` und `--dangerously-skip-permissions` | nein | - |
| `disableAutoMode: "disable"` | entfernt den Auto-Modus; auch als `permissions.disableAutoMode` | nein | - |
| `allowManagedPermissionRulesOnly` | nur Managed-Regeln gelten, `--allowedTools` und Regeln aus anderen Dateien werden ignoriert | ja | - |
| `allowManagedHooksOnly` | nur Managed Hooks und Hooks aus per `enabledPlugins` erzwungenen Plugins laufen | ja | - |
| `strictKnownMarketplaces` | Allowlist für Plugin-Marketplaces; leeres Array sperrt alle | ja | - |
| `blockedMarketplaces` | Blocklist für Marketplaces | ja | - |
| `allowedMcpServers`, `deniedMcpServers` | Allowlist und Denylist für MCP-Server | nein, aber managed erzwingt | - |
| `allowManagedMcpServersOnly` | nur die Managed-Allowlist gilt | ja | - |
| `forceLoginMethod` | `"claudeai"`, `"console"` oder `"gateway"` | nein, managed erzwingt | - |
| `forceLoginOrgUUID` | Login nur in diese Organisation(en) | nur managed erzwingt | - |
| `allowedProviders` | zulässige Anbieter wie `"anthropic"`, `"bedrock"`, `"vertex"`, `"foundry"`, `"customEndpoint"` | ja | v2.1.285 |
| `availableModels` | erlaubte Modelle | nein, managed erzwingt | - |
| `claudeMd` | CLAUDE.md-Text als Organisations-Memory, ohne eigene Datei | ja | - |
| `env` | Umgebungsvariablen, etwa für Telemetrie | nein | - |
| `cleanupPeriodDays` | Aufbewahrung lokaler Transkripte in Tagen | nein | - |
| `requiredMinimumVersion` | ältere Versionen starten nicht | ja | v2.1.163 |
| `disableSideloadFlags` | lehnt `--plugin-dir`, `--plugin-url`, `--agents`, `--mcp-config` ab | ja | v2.1.193 |
| `sandbox.network.allowManagedDomainsOnly` | nur Managed-Domains gelten | ja | - |

### Permissions zentral festlegen

```json
{
  "permissions": {
    "deny": ["Read(.env)", "Read(.env.*)", "Read(~/.ssh/**)", "Read(~/.aws/**)"],
    "disableBypassPermissionsMode": "disable"
  },
  "disableAutoMode": "disable"
}
```

Ungültige Sperr-Keys wie `disableAutoMode` gelten ab v2.1.282 als ihr restriktiver Wert (fail closed). Ist eine `deny`- oder `ask`-Liste unlesbar, hält Claude Code `allow` und `additionalDirectories` zurück.

### Login und Anbieter festlegen

```json
{
  "forceLoginMethod": "claudeai",
  "forceLoginOrgUUID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "allowedProviders": ["anthropic"]
}
```

Die Organisations-ID steht in den claude.ai-Admin-Einstellungen. Ein leeres Array oder ein ungültiger Wert bei `forceLoginOrgUUID` lässt niemanden mehr mit einem Anthropic-Konto starten. Bei Console-Logins wählt Claude Code die Organisation nur vor und prüft sie nicht.

Für ein Firmen-Gateway lässt du nur `"customEndpoint"` zu. Claude Code akzeptiert es nur für genau den Wert, den ein Managed-`env`-Block festlegt:

```json
{
  "allowedProviders": ["customEndpoint"],
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com"
  }
}
```

### Plugin-Marketplaces begrenzen

```json
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "anthropics/claude-plugins-official" },
    { "source": "github", "repo": "pexon-consulting/claude-code-best-practices" }
  ]
}
```

`github`-Einträge passen exakt, inklusive `ref` und `path`. Ab v2.1.223 erlaubt `"<owner>/*"` alle Repos einer Organisation. Der Key registriert nichts; zum Vorinstallieren kombinierst du ihn mit `extraKnownMarketplaces`.

### MCP-Server zentral steuern

Zwei Wege laut [Managed MCP](https://code.claude.com/docs/en/managed-mcp): `managed-mcp.json` im Systemverzeichnis gibt exklusive Kontrolle im gleichen Format wie `.mcp.json`. Alternativ begrenzen Allowlist und Denylist in den Managed Settings, welche Server Nutzer hinzufügen dürfen.

```json
{
  "allowManagedMcpServersOnly": true,
  "allowedMcpServers": [
    { "serverUrl": "https://mcp.example.com/*" }
  ],
  "deniedMcpServers": [
    { "serverName": "filesystem" }
  ]
}
```

Ein ungültiges `allowedMcpServers` wirkt als leere Allowlist, bis du es korrigierst.

### Organisationsweite CLAUDE.md

Zwei Wege: eine Datei `CLAUDE.md` im Systemverzeichnis (Pfade oben) oder der Key `claudeMd` mit dem Text als String. Managed CLAUDE.md-Dateien lassen sich über `claudeMdExcludes` nicht ausschließen.

```json
{
  "claudeMd": "# Firmenregeln\n\n- Keine Echtdaten von Kunden oder Beschäftigten in Prompts.\n- Vor jedem Commit die Tests ausführen.\n- Nie direkt auf main pushen."
}
```

### Telemetrie und Datenschutz

```json
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "DISABLE_FEEDBACK_COMMAND": "1",
    "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1"
  },
  "cleanupPeriodDays": 14
}
```

`DISABLE_TELEMETRY` mit dem Wert `1` übernimmt Claude Code ohne Bestätigungsdialog. Es stoppt auch die Daten für das Analytics-Dashboard der Organisation. Hintergründe stehen in [Claude Code DSGVO](./claude-code-dsgvo.md).

## SSO und Server-managed Settings

Die Doku belegt zu SSO Folgendes: Claude for Teams enthält Admin-Werkzeuge, SSO und Server-managed Settings; Claude for Enterprise ergänzt Domain Capture, rollenbasierte Berechtigungen und die Compliance-API. Ein selbst gehostetes Claude apps gateway erlaubt die Anmeldung mit Firmen-SSO über `/login`. Die SSO-Einrichtung selbst beschreibt Anthropic im Hilfe-Center, nicht in der Claude-Code-Doku.

Server-managed Settings haben Grenzen: Sie gelten nur für Sitzungen mit direkter Anthropic-Anmeldung, nicht für Bedrock, Vertex AI oder Foundry, und nicht, wenn `ANTHROPIC_BASE_URL` woandershin zeigt. Die claude.ai-Konsole kann noch nicht nach Gruppen unterscheiden. Änderungen an Hooks oder `env` warten in interaktiven Sitzungen auf eine Bestätigung des Entwicklers.

## Beispiele

### Beispiel 1: Datei auf macOS verteilen

```bash
sudo mkdir -p "/Library/Application Support/ClaudeCode"
sudo cp managed-settings.json "/Library/Application Support/ClaudeCode/managed-settings.json"
```

Für einzelne Testrechner vor dem MDM-Rollout.

### Beispiel 2: Datei auf Linux verteilen

```bash
sudo install -d -m 755 /etc/claude-code
sudo install -m 644 managed-settings.json /etc/claude-code/managed-settings.json
```

Für Linux-Hosts und eigene Images; die Datei sollte lesbar, aber nur für root schreibbar sein.

### Beispiel 3: JSON vor der Verteilung prüfen

```bash
python3 -m json.tool managed-settings.json > /dev/null && echo "gültig"
```

Pflicht vor jedem Rollout, weil eine ungültige Datei den Start von Claude Code verhindert.

### Beispiel 4: Telemetrie und Sicherheit in getrennten Dateien

```bash
sudo cp 10-telemetrie.json 20-sicherheit.json /etc/claude-code/managed-settings.d/
```

Wenn Datenschutz und IT-Sicherheit ihre Teile getrennt pflegen.

### Beispiel 5: Mindestversion erzwingen

```json
{
  "requiredMinimumVersion": "2.1.294"
}
```

Wenn du Funktionen voraussetzt, die erst ab einer Version wirken; `claude update` und `claude doctor` laufen auch unterhalb der Grenze.

### Beispiel 6: Sideloading per Kommandozeile sperren

```json
{
  "disableSideloadFlags": true
}
```

Damit niemand per `--plugin-dir` oder `--mcp-config` an der Freigabe vorbei Plugins oder MCP-Server lädt. Claude Code beendet sich dann mit einem Fehler, sobald eines der Flags übergeben wird; CI-Jobs, die `--mcp-config` nutzen, brauchen eine eigene Richtlinie.

## Schritt für Schritt

1. Entscheiden, was erzwungen wird: Startpunkt ist [vorlagen/managed-settings.json](../../vorlagen/managed-settings.json).
2. Platzhalter ersetzen (Organisations-ID, Marketplaces, Domains) und nicht benötigte Keys löschen.
3. JSON mit `python3 -m json.tool` prüfen.
4. Auf einem Testrechner in das Systemverzeichnis legen.
5. Claude Code starten, `/status` aufrufen: Die Zeile `Setting sources` muss `Enterprise managed settings (file)` zeigen, bei MDM `(plist)` oder `(HKLM)`.
6. `claude doctor` ausführen und verworfene Einträge korrigieren.
7. Gegenproben: `claude --dangerously-skip-permissions` muss abgelehnt werden, eine gesperrte Datei darf nicht lesbar sein.
8. Über MDM oder Softwareverteilung an die Pilotgruppe, dann an alle verteilen; die Datei regelmäßig neu ausrollen, damit lokale Änderungen überschrieben werden.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Datei unter `C:\ProgramData\ClaudeCode\` | Richtlinie wirkt nicht | `C:\Program Files\ClaudeCode\` verwenden |
| Ungültiges JSON | Claude Code startet nicht und nennt die Quelle | vorher `python3 -m json.tool` |
| Datei enthält nur `managedSourcesBehavior` | `/status` zeigt keine Managed-Quelle | mindestens einen Policy-Key aufnehmen |
| MDM und Datei gleichzeitig, `first-wins` | Dateiwerte werden ignoriert, `Skipped sources` nennt sie | alles in eine Quelle oder bewusst `"merge"` |
| `strictKnownMarketplaces: []` | auch der offizielle Marketplace ist gesperrt | gewünschte Quellen eintragen |
| `model` als Sperre verstanden | Entwickler wechseln per `--model` | `availableModels` verwenden |
| Server-managed Settings für Bedrock-Nutzer | Richtlinie kommt nicht an | Datei oder MDM verteilen |

## Häufige Fragen

### Was sind Managed Settings in Claude Code?

Managed Settings sind die Einstellungen, die eine Organisation auf jeden Rechner verteilt und die über allen anderen Ebenen stehen. Sie haben dieselbe Form wie settings.json und kommen als Datei, MDM-Profil oder aus der claude.ai-Konsole.

### Wo liegt die managed-settings.json?

Unter macOS in `/Library/Application Support/ClaudeCode/`, unter Linux und WSL in `/etc/claude-code/` und unter Windows in `C:\Program Files\ClaudeCode\`. Daneben können `managed-settings.d/` und `managed-mcp.json` liegen.

### Wie prüfe ich, ob die Richtlinie greift?

Mit `/status` in einer Claude-Code-Sitzung: Die Zeile `Setting sources` nennt `Enterprise managed settings` und die Quelle in Klammern. `claude doctor` listet zusätzlich Einträge, die Claude Code verworfen hat.

### Können Entwickler Managed Settings umgehen?

Über eigene Settings-Dateien, Projektdateien oder `--settings` nicht. Wer lokale Admin-Rechte hat, kann die Datei selbst ändern, und wer die API mit einem anderen Werkzeug aufruft, ist nicht erfasst; deshalb verteilt MDM die Datei regelmäßig neu.

### Brauche ich Claude for Enterprise für Managed Settings?

Nein, die Datei- und MDM-Wege funktionieren unabhängig vom Plan, auch mit Bedrock oder Vertex AI. Server-managed Settings aus der claude.ai-Konsole gibt es laut Doku für Teams und Enterprise.

## Weiterlesen

- [Claude Code im Team ausrollen](./claude-code-team-rollout.md)
- [Claude Code DSGVO](./claude-code-dsgvo.md)
- [Claude Code Sicherheit](./claude-code-sicherheit.md)
- [Claude Code settings.json](./claude-code-settings-json.md)
- [Claude Code Plugins](./claude-code-plugins.md)
- Vorlagen: [managed-settings.json](../../vorlagen/managed-settings.json), [Freigabe-Paket](../rollout/freigabe-paket.md), Prüfregel [CC012](../regeln.md#cc012)
