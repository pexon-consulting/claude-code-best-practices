# Claude Code Azure: Claude Code über Microsoft Foundry nutzen

Ja, Claude Code läuft über Microsoft Foundry (Azure): Du legst im [Foundry-Portal](https://ai.azure.com/) eine Ressource mit Deployments für Opus, Sonnet und Haiku an, setzt `CLAUDE_CODE_USE_FOUNDRY=1` und `ANTHROPIC_FOUNDRY_RESOURCE` mit dem Ressourcennamen und meldest dich per `az login` (Entra ID) oder API-Key an. Anders als bei Bedrock und Vertex AI gibt es keinen Einrichtungsassistenten und keine Modellprüfung beim Start, deshalb musst du die Modelle mit den Namen deiner Deployments pinnen. Ob die Anfragen in Azure bleiben, entscheidet die Hosting-Option des Deployments.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

Diese Anleitung erklärt Technik und Einstellungen. Sie ist keine Rechtsberatung. Datenschutz, Verträge und Mitbestimmung klärst du mit Datenschutzbeauftragtem, Rechtsabteilung und Betriebsrat. Angaben zu Regionen und Datenverarbeitung der Anbieter können sich ändern; maßgeblich sind deren aktuelle Dokumentation und Verträge.

## Das Wichtigste in Kürze

- Konfiguration nur über Umgebungsvariablen: `CLAUDE_CODE_USE_FOUNDRY=1` plus `ANTHROPIC_FOUNDRY_RESOURCE` oder `ANTHROPIC_FOUNDRY_BASE_URL`.
- Drei Anmeldewege: API-Key (`ANTHROPIC_FOUNDRY_API_KEY`), Entra ID über die Azure-SDK-Kette (`az login`) oder ein fertiges Token (`ANTHROPIC_FOUNDRY_AUTH_TOKEN`).
- Pinnen ist Pflicht. Ohne Pin löst `opus` zu Opus 4.6 auf, und fehlt das Deployment, scheitern die Anfragen.
- Hosting-Option "Hosted on Azure": Prompts und Antworten bleiben in Azure, nur Nutzungsmetadaten und von Anthropics Sicherheitssystemen markierte Inhalte gehen an Anthropic.
- RBAC: Die Rollen `Azure AI User` oder `Cognitive Services User` reichen.

## Voraussetzungen

- Ein Azure-Abonnement mit Zugriff auf Microsoft Foundry.
- RBAC-Rechte, um Foundry-Ressourcen und Deployments anzulegen.
- Azure CLI, nur wenn du keinen anderen Weg zu Zugangsdaten hast.
- Je ein Deployment für Claude Opus, Sonnet und Haiku. Den Namen jedes Deployments brauchst du später für die Modellvariablen. Wähle eine feste Modellversion statt "auto-update to latest".

## Was geht an wen

| Daten | Empfänger | Standard auf Foundry | Abschalten |
| --- | --- | --- | --- |
| Prompts, Code-Ausschnitte, Antworten bei "Hosted on Azure" | Microsoft Azure; an Anthropic nur Nutzungsmetadaten und markierte Inhalte | an | Hosting-Option im Deployment |
| Prompts, Code-Ausschnitte, Antworten bei "Hosted on Anthropic" | Anthropic-Infrastruktur | an | Hosting-Option im Deployment |
| Metriken | Anthropic | aus | - |
| Fehlerberichte | Fehlerdienst eines Drittanbieters | aus | - |
| `/feedback` | lokal unter `~/.claude/feedback-bundles/` | geht nicht raus | - |
| Bewertung "How is Claude doing this session?" | Anthropic, nur die Bewertung | an | `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1` |
| Hostname vor jedem WebFetch | `api.anthropic.com`, nur der Hostname | an | `"skipWebFetchPreflight": true` |
| Gesprächsverläufe | lokal unter `~/.claude/projects/`, 30 Tage | an | `cleanupPeriodDays` |

Die Verbindung läuft über TLS 1.2+. Die Hosting-Optionen beschreibt Anthropic auf der [Plattform-Doku zu Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options). Welche Azure-Regionen Claude anbieten, steht nicht in der Claude-Code-Doku; das prüfst du im Foundry-Portal. Verträge, Auftragsverarbeitung und Speicherorte klärst du mit dem Datenschutzbeauftragten, siehe [Claude Code und DSGVO](./claude-code-dsgvo.md).

## Beispiele für Claude Code mit Microsoft Foundry

### Beispiel 1: Minimal-Setup mit Entra ID

Ohne API-Key, mit der Azure CLI:

```bash
az login
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=<dein-ressourcenname>
export ANTHROPIC_DEFAULT_OPUS_MODEL='claude-opus-4-8'
export ANTHROPIC_DEFAULT_SONNET_MODEL='claude-sonnet-5'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='claude-haiku-4-5'
claude
```

`ANTHROPIC_FOUNDRY_API_KEY` und `ANTHROPIC_FOUNDRY_AUTH_TOKEN` bleiben dabei leer, dann nutzt Claude Code die Default Credential Chain des Azure SDK. Die drei Modellwerte sind die Namen deiner Deployments; hier entsprechen sie den Modell-IDs.

### Beispiel 2: Mit API-Key aus dem Portal

Den Key findest du in der Ressource unter **Endpoints and keys**:

```bash
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=<dein-ressourcenname>
export ANTHROPIC_FOUNDRY_API_KEY=<dein-foundry-key>
claude
```

Unter Windows in PowerShell:

```powershell
$env:CLAUDE_CODE_USE_FOUNDRY = "1"
$env:ANTHROPIC_FOUNDRY_RESOURCE = "<dein-ressourcenname>"
$env:ANTHROPIC_FOUNDRY_API_KEY = "<dein-foundry-key>"
claude
```

`ANTHROPIC_FOUNDRY_RESOURCE` ist nur der Name, etwa `team-claude`. Eine URL oder ein Hostname wird abgelehnt. Statt des Namens kannst du die ganze Adresse in `ANTHROPIC_FOUNDRY_BASE_URL` setzen: `https://<dein-ressourcenname>.services.ai.azure.com/anthropic`.

### Beispiel 3: Token aus einem eigenen Anmeldeskript

Wenn ein anderer Prozess schon ein Entra-ID-Token geholt hat:

```bash
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=<dein-ressourcenname>
export ANTHROPIC_FOUNDRY_AUTH_TOKEN=<dein-entra-token>
```

Claude Code schickt den Wert als `Authorization: Bearer`. Er hat Vorrang vor `ANTHROPIC_FOUNDRY_API_KEY` und vor der Default Credential Chain.

### Beispiel 4: Eigene Deployment-Namen und 1M Kontext

Heißen deine Deployments nicht wie die Modell-IDs, sagst du Claude Code mit `modelOverrides`, welches Modell dahinter steckt. Dann erkennt es die Fähigkeiten, etwa den 1M-Kontext von Opus 4.7 und neuer:

```json
{
  "modelOverrides": {
    "claude-opus-4-8": "team-opus-prod"
  },
  "env": {
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-8"
  }
}
```

Für Opus 4.6 und Sonnet 4.6 hängst du `[1m]` an den Deployment-Namen in der Modellvariable. Mit `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` bleibst du bei 200K.

### Beispiel 5: Eigene Azure-Rolle mit minimalen Rechten

Statt `Azure AI User` oder `Cognitive Services User` geht eine eigene Rolle mit dieser Data Action:

```json
{
  "permissions": [
    {
      "dataActions": [
        "Microsoft.CognitiveServices/accounts/providers/*"
      ]
    }
  ]
}
```

Der Ausschnitt zeigt nur den Rechte-Teil der Rollendefinition. Wie du daraus eine vollständige Rolle machst, beschreibt die [Foundry-RBAC-Doku](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-azure-ai-foundry).

### Beispiel 6: Team-Setup über Managed Settings

`managed-settings.json` (macOS `/Library/Application Support/ClaudeCode/`, Linux und WSL `/etc/claude-code/`, Windows `C:\Program Files\ClaudeCode\`):

```json
{
  "allowedProviders": ["foundry"],
  "env": {
    "CLAUDE_CODE_USE_FOUNDRY": "1",
    "ANTHROPIC_FOUNDRY_RESOURCE": "<dein-ressourcenname>",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-8",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-5",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5",
    "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1"
  },
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  }
}
```

`allowedProviders` (ab v2.1.285) lässt nur Foundry zu. Jede Person meldet sich mit `az login` an, deshalb steht kein Key in der Datei. Unter Windows kannst du denselben JSON-Text als Wert `Settings` unter `HKLM\SOFTWARE\Policies\ClaudeCode` verteilen.

### Beispiel 7: Team-Setup über die Projekt-Settings

Ohne Managed Settings im Repo in `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_USE_FOUNDRY": "1",
    "ANTHROPIC_FOUNDRY_RESOURCE": "<dein-ressourcenname>",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-8",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-5",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5"
  }
}
```

Die Werte gelten nach dem Vertrauen des Ordners. `ANTHROPIC_FOUNDRY_API_KEY` gehört nicht in diese Datei; `claude-team audit` meldet Zugangsschlüssel in Claude-Dateien als [CC030](../regeln.md#cc030).

## Schritt für Schritt: Foundry im Team einführen

1. **Ressource anlegen** im [Foundry-Portal](https://ai.azure.com/) und den Namen notieren.
2. **Deployments anlegen** für Opus, Sonnet und Haiku, mit fester Modellversion und der gewünschten Hosting-Option.
3. **Rollen vergeben.** `Azure AI User` oder `Cognitive Services User` für die Entwickler, alternativ die eigene Rolle aus Beispiel 5.
4. **Anmeldeweg festlegen.** Entra ID mit `az login` ist der Weg ohne gespeicherten Schlüssel.
5. **Managed Settings verteilen** wie in Beispiel 6, etwa per Intune.
6. **Starten und prüfen.** `claude`, dann `/status`: Die Zeile API provider zeigt `Microsoft Foundry` und den Ressourcennamen.
7. **Projekt absichern** mit `claude-team einrichten` und `claude-team audit`. Die [Vorlage](../../src/claude_team/vorlage/.claude/settings.json) sperrt das Lesen von `~/.azure`.

## Welche Variablen Projekt-Settings ignorieren

`CLAUDE_CODE_USE_FOUNDRY`, `ANTHROPIC_FOUNDRY_RESOURCE` und die Modellvariablen darf eine `.claude/settings.json` setzen. Aus Projekt- und lokalen Settings verwirft Claude Code unter anderem:

- Speicherorte: `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR`, `HOME`, `TMPDIR`, `TMP`, `TEMP`, `XDG_*`.
- Windows-Programmvariablen: `SystemRoot`, `ComSpec`, `ProgramData`, `LOCALAPPDATA`, `PATHEXT`, `PSModulePath` und die `ProgramFiles`-Familie.
- OpenTelemetry-Variablen, die Telemetrie einschalten oder umleiten, ab v2.1.282. Abschaltende Werte gelten weiter.
- `OTEL_LOG_RAW_API_BODIES`, `CLAUDE_CODE_PROCESS_WRAPPER`, die `CLAUDE_CODE_SYNC_*`-Variablen und die Plugin-Ordner.

Verworfene Werte zeigt `claude --debug`. Vollständige Liste in der [Settings-Referenz](https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env).

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Keine Entra-Anmeldung | "Failed to get token from azureADTokenProvider: ChainedTokenCredential authentication failed" | `az login` ausführen oder `ANTHROPIC_FOUNDRY_API_KEY` setzen |
| Falscher Ressourcenname | wiederholte Verbindungsfehler beim ersten Prompt | Echten Ressourcennamen statt Platzhalter in `ANTHROPIC_FOUNDRY_RESOURCE` |
| URL statt Name | Fehlermeldung, dass `ANTHROPIC_FOUNDRY_RESOURCE` ein Ressourcenname sein muss | Nur den Namen eintragen oder `ANTHROPIC_FOUNDRY_BASE_URL` nutzen |
| Kein Pin | Anfragen scheitern, weil das Standardmodell fehlt | Alle drei `ANTHROPIC_DEFAULT_*_MODEL` auf Deployment-Namen setzen |
| Hintergrundaufgaben teuer | Sitzungstitel laufen mit dem Hauptmodell | Ohne Haiku-Pin nutzt Foundry das Hauptmodell dafür; `ANTHROPIC_DEFAULT_HAIKU_MODEL` setzen |
| Logout geht nicht | `/logout` fehlt | Auf Foundry nicht verfügbar; Anmeldung läuft über Azure |
| Auto-Update im Deployment | Version im Deployment ist nicht festgelegt | Deployment mit fester Version statt "auto-update to latest" anlegen |

## Häufige Fragen

### Gibt es einen Einrichtungsassistenten für Foundry?

Nein. Anders als bei Bedrock und Agent Platform gibt es für Foundry keinen Assistenten und keine Modellprüfung beim Start. Die Umgebungsvariablen sind der einzige Weg.

### Bleiben meine Daten bei Foundry in Azure?

Bei Deployments mit "Hosted on Azure" bleiben Prompts und Antworten in Azure; an Anthropic gehen nur Nutzungsmetadaten und Inhalte, die Anthropics Sicherheitssysteme markieren. Bei "Hosted on Anthropic" laufen die Anfragen über Anthropic. Dazu kommen die kleinen Nebenverbindungen aus der Tabelle oben. Die Bewertung für dein Unternehmen klärst du mit dem Datenschutzbeauftragten.

### Brauche ich einen API-Key?

Nein. Mit Entra ID meldest du dich über `az login` oder eine andere Quelle der Azure-SDK-Kette an, dann gibt es keinen Schlüssel zu speichern. Ein API-Key aus dem Portal geht auch, gehört aber nie in eine Datei im Repo.

### Kann ich Foundry über ein Firmen-Gateway ansprechen?

Ja. Du setzt `ANTHROPIC_FOUNDRY_BASE_URL` auf das Gateway und gibst dessen Zugangsdaten in `ANTHROPIC_FOUNDRY_API_KEY` mit. Schreibt das Gateway selbst einen `Authorization`-Header, setzt du `CLAUDE_CODE_SKIP_FOUNDRY_AUTH=1` und lässt beide Credential-Variablen leer. Siehe [Claude Code LLM-Gateway](./claude-code-llm-gateway.md).

### Was kostet Claude Code über Foundry?

Abgerechnet wird über Azure nach den Foundry-Preisen von Microsoft, Anthropic nennt dafür keine eigenen Preise. Zur Steuerung im Team siehe [Claude Code Kosten](./claude-code-kosten.md).

## Weiterlesen

- [Claude Code und DSGVO](./claude-code-dsgvo.md)
- [Claude Code Bedrock](./claude-code-bedrock.md) und [Claude Code Vertex AI](./claude-code-vertex-ai.md)
- [Claude Code LLM-Gateway](./claude-code-llm-gateway.md)
- [Claude Code unter Windows](./claude-code-windows.md)
- [Claude Code Enterprise: Managed Settings](./claude-code-enterprise.md)
- Offizielle Doku: [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry), [Data usage](https://code.claude.com/docs/en/data-usage), [Settings reference](https://code.claude.com/docs/en/settings-reference)
