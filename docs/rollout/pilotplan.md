# Pilotplan: Claude Code bei [Firma]

Vorlage für einen Pilot mit 15-20 Entwicklern über 4-8 Wochen. Sie legt Ziele, Teilnehmer, Messgrößen und Abbruchkriterien vorab fest, damit die Entscheidung nach dem Pilot auf Zahlen beruht.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

| Feld | Eintrag |
| --- | --- |
| Version | [1.0] |
| Datum | [Datum] |
| Verantwortlich | [Name, Rolle] |
| Auftraggeber | [Name, Rolle] |
| Status | [Entwurf / freigegeben] |

## 1. Ausgangslage und Ziel

**Ausgangslage:** [Kurz: Welche Teams entwickeln was, welche Werkzeuge sind im Einsatz, warum Claude Code?]

**Ziel des Pilots:** Herausfinden, ob Claude Code bei [Firma] unter den Regeln der Team-Basis messbar nutzt, sicher betrieben werden kann und im Budget bleibt.

| Ziel | Messgröße | Zielwert | Quelle |
| --- | --- | --- | --- |
| Akzeptanz | Anteil aktiver Teilnehmer je Woche | [z.B. mindestens 70 %] | Analytics oder OpenTelemetry |
| Nutzen | Einschätzung der Teilnehmer, Aufgaben schneller erledigt | [z.B. Mehrheit "eher ja"] | Umfrage Woche 2, 4, Ende |
| Qualität | Rückläufer und Fehler aus KI-Änderungen | [nicht höher als vorher] | Ticketsystem, Review |
| Sicherheit | Sicherheitsvorfälle durch Claude Code | 0 | IT-Sicherheit |
| Einhaltung | Pilot-Repos ohne Audit-Fehler | 100 % | `claude-team audit` in CI |
| Kosten | Kosten je Entwickler und aktivem Tag | [Budget aus Kostenrichtlinie] | Abrechnung |

## 2. Umfang

| Feld | Eintrag |
| --- | --- |
| Zeitraum | [Startdatum] bis [Enddatum], [4-8] Wochen |
| Teams | [Team A], [Team B], [Team C] |
| Teilnehmer | [15-20] Entwickler, Liste in Anhang A |
| Repos | [Repo-Liste]; nur Repos ohne Echtdaten von Kunden oder Beschäftigten, solange der Datenschutz nichts anderes freigibt |
| Betriebsvariante | [Anthropic Team / Enterprise / API / Amazon Bedrock EU / Google Vertex AI EU / Microsoft Foundry / Gateway] |
| Modelle | [z.B. Sonnet als Standard, Opus für Planung] |
| Nicht im Umfang | [z.B. Produktionszugriff, Kundendaten, CI-Automatisierung mit Schreibrechten] |

## 3. Rollen

| Rolle | Name | Aufgabe |
| --- | --- | --- |
| Projektleitung | [Name] | Plan, Termine, Auswertung |
| Plattform-Team | [Name] | Managed Settings, Team-Basis, Support |
| Champion Team A | [Name] | Fragen sammeln, Regeln pflegen |
| Champion Team B | [Name] | wie oben |
| IT-Sicherheit | [Name] | Freigabe, Vorfallbewertung |
| Datenschutz | [Name] | TOM, DSFA-Prüfung |
| Betriebsrat | [Name] | Information, Regelungspunkte |

## 4. Technische Basis

- Managed Settings aus [vorlagen/managed-settings.json](../../vorlagen/managed-settings.json), angepasst und auf den Pilotrechnern verteilt.
- Repo-Basis mit `claude-team einrichten` (CLAUDE.md, `.claude/settings.json`, Schutz-Hooks, `.claude/schutz.json`).
- Plugin `team-basis` mit Schutz-Hooks und Skills.
- `claude-team audit` als GitHub Action in jedem Pilot-Repo.
- Bypass-Modus gesperrt (`disableBypassPermissionsMode`), Telemetrie an Anthropic aus.
- [Optional: Sandbox mit Netz-Allowlist, OpenTelemetry an den eigenen Collector]

## 5. Ablauf

