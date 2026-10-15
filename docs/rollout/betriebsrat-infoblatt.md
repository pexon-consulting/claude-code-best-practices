# Infoblatt für den Betriebsrat: Claude Code bei [Firma]

Dieses Blatt informiert den Betriebsrat über den geplanten Einsatz von Claude Code: was das Werkzeug tut, welche Daten dabei anfallen und welche nicht, und welche Punkte gemeinsam zu klären sind.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

| Feld | Eintrag |
| --- | --- |
| Vorgelegt von | [Name, Rolle] |
| Datum | [Datum] |
| Betroffene Bereiche | [Teams, Anzahl Beschäftigte] |
| Geplanter Start | [Pilot ab Datum / Regelbetrieb ab Datum] |
| Ansprechpartner | [Name, E-Mail @example.com] |

## 1. Was ist Claude Code?

Claude Code ist ein KI-Assistent für die Softwareentwicklung von Anthropic. Er läuft auf dem Rechner der Entwicklerin oder des Entwicklers im Terminal oder in der Entwicklungsumgebung. Er liest Programmcode, schlägt Änderungen vor, setzt sie nach Rückfrage um und führt Befehle wie Tests aus. Für jede Antwort schickt er die Anfrage und die nötigen Inhalte an ein Sprachmodell bei [Anbieter].

Die Beschäftigten bleiben für den Code verantwortlich. Änderungen laufen wie bisher über Review und Freigabe.

## 2. Wozu wir es einsetzen

- [Zeitaufwand für Routinearbeiten wie Tests und Dokumentation senken]
- [Einarbeitung in fremden Code erleichtern]
- [Weitere Ziele]

Die Nutzung ist [freiwillig / Teil der Arbeitsmittel des Teams]. [Wer nicht teilnimmt, hat keine Nachteile.]

## 3. Was protokolliert wird

| Datenquelle | Was anfällt | Wo | Wer Zugriff hat | Aufbewahrung |
| --- | --- | --- | --- | --- |
| Lokaler Verlauf | Sitzungen im Klartext | Rechner der Person, `~/.claude/projects/` | die Person selbst | [x] Tage, dann automatisch gelöscht |
| Modellanbieter | Anfragen und Antworten | [Anbieter, Region] | [Anbieter laut Vertrag] | [30 Tage / keine Speicherung mit Zero Data Retention] |
| Hook-Protokoll der Team-Basis (falls aktiv) | Zeit, gekürzte Sitzungs-ID (8 Zeichen), Werkzeug, Dateiname, Befehl mit maskierten Tokens, Dauer | im Projektordner `.claude/protokoll/`, nicht im Git | [wer] | [x] Tage |
| Abrechnung und Admin-Konsole | [Kosten und Nutzung je Person, siehe Abschnitt 4] | [Anthropic-Konsole / Cloud-Konto] | [Admins: Namen oder Rolle] | [laut Anbieter] |
| OpenTelemetry (falls aktiv) | Sitzungen, Kosten, Tokens, Commits, Pull Requests, Codezeilen, aktive Zeit | eigener Server [Name] | [wer] | [x] Tage |

## 4. Was nicht protokolliert wird

- Das Hook-Protokoll der Team-Basis speichert keine Dateiinhalte und keine Prompts.
- Die Metriken, die Claude Code an Anthropic schicken kann, enthalten laut Hersteller keinen Code, keine Prompts und keine Dateipfade. Bei [Firma] sind sie zusätzlich abgeschaltet.
- `/feedback` und die Sitzungsumfrage sind abgeschaltet; es gehen keine Verläufe als Feedback an den Hersteller.
- Bei OpenTelemetry sind Prompt-Texte, Antworten und Werkzeugdetails standardmäßig nicht enthalten. Sie lassen sich nur mit eigenen Schaltern einschalten (`OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_ASSISTANT_RESPONSES`, `OTEL_LOG_TOOL_DETAILS`). [Firma] schaltet sie [nicht] ein.

## 5. Wo Daten einer Person zugeordnet werden können

Offen gesagt, damit es gemeinsam geregelt werden kann:

