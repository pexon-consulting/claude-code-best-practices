# Claude Code Bedrock: Claude Code über Amazon Bedrock in der EU betreiben

Claude Code für Amazon Bedrock in einer EU-Region konfigurierst du mit zwei Umgebungsvariablen: `CLAUDE_CODE_USE_BEDROCK=1` und `AWS_REGION=eu-central-1` (oder eine andere `eu-*`-Region), dazu gültige AWS-Zugangsdaten über Profil, SSO oder einen Bedrock-API-Key. In einer `eu-*`-Region wählt Claude Code bevorzugt die Cross-Region-Inference-Profile mit dem Präfix `eu.`, ab v2.1.224 kannst du das mit `ANTHROPIC_BEDROCK_REGION_PREFIX=eu` vorgeben. Laut Doku ist das eine Präferenz, keine Garantie: Fehlt ein `eu.`-Profil, kann Claude Code auf ein anderes ausweichen. Für Teams pinnst du außerdem die Modellversionen und verteilst alles zentral über Managed Settings.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

Diese Anleitung erklärt Technik und Einstellungen. Sie ist keine Rechtsberatung. Datenschutz, Verträge und Mitbestimmung klärst du mit Datenschutzbeauftragtem, Rechtsabteilung und Betriebsrat. Angaben zu Regionen und Datenverarbeitung der Anbieter können sich ändern; maßgeblich sind deren aktuelle Dokumentation und Verträge.

## Das Wichtigste in Kürze

- Einstieg ohne Handarbeit: beim Login "3rd-party platform" und dann "Amazon Bedrock" wählen oder `/setup-bedrock` aufrufen. Der Assistent schreibt in den `env`-Block von `~/.claude/settings.json`.
- Region: `AWS_REGION` vor `AWS_DEFAULT_REGION` vor der Region im AWS-Profil, sonst `us-east-1`. `/status` zeigt die aufgelöste Region.
- Telemetrie, Fehlerberichte und `/feedback` sind auf Bedrock standardmäßig aus. WebSearch und `/logout` gibt es auf Bedrock nicht.
- Für mehrere Nutzer Modelle pinnen (`ANTHROPIC_DEFAULT_OPUS_MODEL` usw.), sonst landen alle auf dem eingebauten Standard.
- Zugriff in IAM auf `bedrock:InvokeModel`, `InvokeModelWithResponseStream`, `ListInferenceProfiles` und `GetInferenceProfile` beschränken, am besten in einem eigenen AWS-Konto.

## Voraussetzungen

