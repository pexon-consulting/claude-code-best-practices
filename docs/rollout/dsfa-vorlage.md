# DSFA-Vorlage: Claude Code bei [Firma]

Gerüst für eine Datenschutz-Folgenabschätzung (DSFA) zum Einsatz von Claude Code. Es gibt die Gliederung vor und trägt die technischen Fakten zu Claude Code ein; Bewertung und Ergebnis liegen beim Verantwortlichen und beim Datenschutzbeauftragten.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

Diese Vorlage ist keine Rechtsberatung und ersetzt keine Prüfung im Einzelfall.

## 0. Ist eine DSFA nötig?

Ob eine DSFA nach Art. 35 DSGVO erforderlich ist, klärt der Datenschutzbeauftragte. Die folgenden Fragen helfen, den Sachverhalt für dieses Gespräch aufzubereiten. Sie sind keine Entscheidungsregel.

| Frage | Antwort bei [Firma] |
| --- | --- |
| Verarbeitet Claude Code personenbezogene Daten oder kann es sie im Arbeitsalltag sehen (Code mit Kundendaten, Logs, Datenbank-Dumps, Tickets)? | [ja / nein / möglich] |
| Sind besondere Kategorien von Daten oder Berufsgeheimnisse betroffen (z.B. Gesundheitsdaten, Mandantendaten)? | [ja / nein] |
| Werden Daten in ein Drittland übermittelt? | [ja / nein, Region] |
| Werden Nutzungsdaten der Beschäftigten ausgewertet (OpenTelemetry, Protokolle)? | [ja / nein, Umfang] |
| Ist die Technologie für [Firma] neu im Sinne von Art. 35 Abs. 1 DSGVO? | [Einschätzung DSB] |
| Steht die Verarbeitung auf einer Liste der Aufsichtsbehörde nach Art. 35 Abs. 4 DSGVO? | [Prüfung DSB] |

**Ergebnis der Vorprüfung:** [ ] DSFA erforderlich [ ] nicht erforderlich, Begründung: [Begründung] [ ] wird freiwillig durchgeführt

| Name | Rolle | Datum |
| --- | --- | --- |
| [Name] | Datenschutzbeauftragter | [Datum] |

## 1. Systematische Beschreibung der Verarbeitung

### 1.1 Zweck

[Unterstützung der Softwareentwicklung: Code lesen, Änderungen vorschlagen und umsetzen, Tests ausführen, Reviews.]

### 1.2 Beteiligte

| Rolle | Wer |
| --- | --- |
| Verantwortlicher | [Firma] |
| Auftragsverarbeiter | [Anthropic / AWS / Google / Microsoft / Gateway-Betreiber] |
| Unterauftragsverarbeiter | [laut Liste des Anbieters] |
| Betroffene | [Beschäftigte als Nutzer; Personen, deren Daten im Code, in Logs oder Testdaten vorkommen] |

### 1.3 Datenkategorien

| Kategorie | Beispiel | Weg zum Modell |
| --- | --- | --- |
| Nutzerdaten der Beschäftigten | Konto, E-Mail, Nutzungsmetriken | Anmeldung, [OpenTelemetry] |
| Inhalte der Sitzung | Prompts, Modellausgaben | jede Anfrage |
| Gelesene Dateien | Quellcode, Konfiguration, [Logs, Testdaten] | Read-, Grep-, Bash-Ausgaben |
| Ergebnisse von Werkzeugen | Ausgaben von Befehlen und MCP-Servern | jede Anfrage |
| [Weitere] | [Beispiel] | [Weg] |

### 1.4 Datenflüsse und Speicherorte

| Ort | Inhalt | Dauer |
| --- | --- | --- |
| Entwicklerrechner | Transkripte im Klartext unter `~/.claude/projects/` | `cleanupPeriodDays`, Standard 30 Tage, bei [Firma] [x] Tage |
| Modellanbieter | Prompts und Ausgaben | [30 Tage bei kommerziellen Anthropic-Konten / keine Speicherung mit Zero Data Retention, außer bei Richtlinienverstößen bis zu 2 Jahre / laut Cloud-Anbieter] |
| Anthropic, Telemetrie | Metriken ohne Code und Prompts | [abgeschaltet per `DISABLE_TELEMETRY`] |
| Anthropic, `/feedback` | Verlauf mit Code, 5 Jahre | [abgeschaltet per `DISABLE_FEEDBACK_COMMAND`] |
| Eigener Collector | [OpenTelemetry-Metriken, ggf. Ereignisse] | [Frist] |
| Repo | Hook-Protokoll unter `.claude/protokoll/` (standardmäßig aus), ohne Dateiinhalte | [Frist, Standard `aufbewahrung_tage`: 30] |

