# Claude Code Vertex AI: Claude Code über Google Cloud betreiben

Für Google Vertex AI braucht Claude Code drei Umgebungsvariablen: `CLAUDE_CODE_USE_VERTEX=1`, `ANTHROPIC_VERTEX_PROJECT_ID` mit deiner Projekt-ID und `CLOUD_ML_REGION` mit `global`, einer Multi-Region wie `eu` oder einer Region wie `europe-west1`. Angemeldet wird über die Application Default Credentials von `gcloud` (`gcloud auth application-default login`), die Claude-Modelle schaltest du vorher im Model Garden frei. Google nennt den Dienst inzwischen "Google Cloud's Agent Platform"; im Login-Menü von Claude Code heißt er weiter "Google Vertex AI".

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Einstieg: `claude` starten, "3rd-party platform" und dann "Google Vertex AI" wählen. Der Assistent prüft die Modelle und schreibt in den `env`-Block von `~/.claude/settings.json`; später öffnest du ihn mit `/setup-vertex`.
- `CLOUD_ML_REGION=eu` nutzt den Multi-Region-Host `aiplatform.eu.rep.googleapis.com`. Ohne Wert fällt Claude Code auf `us-east5` zurück.
- Einzelne Modelle verlegst du mit `VERTEX_REGION_CLAUDE_*` in eine andere Region, etwa wenn ein Modell den `global`-Endpunkt nicht kennt.
- Ohne Pin löst `opus` zu `claude-opus-5-5` auf, `sonnet` zu Sonnet 4.5. Für Teams Modelle pinnen.
- IAM-Rolle `roles/aiplatform.user` reicht, empfohlen ist ein eigenes GCP-Projekt für Claude Code.

## Voraussetzungen

