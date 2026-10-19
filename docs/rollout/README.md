# Rollout-Unterlagen für Claude Code im Unternehmen

Vorlagen zum Ausfüllen, mit denen du Claude Code durch die Freigabe bei IT-Sicherheit, Datenschutz, Legal, Betriebsrat und Management bringen. Jede Unterlage ist für eine Zielgruppe geschrieben, enthält schon die technischen Fakten zu Claude Code und lässt die unternehmensspezifischen Angaben als Platzhalter offen.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

Die Unterlagen sind keine Rechtsberatung. Rechtsnormen wie Art. 28, 32 und 35 DSGVO, § 203 StGB oder § 87 BetrVG werden nur als Punkte genannt, die du mit den zuständigen Stellen klärst.

## Welche Unterlage für wen?

| Unterlage | Zielgruppe | Zweck | Wer füllt aus |
| --- | --- | --- | --- |
| [Pilotplan](./pilotplan.md) | Management, Teamleitungen | Ziele, Teilnehmer, Dauer, Messgrößen, Abbruchkriterien, Entscheidungsvorlage | Projektleitung |
| [Freigabe-Paket](./freigabe-paket.md) | IT-Sicherheit, Legal, Einkauf | Steckbrief, Datenflüsse, Konfiguration, Schutzmaßnahmen, Verantwortliche, Checkliste | Plattform-Team mit IT-Sicherheit |
| [TOM-Vorlage](./tom-vorlage.md) | Datenschutzbeauftragter | Technische und organisatorische Maßnahmen nach Art. 32 DSGVO | Datenschutz mit Plattform-Team |
| [DSFA-Vorlage](./dsfa-vorlage.md) | Datenschutzbeauftragter | Gerüst einer Datenschutz-Folgenabschätzung, falls nötig | Datenschutz |
| [Betriebsrat-Infoblatt](./betriebsrat-infoblatt.md) | Betriebsrat, Personalabteilung | Was das Werkzeug tut, was protokolliert wird, Regelungspunkte | Projektleitung mit Personalabteilung |
| [Kostenrichtlinie](./kostenrichtlinie.md) | Management, Controlling, Teamleitungen | Budgets, Modellwahl, Limits, Monitoring, Eskalation | Controlling mit Plattform-Team |

Ergänzend für die Technik:

- [Vorlage Managed Settings](../../vorlagen/managed-settings.json) für die zentrale Verteilung
- [Claude Code DSGVO](../anleitungen/claude-code-dsgvo.md), [Sicherheit](../anleitungen/claude-code-sicherheit.md), [Enterprise](../anleitungen/claude-code-enterprise.md) und [Team-Rollout](../anleitungen/claude-code-team-rollout.md)

## In welcher Reihenfolge?

1. **Pilotplan** zuerst: Er klärt Ziel, Umfang und Budget und gibt allen anderen Unterlagen den Rahmen.
2. **Freigabe-Paket** parallel an IT-Sicherheit und Legal: Es beschreibt Werkzeug, Datenflüsse und Konfiguration.
3. **TOM-Vorlage** mit dem Datenschutzbeauftragten ausfüllen; dabei entscheiden, ob eine **DSFA** nötig ist.
4. **Betriebsrat-Infoblatt** früh übergeben, spätestens vor dem Pilotstart.
5. **Kostenrichtlinie** vor dem Pilotstart festlegen, nach dem Pilot mit echten Zahlen nachschärfen.
6. Nach dem Pilot: Entscheidungsvorlage aus dem Pilotplan an das Management.

```text
Woche 0        Woche 1-2          Woche 2-4         Woche 4-12
Pilotplan  ->  Freigabe-Paket ->  Pilotstart    ->  Auswertung, Entscheidung
               TOM, DSFA-Prüfung  Kostenrichtlinie
               Betriebsrat-Info
```

Die Wochen sind ein Beispiel. In vielen Unternehmen dauert die Freigabe länger als der Pilot selbst; starte sie deshalb so früh wie möglich.

## So nutzt du die Vorlagen

- Platzhalter stehen in eckigen Klammern, zum Beispiel `[Firma]`, `[Datum]`, `[Name, Rolle]`.
- Abschnitte, die für deine Betriebsvariante nicht gelten, löschst du, statt sie leer zu lassen.
- Fakten zu Claude Code sind mit Quelle in der offiziellen Doku belegt. Prüf vor der Abgabe, ob der Stand noch aktuell ist; Claude Code erscheint oft in neuen Versionen.
- Halte die ausgefüllten Fassungen in deinem internen Dokumentensystem, nicht in diesem öffentlichen Repo.

## Typische Fragen der Gremien

| Gremium | Häufige Frage | Antwort steht in |
| --- | --- | --- |
| IT-Sicherheit | Kann der Agent Secrets lesen oder Daten nach außen senden? | Freigabe-Paket, Abschnitt Schutzmaßnahmen |
| Datenschutz | Wer verarbeitet die Daten wo, wie lange? | TOM-Vorlage, DSGVO-Anleitung |
| Legal | Welcher Vertrag gilt, wer ist Vertragspartner? | Freigabe-Paket, Abschnitt Steckbrief |
| Betriebsrat | Wird Leistung oder Verhalten überwacht? | Betriebsrat-Infoblatt |
| Management | Was kostet es, was bringt es? | Pilotplan, Kostenrichtlinie |

## Was vor der Abgabe technisch stehen sollte

Die Unterlagen beschreiben eine Konfiguration. Gremien fragen oft nach einem Nachweis, dass sie wirklich greift. Halte deshalb vor der Abgabe Folgendes bereit:

- [ ] Managed Settings auf einem Testrechner verteilt; `/status` nennt sie als Quelle.
- [ ] Gegenprobe: `claude --dangerously-skip-permissions` wird abgelehnt, das Lesen von `.env` blockiert.
- [ ] `claude-team audit` läuft im Pilot-Repo ohne Fehler; der Bericht als Markdown oder SARIF liegt bei.
- [ ] Die Liste der freigegebenen MCP-Server und Plugin-Marketplaces ist fertig.
- [ ] Vertragsweg und Region sind entschieden, damit Datenflüsse und TOM konkret ausgefüllt werden können.

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team audit . --format markdown --out audit.md
```

## Pflege der Unterlagen

| Anlass | Was anpassen |
| --- | --- |
| Wechsel der Betriebsvariante (z.B. von der Anthropic API zu Bedrock) | Freigabe-Paket, TOM, DSFA, Kostenrichtlinie |
| Neue Datenquelle, z.B. OpenTelemetry einschalten | Betriebsrat-Infoblatt, DSFA, TOM |
| Neue MCP-Server oder Plugins | Freigabe-Paket, Managed Settings |
| Neue Claude-Code-Version mit geänderten Datenflüssen | Freigabe-Paket, TOM; Changelog prüfen |
| Ende des Pilots | Kostenrichtlinie mit gemessenen Werten, Entscheidungsvorlage |

## Weiterlesen

- [Claude Code im Team ausrollen](../anleitungen/claude-code-team-rollout.md)
- [Claude Code DSGVO](../anleitungen/claude-code-dsgvo.md)
- [Claude Code Enterprise](../anleitungen/claude-code-enterprise.md)
- [Prüfregeln von claude-team](../regeln.md)
