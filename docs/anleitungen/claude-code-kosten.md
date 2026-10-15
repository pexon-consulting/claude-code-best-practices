# Claude Code Kosten: Abo oder API, Budgets und Limits im Team

Was Claude Code pro Entwickler kostet, hängt von Modellwahl, Größe der Codebasis und Arbeitsweise ab; laut offizieller Kosten-Doku liegen die Kosten in Unternehmensumgebungen im Schnitt bei etwa 13 US-Dollar pro Entwickler und aktivem Tag und 150-250 US-Dollar pro Entwickler und Monat, bei 90 % der Nutzer unter 30 US-Dollar pro aktivem Tag. Abgerechnet wird je nach Zugang über ein Abo mit Kontingent pro Sitz, nach Tokens über die Claude API oder nach Tokens über Bedrock, Vertex AI oder Foundry. Gegen Ausreißer helfen Budgets: Spend Limits im Abo, Workspace-Limits in der Console, Gateway-Budgets, `--max-budget-usd` für automatisierte Läufe und feste Modelle.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Die einzige offizielle Durchschnittsangabe stammt aus https://code.claude.com/docs/en/costs (abgerufen am 15.10.2026) und ist ein Durchschnitt über Unternehmensumgebungen, keine Zusage.
- Aktuelle Tokenpreise stehen unter https://claude.com/platform/api, Abo-Preise unter https://claude.com/pricing; diese Anleitung nennt bewusst keine Preise.
- Team und Enterprise rechnen über ein Kontingent pro Sitz ab, das sich in einem rollierenden 5-Stunden-Fenster und wöchentlich erneuert; darüber hinaus geht es nur mit Usage Credits und Spend Limits.
- Über die Claude Console und über Cloud-Anbieter wird pro Token abgerechnet; dort deckeln Workspace-Limits, Cloud-Budgets oder ein Gateway die Ausgaben.
- Die teuersten Gewohnheiten sind lange Sitzungen ohne `/clear` und Opus als Default; feste Modelle pro Rolle senken die Kosten am stärksten.
- Ohne Leitplanken sind einzelne Ausreißer teuer: Aus der Praxis werden Fälle von bis zu 10.000 EUR zusätzlichen Token-Kosten pro Entwickler und Monat berichtet.

## Was kostet Claude Code pro Entwickler?

