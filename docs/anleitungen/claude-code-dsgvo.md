# Claude Code DSGVO: datenschutzkonform im Unternehmen einsetzen

Für einen datenschutzkonformen Einsatz von Claude Code im Unternehmen braucht es mindestens drei Dinge: einen kommerziellen Vertrag (Team, Enterprise, API oder einen Cloud-Anbieter wie Amazon Bedrock) mit geklärtem Auftragsverarbeitungsvertrag und Drittlandtransfer, eine bewusst gewählte Region und technische Einstellungen, die Telemetrie, Feedback-Uploads und personenbezogene Daten im Prompt begrenzen. Ob das im Einzelfall reicht, bewertet der Datenschutzbeauftragte. Alles, was Claude Code liest oder du eingibst, geht als Prompt an das Modell; deshalb entscheidet die Betriebsvariante darüber, wer die Daten verarbeitet und wie lange sie gespeichert werden.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

Diese Anleitung ist keine Rechtsberatung. Sie fasst zusammen, was die offizielle Doku von Anthropic zu Datenflüssen und Aufbewahrung sagt, und zeigt die Einstellungen, mit denen du die Menge der Daten technisch begrenzt. Die rechtliche Bewertung treffen Datenschutzbeauftragter und Rechtsabteilung.

## Das Wichtigste in Kürze

- Claude Code sendet alle Prompts und Modellausgaben an den Modellanbieter, dazu gehören auch die Dateiinhalte, die der Agent liest.
- Bei kommerziellen Konten (Team, Enterprise, API, Bedrock, Vertex AI, Foundry) trainiert Anthropic laut Doku keine Modelle mit deinen Daten und speichert standardmäßig 30 Tage.
- Zero Data Retention gibt es nur für qualifizierte Konten auf Claude for Enterprise, nach Freischaltung durch Anthropic, und nicht für jede Funktion.
- Telemetrie, Fehlerberichte, `/feedback` und Umfragen schaltest du zentral über den `env`-Block der Managed Settings ab; `/feedback` speichert Transkripte 5 Jahre.
- Lokale Transkripte liegen im Klartext unter `~/.claude/projects/` und werden nach `cleanupPeriodDays` (Standard 30 Tage) gelöscht.
- Hooks mit deutschen Prüfziffern erkennen IBAN, Steuer-ID und Sozialversicherungsnummer in Prompts, Shell-Befehlen und neu geschriebenem Code. Inhalte, die Claude Code aus Dateien liest, prüfen sie nicht, und Namen oder Anschriften erkennen sie nicht; Datenordner sperrst du deshalb zusätzlich mit deny-Regeln und arbeitest mit Testdaten ohne Echtdaten.

## Welche Daten sendet Claude Code an Anthropic?