Quelle der Herstellerangaben: [Data usage](https://code.claude.com/docs/en/data-usage), [Zero data retention](https://code.claude.com/docs/en/zero-data-retention). Ausführlich: [Claude Code DSGVO](../anleitungen/claude-code-dsgvo.md).

### 1.5 Eingesetzte Technik

[Version, Betriebsvariante, Region, Managed Settings laut [Freigabe-Paket](./freigabe-paket.md).]

## 2. Notwendigkeit und Verhältnismäßigkeit

| Punkt | Darstellung bei [Firma] |
| --- | --- |
| Rechtsgrundlage | [vom DSB festzulegen] |
| Zweckbindung | [Nutzung nur für Entwicklung; keine Auswertung zur Leistungs- oder Verhaltenskontrolle] |
| Datenminimierung | deny-Regeln für Secrets und Datenordner, Hook `pii_schutz.py`, synthetische Testdaten, [weitere] |
| Speicherbegrenzung | `cleanupPeriodDays`, [Zero Data Retention], Löschfrist für Protokolle |
| Transparenz | [Information der Beschäftigten, Betriebsrats-Infoblatt] |
| Betroffenenrechte | [Prozess für Auskunft und Löschung, auch lokale Transkripte] |
| Alternativen | [geprüfte Alternativen, z.B. andere Betriebsvariante oder Region] |

## 3. Risiken für die Rechte und Freiheiten der Betroffenen

Bewertung durch [Firma]. Die Spalten Eintrittswahrscheinlichkeit und Schwere bleiben offen, bis sie gemeinsam mit dem DSB eingeschätzt sind.

| Nr. | Risiko | Ursache | Wahrscheinlichkeit | Schwere |
| --- | --- | --- | --- | --- |
| R1 | Personenbezogene Daten gelangen zum Modellanbieter | Echtdaten in Prompt, Log oder Testdatei | [ ] | [ ] |
| R2 | Daten werden länger als nötig gespeichert | lokale Transkripte, Feedback-Upload, Aufbewahrung beim Anbieter | [ ] | [ ] |
| R3 | Datenabfluss an Dritte | MCP-Server, WebFetch, Netzbefehle, Prompt Injection | [ ] | [ ] |
| R4 | Unbefugter Zugriff auf Secrets und damit auf Systeme mit Personendaten | Agent liest `.env` oder Cloud-Credentials | [ ] | [ ] |
| R5 | Drittlandübermittlung | Region des Anbieters, Konto am Firmenvertrag vorbei | [ ] | [ ] |
| R6 | Überwachung der Beschäftigten | OpenTelemetry mit `user.email`, Auswertung von Protokollen | [ ] | [ ] |
| R7 | [Weiteres Risiko] | [Ursache] | [ ] | [ ] |

## 4. Abhilfemaßnahmen

| Risiko | Maßnahme | Restrisiko |
| --- | --- | --- |
| R1 | Deny-Regeln für Datenordner (Read, Grep, Bash); Hook `pii_schutz.py` erkennt IBAN, Steuer-ID, SV-Nummer und Kreditkarte mit gültiger Prüfziffer in Prompts, Befehlen und geschriebenem Code, nicht in gelesenen Dateien; Schulung; `claude-team scannen` in CI | [ ] |
| R2 | `cleanupPeriodDays: [x]`; `DISABLE_FEEDBACK_COMMAND=1`; [Zero Data Retention]; Löschfrist für Protokolle | [ ] |
| R3 | Allowlist für MCP-Server; `strictKnownMarketplaces`; [Sandbox mit `allowedDomains`]; [deny für WebFetch und `curl`] | [ ] |
| R4 | deny-Regeln für Secrets in den Managed Settings; Hook `secrets_schutz.py`; `disableBypassPermissionsMode` | [ ] |
| R5 | [Bedrock mit `AWS_REGION=eu-central-1` und `ANTHROPIC_BEDROCK_REGION_PREFIX=eu` / Vertex AI mit `CLOUD_ML_REGION=eu`]; `forceLoginOrgUUID`; `allowedProviders` | [ ] |
| R6 | [keine OpenTelemetry-Auswertung je Person / nur aggregiert]; Regelung mit dem Betriebsrat; Protokoll ohne Dateiinhalte | [ ] |
| R7 | [Maßnahme] | [ ] |

Die vollständige Liste der Maßnahmen steht in der [TOM-Vorlage](./tom-vorlage.md).

## 5. Ergebnis

| Punkt | Eintrag |
| --- | --- |
| Restrisiko gesamt | [niedrig / mittel / hoch] |
| Stellungnahme des DSB | [Text] |
| Konsultation der Aufsichtsbehörde (Art. 36 DSGVO) erforderlich | [Einschätzung DSB] |
| Nächste Überprüfung | [Datum, spätestens bei Wechsel der Betriebsvariante oder größeren Änderungen an Claude Code] |

| Name | Rolle | Datum | Unterschrift |
| --- | --- | --- | --- |
| [Name] | Verantwortlicher | [Datum] | |
| [Name] | Datenschutzbeauftragter | [Datum] | |
