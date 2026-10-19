# Kostenrichtlinie: Claude Code bei [Firma]

Richtlinie für Budget, Modellwahl, Grenzen und Überwachung der Kosten von Claude Code. Sie legt fest, wer wie viel ausgeben darf, wie die Grenzen technisch gesetzt werden und was bei Überschreitung passiert.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

| Feld | Eintrag |
| --- | --- |
| Gültig ab | [Datum] |
| Gültig für | [Teams, Anzahl Personen] |
| Abrechnungsweg | [Claude for Teams / Enterprise mit Seats / Claude Console (API) / Amazon Bedrock / Google Vertex AI / Microsoft Foundry] |
| Kostenstelle | [Kostenstelle] |
| Verantwortlich | [Name, Rolle] |

## 1. Orientierungswert

Die Doku von Claude Code nennt als Durchschnitt aus Unternehmenseinsätzen:

> "Across enterprise deployments, the average cost is around $13 per developer per active day and $150-250 per developer per month, with costs remaining below $30 per active day for 90% of users."
>
> Quelle: [Manage costs effectively](https://code.claude.com/docs/en/costs), abgerufen am 15.10.2026.

Die Doku empfiehlt, mit einer kleinen Pilotgruppe zu beginnen und eine eigene Basislinie zu messen. Die Werte unten werden nach dem Pilot mit den gemessenen Zahlen von [Firma] ersetzt. Preise je Plan stehen auf [claude.com/pricing](https://claude.com/pricing) bzw. in den Preislisten des Cloud-Anbieters.

## 2. Budget

| Ebene | Budget | Zeitraum | Gesetzt in |
| --- | --- | --- | --- |
| Organisation | [Betrag] EUR | Monat | [Admin-Einstellungen / Console-Workspace / Cloud-Budget] |
| Team [Name] | [Betrag] EUR | Monat | [Gruppen-Limit / Gateway-Budget] |
| Entwickler | [Betrag] EUR | Monat | [Member-Limit / Gateway-Budget je Person] |
| CI-Lauf | [Betrag] USD | je Lauf | `--max-budget-usd` |

## 3. Technische Grenzen je Abrechnungsweg

| Abrechnungsweg | Grenze | Wo |
| --- | --- | --- |
| Claude for Teams und Enterprise | Seat-Kontingent als Standardgrenze; mit Usage Credits Spend-Limits je Organisation, Gruppe oder Mitglied | Organization settings > Usage |
| Claude Console (API) | Spend-Limit und Rate-Limit für den Workspace "Claude Code" | Console, Workspace Limits |
| Amazon Bedrock, Google Vertex AI, Microsoft Foundry | Budgets und Alarme des Cloud-Anbieters | Billing-Konsole des Anbieters |
| Claude apps gateway | Spend-Limits je Person | Gateway-Konfiguration |
| LLM-Gateway (z.B. LiteLLM) | Ausgaben je Schlüssel | Gateway-Konfiguration; laut Doku nicht von Anthropic geprüft |

Rate-Limits für die API: Die Doku gibt Empfehlungen für Tokens und Requests pro Minute je Nutzer nach Teamgröße. Bei [Anzahl] Personen wählt [Firma] [TPM] TPM und [RPM] RPM je Nutzer. Quelle: Abschnitt "Rate limit recommendations" in [costs](https://code.claude.com/docs/en/costs).

## 4. Modellwahl

Die Doku empfiehlt Sonnet für die meisten Coding-Aufgaben, Opus für komplexe Architekturentscheidungen und mehrstufiges Denken und Haiku für einfache Subagent-Aufgaben.

| Regel | Umsetzung |
| --- | --- |
| Standardmodell | `"model": "sonnet"` in den Managed Settings |
| Erlaubte Modelle | `"availableModels": [Liste]` in den Managed Settings |
| Einfache Subagents | `model: haiku` in der Subagent-Datei |
| Opus | [frei / nach Absprache / nur für Rollen] |
| Abrechnungspreise in der Anzeige | [`modelPricing` mit Vertragskonditionen, ab v2.1.242] |

Beispiel für die Managed Settings:

```json
{
  "model": "sonnet",
  "availableModels": ["sonnet", "haiku", "opus"]
}
```

## 5. CI und Automatisierung

- Jeder Lauf von `claude -p` in CI bekommt `--max-budget-usd [Betrag]`. Die Grenze gilt nur im Print-Modus und prüft die Kostenschätzung auf dem Client, die von der Rechnung abweichen kann; die Ausgaben können die Grenze überschreiten.
- Ausgaben von Subagents zählen zur Grenze.
- CI-Läufe nutzen einen eigenen [Workspace / Schlüssel / Gateway-Key], damit sie getrennt auswertbar sind.

```bash
claude -p --max-budget-usd 2.00 "Prüfe den Diff auf fehlende Tests"
```

## 6. Überwachung

| Werkzeug | Was es zeigt | Wer |
| --- | --- | --- |
| `/usage` | Tokens und geschätzte Kosten der Sitzung; bei Plänen die Nutzung gegen die Limits | jede Person selbst |
| Spend-Report (Teams, Enterprise) | geschätzte Ausgaben je Person und Modell, täglich, CSV | [Admin] |
| Console-Dashboard (API) | Ausgaben und angenommene Zeilen je Mitglied | [Admin] |
| Billing des Cloud-Anbieters | Kosten im Cloud-Konto | [FinOps] |
| OpenTelemetry | Metriken wie `claude_code.cost.usage` und `claude_code.token.usage` an den eigenen Collector | [Plattform-Team] |

OpenTelemetry wird über `CLAUDE_CODE_ENABLE_TELEMETRY=1` und die `OTEL_*`-Variablen eingeschaltet. Seit v2.1.282 wirken diese Variablen nur noch aus Shell, User Settings, Managed Settings und `--settings`, nicht aus Projekt- oder lokalen Settings. [Firma] setzt sie in den Managed Settings:

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://collector.example.com:4317"
  }
}
```

Die Metriken enthalten bei Anmeldung über ein Claude-Konto die E-Mail-Adresse. Auswertungen je Person nur im Rahmen der Absprache mit dem Betriebsrat, siehe [Betriebsrats-Infoblatt](./betriebsrat-infoblatt.md).

## 7. Sparregeln für alle

- `/clear` zwischen unabhängigen Aufgaben.
- Sonnet als Standard, Opus nur bei Bedarf.
- Aufwand mit `/effort` senken, wenn keine tiefe Analyse nötig ist.
- Lange Ausgaben (Logs, Testläufe) vorher filtern.

## 8. Eskalation

| Stufe | Auslöser | Maßnahme | Wer |
| --- | --- | --- | --- |
| 1 | Person erreicht [80] % ihres Budgets | Hinweis an die Person | [automatisch / Admin] |
| 2 | Person erreicht ihr Limit | Limit greift; Erhöhung auf Antrag | [Teamleitung] |
| 3 | Team überschreitet [x] % des Monatsbudgets | Prüfung der Ursachen (lange Sitzungen, Opus als Standard, CI-Schleifen) | [Verantwortlicher] |
| 4 | Organisation erreicht das Gesamtbudget | Entscheidung über Erhöhung oder Begrenzung | [Budgetverantwortlicher] |

Anträge auf Erhöhung an [Kanal]. Entscheidung innerhalb von [x] Arbeitstagen.

## 9. Überprüfung

Diese Richtlinie wird nach dem Pilot und danach [quartalsweise] mit den gemessenen Kosten überprüft. Nächste Überprüfung: [Datum].