Claude Code läuft lokal, schickt aber für jede Antwort den Kontext an das Modell. Laut [Data usage](https://code.claude.com/docs/en/data-usage) gehen diese Datenarten nach außen:

| Datenart | Inhalt | Ziel | Abschaltbar |
| --- | --- | --- | --- |
| Modellanfragen | alle Prompts und Modellausgaben, inklusive gelesener Dateien, verschlüsselt mit TLS 1.2+ | Modellanbieter (Anthropic, Bedrock, Vertex AI, Foundry, Gateway) | nein, das ist der Kern des Werkzeugs |
| Metriken | Latenz, Zuverlässigkeit, Nutzungsmuster; laut Doku nie Code, Prompts oder Dateipfade | Anthropic und Logging-Dienstleister | `DISABLE_TELEMETRY` |
| Fehlerberichte | Fehlermeldungen und Stacktraces von Claude Code selbst, Secrets, Pfade und E-Mails vorher redigiert | Fehler-Tracking-Dienstleister | `DISABLE_ERROR_REPORTING` |
| `/feedback`, `/bug`, `/share` | Konversationsverlauf inklusive Code, Aufbewahrung 5 Jahre | Anthropic (Google Cloud Storage), optional GitHub-Issue | `DISABLE_FEEDBACK_COMMAND` |
| Sitzungsumfrage | nur die Bewertung; Transkript nur nach ausdrücklichem "Yes", Aufbewahrung bis 6 Monate | Anthropic | `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY` |
| WebFetch-Domain-Check | nur der Hostname einer abgerufenen URL | `api.anthropic.com` | `"skipWebFetchPreflight": true` |

Fehlerberichte sind laut Doku nur aktiv, wenn alle Bedingungen zutreffen: Anmeldung mit Pro oder Max, Claude Code ab v2.1.198, direkte Claude API und keine Zero-Data-Retention- oder HIPAA-Vereinbarung. Bei Amazon Bedrock, Google Vertex AI, Microsoft Foundry und Claude Platform on AWS sind Metriken, Fehlerberichte und `/feedback`-Upload standardmäßig aus. Sitzungsumfrage und WebFetch-Domain-Check laufen dort trotzdem.

Bei Bedrock, Vertex AI und Foundry schreibt `/feedback` den Bericht statt eines Uploads in ein lokales Archiv unter `~/.claude/feedback-bundles/`. Nichts verlässt den Rechner, bis jemand die Datei weiterleitet.

## Aufbewahrung und Training je Kontotyp

Die Aufbewahrung hängt vom Vertrag ab, nicht vom Werkzeug. Laut [Data usage](https://code.claude.com/docs/en/data-usage) gilt:

| Kontotyp | Training mit deinen Daten | Aufbewahrung bei Anthropic | Vertragsgrundlage |
| --- | --- | --- | --- |
| Free, Pro, Max mit Trainings-Einstellung an | ja | 5 Jahre | Consumer Terms |
| Free, Pro, Max mit Trainings-Einstellung aus | nein | 30 Tage | Consumer Terms |
| Team, Enterprise, API (Commercial) | nein, außer Opt-in wie Development Partner Program | Standard 30 Tage | Commercial Terms |
| Bedrock, Vertex AI, Foundry | nein (gilt als 3rd-Party-Plattform) | Richtlinien des Cloud-Anbieters | Vertrag mit dem Cloud-Anbieter |
| Claude for Enterprise mit Zero Data Retention | nein | keine Speicherung nach der Antwort, Ausnahmen siehe unten | Commercial Terms plus ZDR-Freischaltung |

Für den Firmeneinsatz kommen nur kommerzielle Konten in Frage. Private Pro- oder Max-Abos laufen unter den Consumer Terms. Das Development Partner Program ist laut Doku nur für die direkte Anthropic-API verfügbar, nicht für Bedrock oder Vertex AI, und muss von einem Organisations-Admin ausdrücklich aktiviert werden. Prüfe in der Admin-Konsole, dass es aus ist.

## Zero Data Retention: was es abdeckt und was nicht

Zero Data Retention (ZDR) bedeutet laut [Zero data retention](https://code.claude.com/docs/en/zero-data-retention), dass Prompts und Antworten in Claude-Code-Sitzungen in Echtzeit verarbeitet und nach der Antwort nicht gespeichert werden, außer wenn Gesetz oder Missbrauchsbekämpfung es verlangen.

Voraussetzungen und Grenzen:

- ZDR gibt es für qualifizierte Konten auf Claude for Enterprise. Es ist nicht im Standard-Enterprise-Plan enthalten und lässt sich nicht in den Admin-Einstellungen einschalten; das Account-Team von Anthropic schaltet es je Organisation frei.
- ZDR gilt nur auf Anthropics direkter Plattform. Für Bedrock, Vertex AI und Foundry gelten deren Aufbewahrungsrichtlinien.
- Nicht abgedeckt sind Chat auf claude.ai, Cowork, Claude Code Analytics (Metadaten wie Konto-E-Mail und Nutzungsstatistik), Nutzer- und Seat-Verwaltung sowie Daten, die MCP-Server und andere Drittintegrationen verarbeiten.
- Unter ZDR sind Cloud-Sessions, Claude Tag, Artifacts, `/feedback`, `/bug`, `/share` und Remote Control serverseitig gesperrt.
- Bei einem Verstoß gegen die Nutzungsrichtlinie kann Anthropic Ein- und Ausgaben bis zu 2 Jahre und die Ergebnisse der Sicherheitsklassifizierung bis zu 7 Jahre aufbewahren ([Privacy Center](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data), Stand 01.07.2026).
- Fable 5.1 und Fable 5 sind "Covered Models", die standardmäßig Datenaufbewahrung erfordern; ob eine ZDR-Organisation sie nutzen kann, regeln die Covered-Models-Richtlinien.
- ZDR wirkt nur für Sitzungen, die sich in die ZDR-Organisation einloggen. Ein privates Konto oder ein API-Schlüssel einer anderen Organisation ist nicht abgedeckt. Dagegen helfen `forceLoginMethod` und `forceLoginOrgUUID` in den Managed Settings.

```json
{
  "forceLoginMethod": "claudeai",
  "forceLoginOrgUUID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

## Welche Betriebsvariante passt für die DSGVO?

Die Betriebsvariante bestimmt Vertragspartner, Region und Aufbewahrung. Die Tabelle zeigt, was die Doku je Variante belegt, und was du mit Datenschutz und Einkauf klären musst. Ob eine Variante für dein Unternehmen zulässig ist, entscheidet nicht diese Tabelle, sondern deine Prüfung.

| Variante | Vertragspartner | Region laut Doku | Aufbewahrung | Was zu klären ist |
| --- | --- | --- | --- | --- |
| Anthropic direkt: Team, Enterprise oder API (Console) | Anthropic | in der Claude-Code-Doku keine EU-Region dokumentiert; die Kostendoku nennt nur einen Aufpreis für US-Inferenz | 30 Tage, mit ZDR keine | Auftragsverarbeitungsvertrag (DPA) nach Art. 28 DSGVO, Drittlandtransfer, TOM aus dem Trust Center, Verschlüsselung AES-256 at rest |
| Claude for Enterprise mit ZDR | Anthropic | wie oben | keine Speicherung nach der Antwort, Ausnahmen siehe oben | wie oben, plus Nachweis der ZDR-Freischaltung je Organisation und `forceLoginOrgUUID` |
| Amazon Bedrock, EU-Region | AWS (dein AWS-Vertrag) | z.B. `eu-central-1`, Cross-Region-Präfix `eu.` | Richtlinien von AWS | AWS-Auftragsverarbeitung, welche EU-Regionen die Cross-Region-Inferenz nutzt, Schlüssel per AWS KMS |
| Google Vertex AI, EU | Google Cloud (dein GCP-Vertrag) | Multi-Region `eu` oder Region wie `europe-west1` | Richtlinien von Google Cloud | Google-Auftragsverarbeitung, Modellverfügbarkeit je Region, CMEK |
| Microsoft Foundry | Microsoft (dein Azure-Vertrag) | hängt von Azure-Region und Hosting-Option ab | "Hosted on Azure": Prompts bleiben in Azure; "Hosted on Anthropic": Verarbeitung bei Anthropic | welche Hosting-Option dein Deployment nutzt; EU-Residenz im Detail nicht in der Claude-Code-Doku belegt |
| Eigenes LLM-Gateway (z.B. LiteLLM) vor einem der obigen | Gateway-Betreiber plus Backend-Anbieter | wie das Backend | Gateway-Logs zusätzlich | Was das Gateway protokolliert, wer Zugriff hat, Löschfristen, Vertrag mit dem Backend |

Belegte Details aus der Doku:

- Bei "Hosted on Azure" bleiben laut [Data usage](https://code.claude.com/docs/en/data-usage) Prompts und Completions in Azure; nur Nutzungsmetadaten und von Anthropics Sicherheitssystemen markierte Inhalte gehen an Anthropic.
- Verschlüsselung at rest: Anthropic API AES-256; Bedrock AES-256 mit AWS-Schlüsseln, eigene Schlüssel über AWS KMS; Vertex AI mit Google-Schlüsseln, CMEK möglich.
- Dein bestehender kommerzieller Vertrag gilt laut [Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance) auch für Claude Code, egal ob direkt oder über Bedrock oder Vertex AI.
- Bei Bedrock ist das WebSearch-Tool nicht verfügbar. Das senkt eine Abflussquelle, ersetzt aber keine Regel für WebFetch.

Amazon Bedrock in der EU, Variablen laut [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock):

```bash
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=eu-central-1
export ANTHROPIC_BEDROCK_REGION_PREFIX=eu
```

Google Vertex AI in der EU, laut [Google Vertex AI](https://code.claude.com/docs/en/google-vertex-ai):

```bash
export CLAUDE_CODE_USE_VERTEX=1
export CLOUD_ML_REGION=eu
export ANTHROPIC_VERTEX_PROJECT_ID=<gcp-projekt-id>
```

`ANTHROPIC_BEDROCK_REGION_PREFIX` gibt es ab v2.1.224. Modell-IDs pinnst du für Bedrock und Vertex AI über `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` und `ANTHROPIC_DEFAULT_HAIKU_MODEL`; das genaue ID-Format prüfst du in deiner eigenen Konsole. Details stehen in [Claude Code Bedrock](./claude-code-bedrock.md) und [Claude Code Vertex AI](./claude-code-vertex-ai.md).

Damit niemand am Firmenvertrag vorbei einen anderen Anbieter nutzt, beschränkst du ab v2.1.285 die zulässigen Anbieter in den Managed Settings:

```json
{
  "allowedProviders": ["bedrock"]
}
```

## Telemetrie abschalten, ohne in Fallen zu laufen

Telemetrie, Fehlerberichte und Feedback steuerst du über Umgebungsvariablen. Im Team gehören sie in den `env`-Block der Managed Settings, damit sie nicht von der Shell jedes Einzelnen abhängen.

| Variable | Wirkung | Falle |
| --- | --- | --- |
| `DISABLE_TELEMETRY=1` | Metriken aus, auch Feature-Flag-Abruf aus | auch `0` oder `false` schaltet ab; zum Einschalten Variable entfernen |
| `DISABLE_ERROR_REPORTING=1` | Fehlerberichte aus | gleiche `0`/`false`-Falle |
| `DISABLE_FEEDBACK_COMMAND=1` | `/feedback`, `/bug`, `/share` und von Claude entworfenes Feedback aus | keine |
| `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1` | Sitzungsumfragen aus | keine |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` | alles oben plus Auto-Updates, Release Notes, Verfügbarkeitschecks | schaltet auch Auto-Updates ab; `0`/`false` schaltet ebenfalls ab |
| `"skipWebFetchPreflight": true` (Setting, keine Variable) | WebFetch-Domain-Check aus | WebFetch nutzt dann keine Sperrliste mehr; mit `WebFetch`-Regeln kombinieren |

Zwei Punkte entscheiden über die Wahl:

1. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` schaltet auch Auto-Updates ab. Wer diese Variable setzt, braucht einen eigenen Update-Weg über Softwareverteilung oder `claude update`, sonst veralten die Clients. Ohne Auto-Updates helfen `requiredMinimumVersion` in den Managed Settings, damit veraltete Versionen nicht starten.
2. `DISABLE_TELEMETRY` und `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` schalten den Feature-Flag-Abruf ab. Damit kann Remote Control nicht mehr verfügbar sein, und das Analytics-Dashboard deiner Organisation bekommt für diese Entwickler keine Nutzungsdaten mehr.

Weder `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` noch die anderen Variablen erfassen den WebFetch-Domain-Check und die automatische Installation des offiziellen Marketplace. Dafür gibt es `skipWebFetchPreflight` und `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL`.

## Lokale Daten: Transkripte und Aufbewahrungsfrist

Claude Code speichert Sitzungstranskripte im Klartext unter `~/.claude/projects/`, standardmäßig 30 Tage, damit `/resume` funktioniert. Diese Transkripte enthalten alles, was im Kontext war, also auch gelesene Dateien und eingefügte Texte. Für den Datenschutz sind sie lokale Kopien personenbezogener Daten, wenn solche Daten in der Sitzung vorkamen.

- `cleanupPeriodDays` setzt die Frist in Tagen. Der kleinste Wert ist `1`; `0` ist ungültig.
- `CLAUDE_CODE_SKIP_PROMPT_HISTORY=1` verhindert, dass Prompt-Verlauf und Transkripte überhaupt auf die Platte geschrieben werden. Solche Sitzungen tauchen nicht in `--resume` oder `--continue` auf. Sinnvoll für Skripte.
- Transkripte von Sitzungen aus Claude Desktop oder Cowork sind standardmäßig von der Frist ausgenommen; dafür gibt es `desktopSessionCleanupPeriodDays` (ab v2.1.248).

```json
{
  "cleanupPeriodDays": 14
}
```

## Personenbezogene Daten technisch aus dem Prompt halten

Einstellungen begrenzen, wohin Daten gehen. Sie verhindern nicht, dass jemand eine Kundenliste in den Prompt kopiert oder der Agent eine Datei mit Personaldaten liest. Dafür gibt es drei technische Schichten:

1. **deny-Regeln in settings.json** sperren Dateien mit Secrets und bekannten Datenablagen für die Datei-Tools. Sie greifen auch für erkannte Bash-Befehle wie `cat`, aber nicht für beliebige Skripte.
2. **Der Hook `pii_schutz.py`** aus der [Vorlage](../../src/claude_team/vorlage/.claude/hooks/pii_schutz.py) läuft bei `UserPromptSubmit` und vor `Edit`, `Write` und `Bash`, nicht vor `Read` oder `Grep`. Was Claude aus Dateien liest, prüft er also nicht. Er blockt IBAN (Mod 97), Steuer-ID (ISO 7064 Mod 11,10 plus Ziffernregel), Sozialversicherungsnummer (Prüfziffer der DRV) und Kreditkartennummern (Luhn), aber nur mit gültiger Prüfziffer. Beim Prompt blockt er, bevor der Text ans Modell geht. USt-IdNr. und viele E-Mail-Adressen oder Telefonnummern (ab 5) führen zu einer Rückfrage. Verbreitete Beispielwerte wie die Beispiel-IBAN `DE89 3704 0044 0532 0130 00` bleiben erlaubt. Namen, Anschriften und Gesundheitsdaten erkennt der Hook nicht. Grenzen im Detail: [Was die Hooks nicht abdecken](./claude-code-hooks.md#was-die-hooks-nicht-abdecken).
3. **Das Profil streng** von `claude-team einrichten` sperrt zusätzlich WebFetch, WebSearch, `curl`, `wget`, `nc`, `scp` und `ssh` und schaltet Feedback und Umfragen ab.

Konfiguriert wird der Hook in `.claude/schutz.json`:

```json
{
  "pii": {
    "modus": "deny",
    "kontakte_ab": 5,
    "pfade_ausnehmen": ["tests/fixtures/**"]
  }
}
```

Ein Hook, der selbst abstürzt, lässt die Aktion durch (fail open), damit ein kaputter Hook niemanden aussperrt. Deshalb bleiben die deny-Regeln in settings.json die erste Schutzschicht. Für Repos und CI gibt es zusätzlich `claude-team scannen`, das Dateien vor dem Commit auf Secrets und deutsche personenbezogene Daten prüft.

## Hinweis für Berufsgeheimnisträger (§ 203 StGB)

Kanzleien, Steuerberatung, Arztpraxen, Versicherungen und andere Berufsgeheimnisträger haben zusätzliche Pflichten, wenn Dienstleister Zugang zu geschützten Geheimnissen bekommen. Diese Anleitung bewertet das nicht. Kläre mit Rechtsabteilung und Datenschutzbeauftragtem mindestens:

- Ob der Modellanbieter (Anthropic, AWS, Google, Microsoft) als mitwirkende Person gilt und welche vertraglichen Verschwiegenheitsregeln dafür nötig sind.
- Ob eine Variante mit Zero Data Retention oder eine EU-Variante über einen Cloud-Anbieter für deinen Fall erforderlich ist.
- Ob Mandanten- oder Patientendaten technisch ausgeschlossen werden können, etwa durch Arbeit nur an Code ohne Echtdaten, deny-Regeln für Datenordner und den PII-Hook.
- Ob Testdaten anonymisiert oder synthetisch sein müssen.

## Beispiele für datenschutzfreundliche Einstellungen

### Beispiel 1: Managed Settings für Datenschutz-Grundschutz

```json
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1",
    "DISABLE_FEEDBACK_COMMAND": "1",
    "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY": "1"
  },
  "cleanupPeriodDays": 14,
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  }
}
```

Die Basis für jedes Unternehmen; die vollständige Vorlage liegt unter [vorlagen/managed-settings.json](../../vorlagen/managed-settings.json).

### Beispiel 2: Personaldaten-Ordner für den Agenten sperren

```json
{
  "permissions": {
    "deny": [
      "Read(**/personal/**)",
      "Read(**/*.csv)",
      "Read(**/exports/**)",
      "Edit(**/personal/**)"
    ]
  }
}
```

Für Repos, in denen Exporte oder Testdaten mit echten Personen liegen könnten.

### Beispiel 3: Ohne Anthropic-Verbindung außer dem Modell (Bedrock)

```json
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "eu-central-1",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  },
  "skipWebFetchPreflight": true,
  "permissions": {
    "deny": ["WebFetch", "WebSearch"]
  }
}
```

Wenn die Netzwerkrichtlinie keinen Verkehr zu `api.anthropic.com` erlaubt; Updates kommen dann über die Softwareverteilung.

### Beispiel 4: Transkripte in Skripten gar nicht speichern

```bash
CLAUDE_CODE_SKIP_PROMPT_HISTORY=1 claude -p "Fasse die Änderungen in CHANGELOG.md zusammen" --allowedTools "Read"
```

Für automatisierte Läufe, deren Verlauf niemand fortsetzen muss.

### Beispiel 5: Team-Basis mit PII-Hook in ein Repo legen

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team einrichten . --profil streng --dry-run
```

