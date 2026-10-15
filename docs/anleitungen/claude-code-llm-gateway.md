# Claude Code Proxy und LLM-Gateway: LiteLLM, OpenRouter und Firmen-Gateways

Claude Code leitest du über ein firmeneigenes LLM-Gateway, indem du `ANTHROPIC_BASE_URL` auf die Adresse des Gateways setzt und den Zugang des Gateways in `ANTHROPIC_AUTH_TOKEN` (Header `Authorization: Bearer`), `ANTHROPIC_API_KEY` (Header `x-api-key`) oder ein `apiKeyHelper`-Skript legst. Ob es klappt, prüfst du vorab mit einem `curl` auf `/v1/messages` und danach mit `/status`, wo die Zeile `Anthropic base URL` das Gateway zeigen muss. Für ein ganzes Team verteilst du beides über Managed Settings und sperrst mit `allowedProviders: ["customEndpoint"]` alle anderen Ziele.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Jedes Gateway mit einem unterstützten API-Format funktioniert. Anthropic unterstützt aber kein Routing zu Modellen, die nicht von Claude stammen.
- `ANTHROPIC_BASE_URL` allein ersetzt das Abo nicht. Erst mit einem Gateway-Zugang laufen die Anfragen über diesen Zugang und werden pro Token beim Inhaber abgerechnet.
- Den Zugang nie in die `.claude/settings.json` im Repo schreiben. Sie wird mit allen geteilt, die das Repo klonen.
- Auch mit Gateway sendet Claude Code Nebenverkehr direkt an Anthropic und andere Dienste. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` schaltet das meiste ab, die WebFetch-Prüfung nicht.
- Ein Gateway kann zu Anthropic, Bedrock, Vertex AI oder Foundry weiterleiten, jeweils mit eigener Basis-URL-Variable.

## Was ist mit LiteLLM und OpenRouter?

Die Claude-Code-Doku nennt keine bestimmten Gateway-Produkte als unterstützt. Sie sagt: Jedes Gateway mit einem unterstützten API-Format funktioniert, und Anthropic empfiehlt, wartet oder prüft keine Gateway-Produkte von Dritten.

- **LiteLLM** taucht an zwei Stellen auf. In der [Kosten-Doku](https://code.claude.com/docs/en/costs) berichten mehrere große Unternehmen, LiteLLM zu nutzen, um Ausgaben je Schlüssel zu verfolgen; das Projekt ist nicht mit Anthropic verbunden und nicht auf Sicherheit geprüft. In der Variablen-Referenz ist LiteLLM neben Kong ein Beispiel für ein Gateway mit Modellabfrage.
- **OpenRouter** kommt in der Claude-Code-Doku nicht vor. Ob es zu Claude Code passt, musst du gegen den [Gateway-Kompatibilitätsleitfaden](https://code.claude.com/docs/en/llm-gateway-protocol) selbst prüfen.
- **Claude apps gateway** ist das selbst gehostete Gateway von Anthropic mit SSO-Anmeldung und OTLP-Telemetrie. Es hat eine eigene Doku-Seite und ist hier nicht Thema.

Ein Gateway ist Infrastruktur, die du selbst betreibst und aktuell halten musst: Neue Claude-Code-Funktionen brechen, wenn das Gateway neue Felder oder Header nicht weitergibt.

## Was geht an wen

| Daten | Empfänger | Standard | Abschalten |
| --- | --- | --- | --- |
| Prompts, Code-Ausschnitte, Tool-Ergebnisse, Antworten | dein Gateway und dessen Upstream (Anthropic API oder Cloud-Anbieter) | an, das ist der Betrieb | - |
| Protokolle beim Gateway | wer das Gateway betreibt | je nach Gateway | Konfiguration des Gateways |
| Telemetrie-Ereignisse | Anthropic, ohne Gateway-Zugang | an | `DISABLE_TELEMETRY=1` oder `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` |
| Fehlerberichte | Fehlerdienst eines Drittanbieters | je nach Anmeldung | `DISABLE_ERROR_REPORTING=1` |
| Versionsprüfung, Release Notes und ähnlicher Nebenverkehr | Anthropic und Dienste wie GitHub | an | `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` |
| Hostname vor jedem WebFetch | `api.anthropic.com`, nur der Hostname | an | `"skipWebFetchPreflight": true` |
| Fast-Mode-Prüfung | `api.anthropic.com`, folgt nicht `ANTHROPIC_BASE_URL` | an | `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` |
| Gesprächsverläufe | lokal unter `~/.claude/projects/`, 30 Tage | an | `cleanupPeriodDays` |

Was das Gateway speichert und wohin es weiterleitet, entscheidest du. Ob ein Gateway mit Protokollierung aller Prompts zu deinen Vorgaben passt, klärst du mit dem Datenschutzbeauftragten, siehe [Claude Code und DSGVO](./claude-code-dsgvo.md).

## Beispiele

### Beispiel 1: Verbindung in der Shell testen

Erst prüfen, dann speichern:

```bash
export ANTHROPIC_BASE_URL=https://llm-gateway.example.com
export ANTHROPIC_AUTH_TOKEN=<dein-gateway-token>
curl -sS -w '\n%{http_code}\n' -X POST "$ANTHROPIC_BASE_URL/v1/messages" \
  -H "Authorization: Bearer $ANTHROPIC_AUTH_TOKEN" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "."}]}'