Die Kosten-Doku sagt wörtlich: "Across enterprise deployments, the average cost is around $13 per developer per active day and $150-250 per developer per month, with costs remaining below $30 per active day for 90% of users." (Quelle: https://code.claude.com/docs/en/costs, abgerufen am 15.10.2026.)

Drei Punkte zur Einordnung:

1. Es ist ein Durchschnitt. Einzelne Personen mit vielen parallelen Sitzungen, Agent Teams oder Automatisierung liegen deutlich darüber.
2. Die Doku empfiehlt, mit einer kleinen Pilotgruppe zu starten und erst mit eigenen Messwerten breiter auszurollen.
3. Für Coding-Sitze sollte mehr Budget eingeplant werden als für reine Chat-Sitze: Jeder Claude-Code-Turn trägt Dateiinhalte, Tool-Aufrufe und mehrstufiges Denken. Eine Debugging-Sitzung kann laut Doku mehr verbrauchen als ein Tag Chat.

## Abo, API oder Cloud-Anbieter: welches Modell passt?

| Zugang | Abrechnung | Ausgaben sehen | Ausgaben deckeln | Auswertung je Nutzer |
| --- | --- | --- | --- | --- |
| Pro, Max | Abo, Kontingent mit Limits | `/usage`, claude.ai | eigenes monatliches Spend Limit für Usage Credits | nur eigene Nutzung |
| Team, Enterprise | Kontingent pro Sitz (Standard oder Premium), geteilt mit Chat und Cowork | Spend Report in den Org-Analytics | Spend Limits für Organisation, Gruppe oder Mitglied | Spend-Report-CSV; Enterprise Analytics API |
| Claude Console (API) | pro Token | Usage-Seite der Console | Workspace Spend Limits | Console-Dashboard, Claude Code Analytics API |
| Bedrock, Vertex AI, Foundry | pro Token über das Cloud-Konto | Billing-Konsole der Cloud | Budget-Werkzeuge der Cloud | OpenTelemetry oder Gateway |

Qualitativ:

- **Abo (Team, Enterprise)** ist planbar: Das Kontingent pro Sitz ist die eingebaute Obergrenze. Wer mehr braucht, bekommt Usage Credits, die du mit Limits pro Organisation, Gruppe oder Person begrenzt. Nutzung innerhalb des Kontingents wird nicht in Dollar ausgewiesen.
- **API über die Console** ist flexibel und für Automatisierung und CI üblich. Beim ersten Login legt Claude Code einen Workspace "Claude Code" an, über den die Kosten zentral laufen. Für diesen Workspace lassen sich ein Spend Limit und ein eigenes Rate Limit setzen, damit Claude Code andere Produktionslasten nicht ausbremst.
- **Cloud-Anbieter** passen, wenn Verträge, Region und Abrechnung schon beim Hyperscaler liegen. Claude Code schickt dann keine Metriken an Anthropic; die Analytics-Ansichten von Anthropic decken diese Nutzung nicht ab. Kosten je Nutzer liefern OpenTelemetry oder ein Gateway.

Mischt eine Organisation Anmeldewege, wird jede Person nach dem Weg abgerechnet, mit dem sie sich angemeldet hat.

## Wie setze ich Budgets und Limits im Team?

### Spend Limits im Abo

Für Team und Enterprise schaltet ein Admin unter **Organization settings > Usage** Usage Credits ein und setzt Limits auf Organisations-, Gruppen- oder Personenebene. Entwickler ohne Abrechnungsrechte fordern mit `/usage-credits` beim Admin mehr an. Meldungen wie "You've hit your session limit" betreffen das Kontingent und lassen sich nicht durch Modellwechsel umgehen; "You've hit your individual spend limit" heißt, dass ein von dir oder deiner Organisation gesetztes Limit erreicht ist.

### Rate Limits für API-Organisationen

Die Doku empfiehlt pro Nutzer diese Werte für Tokens pro Minute (TPM) und Anfragen pro Minute (RPM). Sie gelten auf Organisationsebene, einzelne Personen können kurzzeitig mehr nutzen:

| Teamgröße | TPM pro Nutzer | RPM pro Nutzer |
| --- | --- | --- |
| 1-5 | 200k-300k | 5-7 |
| 5-20 | 100k-150k | 2.5-3.5 |
| 20-50 | 50k-75k | 1.25-1.75 |
| 50-100 | 25k-35k | 0.62-0.87 |
| 100-500 | 15k-20k | 0.37-0.47 |
| 500+ | 10k-15k | 0.25-0.35 |

Bei Schulungen mit vielen gleichzeitigen Nutzern brauchst du mehr.

### Gateway-Budgets

Bei Cloud-Anbietern gibt es zwei Gateway-Wege mit Budgets:

- Ein selbst betriebenes **Claude apps gateway** liefert Nutzung je Person, OTLP-Metriken und Spend Limits je Nutzer für Bedrock, Vertex AI und Foundry. Die Statuszeile kann den Stand ab v2.1.251 anzeigen (`rate_limits.spend_limit`).
- Ein **LLM-Gateway** wie LiteLLM erfasst Ausgaben je Schlüssel. Laut Doku setzen das mehrere große Unternehmen ein; das Projekt gehört nicht zu Anthropic und wurde von Anthropic nicht auf Sicherheit geprüft.

Details in [Claude Code LLM-Gateway](./claude-code-llm-gateway.md).

### Budget pro Lauf: --max-budget-usd

Für Skripte, CI und das Agent SDK: `--max-budget-usd` stoppt einen `claude -p`-Lauf, sobald die geschätzten Kosten den Betrag erreichen. Subagents zählen mit; ab v2.1.217 scheitern neue Subagents dann mit `Budget limit reached`. Die Schätzung kann von der Rechnung abweichen und der Betrag kann leicht überschritten werden.

### Modelle pinnen und begrenzen

Mit `availableModels` in Managed Settings schränkst du die wählbaren Modelle ein; `enforceAvailableModels: true` (ab v2.1.175) wendet die Liste auch auf die Default-Option an. Auf Bedrock, Vertex AI und Foundry lösen Aliase wie `sonnet` teils auf ältere Versionen auf, deshalb dort feste Modell-IDs über `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` und `ANTHROPIC_DEFAULT_HAIKU_MODEL` setzen.

### Kosten zu Vertragspreisen anzeigen

Standardmäßig rechnet Claude Code alle angezeigten Beträge zum Listenpreis. Wer andere Konditionen hat, hinterlegt ab v2.1.242 in Managed Settings den Key `modelPricing` mit den Sätzen aus dem Vertrag. Das ändert nur die Anzeige in `/usage`, Statuszeile und OpenTelemetry, nicht die Abrechnung. In Nutzer- oder Projekt-Settings wird der Key ignoriert.

## Beispiele

### Beispiel 1: Modelle für das Team festlegen (Managed Settings)

Wenn Opus nur gezielt und nicht als Default laufen soll.

```json
{
  "model": "sonnet",
  "availableModels": ["sonnet", "haiku", "opus"],
  "enforceAvailableModels": true,
  "env": {
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```

`model` setzt den Standard, `availableModels` die erlaubte Auswahl. Wer Opus komplett ausschließen will, lässt es aus der Liste. Verteilung über die Vorlage [`../../vorlagen/managed-settings.json`](../../vorlagen/managed-settings.json).

### Beispiel 2: Feste Modell-IDs auf Bedrock

Wenn Aliase auf dem Cloud-Anbieter auf ältere Versionen zeigen würden.

```bash
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=eu-central-1
export ANTHROPIC_DEFAULT_SONNET_MODEL='eu.anthropic.claude-sonnet-4-6'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='<haiku-modell-id-aus-der-bedrock-konsole>'
```

Die genauen IDs prüfst du in der eigenen Bedrock-Konsole. Mehr in [Claude Code Bedrock](./claude-code-bedrock.md).

### Beispiel 3: Budget für einen CI-Lauf

Wenn ein nächtlicher Job nie mehr als einen festen Betrag kosten darf.

```bash
claude --bare -p "Aktualisiere die Abhängigkeiten in package.json und führe die Tests aus" \
  --permission-mode acceptEdits \
  --allowedTools "Read,Edit,Bash(npm install *),Bash(npm test *)" \
  --max-turns 15 \
  --max-budget-usd 3.00 \
  --output-format json \
  | jq '{status: .subtype, kosten: .total_cost_usd}'
```

`total_cost_usd` im JSON ist eine Schätzung auf Client-Seite. In GitHub Actions setzt du zusätzlich `--max-turns` in `claude_args` und `timeout-minutes` am Job, siehe [Claude Code Review mit GitHub Actions](./claude-code-review-github-actions.md).

### Beispiel 4: Vertragspreise in der Anzeige (Managed Settings)

Wenn `/usage` und Statuszeile deine Vertragskonditionen zeigen sollen. Ein pauschaler Abschlag:

```json
{
  "modelPricing": {
    "multiplier": 0.8
  }
}
```

`multiplier` unter 1 bildet einen Rabatt ab, über 1 einen Aufschlag (Aufschlag ab v2.1.271). Für Sätze je Modell gibt es `overrides`; die Form steht in https://code.claude.com/docs/en/settings-reference#modelpricing. Prüfen: `/usage` zeigt dann `at your organization's configured rates`.

### Beispiel 5: Kosten je Nutzer per OpenTelemetry

Wenn du über Bedrock oder Vertex abrechnest und trotzdem Kosten je Person sehen willst.

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  }
}
```

Endpunkt und Header ergänzt du nach https://code.claude.com/docs/en/monitoring-usage. Auswertungen je Person mit Betriebsrat und Datenschutzbeauftragtem abstimmen, siehe [`../rollout/betriebsrat-infoblatt.md`](../rollout/betriebsrat-infoblatt.md).

### Beispiel 6: Agent Teams günstig halten

Wenn du Agent Teams testest. Laut Doku verbrauchen Teams etwa 7-mal mehr Tokens als normale Sitzungen, wenn die Teammitglieder im Plan Mode laufen.

```text
Starte zwei Teammitglieder mit Sonnet: eins prüft src/api auf fehlende Tests,
eins prüft src/web. Jedes liefert eine Liste mit Datei und Fund. Beende beide,
sobald die Listen fertig sind.
```

Kleine Teams, fokussierte Prompts, Sonnet für Teammitglieder und beenden, wenn die Arbeit erledigt ist. Mehr in [Claude Code Agent Teams](./claude-code-agent-teams.md).

## Schritt für Schritt: Kostenrichtlinie für ein Team einführen

1. Zugang wählen: Abo (Team oder Enterprise) für planbare Sitze, API oder Cloud für Automatisierung. Oft beides.
2. Pilot mit einer kleinen Gruppe, wie die Doku empfiehlt; Ausgangswerte aus Analytics, Console oder OpenTelemetry sammeln. Siehe [`../rollout/pilotplan.md`](../rollout/pilotplan.md).
3. Obergrenzen festlegen: Spend Limits pro Person im Abo, Workspace-Limit in der Console, Budgets in der Cloud oder im Gateway.
4. Modelle festlegen: Sonnet als Default, Opus gezielt, Haiku für Subagents; per `availableModels` verteilen.
5. Automatisierung absichern: Jeder `claude -p`-Lauf und jeder Actions-Workflow bekommt `--max-turns`, `--max-budget-usd` bzw. Timeouts.
6. Gewohnheiten schulen: `/clear` zwischen Aufgaben, kurze CLAUDE.md, `/usage` regelmäßig ansehen. Siehe [Claude Code Usage und Tokens](./claude-code-usage-tokens.md).
7. Richtlinie schriftlich festhalten und monatlich prüfen: Vorlage [`../rollout/kostenrichtlinie.md`](../rollout/kostenrichtlinie.md).

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Opus als Default für alle | hohe Rechnung bei Routinearbeit | Sonnet als Default, `availableModels` setzen |
| Sitzungen nie geleert | Verbrauch steigt im Tagesverlauf | `/clear` zwischen Aufgaben schulen |
| Usage Credits ohne Limit | unerwartete Zusatzkosten | Spend Limits pro Person oder Gruppe setzen |
| CI ohne Budget | ein fehlerhafter Job läuft lange | `--max-budget-usd`, `--max-turns`, Timeouts |
| Aliase auf Bedrock oder Vertex | anderes Modell als erwartet | feste IDs über `ANTHROPIC_DEFAULT_*_MODEL` |
| `/usage`-Betrag als Rechnung genommen | Abweichung zur Abrechnung | Schätzung zum Listenpreis; `modelPricing` setzen oder Console nutzen |
| Kein Pilot | Budget auf Basis von Annahmen | erst messen, dann ausrollen |

## Häufige Fragen

### Was kostet Claude Code pro Monat?

Laut offizieller Doku im Schnitt 150-250 US-Dollar pro Entwickler und Monat in Unternehmensumgebungen, etwa 13 US-Dollar pro aktivem Tag, bei 90 % der Nutzer unter 30 US-Dollar pro aktivem Tag (Stand der Doku: 15.10.2026). Eure Werte hängen von Modell, Codebasis und Arbeitsweise ab; ein Pilot liefert die belastbare Zahl.

### Ist ein Abo oder die API günstiger?

Das lässt sich nicht pauschal sagen, die aktuellen Preise stehen unter https://claude.com/pricing und https://claude.com/platform/api. Ein Abo mit Sitz-Kontingent ist planbarer, die API rechnet genau nach Verbrauch ab und eignet sich für CI und Automatisierung. Viele Teams kombinieren beides.

### Wie verhindere ich, dass ein Entwickler tausende Euro verbraucht?

Mit harten Obergrenzen: Spend Limits pro Person im Abo, Workspace Spend Limits in der Console oder Budgets je Nutzer im Gateway. Dazu feste Modelle über `availableModels` und `--max-budget-usd` in jeder Automatisierung.

### Was zählt alles zu den Claude-Code-Kosten?

Jede Anfrage mit dem ganzen Kontext, Thinking-Tokens (als Ausgabe abgerechnet), Subagents, Agent Teams, `/compact` und zeitgesteuerte Aufgaben. Dazu kommen kleine Hintergrundanfragen, etwa für Zusammenfassungen früherer Sitzungen. In GitHub Actions kommen Actions-Minuten hinzu.

### Wo sehe ich die Kosten für mein Team?

Bei Team und Enterprise im Spend Report der Org-Analytics, bei der API im Console-Dashboard und über die Claude Code Analytics API, bei Cloud-Anbietern in deren Billing-Konsole. OpenTelemetry funktioniert in allen Varianten.

## Weiterlesen

- [Claude Code Usage: Token-Verbrauch messen und senken](./claude-code-usage-tokens.md)
- [Claude Code LLM-Gateway](./claude-code-llm-gateway.md)
- [Claude Code Bedrock](./claude-code-bedrock.md)
- [Claude Code Enterprise](./claude-code-enterprise.md)
- [Claude Code Team-Rollout](./claude-code-team-rollout.md)
- Vorlage: [Kostenrichtlinie](../rollout/kostenrichtlinie.md)