- Ein GCP-Konto mit aktivierter Abrechnung.
- Ein Projekt mit aktivierter Agent-Platform-API.
- Freigegebene Claude-Modelle im [Model Garden](https://console.cloud.google.com/vertex-ai/model-garden). Die Freigabe kann 24-48 Stunden dauern.
- Das Google Cloud SDK (`gcloud`).
- Kontingent (Quota) in der gewünschten Region.

## Was geht an wen

| Daten | Empfänger | Standard auf Vertex AI | Abschalten |
| --- | --- | --- | --- |
| Prompts, Code-Ausschnitte, Tool-Ergebnisse, Antworten | Google Cloud, Endpunkt nach `CLOUD_ML_REGION` (TLS 1.2+) | an, das ist der Betrieb | - |
| Gespeicherte Daten bei Google | Google, mit Google-Schlüsseln, CMEK möglich | laut Google-Vertrag | - |
| Metriken | Anthropic | aus | - |
| Fehlerberichte | Fehlerdienst eines Drittanbieters | aus | - |
| `/feedback` | lokal unter `~/.claude/feedback-bundles/` | geht nicht raus | - |
| Bewertung "How is Claude doing this session?" | Anthropic, nur die Bewertung | an | `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1` |
| Hostname vor jedem WebFetch | `api.anthropic.com`, nur der Hostname | an | `"skipWebFetchPreflight": true` |
| Gesprächsverläufe | lokal unter `~/.claude/projects/`, 30 Tage | an | `cleanupPeriodDays` |

Wer Daten in der EU halten will, setzt `CLOUD_ML_REGION` auf `eu` oder eine EU-Region statt auf `global`, prüft im Model Garden, welche Modelle dort angeboten werden, und setzt keine `VERTEX_REGION_CLAUDE_*`-Variable auf eine Region außerhalb der EU. Das Development Partner Program von Anthropic gibt es für Agent Platform nicht. Verträge und Auftragsverarbeitung bei Google klärst du mit dem Datenschutzbeauftragten, siehe [Claude Code und DSGVO](./claude-code-dsgvo.md).

## Beispiele

### Beispiel 1: API aktivieren und anmelden

Einmal je Projekt und Rechner:

```bash
gcloud config set project <deine-projekt-id>
gcloud services enable aiplatform.googleapis.com
gcloud auth application-default login
```

Danach im Model Garden nach "Claude" suchen und die gewünschten Modelle anfragen. Für Dienstkonten setzt du `GOOGLE_APPLICATION_CREDENTIALS` auf die Schlüssel- oder Konfigurationsdatei; Workload Identity Federation mit X.509-Zertifikaten läuft über dieselbe Kette.

### Beispiel 2: Minimal-Setup in der Shell mit EU-Multi-Region

```bash
export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_PROJECT_ID=<deine-projekt-id>
export CLOUD_ML_REGION=eu
claude
```

`ANTHROPIC_VERTEX_PROJECT_ID` gilt auch dann, wenn `GCLOUD_PROJECT`, `GOOGLE_CLOUD_PROJECT` oder die Credential-Datei ein anderes Projekt nennen. `/status` zeigt danach in der Zeile `API provider` den Wert `Google Vertex AI` und darunter Projekt, Region und Modell.

### Beispiel 3: Nutzer-Settings mit automatischem Token-Refresh

In `~/.claude/settings.json`:

```json
{
  "gcpAuthRefresh": "gcloud auth application-default login",
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "ANTHROPIC_VERTEX_PROJECT_ID": "<deine-projekt-id>",
    "CLOUD_ML_REGION": "eu"
  }
}
```

`gcpAuthRefresh` läuft nur, wenn die Anmeldung abgelaufen ist, und bricht nach drei Minuten ab. Steht der Key in einer `.claude/settings.json` im Repo, führt Claude Code ihn erst nach dem Vertrauen des Ordners aus.

### Beispiel 4: Einzelne Modelle in eine andere Region legen

Bietet `global` oder `eu` ein Modell nicht an, verschiebst du nur dieses Modell:

```bash
export CLOUD_ML_REGION=global
export VERTEX_REGION_CLAUDE_HAIKU_4_5=europe-west1
export VERTEX_REGION_CLAUDE_4_6_SONNET=europe-west1
```

Es gibt eine Variable je Modellversion, etwa `VERTEX_REGION_CLAUDE_5_5_OPUS` (ab v2.1.280), `VERTEX_REGION_CLAUDE_5_5_SONNET` (ab v2.1.284) und `VERTEX_REGION_CLAUDE_HAIKU_5_5` (ab v2.1.293). Ohne Wert gilt `CLOUD_ML_REGION`. Ob ein Modell in `europe-west1` verfügbar ist, zeigt der Model Garden.

### Beispiel 5: Modelle für alle pinnen

```json
{
  "env": {
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-8",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-5",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5@20251001"
  }
}
```

Hintergrundaufgaben wie Sitzungstitel laufen auf Agent Platform standardmäßig mit dem Sonnet-Standardmodell, weil Haiku nicht in jedem Projekt freigegeben ist. Mit `ANTHROPIC_DEFAULT_HAIKU_MODEL` nutzt Claude Code dafür Haiku. Ohne Pin zahlst du für das Hauptmodell den Opus-Preis; Opus ist teurer als Sonnet.

### Beispiel 6: Team-Setup über Managed Settings

`managed-settings.json` (macOS `/Library/Application Support/ClaudeCode/`, Linux und WSL `/etc/claude-code/`, Windows `C:\Program Files\ClaudeCode\`):

```json
{
  "allowedProviders": ["vertex"],
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "ANTHROPIC_VERTEX_PROJECT_ID": "<deine-projekt-id>",
    "CLOUD_ML_REGION": "eu",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-8",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-5",
    "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1"
  },
  "availableModels": ["claude-opus-4-8", "claude-sonnet-5"],
  "enforceAvailableModels": true,
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  }
}
```

`allowedProviders` (ab v2.1.285) lässt nur Agent Platform zu. Mit `enforceAvailableModels` (ab v2.1.287) prüft Claude Code beim Start nur Modelle aus `availableModels`. Die Zugangsdaten kommen pro Person über `gcloud`, nicht aus dieser Datei.

### Beispiel 7: Team-Setup über die Projekt-Settings

Ohne Managed Settings in `.claude/settings.json` im Repo:

```json
{
  "env": {
    "CLAUDE_CODE_USE_VERTEX": "1",
    "ANTHROPIC_VERTEX_PROJECT_ID": "<deine-projekt-id>",
    "CLOUD_ML_REGION": "eu"
  }
}
```

Die Werte gelten erst nach dem Vertrauen des Ordners. Schlüsseldateien und Pfade zu Dienstkonto-Schlüsseln gehören nicht ins Repo. Die [Vorlage](../../src/claude_team/vorlage/.claude/settings.json) sperrt außerdem das Lesen von `~/.config/gcloud`.

### Beispiel 8: MCP Tool Search abschalten

Für Opus 4.5, Sonnet 4.5, Haiku 4.5 und neuer ist MCP Tool Search auf Agent Platform an. Bei Problemen mit vielen MCP-Servern:

```json
{
  "env": {
    "ENABLE_TOOL_SEARCH": "false"
  }
}
```

Bei älteren Modellen lädt Claude Code die MCP-Tool-Definitionen immer vorab, `ENABLE_TOOL_SEARCH=true` ändert daran nichts.

## Schritt für Schritt: Vertex AI im Team einführen

1. **Eigenes GCP-Projekt** für Claude Code anlegen, Abrechnung aktivieren.
2. **API aktivieren** mit `gcloud services enable aiplatform.googleapis.com`.
3. **Modelle anfragen** im Model Garden und auf die Freigabe warten (bis 48 Stunden).
4. **Region festlegen.** `eu` oder eine EU-Region; im Model Garden prüfen, welche Modelle dort laufen.
5. **IAM vergeben.** `roles/aiplatform.user` oder eine eigene Rolle mit `aiplatform.endpoints.predict`.
6. **Managed Settings verteilen** wie in Beispiel 6.
7. **Anmelden** auf jedem Rechner: `gcloud auth application-default login`.
8. **Prüfen** mit `/status`: `API provider` ist `Google Vertex AI`, Projekt und Region stimmen.
9. **Projekt absichern** mit `claude-team einrichten` und `claude-team audit`.

## Welche Variablen Projekt-Settings ignorieren

`CLAUDE_CODE_USE_VERTEX`, `ANTHROPIC_VERTEX_PROJECT_ID` und `CLOUD_ML_REGION` darf eine `.claude/settings.json` setzen. Aus Projekt- und lokalen Settings verwirft Claude Code aber unter anderem:

- Speicherorte: `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR`, `HOME`, `TMPDIR`, `TMP`, `TEMP`, `XDG_*`.
- Windows-Programmvariablen wie `SystemRoot`, `ComSpec`, `PATHEXT` und `PSModulePath`.
- OpenTelemetry-Variablen, die Telemetrie einschalten oder umleiten (`CLAUDE_CODE_ENABLE_TELEMETRY`, `OTEL_EXPORTER_OTLP_*`-Endpunkte und -Header, `OTEL_LOG_USER_PROMPTS` und Verwandte), ab v2.1.282. Abschaltende Werte wie `none` gelten weiter.
- `OTEL_LOG_RAW_API_BODIES`, `CLAUDE_CODE_PROCESS_WRAPPER`, die `CLAUDE_CODE_SYNC_*`-Variablen und die Plugin-Ordner.

`claude --debug` zeigt jede verworfene Variable. Vollständig in der [Settings-Referenz](https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env).

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Keine Anmeldung | "Could not load the default credentials" | `gcloud auth application-default login` oder `GOOGLE_APPLICATION_CREDENTIALS` setzen |
| Modell fehlt | 404 "model not found" | Im Model Garden freigeben; prüfen, ob das Modell am Standort angeboten wird |
| `global` ohne Modell | 404 bei `CLOUD_ML_REGION=global` | Modell mit `VERTEX_REGION_CLAUDE_*` in eine Region legen oder anderes Modell pinnen |
| Zu wenig Kontingent | 429-Fehler | Primär- und Hintergrundmodell müssen in der Region verfügbar sein; Quota erhöhen oder `global` testen |
| Provider fehlt in `/status` | Claude Code fragt nach Anthropic-Login | Variablen erreichen den Prozess nicht; in der Shell exportieren oder in den `env`-Block |
| Region ignoriert | Anfragen laufen nach `us-east5` | Wert enthält Punkt, Schrägstrich oder Leerzeichen und gilt als leer; Schreibweise prüfen |
| Falsches Projekt | Anfragen landen in einem anderen Projekt | `ANTHROPIC_VERTEX_PROJECT_ID` explizit setzen |

## Häufige Fragen

### Ist Vertex AI dasselbe wie Google Cloud's Agent Platform?

Ja. Die Claude-Code-Doku nennt den Dienst "Google Cloud's Agent Platform, formerly Vertex AI". Die Variablen heißen weiter `CLAUDE_CODE_USE_VERTEX` und `ANTHROPIC_VERTEX_PROJECT_ID`, im Login-Menü steht "Google Vertex AI".

### Kann ich Claude Code auf Vertex AI in der EU betreiben?

Ja, mit `CLOUD_ML_REGION=eu` für den Multi-Region-Endpunkt oder einer EU-Region wie `europe-west1`. Welche Claude-Modelle dort angeboten werden, ändert sich und steht im Model Garden. Ob das für die Daten deines Unternehmens genügt, klärst du mit dem Datenschutzbeauftragten.

### Brauche ich ein Anthropic-Konto?

Nein. Claude Code nutzt die Google-Anmeldung, abgerechnet wird über Google Cloud. `/logout` gibt es deshalb nicht; höhere Rate Limits bekommst du über den Google Cloud Support.

### Wie nutze ich Vertex AI über ein Firmen-Gateway?

Mit `ANTHROPIC_VERTEX_BASE_URL` auf das Gateway und `CLAUDE_CODE_SKIP_VERTEX_AUTH=1`, wenn das Gateway die Google-Anmeldung übernimmt. Details in [Claude Code LLM-Gateway](./claude-code-llm-gateway.md).

### Unterstützt Claude Code auf Vertex AI 1M Token Kontext?

Ja, Fable-Modelle, Sonnet 5 und neuer sowie Opus 4.7 und neuer laufen dort standardmäßig mit 1M Token. Opus 4.6 und Sonnet 4.6 brauchen das Suffix `[1m]` an der Modell-ID. Mit `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` bleibst du bei 200K.

## Weiterlesen

- [Claude Code und DSGVO](./claude-code-dsgvo.md)
- [Claude Code Bedrock](./claude-code-bedrock.md) und [Claude Code Azure Foundry](./claude-code-azure-foundry.md)
- [Claude Code LLM-Gateway](./claude-code-llm-gateway.md)
- [Claude Code Enterprise: Managed Settings](./claude-code-enterprise.md)
- [Claude Code Kosten](./claude-code-kosten.md)
- Offizielle Doku: [Google Cloud's Agent Platform](https://code.claude.com/docs/en/google-vertex-ai), [Data usage](https://code.claude.com/docs/en/data-usage), [Environment variables](https://code.claude.com/docs/en/env-vars)