```

Eine Antwort, die mit `{"id":"msg_` beginnt, heißt: Adresse und Zugang stimmen. Auch eine Meldung über ein unbekanntes Modell beweist das. Ein `401` heißt: Der Zugang wurde abgelehnt; probiere `ANTHROPIC_API_KEY` mit dem Header `x-api-key` statt des Bearer-Tokens. Danach `claude` aus derselben Shell starten und `/status` aufrufen.

### Beispiel 2: Dauerhaft in den Nutzer-Settings

In `~/.claude/settings.json` (Windows `%USERPROFILE%\.claude\settings.json`):

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
    "ANTHROPIC_AUTH_TOKEN": "<dein-gateway-token>",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

Settings-Werte schlagen Shell-Exporte. Sie erreichen auch Hintergrund-Agents, Shell-Exporte nicht zuverlässig. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` schaltet auch die automatischen Updates ab, plane dafür einen anderen Weg ein.

### Beispiel 3: Token mit apiKeyHelper aus einem Tresor holen

Wenn das Token abläuft oder aus einem Vault kommt. Das Skript `~/bin/get-gateway-key.sh`:

```bash
#!/bin/bash
vault kv get -field=api_key secret/llm-gateway/claude-code
```

Dann in `~/.claude/settings.json`:

```json
{
  "apiKeyHelper": "~/bin/get-gateway-key.sh",
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
    "CLAUDE_CODE_API_KEY_HELPER_TTL_MS": "900000"
  }
}
```

Claude Code schickt den Wert in beiden Headern, `Authorization` und `x-api-key`. Die Ausgabe hält es standardmäßig fünf Minuten vor, hier 15 Minuten. Ab v2.1.227 darf das Skript nur den Schlüssel ausgeben; ein Banner oder eine Logzeile lässt den Helfer scheitern. Ab v2.1.246 läuft er bei `401`, `403` oder abgelaufenem JWT neu.

### Beispiel 4: Zusätzliche Header und Modelle aus dem Gateway

Manche Gateways brauchen einen Routing- oder Mandanten-Header. Im JSON trennt `\n` die Header:

```json
{
  "env": {
    "ANTHROPIC_CUSTOM_HEADERS": "X-Org-Route: prod\nX-Tenant: example",
    "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY": "1"
  }
}
```

Mit der Modellabfrage fragt Claude Code beim Start `/v1/models` des Gateways ab und zeigt die Modelle zusätzlich in `/model`. Sie ist standardmäßig aus, weil ein Gateway mit gemeinsamem Schlüssel sonst jedem alle Modelle zeigt. Ob sie lief, zeigen die Zeilen `[gatewayDiscovery]` in `claude --debug`.

### Beispiel 5: Gateway vor Bedrock, Vertex AI oder Foundry

Nur, wenn dein Gateway-Team ausdrücklich das Format eines Cloud-Anbieters nennt. Für Bedrock:

```bash
export CLAUDE_CODE_USE_BEDROCK=1
export ANTHROPIC_BEDROCK_BASE_URL=https://llm-gateway.example.com/bedrock
export CLAUDE_CODE_SKIP_BEDROCK_AUTH=1
```

Für Vertex AI:

```bash
export CLAUDE_CODE_USE_VERTEX=1
export ANTHROPIC_VERTEX_BASE_URL=https://llm-gateway.example.com/vertex
export ANTHROPIC_VERTEX_PROJECT_ID=<deine-projekt-id>
export CLOUD_ML_REGION=eu
export CLAUDE_CODE_SKIP_VERTEX_AUTH=1
```

Für Foundry:

```bash
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_BASE_URL=https://llm-gateway.example.com/foundry
export ANTHROPIC_FOUNDRY_API_KEY=<dein-gateway-token>
```

Die `SKIP_*_AUTH`-Variablen sagen Claude Code, dass es nicht mit AWS- oder Google-Zugangsdaten signieren soll, weil das Gateway sie hält. Braucht das Gateway selbst ein Token, kommt bei Bedrock und Vertex AI `ANTHROPIC_AUTH_TOKEN` dazu. Bei Bedrock darf `AWS_BEARER_TOKEN_BEDROCK` dann nicht gesetzt sein.

### Beispiel 6: Team-Setup über Managed Settings

`managed-settings.json` (macOS `/Library/Application Support/ClaudeCode/`, Linux und WSL `/etc/claude-code/`, Windows `C:\Program Files\ClaudeCode\`):

```json
{
  "allowedProviders": ["customEndpoint"],
  "apiKeyHelper": "/usr/local/bin/get-gateway-key.sh",
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1"
  },
  "skipWebFetchPreflight": true,
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  }
}
```

Mit `allowedProviders: ["customEndpoint"]` (ab v2.1.285) und der festen `ANTHROPIC_BASE_URL` im Managed-`env` verweigert Claude Code jede Sitzung, die woanders hinzeigt, auch direkt zu Anthropic oder zu einem eigenen Proxy. Jede Person bekommt ein eigenes Gateway-Token, das der Helfer holt; so ist die Nutzung zuordenbar und beim Austritt sperrst du einen Zugang. `forceLoginMethod` und `forceLoginOrgUUID` dürfen in dieser Datei nicht stehen, sie vertragen sich nicht mit Gateway-Zugängen. `skipWebFetchPreflight` brauchst du, wenn dein Netz `api.anthropic.com` sperrt; dann prüft WebFetch URLs nicht mehr gegen die Sperrliste.

### Beispiel 7: Team-Setup über die Projekt-Settings

Ohne Managed Settings kann die `.claude/settings.json` im Repo nur die Adresse vorgeben, nie den Zugang:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://llm-gateway.example.com",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  }
}
```

