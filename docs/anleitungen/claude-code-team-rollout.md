# Claude Code im Team: Rollout, Onboarding und gemeinsame Konfiguration

Claude Code rollst du im Team einheitlich aus, indem du mit einem Pilot von 15-20 Entwicklern startest, allen dieselbe Basis gibst (Managed Settings zentral, `.claude/settings.json`, Hooks und CLAUDE.md im Repo) und vor der Ausweitung misst, was der Pilot bringt und kostet. Die Freigabe durch IT-Sicherheit, Datenschutz, Legal und Betriebsrat läuft parallel zum Pilot, nicht danach. Diese Anleitung beschreibt Phasen, gemeinsame Basis, Onboarding und Kennzahlen.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

Diese Anleitung erklärt Technik und Einstellungen. Sie ist keine Rechtsberatung. Datenschutz, Verträge und Mitbestimmung klärst du mit Datenschutzbeauftragtem, Rechtsabteilung und Betriebsrat. Angaben zu Regionen und Datenverarbeitung der Anbieter können sich ändern; maßgeblich sind deren aktuelle Dokumentation und Verträge.

## Das Wichtigste in Kürze

- Ein Pilot mit 15-20 Entwicklern aus 2-3 Teams über 4-8 Wochen liefert belastbare Zahlen zu Nutzen, Kosten und Problemen.
- Die gemeinsame Basis besteht aus drei Ebenen: Managed Settings für Unternehmensregeln, `.claude/settings.json` und Hooks je Repo, CLAUDE.md für Projektwissen.
- `claude-team einrichten` legt die Repo-Basis an, das Plugin `team-basis` bringt Hooks und Skills auf jeden Rechner, `claude-team audit` prüft beides in CI.
- Die Freigabe-Unterlagen (Pilotplan, Freigabe-Paket, TOM, DSFA, Betriebsrat, Kosten) liegen als Vorlagen unter [docs/rollout](../rollout/README.md).
- Die Doku nennt als Richtwert für Unternehmen rund 13 US-Dollar je Entwickler und aktivem Tag; miss im Pilot deine eigene Basis.
- Ohne Schulung und gemeinsame Regeln entstehen Insellösungen; plane Onboarding und einen festen Ansprechpartner ein.

## Wie läuft ein Claude-Code-Rollout ab?

| Phase | Dauer | Ziel | Ergebnis |
| --- | --- | --- | --- |
| 0 Vorbereitung | 2-4 Wochen | Vertragsweg, Betriebsvariante, Freigabe-Unterlagen | Entscheidung Anbieter und Region, Freigabe-Paket im Umlauf |
| 1 Basis bauen | 1 Woche | Managed Settings, Team-Basis, Plugin-Marketplace | geprüfte `managed-settings.json`, Pilot-Repos eingerichtet |
| 2 Pilot | 4-8 Wochen | Nutzung unter echten Bedingungen | Kennzahlen, Feedback, Liste offener Punkte |
| 3 Entscheidung | 1 Woche | Auswertung gegen die Ziele | Entscheidungsvorlage: ausweiten, anpassen oder stoppen |
| 4 Ausweitung | team-weise | Rollout an weitere Teams | Onboarding je Team, Audit in allen Repos |
| 5 Betrieb | laufend | Pflege von Basis, Kosten und Versionen | Quartalsreview der Regeln und Kosten |

Die Freigabe läuft in Phase 0 an. Für den Pilot reicht häufig eine eingeschränkte Freigabe, etwa nur für Repos ohne personenbezogene Daten. Das klärst du mit IT-Sicherheit und Datenschutz; den Rahmen beschreibt der [Pilotplan](../rollout/pilotplan.md).

## Wen nehme ich in den Pilot?

- 15-20 Entwickler aus 2-3 Teams mit unterschiedlichen Stacks, zum Beispiel Backend, Frontend und Infrastruktur.
- Mischung aus erfahrenen und neuen Kollegen, damit du siehst, wie gut Onboarding funktioniert.
- Pro Team ein Pilot-Champion, der Fragen sammelt und Regeln mitpflegt.
- Repos ohne Echtdaten von Kunden oder Beschäftigten, solange der Datenschutz nicht freigegeben hat.