Zeigt, welche Dateien angelegt würden; ohne `--dry-run` legt der Befehl CLAUDE.md, settings.json, Hooks und `.claude/schutz.json` an und überschreibt nichts.

### Beispiel 6: Repo vor dem Commit auf personenbezogene Daten prüfen

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team scannen src/ --kontakte-ab 5
```

Für pre-commit und CI; Exit 1 bei einem Treffer.

## Schritt für Schritt

1. Vertragsweg festlegen: Team, Enterprise, API oder ein Cloud-Anbieter. Private Pro- oder Max-Konten ausschließen.
2. Mit dem Datenschutzbeauftragten Auftragsverarbeitungsvertrag, Drittlandtransfer und TOM des Anbieters prüfen. Unterlagen von Anthropic liegen im [Trust Center](https://trust.anthropic.com).
3. Bei Bedarf Zero Data Retention beim Anthropic-Account-Team anfragen oder eine EU-Region über Bedrock oder Vertex AI wählen.
4. Login und Anbieter festnageln: `forceLoginMethod`, `forceLoginOrgUUID` und ab v2.1.285 `allowedProviders` in die Managed Settings.
5. `env`-Block mit `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`, `DISABLE_FEEDBACK_COMMAND` und `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY` in die Managed Settings; `cleanupPeriodDays` setzen.
6. Managed Settings verteilen und auf einem Rechner mit `/status` prüfen: Die Zeile `Setting sources` muss `Enterprise managed settings` zeigen. Details in [Claude Code Enterprise](./claude-code-enterprise.md).
7. In jedem Repo die Team-Basis mit `claude-team einrichten` anlegen und mit `claude-team audit` in CI prüfen.
8. Verarbeitungsverzeichnis ergänzen, TOM und gegebenenfalls DSFA mit den [Rollout-Vorlagen](../rollout/README.md) dokumentieren.

## Checkliste für den Datenschutzbeauftragten

- [ ] Vertragspartner und Kontotyp sind festgelegt, private Konten sind per `forceLoginMethod` und `forceLoginOrgUUID` ausgeschlossen.
- [ ] Auftragsverarbeitungsvertrag (Art. 28 DSGVO) mit dem Anbieter liegt vor oder ist in Prüfung.
- [ ] Drittlandtransfer und Region sind dokumentiert, inklusive Cross-Region-Inferenz bei Bedrock.
- [ ] Aufbewahrung beim Anbieter ist bekannt (30 Tage Standard, ZDR, oder Richtlinie des Cloud-Anbieters).
- [ ] Development Partner Program ist in der Organisation nicht aktiviert.
- [ ] Telemetrie, Fehlerberichte, `/feedback` und Umfragen sind per Managed Settings abgeschaltet.
- [ ] `cleanupPeriodDays` ist gesetzt und im Löschkonzept beschrieben.
- [ ] MCP-Server sind per Allowlist begrenzt, weil deren Datenverarbeitung nicht unter ZDR fällt.
- [ ] deny-Regeln und PII-Hook sind in allen Repos aktiv, `claude-team audit` läuft in CI.
- [ ] Es gibt eine Regel, dass keine Echtdaten (Kunden-, Personal-, Gesundheitsdaten) in Prompts gehören, und Testdaten sind synthetisch.
- [ ] Die Notwendigkeit einer DSFA (Art. 35 DSGVO) ist geprüft und das Ergebnis dokumentiert.
- [ ] Bei Berufsgeheimnisträgern sind die Punkte zu § 203 StGB mit der Rechtsabteilung geklärt.
- [ ] Betriebsrat ist informiert, siehe [Infoblatt](../rollout/betriebsrat-infoblatt.md).

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| `DISABLE_TELEMETRY=0` gesetzt, um Telemetrie einzuschalten | Telemetrie bleibt aus | Variable entfernen statt auf `0` setzen |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` gesetzt, aber kein Update-Weg | Clients bleiben auf alter Version | Updates über Softwareverteilung, `requiredMinimumVersion` setzen |
| Telemetrie nur in der Shell abgeschaltet | neue Rechner senden wieder | Variablen in den `env`-Block der Managed Settings |
| ZDR angenommen, aber Entwickler mit privatem Konto angemeldet | Sitzungen nicht abgedeckt | `forceLoginMethod` und `forceLoginOrgUUID` erzwingen |
| `cleanupPeriodDays: 0` | Settings-Datei wird abgelehnt | Mindestwert `1`, für keine Speicherung `CLAUDE_CODE_SKIP_PROMPT_HISTORY` |
| Nur auf ZDR verlassen | MCP-Server verarbeiten Daten weiter | MCP-Allowlist, Drittanbieter separat prüfen |
| `skipWebFetchPreflight` ohne WebFetch-Regeln | WebFetch erreicht jede URL ohne Sperrliste | WebFetch sperren oder Domains per `WebFetch(domain:...)` begrenzen |