Das Token setzt jede Person in `~/.claude/settings.json`, in `.claude/settings.local.json` (vorher in `.gitignore` eintragen) oder als Shell-Export. Projekt-Werte gelten erst nach dem Vertrauen des Ordners. Liegt nur die URL im Projekt und das Token fehlt in Shell und Nutzer-Settings, zeigt Claude Code beim ersten Start den Login-Bildschirm.

### Beispiel 8: VS Code über das Gateway

Die Extension prüft Zugänge vor dem Start nur aus ihrer eigenen Einstellung. In den VS-Code-Nutzereinstellungen ("Preferences: Open User Settings (JSON)"):

```json
{
  "claudeCode.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL", "value": "https://llm-gateway.example.com" },
    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "<dein-gateway-token>" }
  ]
}
```

Die Desktop-App liest das Gateway nicht aus `ANTHROPIC_BASE_URL`, sondern aus ihrer eigenen Third-Party-Inference-Konfiguration. Mehr zu den IDEs in [Claude Code in VS Code und JetBrains](./claude-code-vscode-jetbrains.md).

## Schritt für Schritt: Gateway im Team einführen

1. **Gateway betreiben** nach dessen eigener Doku und ihm den Zugang zum Upstream geben (Anthropic-Konto oder Cloud-Anbieter).
2. **Je Person ein Gateway-Token ausgeben**, damit Nutzung und Budgets zuordenbar sind.
3. **Kompatibilität prüfen.** Der [Gateway-Kompatibilitätsleitfaden](https://code.claude.com/docs/en/llm-gateway-protocol) sagt, welche Header und Felder das Gateway weitergeben muss.
4. **Testen** mit dem `curl` aus Beispiel 1 auf einem Rechner.
5. **Verteilen** über Managed Settings wie in Beispiel 6 und deine Secrets-Werkzeuge.
6. **Bei jeder Person prüfen.** `claude` startet ohne Login-Bildschirm, `/status` zeigt `Anthropic base URL` und eine Zeile `Auth token` oder `API key`.
7. **Netz absichern.** Bei gesperrtem Ausgangsverkehr `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` und `skipWebFetchPreflight` setzen.
8. **Repo prüfen.** `claude-team audit .` meldet Zugangsschlüssel in Claude-Dateien ([CC030](../regeln.md#cc030)) und gibt einen Hinweis, wenn die Telemetrie nicht abgeschaltet ist ([CC019](../regeln.md#cc019)).

## Welche Variablen Projekt-Settings ignorieren

`ANTHROPIC_BASE_URL` und `ANTHROPIC_CUSTOM_HEADERS` darf eine `.claude/settings.json` setzen; Routing- und Mandanten-Header zählen dabei als Header, die eine Freigabe brauchen. Aus Projekt- und lokalen Settings verwirft Claude Code unter anderem:

- Speicherorte: `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR`, `HOME`, `TMPDIR`, `TMP`, `TEMP`, `XDG_*`.
- Windows-Programmvariablen wie `SystemRoot`, `ComSpec`, `PATHEXT` und `PSModulePath`.
- OpenTelemetry-Variablen, die Telemetrie einschalten oder umleiten, ab v2.1.282. Wer Gateway-Kosten mit einem eigenen OTel-Collector auswertet, setzt `OTEL_EXPORTER_OTLP_ENDPOINT` deshalb in Managed oder Nutzer-Settings.
- `OTEL_LOG_RAW_API_BODIES`, `CLAUDE_CODE_PROCESS_WRAPPER`, die `CLAUDE_CODE_SYNC_*`-Variablen und die Plugin-Ordner.

Ein `apiKeyHelper` aus Projekt-Settings läuft erst nach dem Vertrauen des Ordners. Verworfene Werte zeigt `claude --debug`. Die vollständige Liste steht in der [Settings-Referenz](https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env).

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Falscher Header | `401` mit ungültigem Token | `ANTHROPIC_AUTH_TOKEN` und `ANTHROPIC_API_KEY` tauschen oder `apiKeyHelper` nutzen |
| Zwei Zugänge aktiv | Warnung mit zwei Quellen und `auth may not work as expected` | Variable entfernen oder `/logout` für den gespeicherten Login |
| API-Key ignoriert | `ANTHROPIC_API_KEY` gesetzt, aber ohne Wirkung | Einmalige Freigabe nötig; in `/config` "Use custom API key" einschalten |
| WAF blockt | `403 Forbidden` als HTML, das Gateway sieht keine Anfrage | `/v1/messages` von der Prüfung des Request-Body ausnehmen |
| Unbekannte Felder | `400` mit `context_management` oder `Extra inputs are not permitted` | `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` |
| Kleineres Kontextlimit | `400` mit eigener Limit-Meldung des Gateways | `/compact`; vorbeugend `CLAUDE_CODE_AUTO_COMPACT_WINDOW` setzen |
| Zertifikat | `SSL certificate verification failed`, obwohl `curl` geht | `NODE_EXTRA_CA_CERTS` auf das Firmen-CA-Bundle |
| Login trotz Gateway | Login-Bildschirm, obwohl `curl` klappt | Token in Shell oder Nutzer-Settings, nicht nur in Projekt-Settings |
| Managed Login-Zwang | `This machine's managed settings require a first-party login` | Admin entfernt `forceLoginMethod` und `forceLoginOrgUUID` |

## Häufige Fragen

### Kann ich Claude Code mit LiteLLM nutzen?

Die Doku nennt LiteLLM als Gateway, das Unternehmen zur Kostenverfolgung je Schlüssel einsetzen, und als Beispiel für die Modellabfrage. Anthropic prüft oder unterstützt das Projekt nicht. Technisch gilt wie für jedes Gateway: `ANTHROPIC_BASE_URL` auf LiteLLM, Token setzen, mit `curl` und `/status` prüfen.

### Kann ich über ein Gateway andere Modelle als Claude nutzen?

Anthropic unterstützt das nicht. Die Doku sagt ausdrücklich, dass Routing von Claude Code zu Nicht-Claude-Modellen über ein Gateway nicht unterstützt wird. Funktionen von Claude Code können dann fehlen oder brechen.

### Gilt mein Claude-Abo, wenn ich ein Gateway nutze?

Nicht, sobald ein Gateway-Zugang aktiv ist: Dann werden die Anfragen pro Token beim Inhaber des Zugangs abgerechnet, die Limits des Abos gelten nicht. Setzt du nur `ANTHROPIC_BASE_URL` ohne Zugang, bleibt der gespeicherte claude.ai-Login aktiv.

### Welche Funktionen fehlen mit Gateway?

Remote Control und Spracheingabe brauchen eine claude.ai-Identität und sind mit Gateway-Zugang aus. Remote Control ist auch aus, wenn `ANTHROPIC_BASE_URL` auf einen fremden Host zeigt. MCP Tool Search ist für fremde Hosts standardmäßig aus; leitet das Gateway `tool_reference` weiter, schaltest du sie mit `ENABLE_TOOL_SEARCH=true` ein.

### Wie verhindere ich, dass Entwickler das Gateway umgehen?

Mit `allowedProviders: ["customEndpoint"]` und fester `ANTHROPIC_BASE_URL` im `env`-Block der Managed Settings, wie in Beispiel 6. Claude Code verweigert dann jede Sitzung mit anderem Ziel. Cloud-Sitzungen und Claude in Slack gehören nicht zur Gateway-Strecke; schalte sie für diese Nutzer nicht frei.

### Wie behalte ich die Kosten im Blick?

Das Gateway kann Nutzung je Person erfassen und Budgets sowie Rate Limits durchsetzen. Mit eigenem Token je Person ist die Zuordnung eindeutig. Mehr dazu in [Claude Code Kosten](./claude-code-kosten.md).

## Weiterlesen

- [Claude Code und DSGVO](./claude-code-dsgvo.md)
- [Claude Code Bedrock](./claude-code-bedrock.md), [Claude Code Vertex AI](./claude-code-vertex-ai.md) und [Claude Code Azure Foundry](./claude-code-azure-foundry.md)
- [Claude Code Enterprise: Managed Settings](./claude-code-enterprise.md)
- [Claude Code Kosten](./claude-code-kosten.md)
- [Claude Code Sicherheit](./claude-code-sicherheit.md)
- Offizielle Doku: [LLM gateways](https://code.claude.com/docs/en/llm-gateway), [Connect to an LLM gateway](https://code.claude.com/docs/en/llm-gateway-connect), [Gateway compatibility](https://code.claude.com/docs/en/llm-gateway-protocol)