Die Kostendoku empfiehlt ausdrücklich, mit einer kleinen Pilotgruppe zu starten und mit den Tracking-Werkzeugen eine Basis zu messen, bevor du breiter ausrollst ([Costs](https://code.claude.com/docs/en/costs)).

## Welche gemeinsame Basis brauchen alle?

| Ebene | Was | Wer pflegt | Werkzeug |
| --- | --- | --- | --- |
| Unternehmen | Managed Settings: Bypass gesperrt, deny-Regeln für Secrets, Telemetrie aus, Login-Organisation, Marketplaces, MCP-Allowlist | IT, Plattform-Team | [vorlagen/managed-settings.json](../../vorlagen/managed-settings.json), MDM |
| Rechner | Plugin `team-basis` mit Schutz-Hooks und Skills | Plattform-Team | `claude plugin install team-basis@claude-code-best-practices` |
| Repo | `.claude/settings.json`, Hooks, `.claude/schutz.json`, Regeln, Subagents | Team | `claude-team einrichten` |
| Projektwissen | CLAUDE.md mit Befehlen und Konventionen | Team | `claude-team einrichten`, `/init` |
| Prüfung | Audit in CI | Team, Plattform-Team | GitHub Action `pexon-consulting/claude-code-best-practices@v0.2.0` |

### Repo-Basis mit claude-team einrichten

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team einrichten . --dry-run
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team einrichten .
```

Der Befehl legt CLAUDE.md (mit erkannten Befehlen aus `package.json`, `pyproject.toml` oder `Makefile`), `.claude/settings.json`, Hooks, `.claude/schutz.json`, Regeln, Agents, Skills und `.mcp.json.example` an. Er überschreibt nie: Bei vorhandener settings.json entsteht `.claude/settings.vorschlag.json`, bei vorhandener CLAUDE.md `CLAUDE.vorschlag.md`. Mit `--profil streng` sperrt er zusätzlich WebFetch, WebSearch, `curl`, `wget`, `nc`, `scp` und `ssh`.

### Plugin team-basis verteilen

```bash
claude plugin marketplace add pexon-consulting/claude-code-best-practices
claude plugin install team-basis@claude-code-best-practices
```

Zentral geht es über `extraKnownMarketplaces` und `enabledPlugins` in den Managed Settings. Ein Plugin, das dort auf `false` steht, ist auf allen Ebenen gesperrt. Für die zentrale Verteilung forkst du das Repo in die eigene Organisation, prüfst den Fork und pinnst ihn auf einen Tag, statt das öffentliche Repo direkt einzutragen. Plugins führen Hooks auf jedem Rechner aus.

```json
{
  "extraKnownMarketplaces": {
    "claude-code-best-practices": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-code-best-practices",
        "ref": "v0.2.0"
      }
    }
  },
  "enabledPlugins": {
    "team-basis@claude-code-best-practices": true
  }
}
```

### Managed Settings verteilen

Die Unternehmensregeln liegen in `managed-settings.json` im Systemverzeichnis oder kommen per MDM. Pfade, Vorrang und Prüfung beschreibt [Claude Code Enterprise](./claude-code-enterprise.md). Für den Pilot reicht oft die Datei auf den Pilotrechnern.

## Wer ist im Rollout wofür zuständig?

| Rolle | Aufgabe im Rollout | Unterlage |
| --- | --- | --- |
| Management | Ziel, Budget, Entscheidung nach dem Pilot | [Pilotplan](../rollout/pilotplan.md), Entscheidungsvorlage |
| IT-Sicherheit | Freigabe der Konfiguration, Managed Settings, MCP-Allowlist | [Freigabe-Paket](../rollout/freigabe-paket.md) |
| Datenschutzbeauftragter | Vertragsweg, AVV, TOM, DSFA-Prüfung | [TOM-Vorlage](../rollout/tom-vorlage.md), [DSFA-Vorlage](../rollout/dsfa-vorlage.md) |
| Legal und Einkauf | Vertrag, Lizenzmodell, Beschaffungsweg | [Freigabe-Paket](../rollout/freigabe-paket.md) |
| Betriebsrat | Information, Regelungspunkte zur Protokollierung | [Infoblatt](../rollout/betriebsrat-infoblatt.md) |
| Plattform-Team | Basis bauen, verteilen, Versionen pflegen | diese Anleitung, [Enterprise](./claude-code-enterprise.md) |
| Pilot-Champions | Fragen sammeln, Regeln pflegen, Fehlalarme melden | Onboarding-Checkliste |
| Controlling | Budgets und Auswertung | [Kostenrichtlinie](../rollout/kostenrichtlinie.md) |

## Was gehört in die Schulung?

Eine Einführung von 2-3 Stunden je Team reicht für den Start, wenn sie praktisch ist. Bewährte Inhalte:

1. Wie Claude Code arbeitet: Kontext, Tools, Rückfragen, Permission-Modi.
2. Unsere Regeln: was gesperrt ist und warum, was mit Echtdaten passiert, wie man eine Ausnahme beantragt.
3. Der Ablauf erkunden, planen, umsetzen, testen, committen an einer echten Aufgabe aus dem eigenen Repo.
4. CLAUDE.md pflegen: Befehle, Konventionen, was der Agent nicht tun soll ([CLAUDE.md](./claude-md.md)).
5. Kosten im Blick: `/usage`, `/context`, `/compact`, Modellwahl.
6. Review: KI-Änderungen wie Änderungen von Kollegen prüfen, `/security-review` vor dem Merge.

## Onboarding-Checkliste für neue Nutzer

- [ ] Claude Code installiert und mit `claude doctor` geprüft ([Installation](./claude-code-installieren.md)).
- [ ] Anmeldung mit dem Firmenkonto oder Cloud-Anbieter, nicht mit einem privaten Konto.
- [ ] `/status` zeigt `Enterprise managed settings` in der Zeile `Setting sources`.
- [ ] Plugin `team-basis` installiert, `/hooks` zeigt die Schutz-Hooks.
- [ ] Im Pilot-Repo liegen CLAUDE.md und `.claude/settings.json`; `claude-team audit .` meldet keine Fehler.
- [ ] Regeln gelesen: keine Echtdaten in Prompts, keine Secrets kopieren, Bypass-Modus ist gesperrt.
- [ ] Arbeitsablauf geübt: erkunden, mit Plan Mode planen, umsetzen, testen, committen ([Workflow](./claude-code-workflow.md)).
- [ ] `/usage` und `/context` bekannt, um Verbrauch und Kontext im Blick zu behalten.
- [ ] Ansprechpartner für Fragen und für gemeldete Fehlalarme der Hooks bekannt.

## Welche Kennzahlen messe ich im Pilot?

| Kennzahl | Quelle | Wofür |
| --- | --- | --- |
| Aktive Nutzer je Woche | Analytics der Admin-Konsole oder OpenTelemetry `claude_code.session.count` | Akzeptanz |
| Kosten je Entwickler und aktivem Tag | Spend-Report, Console, Cloud-Abrechnung oder `claude_code.cost.usage` | Budget, Vergleich mit Doku-Richtwert |
| Tokens je Modell | `claude_code.token.usage` | Modellwahl |
| Commits und Pull Requests mit Claude Code | `claude_code.commit.count`, `claude_code.pull_request.count` | Einfluss auf den Ablauf |
| Blockierte Aktionen der Hooks | Rückmeldungen, `.claude/protokoll/` | Fehlalarme, Regelpflege |
| Audit-Befunde je Repo | `claude-team audit` in CI | Einhaltung der Basis |
| Zufriedenheit und Nutzen | Umfrage im Team zu Woche 2, 4 und Ende | qualitative Bewertung |

OpenTelemetry-Metriken enthalten `user.email`, sobald verfügbar. Kennzahlen je Person können eine Leistungs- und Verhaltenskontrolle ermöglichen; kläre Auswertungstiefe und Zugriff vorher mit dem Betriebsrat ([Infoblatt](../rollout/betriebsrat-infoblatt.md)). Für die Pilotauswertung reichen häufig Team-Summen.

Als Vergleichswert nennt die Doku: "Across enterprise deployments, the average cost is around $13 per developer per active day and $150-250 per developer per month, with costs remaining below $30 per active day for 90% of users." ([Costs](https://code.claude.com/docs/en/costs), abgerufen 15.10.2026). Deine eigenen Werte hängen von Modell, Aufgaben und Kontextgröße ab.

## Beispiele für den Rollout im Team

### Beispiel 1: Audit aller Pilot-Repos lokal

```bash
for repo in ~/code/service-a ~/code/frontend ~/code/infra; do
  uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team audit "$repo" --format text