| Woche | Schritt | Ergebnis |
| --- | --- | --- |
| 0 | Freigabe-Paket, TOM, Betriebsrat-Info übergeben | Freigabe für den Pilot |
| 0 | Konten oder Cloud-Zugang einrichten, Managed Settings verteilen | Rechner bereit |
| 1 | Kick-off und Schulung (2-3 Stunden je Team) | alle Teilnehmer arbeitsfähig |
| 1-8 | Arbeit an echten Aufgaben, wöchentlicher Austausch mit Champions | Feedback, Regelanpassungen |
| 2 | Zwischenumfrage, erste Kostenauswertung | Kurskorrektur |
| 4 | Zwischenbilanz mit Auftraggeber | Fortsetzen, verlängern oder abbrechen |
| Ende | Abschlussumfrage, Auswertung aller Messgrößen | Entscheidungsvorlage |

## 6. Messgrößen und Datenerhebung

- Kosten: [Spend-Report der Admin-Konsole / Console-Workspace / Cloud-Abrechnung / Gateway].
- Nutzung: [Analytics / OpenTelemetry mit `claude_code.session.count`, `claude_code.cost.usage`, `claude_code.token.usage`].
- Auswertung auf Team-Ebene, nicht je Person, soweit mit dem Betriebsrat nicht anders vereinbart.
- Umfrage mit [Werkzeug], anonym, zu Woche 2, 4 und Ende.

Vergleichswert aus der Doku: "Across enterprise deployments, the average cost is around $13 per developer per active day and $150-250 per developer per month, with costs remaining below $30 per active day for 90% of users." ([Costs](https://code.claude.com/docs/en/costs), abgerufen 15.10.2026)

## 7. Abbruchkriterien

Der Pilot wird gestoppt oder pausiert, wenn eines davon eintritt:

- [ ] Ein Sicherheitsvorfall, bei dem Secrets oder personenbezogene Daten abgeflossen sind oder abfließen konnten.
- [ ] Ein Verstoß gegen die Datenschutzauflagen, der nicht technisch abstellbar ist.
- [ ] Kosten über [x] % des Pilotbudgets vor Woche [y].
- [ ] Akzeptanz unter [z] % aktiver Teilnehmer in zwei aufeinanderfolgenden Wochen.
- [ ] Rücknahme der Freigabe durch IT-Sicherheit, Datenschutz oder Betriebsrat.
- [ ] [Weiteres Kriterium]

## 8. Risiken

| Risiko | Gegenmaßnahme | Verantwortlich |
| --- | --- | --- |
| Secrets im Kontext | deny-Regeln, `secrets_schutz.py` | [Name] |
| Personenbezogene Daten im Prompt | `pii_schutz.py`, Repos ohne Echtdaten | [Name] |
| Kosten laufen aus dem Ruder | Budgets und Limits laut Kostenrichtlinie | [Name] |
| Uneinheitliche Nutzung | Team-Basis, Audit in CI, Schulung | [Name] |
| Qualität der KI-Änderungen | Review-Pflicht, Tests, `/security-review` | [Name] |

## 9. Entscheidungsvorlage nach dem Pilot

| Feld | Eintrag |
| --- | --- |
| Zeitraum und Teilnehmer | [tatsächlich] |
| Zielerreichung | [je Ziel aus Abschnitt 1: erreicht / teilweise / nicht] |
| Kosten gesamt und je Entwickler und aktivem Tag | [Wert] |
| Wichtigste Rückmeldungen | [3-5 Punkte] |
| Vorfälle | [keine / Beschreibung] |
| Offene Punkte aus der Freigabe | [Liste] |
| Empfehlung | [ausweiten / mit Auflagen ausweiten / verlängern / stoppen] |
| Nächste Schritte bei Zustimmung | [Teams, Zeitplan, Budget] |

**Entscheidung:** [ ] ausweiten [ ] mit Auflagen ausweiten [ ] verlängern [ ] stoppen

| Name | Rolle | Datum | Unterschrift |
| --- | --- | --- | --- |
| [Name] | [Rolle] | [Datum] | |

## Anhang A: Teilnehmer

| Name | Team | Champion | Repos |
| --- | --- | --- | --- |
| [Name] | [Team] | [ja/nein] | [Repo] |