## Häufige Fragen

### Ist Claude Code DSGVO-konform?

Claude Code kann datenschutzkonform betrieben werden, wenn ein kommerzieller Vertrag mit Auftragsverarbeitung, eine passende Region und technische Begrenzungen zusammenkommen. Ob das für dein Unternehmen gilt, prüfen Datenschutzbeauftragter und Rechtsabteilung; das Werkzeug allein ist weder konform noch nicht konform.

### Trainiert Anthropic mit unserem Code?

Bei Team, Enterprise, API und Cloud-Anbietern trainiert Anthropic laut Doku nicht mit Code oder Prompts, außer du meldest dich ausdrücklich etwa für das Development Partner Program an. Bei Free, Pro und Max hängt es von der Trainings-Einstellung des Kontos ab.

### Wie lange speichert Anthropic die Daten?

Bei kommerziellen Konten standardmäßig 30 Tage, mit Zero Data Retention nicht über die Antwort hinaus. Über `/feedback` geteilte Transkripte werden 5 Jahre aufbewahrt, deshalb gehört `DISABLE_FEEDBACK_COMMAND` in die Managed Settings.

### Bleiben die Daten mit Bedrock in der EU?

Nicht automatisch. `AWS_REGION=eu-central-1` und `ANTHROPIC_BEDROCK_REGION_PREFIX=eu` sind laut [Doku](https://code.claude.com/docs/en/amazon-bedrock#cross-region-inference-profile-prefixes) nur eine Präferenz: Fehlt für ein Modell ein `eu.`-Profil, kann Claude Code auf ein anderes Profil ausweichen, etwa `global.`. Für eine belastbare EU-Verarbeitung pinnst du alle drei Modelle auf `eu.`-IDs, beschränkst `availableModels` auf diese IDs und erlaubst in der IAM-Policy nur EU-Regionen und `eu.`-Inference-Profile. Welche EU-Regionen ein `eu.`-Profil nutzt und was AWS speichert, regeln AWS-Dokumentation und dein AWS-Vertrag.

### Sendet Claude Code Daten, wenn ich Bedrock nutze?

Metriken, Fehlerberichte und `/feedback`-Upload sind bei Bedrock standardmäßig aus. Die Sitzungsumfrage und der WebFetch-Domain-Check, der nur den Hostnamen an `api.anthropic.com` sendet, laufen trotzdem; beides lässt sich abschalten.

### Brauchen wir für Claude Code eine Datenschutz-Folgenabschätzung?

Das hängt davon ab, welche Daten verarbeitet werden und ob ein hohes Risiko für Betroffene besteht; das entscheidet der Datenschutzbeauftragte. Ein Gerüst liegt in der [DSFA-Vorlage](../rollout/dsfa-vorlage.md).

## Weiterlesen

- [Claude Code Sicherheit](./claude-code-sicherheit.md)
- [Claude Code Enterprise: Managed Settings](./claude-code-enterprise.md)
- [Claude Code im Team ausrollen](./claude-code-team-rollout.md)
- [Claude Code Hooks](./claude-code-hooks.md)
- [Claude Code Bedrock](./claude-code-bedrock.md)
- Vorlagen: [TOM-Vorlage](../rollout/tom-vorlage.md), [DSFA-Vorlage](../rollout/dsfa-vorlage.md), [Managed Settings](../../vorlagen/managed-settings.json), Prüfregel [CC019 Telemetrie](../regeln.md#cc019)