done
```

Zum Start des Pilots, um alle Repos auf denselben Stand zu bringen.

### Beispiel 2: Audit als GitHub Action

```yaml
name: Claude Code Audit
on: [pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: pexon-consulting/claude-code-best-practices@v0.2.0
        with:
          schwelle: fehler
```

Damit keine Pull Requests die Team-Basis aufweichen.

### Beispiel 3: Pilot-Kennzahlen per OpenTelemetry an den eigenen Collector

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

In die Managed Settings, nicht in die Projekt-settings.json: Dort ignoriert Claude Code ab v2.1.282 `CLAUDE_CODE_ENABLE_TELEMETRY` und die Exporter-Variablen.

### Beispiel 4: Firmenregeln als Organisations-CLAUDE.md

```json
{
  "claudeMd": "# Regeln im Unternehmen\n\n- Keine Echtdaten in Prompts.\n- Tests vor jedem Commit.\n- Bei Unklarheit nachfragen statt raten."
}
```

Für Regeln, die in jedem Repo gelten sollen, ohne dass jedes Team sie kopiert.

### Beispiel 5: Teams mit eigenen Repos auf den Vorschlag prüfen lassen

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team einrichten . --ohne claude-md,agents
git diff --no-index .claude/settings.json .claude/settings.vorschlag.json
```

Für Repos, die schon eine settings.json haben; der Vorschlag führt beides zusammen und das Team entscheidet.

## Schritt für Schritt

1. Ziele, Teilnehmer und Abbruchkriterien im [Pilotplan](../rollout/pilotplan.md) festhalten.
2. [Freigabe-Paket](../rollout/freigabe-paket.md) an IT-Sicherheit, Datenschutz, Legal und Betriebsrat geben.
3. Betriebsvariante wählen ([DSGVO-Anleitung](./claude-code-dsgvo.md)) und Konten oder Cloud-Zugang einrichten.
4. Managed Settings aus der [Vorlage](../../vorlagen/managed-settings.json) anpassen und auf den Pilotrechnern verteilen.
5. Pilot-Repos mit `claude-team einrichten` ausstatten, Audit-Action hinzufügen.
6. Kick-off mit Onboarding-Checkliste und einer gemeinsamen Übungsaufgabe.
7. Wöchentlich 30 Minuten Austausch mit den Champions: Probleme, Fehlalarme, Regeländerungen.
8. Kennzahlen zu Woche 2, 4 und Pilotende auswerten, [Kostenrichtlinie](../rollout/kostenrichtlinie.md) prüfen.
9. Entscheidungsvorlage erstellen und an das Management geben.
10. Bei Zustimmung team-weise ausweiten, Basis und Version im Quartal prüfen.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Pilot ohne Messung | Entscheidung nach Bauchgefühl | Kennzahlen vor Start festlegen |
| Jedes Team baut eigene Settings | unterschiedliche Schutzstände | `claude-team einrichten` und Audit in CI |
| Freigabe erst nach dem Pilot | wochenlange Pause vor dem Rollout | Freigabe-Paket in Phase 0 starten |
| Regeln nur im Wiki | niemand hält sie ein | Regeln technisch in Managed Settings und Hooks |
| Telemetrie-Variablen in `.claude/settings.json` | Collector bekommt keine Daten | in Managed oder Nutzer-Settings setzen |
| Kein Ansprechpartner | Fehlalarme führen zum Abschalten der Hooks | Champion je Team, Ausnahmen über `pfade_ausnehmen` |

## Häufige Fragen

### Wie viele Entwickler sollten in den Pilot?

15-20 Entwickler aus 2-3 Teams sind ein guter Startpunkt: genug für belastbare Zahlen, wenig genug für engen Austausch. Kleinere Firmen starten mit einem Team.

### Wie lange dauert ein Claude-Code-Pilot?

4-8 Wochen. Unter 4 Wochen dominieren Einarbeitung und Neugier, über 8 Wochen verliert der Pilot an Spannung.

### Was kostet Claude Code im Team?

Die Doku nennt als Durchschnitt in Unternehmen rund 13 US-Dollar je Entwickler und aktivem Tag und 150-250 US-Dollar je Entwickler und Monat. Deine Werte misst du im Pilot; Budgets regelt die [Kostenrichtlinie](../rollout/kostenrichtlinie.md).

### Wie verteile ich dieselbe Konfiguration an alle?

Unternehmensregeln über Managed Settings per MDM oder Datei, Hooks und Skills über das Plugin `team-basis`, Repo-Konfiguration über `claude-team einrichten` und Git. Das Audit in CI stellt sicher, dass es so bleibt.

### Muss der Betriebsrat zustimmen?

Ob und in welchem Umfang Mitbestimmung besteht, klärst du mit Personalabteilung und Betriebsrat, etwa zu § 87 Abs. 1 Nr. 6 BetrVG. Das [Infoblatt](../rollout/betriebsrat-infoblatt.md) beschreibt, was protokolliert wird und was nicht.

## Weiterlesen

- [Claude Code Enterprise: Managed Settings](./claude-code-enterprise.md)
- [Claude Code DSGVO](./claude-code-dsgvo.md)
- [Claude Code Sicherheit](./claude-code-sicherheit.md)
- [Claude Code Kosten](./claude-code-kosten.md)
- [CLAUDE.md](./claude-md.md)
- Rollout-Unterlagen: [Übersicht](../rollout/README.md), [Pilotplan](../rollout/pilotplan.md), [Freigabe-Paket](../rollout/freigabe-paket.md)
- [Claude Code vs Codex und Cursor: Unterschiede für Teams](./claude-code-vs-codex-cursor.md)
- [Claude Code Review: automatische Reviews mit GitHub Actions](./claude-code-review-github-actions.md)