- Wenn OpenTelemetry aktiv ist und die Anmeldung über ein Claude-Konto läuft, enthält jeder Datensatz laut Doku die E-Mail-Adresse der Person (`user.email`), dazu Konto- und Sitzungs-IDs. Die Daten gehen nur an den Server, den [Firma] einträgt, nicht an Anthropic. Die Doku empfiehlt, das Feld im eigenen Backend zu filtern, wenn das ein Problem ist.
- Bei Claude for Teams und Enterprise zeigen Spend-Report und Analytics-Dashboard Ausgaben und Beiträge je Person; auf Enterprise liefert eine Analytics-API Nutzung und Kosten je Person. In der Claude Console sieht man Ausgaben und angenommene Codezeilen je Mitglied.
- Das Hook-Protokoll liegt im Projektordner. Es enthält keine Namen, aber Zeitpunkte und Sitzungen, die sich einem Rechner zuordnen lassen.
- Auf Amazon Bedrock, Google Vertex AI und Microsoft Foundry fallen Kosten im Cloud-Konto an; die Anthropic-Dashboards decken diese Nutzung nicht ab.

## 6. Keine Absicht zur Leistungs- oder Verhaltenskontrolle

[Firma] setzt Claude Code als Arbeitsmittel ein. Es ist nicht beabsichtigt, die Daten aus Abschnitt 3 und 5 zur Leistungs- oder Verhaltenskontrolle einzelner Beschäftigter zu nutzen. Auswertungen dienen [der Kostenkontrolle und der Bewertung des Werkzeugs auf Team-Ebene].

## 7. Punkt zur Klärung: § 87 Abs. 1 Nr. 6 BetrVG

Ob und in welchem Umfang ein Mitbestimmungsrecht nach § 87 Abs. 1 Nr. 6 BetrVG berührt ist, klären Arbeitgeber und Betriebsrat gemeinsam, bei Bedarf mit juristischer Beratung. Dieses Blatt nimmt dazu keine Bewertung vor. Für das Gespräch relevant sind vor allem die Punkte in Abschnitt 5.

## 8. Vorschläge für Regelungspunkte

Mögliche Inhalte einer Vereinbarung oder Regelungsabsprache, als Ausgangspunkt für das Gespräch:

| Nr. | Regelungspunkt | Vorschlag |
| --- | --- | --- |
| 1 | Zweck | Einsatz als Arbeitsmittel in der Softwareentwicklung |
| 2 | Ausschluss | keine Auswertung zur Leistungs- oder Verhaltenskontrolle einzelner Personen |
| 3 | Auswertungen | nur aggregiert auf Team-Ebene ab [x] Personen; Ausnahme: [Kostenüberschreitung, Sicherheitsvorfall] |
| 4 | Zugriffsrechte | Liste der Personen mit Zugriff auf Admin-Konsole, Analytics und Telemetrie |
| 5 | OpenTelemetry | [nicht aktiv / aktiv ohne `user.email` im Backend / aktiv mit Pseudonymisierung] |
| 6 | Prompt- und Inhaltsprotokolle | bleiben ausgeschaltet |
| 7 | Löschfristen | lokale Verläufe [x] Tage, Hook-Protokoll [x] Tage, Telemetrie [x] Tage |
| 8 | Freiwilligkeit | [Regelung] |
| 9 | Schulung | vor Nutzung, in der Arbeitszeit |
| 10 | Änderungen | neue Datenquellen oder Auswertungen nur nach Information des Betriebsrats |
| 11 | Überprüfung | gemeinsame Überprüfung nach [6] Monaten |

## 9. Weitere Unterlagen

- [Pilotplan](./pilotplan.md)
- [Freigabe-Paket](./freigabe-paket.md) mit Datenflüssen und Konfiguration
- [TOM-Vorlage](./tom-vorlage.md)
- [Kostenrichtlinie](./kostenrichtlinie.md)
- Hintergrund: [Claude Code DSGVO](../anleitungen/claude-code-dsgvo.md)

Rückfragen an [Name, E-Mail @example.com].