- Ein AWS-Konto mit Zugriff auf Amazon Bedrock.
- Einmal je AWS-Konto das Use-Case-Formular: In der [Bedrock-Konsole](https://console.aws.amazon.com/bedrock/) im Model catalog ein Anthropic-Modell wählen und das Formular ausfüllen. Der Zugriff gilt sofort. Mit AWS Organizations geht das einmal zentral über die API `PutUseCaseForModelAccess` (IAM-Recht `bedrock:PutUseCaseForModelAccess`).
- Die nötigen IAM-Rechte (siehe Beispiel 4).
- AWS CLI, nur wenn du sonst keinen Weg zu Zugangsdaten hast.

## Was geht an wen

Mit Bedrock laufen Prompts und Antworten über dein AWS-Konto. Einige Nebenverbindungen gibt es trotzdem. Stand laut [Data usage](https://code.claude.com/docs/en/data-usage):

| Daten | Empfänger | Standard auf Bedrock | Abschalten |
| --- | --- | --- | --- |
| Prompts, Code-Ausschnitte, Tool-Ergebnisse, Antworten | Amazon Bedrock in der gewählten Region (TLS 1.2+) | an, das ist der Betrieb | - |
| Gespeicherte Daten bei Bedrock | AWS, AES-256 mit AWS-Schlüsseln, eigene Schlüssel über AWS KMS möglich | laut AWS-Vertrag | - |
| Metriken (Latenz, Nutzung, ohne Code und Prompts) | Anthropic | aus | - |
| Fehlerberichte | Fehlerdienst eines Drittanbieters | aus | - |
| `/feedback` | lokal unter `~/.claude/feedback-bundles/` | geht nicht raus | - |
| Bewertung "How is Claude doing this session?" | Anthropic, nur die Bewertung | an | `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1` |
| Hostname vor jedem WebFetch | `api.anthropic.com`, nur der Hostname | an | `"skipWebFetchPreflight": true` |
| Gesprächsverläufe | lokal unter `~/.claude/projects/`, 30 Tage | an | `cleanupPeriodDays` |

Das Development Partner Program von Anthropic gibt es für Bedrock nicht. Welche Verträge, Auftragsverarbeitung und Speicherorte für die Daten deines Unternehmens bei AWS gelten, klärst du mit dem Datenschutzbeauftragten. Mehr dazu in [Claude Code und DSGVO](./claude-code-dsgvo.md).

## Beispiele für Claude Code mit Bedrock

### Beispiel 1: Minimal-Setup in der Shell für Frankfurt

Für einen ersten Test mit einem SSO-Profil:

```bash
aws sso login --profile=dein-profil
export AWS_PROFILE=dein-profil
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=eu-central-1
claude
```

In der Sitzung zeigt `/status` die Region. Ohne SSO gehen auch `aws configure`, `aws login` (ab AWS CLI 2.32.0, Sitzung bis 12 Stunden) oder Umgebungsvariablen mit Zugangsschlüssel. Eine EC2-Instanzrolle oder ECS-Task-Rolle nutzt Claude Code automatisch.

### Beispiel 2: Dauerhaft in den Nutzer-Settings mit automatischem SSO-Refresh

In `~/.claude/settings.json`:

```json
{
  "awsAuthRefresh": "aws sso login --profile dein-profil",
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_PROFILE": "dein-profil",
    "AWS_REGION": "eu-central-1",
    "ANTHROPIC_BEDROCK_REGION_PREFIX": "eu"
  }
}
```

`awsAuthRefresh` läuft nur, wenn die Zugangsdaten abgelaufen sind. Vorher prüft Claude Code das mit einem STS-Aufruf `GetCallerIdentity`. Öffnet sich hinter einem Firmen-Proxy ein Browser-Tab nach dem anderen, entferne `awsAuthRefresh` und melde dich vor dem Start selbst mit `aws sso login` an.

### Beispiel 3: Modelle für alle pinnen

Ohne Pin löst der Alias `opus` auf Bedrock zu Opus 5.5 auf, `sonnet` zu Sonnet 4.5. Mit `ANTHROPIC_BEDROCK_REGION_PREFIX=eu` wird aus dem Standard `eu.anthropic.claude-opus-5-5`. Welche Profile dein Konto in der EU hat, zeigt:

```bash
aws bedrock list-inference-profiles --region eu-central-1
```

Die gefundenen IDs trägst du ein:

```json
{
  "env": {
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "eu.anthropic.claude-opus-5-5",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "<sonnet-profil-id-aus-der-liste>",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "<haiku-profil-id-aus-der-liste>"
  }
}
```

Hintergrundaufgaben wie Sitzungstitel laufen auf Bedrock standardmäßig mit dem Sonnet-Standardmodell, weil Haiku nicht in jedem Konto freigeschaltet ist. Erst mit `ANTHROPIC_DEFAULT_HAIKU_MODEL` nutzt Claude Code dafür Haiku. `ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION` wirkt auf Bedrock nur, wenn diese Variable gesetzt ist.

### Beispiel 4: IAM-Policy für Claude Code

Die Policy aus der [Bedrock-Doku](https://code.claude.com/docs/en/amazon-bedrock#iam-configuration):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowModelAndInferenceProfileAccess",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles",
        "bedrock:GetInferenceProfile"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*",
        "arn:aws:bedrock:*:*:application-inference-profile/*",
        "arn:aws:bedrock:*:*:foundation-model/*"
      ]
    },
    {
      "Sid": "AllowMarketplaceSubscription",
      "Effect": "Allow",
      "Action": [
        "aws-marketplace:ViewSubscriptions",
        "aws-marketplace:Subscribe"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:CalledViaLast": "bedrock.amazonaws.com"
        }
      }
    }
  ]
}
```

Die Policy erlaubt alle Regionen. Soll die Verarbeitung belastbar in der EU bleiben, reicht das Präfix allein nicht. Dann begrenzt du `Resource` auf EU-Regionen und `eu.`-Profile; ein `global.`- oder `us.`-Profil scheitert so an IAM statt still zu laufen:

```json
"Resource": [
  "arn:aws:bedrock:eu-*:<konto-id>:inference-profile/eu.*",
  "arn:aws:bedrock:eu-*:<konto-id>:application-inference-profile/*",
  "arn:aws:bedrock:eu-*::foundation-model/*"
]
```

Zusätzlich pinnst du die Modelle auf `eu.`-IDs (Beispiel 3) und beschränkst `availableModels` auf diese IDs. Die Doku empfiehlt ein eigenes AWS-Konto für Claude Code, damit Kosten und Zugriffe getrennt bleiben.

### Beispiel 5: Team-Setup über Managed Settings

Für eine Flotte legst du die Datei `managed-settings.json` an (macOS `/Library/Application Support/ClaudeCode/`, Linux und WSL `/etc/claude-code/`, Windows `C:\Program Files\ClaudeCode\`):

```json
{
  "allowedProviders": ["bedrock"],
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "eu-central-1",
    "ANTHROPIC_BEDROCK_REGION_PREFIX": "eu",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "eu.anthropic.claude-opus-5-5",
    "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1"
  },
  "skipWebFetchPreflight": true,
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  }
}
```

`allowedProviders` (ab v2.1.285) lässt nur Bedrock zu; eine Sitzung mit einem anderen Anbieter verweigert Claude Code beim Start. `skipWebFetchPreflight` nimmt die Hostname-Prüfung bei `api.anthropic.com` heraus, dann prüft WebFetch URLs aber nicht mehr gegen die Sperrliste. Wer `api.anthropic.com` ohnehin blockt, braucht den Schalter, sonst scheitert WebFetch. Die Zugangsdaten kommen pro Person über SSO oder die Instanzrolle, nicht aus dieser Datei.

### Beispiel 6: Team-Setup über die Projekt-Settings

Ohne Managed Settings geht dasselbe im Repo, in `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "eu-central-1",
    "ANTHROPIC_BEDROCK_REGION_PREFIX": "eu"
  }
}
```

Projekt-Werte im `env`-Block gelten erst, wenn die Person dem Ordner vertraut hat (im Modus `-p` gleich beim Start). Keine Profilnamen, Schlüssel oder Konto-IDs ins Repo.

### Beispiel 7: Guardrails und Service-Tier

Ein [Bedrock Guardrail](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) filtert Inhalte. Du gibst ihn als Header mit; im JSON trennt `\n` die Header:

```json
{
  "env": {
    "ANTHROPIC_CUSTOM_HEADERS": "X-Amzn-Bedrock-GuardrailIdentifier: <deine-guardrail-id>\nX-Amzn-Bedrock-GuardrailVersion: 1",
    "ANTHROPIC_BEDROCK_SERVICE_TIER": "default"
  }
}
```

`ANTHROPIC_BEDROCK_SERVICE_TIER` kennt `default`, `flex` und `priority` und tauscht Kosten gegen Latenz. Die Preise nennt AWS.

### Beispiel 8: Zugang prüfen

Wenn Claude Code nicht antwortet oder Modelle fehlen:

```bash
aws sts get-caller-identity
aws bedrock list-inference-profiles --region eu-central-1
claude --debug
```

Die erste Zeile zeigt, mit welcher Identität du arbeitest, die zweite, welche Profile in der Region verfügbar sind.

## Schritt für Schritt: Bedrock im Team einführen

1. **Eigenes AWS-Konto anlegen** oder ein vorhandenes festlegen, Bedrock in der EU-Region aktivieren.
2. **Use-Case-Formular** einmal im Konto ausfüllen.
3. **IAM-Rolle** mit der Policy aus Beispiel 4 anlegen und per SSO den Entwicklern zuweisen.
4. **Verfügbare Profile prüfen** mit `aws bedrock list-inference-profiles --region eu-central-1` und die Modell-IDs festlegen.
5. **Managed Settings verteilen** wie in Beispiel 5, über MDM, Intune oder Server-managed Settings.
6. **Bei jedem Entwickler anmelden**: `aws sso login --profile=...`, dann `claude`.
7. **Prüfen**: `/status` zeigt Region und `Setting sources` mit `Enterprise managed settings (file)`.
8. **Projekt absichern** mit `claude-team einrichten` und `claude-team audit`. Die [Vorlage](../../src/claude_team/vorlage/.claude/settings.json) sperrt das Lesen von `~/.aws`, damit Claude keine Zugangsdaten anfasst ([CC014](../regeln.md#cc014)).

## Welche Variablen Projekt-Settings ignorieren

Die Bedrock-Variablen wie `CLAUDE_CODE_USE_BEDROCK`, `AWS_REGION` oder `ANTHROPIC_BEDROCK_REGION_PREFIX` darf eine `.claude/settings.json` setzen, sie greifen nach dem Vertrauen des Ordners. Claude Code verwirft aber aus Projekt- und lokalen Settings (`.claude/settings.local.json`) unter anderem:

- Speicherorte: `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_TMPDIR`, `HOME`, `TMPDIR`, `TMP`, `TEMP` und `XDG_*`.
- Windows-Programmvariablen wie `SystemRoot`, `ComSpec` und `PSModulePath`.
- OpenTelemetry-Variablen, die Telemetrie einschalten oder umleiten, etwa `CLAUDE_CODE_ENABLE_TELEMETRY`, `OTEL_EXPORTER_OTLP_ENDPOINT` und `OTEL_LOG_USER_PROMPTS` (ab v2.1.282). Werte, die etwas abschalten, gelten weiter.
- `OTEL_LOG_RAW_API_BODIES`, `CLAUDE_CODE_PROCESS_WRAPPER`, `CLAUDE_CODE_SYNC_SKILLS`, `CLAUDE_CODE_SYNC_PLUGINS` und die Plugin-Ordner.

Welche Werte verworfen wurden, zeigt `claude --debug`. Die vollständige Liste steht in der [Settings-Referenz](https://code.claude.com/docs/en/settings-reference#variables-claude-code-ignores-in-env).

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Falsche Region | Modell nicht gefunden, Anfragen gehen nach `us-east-1` | `AWS_REGION` setzen, mit `/status` prüfen |
| Modell ohne Profil | "on-demand throughput isn't supported" | Modell als Inference-Profile-ID angeben, nicht als Modell-ID |
| Präfix ohne Profil | 400-Fehler nach `ANTHROPIC_BEDROCK_REGION_PREFIX` | Prüfen, ob das Konto Profile mit diesem Präfix hat |
| SSO-Schleife | Browser-Tabs öffnen sich immer wieder | `awsAuthRefresh` entfernen, vorher `aws sso login` |
| TLS-Proxy | `unable to get local issuer certificate` | Firmen-Root-Zertifikat im OS-Store oder in `NODE_EXTRA_CA_CERTS` |
| Hängende Anmeldung | `AWS default-chain credential resolve timed out` | Der Credential-Helfer wartet auf Eingabe; Zeitlimit mit `CLAUDE_CODE_AWS_CHAIN_RESOLVE_TIMEOUT_MS` anpassen oder Helfer reparieren |
| Modell gewechselt | `Switched to <fallback> because <model> is not available` | Modell im Konto freischalten oder fest pinnen |
| WebSearch fehlt | Claude sucht nicht im Web | Auf Bedrock nicht verfügbar; WebFetch für einzelne URLs nutzen |

## Häufige Fragen

### Bleiben meine Daten mit Bedrock in der EU?

Nicht automatisch. Prompts und Antworten gehen an Bedrock über das Inference-Profil, das Claude Code wählt. Das Präfix `eu.` ist dabei nur eine Präferenz; erst gepinnte `eu.`-Modell-IDs und eine IAM-Policy, die nur EU-Regionen und `eu.`-Profile erlaubt (Beispiel 4), machen daraus eine feste Grenze. Wohin Bedrock ein Cross-Region-Profil innerhalb von AWS routet, beschreibt die AWS-Doku zu Inference-Profilen. Kleine Nebenverbindungen wie die Hostname-Prüfung von WebFetch gehen an `api.anthropic.com`, siehe Tabelle oben. Ob das für dein Unternehmen reicht, klärst du mit dem Datenschutzbeauftragten.

### Brauche ich ein Anthropic-Konto für Claude Code auf Bedrock?

Nein. Claude Code nutzt die AWS-Zugangsdaten, abgerechnet wird über AWS. `/logout` gibt es deshalb nicht.

### Welche Modelle nutzt Claude Code auf Bedrock ohne Pin?

Der Alias `opus` und das Hauptmodell lösen zu Opus 5.5 auf, `sonnet` zu Sonnet 4.5. Ist der Standard im Konto nicht freigeschaltet, weicht Claude Code für die Sitzung auf eine ältere Version aus. Für Teams pinnst du die Modelle, damit alle dasselbe nutzen.

### Kann ich Bedrock über ein Firmen-Gateway nutzen?

Ja, mit `ANTHROPIC_BEDROCK_BASE_URL` auf das Gateway und `CLAUDE_CODE_SKIP_BEDROCK_AUTH=1`, wenn das Gateway die AWS-Anmeldung übernimmt. Siehe [Claude Code LLM-Gateway](./claude-code-llm-gateway.md).

### Unterstützt Claude Code die Converse API?

Nein, Claude Code nutzt die Invoke API von Bedrock. Daneben gibt es den Mantle-Endpunkt mit `CLAUDE_CODE_USE_MANTLE` und den IAM-Rechten `bedrock-mantle:CreateInference` und `bedrock-mantle:CountTokens`.

### Was kostet Claude Code auf Bedrock?

Du zahlst die Bedrock-Preise je Token an AWS, Anthropic nennt dafür keine eigenen Preise. Opus kostet mehr als Sonnet. Zur Steuerung im Team siehe [Claude Code Kosten](./claude-code-kosten.md).

## Weiterlesen

- [Claude Code und DSGVO](./claude-code-dsgvo.md)
- [Claude Code LLM-Gateway](./claude-code-llm-gateway.md)
- [Claude Code Vertex AI](./claude-code-vertex-ai.md) und [Claude Code mit Microsoft Foundry (Azure)](./claude-code-azure-foundry.md)
- [Claude Code Enterprise: Managed Settings](./claude-code-enterprise.md)
- [Claude Code settings.json](./claude-code-settings-json.md)
- Offizielle Doku: [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock), [Data usage](https://code.claude.com/docs/en/data-usage), [Settings reference](https://code.claude.com/docs/en/settings-reference)
