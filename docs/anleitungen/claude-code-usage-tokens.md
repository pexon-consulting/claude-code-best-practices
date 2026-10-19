# Claude Code Usage: Token-Verbrauch messen und senken

Den Token-Verbrauch von Claude Code siehst du mit `/usage` (Aliase `/cost` und `/stats`): Der Befehl zeigt Session-Kosten, Tokens je Modell, Cache-Treffer und bei Abos die Auslastung der Planlimits. Was den Kontext füllt, zeigt `/context`; senken lässt sich der Verbrauch vor allem mit `/clear` zwischen Aufgaben, einer kurzen CLAUDE.md, Skills und Regeln statt Dauertext, Subagents für große Ausgaben und dem passenden Modell und Effort.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- `/usage` zeigt den Verbrauch der aktuellen Sitzung; der Dollarbetrag ist eine lokale Schätzung zum Listenpreis, verbindlich ist die Abrechnung in der Claude Console.
- `/context` zeigt als Raster, was im Kontextfenster steckt, mit Hinweisen, was sich einsparen lässt.
- Claude Code schickt bei jeder Anfrage die ganze Konversation mit, deshalb kostet eine lange Sitzung auch bei kurzen Fragen viel.
- Die größten Hebel laut Doku sind `/clear` zwischen unabhängigen Aufgaben und das passende Modell für die Aufgabe.
- Eine Statuszeile mit `cost.total_cost_usd` und `context_window.used_percentage` macht den Verbrauch dauerhaft sichtbar.
- Im Headless-Modus begrenzt `--max-budget-usd` die Kosten eines Laufs.

## Wie sehe ich den Token-Verbrauch in Claude Code?

### /usage, /cost und /stats

`/usage` ist ein Befehl mit drei Namen, `/cost` und `/stats` sind Aliase. Der Block **Session** oben zeigt die aktuelle Sitzung:

```text
Total cost:            $0.55
Total duration (API):  6m 20s
Total duration (wall): 6h 33m 10s
Total code changes:    0 lines added, 0 lines removed
Usage by model:
   claude-sonnet-4-6:  1.2k input, 5.3k output, 940.0k cache read, 50.0k cache write ($0.55)
```

Wichtig zum Lesen:

- Den Betrag rechnet Claude Code lokal aus Token-Zahlen zum Listenpreis aus. Hat die Organisation in Managed Settings eine Tabelle `modelPricing` hinterlegt (ab v2.1.242), steht dahinter `at your organization's configured rates`.
- Für Pro und Max ist der Session-Betrag nicht abrechnungsrelevant, weil die Nutzung im Abo steckt. Abonnenten sehen auf demselben Bildschirm Balken für die Planlimits.
- `/clear` setzt die Summen zurück (seit v2.1.211).
- Ab v2.1.251 zeigt eine Zeile `Prompt cache (main)` Anfragen, Anteil der Tokens aus dem Cache, Cache-Fehlschläge und ob der Cache noch warm ist.

Auf Pro, Max, Team und Enterprise zeigt `/usage` zusätzlich eine Aufschlüsselung: welcher Anteil auf Skills, Subagents, Plugins und einzelne MCP-Server entfällt, welche Verhaltensweisen (lange Kontexte, Cache-Fehlschläge) über 10 % des Verbrauchs ausmachen, und ab v2.1.242 die teuersten `/loop`-Aufgaben. Mit `d` und `w` wechselst du zwischen 24 Stunden und 7 Tagen. Die Werte stammen aus der lokalen Historie dieses Rechners.

### /context: was steckt im Kontextfenster?

```text
/context
/context all
```

Das Raster zeigt die Belegung nach Kategorien: System-Prompt, CLAUDE.md und Auto Memory, MCP-Tool-Namen, Skill-Beschreibungen und die Konversation. Dazu kommen Hinweise auf kontextlastige Tools und aufgeblähte Memory-Dateien. `all` klappt die Einzelposten aus.

Schon vor deiner ersten Eingabe liegen CLAUDE.md, Auto Memory, MCP-Tool-Namen und Skill-Beschreibungen im Kontext. Jede gelesene Datei kommt hinzu.

### Der Zähler neben dem Spinner

Die Zeile beim Arbeiten, etwa `(10m 27s · ↓ 5.5k tokens)`, zählt nur die Ausgabe des aktuellen Turns, also Text, Tool-Aufrufe und Thinking. Was an das Modell geht (Prompt, Verlauf, Kontext), bewegt diese Zahl nicht. Sie ist deshalb kein Maß für die Kosten einer Anfrage.

### /insights: wie du arbeitest

`/insights` erzeugt einen HTML-Bericht über deine letzten Sitzungen auf diesem Rechner: woran du arbeitest, wo es hakt, welche Funktionen sich lohnen würden. Der Bericht liegt unter `~/.claude/usage-data/report.html`. Er verbraucht selbst Tokens.

### ccusage

ccusage ist ein bekanntes Community-Werkzeug, das lokale Claude-Code-Protokolle auswertet. Es stammt nicht von Anthropic. Wer es einsetzt, prüft vorher Herkunft, Version und was es liest, wie bei jedem Werkzeug, das auf `~/.claude/` zugreift.

## Warum steigt der Verbrauch in langen Sitzungen?

Die Doku nennt diese Gründe:

| Ursache | Was passiert | Gegenmittel |
| --- | --- | --- |
| Langer Kontext | jede Anfrage enthält den ganzen Verlauf, jede Tool-Runde eine weitere Anfrage | `/clear` zwischen Aufgaben, `/compact` mit Fokus |
| Cache-Fehlschlag nach Pause | die erste Nachricht nach Ablauf der Cache-Lebensdauer verarbeitet den ganzen Kontext neu | Pausen einplanen, nach langer Pause neu beginnen |
| Zeitgesteuerte Aufgaben | `/loop` und geplante Aufgaben senden den ganzen Kontext bei jedem Lauf | Aufgaben beenden, die niemand mehr braucht |
| Subagents und Workflows | jeder Subagent sendet eigene Anfragen | kleineres Modell für Subagents |
| Agent Teams | jedes aktive Teammitglied verbraucht Tokens, bis es endet | Teams klein halten, Mitglieder beenden |
| Kompaktierung | `/compact` liest den ganzen Verlauf, den es zusammenfasst | für einen echten Neustart `/clear`, das kostet nichts |

Die Cache-Lebensdauer beträgt laut Doku im Abo eine Stunde und fällt beim Verbrauch von Usage Credits auf fünf Minuten; mit API-Schlüssel oder Cloud-Anbieter sind es standardmäßig fünf Minuten.

## Wie spare ich Tokens in Claude Code?

### 1. Kontext aktiv verwalten

- `/clear` beim Wechsel zu einer unabhängigen Aufgabe. Vorher mit `/rename` benennen, dann findest du die Sitzung mit `/resume` wieder.
- `/compact <anweisung>` behält, was du nennst: `/compact Behalte nur die geänderten Dateien und die Testbefehle`.
- Über `/rewind` lässt sich ein Teil der Konversation zusammenfassen (**Summarize from here** oder **Summarize up to here**).
- `/btw <frage>` beantwortet eine Nebenfrage, ohne dass sie in den Verlauf eingeht.
- `/autocompact 500k` legt fest, ab welcher Füllung automatisch kompaktiert wird.

### 2. CLAUDE.md kurz halten

CLAUDE.md wird bei jedem Start geladen und bei jeder Anfrage mitgeschickt. Die Doku empfiehlt unter 200 Zeilen. Block-HTML-Kommentare `<!-- ... -->` werden vor dem Einspeisen entfernt. `@`-Imports sparen keinen Kontext, sie laden beim Start mit. Siehe [CLAUDE.md](./claude-md.md) und Prüfregel [CC002](../regeln.md#cc002).

### 3. Regeln mit paths statt Dauertext

Regeln unter `.claude/rules/` mit `paths` im Frontmatter laden erst, wenn Claude eine passende Datei anfasst. Siehe [Claude Code Rules](./claude-code-rules.md).

### 4. Skills statt Abläufe in der CLAUDE.md

Ein Skill lädt seinen Inhalt erst beim Aufruf, im Kontext steht vorher nur die Beschreibung. Mit `disable-model-invocation: true` steht nicht einmal die Beschreibung im Kontext; der Skill läuft dann nur über `/name`. Siehe [Claude Code Skills](./claude-code-skills.md).

### 5. MCP-Ausgaben begrenzen

MCP-Tool-Definitionen sind standardmäßig zurückgestellt: Im Kontext stehen nur Namen, die Schemas lädt Claude bei Bedarf. Für die Ausgaben gilt: Warnung ab 10.000 Tokens, Standardlimit 25.000 Tokens über `MAX_MCP_OUTPUT_TOKENS`. Ungenutzte Server schaltest du mit `/mcp` ab. CLI-Werkzeuge wie `gh` oder `aws` sind laut Doku sparsamer als MCP-Server, weil sie keine Tool-Liste mitbringen. Siehe [Claude Code MCP](./claude-code-mcp.md).

### 6. Subagents für viel Ausgabe

Testläufe, Logdateien und Doku-Recherche erzeugen viel Text. Ein Subagent arbeitet in eigenem Kontext und liefert nur eine Zusammenfassung zurück. Seine Anfragen zählen trotzdem zum Verbrauch, deshalb für einfache Aufgaben `model: haiku` setzen. Siehe [Claude Code Subagents](./claude-code-subagents.md).

### 7. Modell und Effort passend wählen

Sonnet erledigt laut Doku die meisten Programmieraufgaben gut und kostet weniger als Opus. Opus lohnt sich für Architekturentscheidungen und mehrstufiges Denken. Thinking-Tokens werden als Ausgabe-Tokens abgerechnet; bei einfachen Aufgaben senkt `/effort low` den Verbrauch. Bei Opus 5.5, Sonnet 5.5, Haiku 5.5 und den Fable-Modellen lässt sich Thinking nicht ganz abschalten, dort steuerst du nur über Effort.

### 8. Präzise Prompts

"Verbessere die Codebasis" löst breites Suchen aus. "Ergänze Eingabevalidierung in der Login-Funktion in auth.ts" führt zu wenigen gezielten Dateizugriffen.

## Beispiele für Usage und Tokens

### Beispiel 1: Statuszeile mit Modell, Kosten und Kontext

Wenn du den Verbrauch immer im Blick haben willst. Datei `~/.claude/statusline.sh`:

```bash
#!/bin/bash
input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
printf '[%s] $%.2f | %s%% Kontext\n' "$MODEL" "$COST" "$PCT"
```

Ausführbar machen mit `chmod +x ~/.claude/statusline.sh` und in `~/.claude/settings.json` eintragen:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 0
  }
}
```

`cost.total_cost_usd` ist dieselbe Schätzung wie in `/usage`. Alternativ beschreibst du mit `/statusline` in Worten, was angezeigt werden soll. Mehr in [Claude Code Statusline](./claude-code-statusline.md).

### Beispiel 2: Kompaktierungsregeln in der CLAUDE.md

Wenn nach `/compact` immer dieselben Informationen fehlen.

```markdown
# Compact instructions

Beim Kompaktieren immer behalten: Liste der geänderten Dateien, Testbefehle
und offene Fehlermeldungen. Diskussionen über verworfene Ansätze weglassen.
```

### Beispiel 3: Subagent-Modell und MCP-Limit für das Team festlegen

Wenn Subagents im Team standardmäßig ein günstiges Modell nutzen sollen. In `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku",
    "MAX_MCP_OUTPUT_TOKENS": "25000"
  }
}
```

Einzelne Subagents, die mehr können müssen, setzen im Frontmatter ihr eigenes `model`.

### Beispiel 4: Testausgabe vor dem Lesen filtern (Hook)

Wenn Testläufe tausende Zeilen in den Kontext spülen. Das Beispiel aus der Kosten-Doku schreibt den Testbefehl so um, dass nur Fehler zurückkommen. Datei `~/.claude/hooks/filter-test-output.sh`:

```bash
#!/bin/bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command')
if [[ "$cmd" =~ ^(npm test|pytest|go test) ]]; then
  filtered_cmd="$cmd 2>&1 | grep -A 5 -E '(FAIL|ERROR|error:)' | head -100"
  echo "$input" | jq --arg filtered "$filtered_cmd" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "allow", updatedInput: (.tool_input + {command: $filtered})}}'
else
  echo "{}"
fi
```

Eintrag in `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/filter-test-output.sh" }
        ]
      }
    ]
  }
}
```

Achtung: Der Hook gibt `permissionDecision: "allow"` zurück und genehmigt damit den Testbefehl ohne Rückfrage. Mit `/hooks` prüfst du, ob er registriert ist.

### Beispiel 5: Kosten eines Headless-Laufs begrenzen und auslesen

Wenn Skripte oder CI-Jobs ein festes Budget haben.

```bash
claude -p "Führe die Tests aus und behebe Fehler" \
  --max-turns 10 \
  --max-budget-usd 2.00 \
  --output-format json \
  --allowedTools "Read,Edit,Bash(npm test *)" \
  | jq '{ergebnis: .result, kosten: .total_cost_usd}'
```

`--max-budget-usd` stoppt den Lauf, wenn die geschätzten Kosten den Betrag erreichen; die Ausgaben können ihn leicht überschreiten, also Puffer lassen. Subagents zählen mit. Beide Flags gelten nur mit `-p`. Mehr in [Claude Agent SDK](./claude-agent-sdk.md).

### Beispiel 6: Modell und Effort für eine Aufgabe wechseln

Wenn eine Routineaufgabe kein großes Modell braucht.

```text
/model sonnet
/effort low
Benenne die Variable usr in allen Dateien unter src/api in user um.
```

Im `/model`-Picker wechselst du mit `s` nur für die aktuelle Sitzung, ohne den Default zu ändern. `opusplan` nutzt Opus im Plan Mode und Sonnet bei der Umsetzung.

### Beispiel 7: Verbrauch im Team per OpenTelemetry sammeln

Wenn du Tokens und Kosten je Nutzer in deinem eigenen Monitoring sehen willst, auch bei Bedrock oder Vertex.

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  }
}
```

Endpunkt und Protokoll setzt du zusätzlich nach https://code.claude.com/docs/en/monitoring-usage. OpenTelemetry ist laut Doku die einzige Option, die Token- und Kostenmetriken je Nutzer nahezu in Echtzeit in den eigenen Stack bringt. Mit dem Betriebsrat klären, welche Auswertung je Person zulässig ist.

## Schritt für Schritt: Verbrauch in einer Woche halbieren

1. Ausgangswert messen: eine Woche normal arbeiten und am Ende `/usage` mit `w` (7 Tage) ansehen. Notieren, welche Skills, Subagents und MCP-Server den größten Anteil haben.
2. Statuszeile aus Beispiel 1 einrichten, damit Kontext und Kosten sichtbar bleiben.
3. `/context` in einer frischen Sitzung ausführen: Wie viel belegen CLAUDE.md, MCP und Skills schon vor dem ersten Prompt?
4. CLAUDE.md auf unter 200 Zeilen kürzen; Abläufe in Skills, Bereichsregeln nach `.claude/rules/` mit `paths`.
5. Ungenutzte MCP-Server mit `/mcp` abschalten, wo es geht CLI-Werkzeuge nutzen.
6. Gewohnheit ändern: `/clear` bei jedem Aufgabenwechsel, nach zwei erfolglosen Korrekturen neu starten.
7. Default-Modell prüfen: Sonnet als Standard, Opus gezielt mit `/model`.
8. Nach einer Woche erneut messen und vergleichen.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Eine Sitzung für den ganzen Tag | Verbrauch steigt, Antworten werden schlechter | `/clear` zwischen Aufgaben |
| Den Spinner-Zähler als Kosten lesen | Zahl wirkt klein, Rechnung ist hoch | `/usage` nutzen, der Zähler misst nur die Ausgabe des Turns |
| Session-Betrag als Rechnung behandeln | Abweichung zur Console | Betrag ist eine Schätzung zum Listenpreis; maßgeblich ist die Console oder Cloud-Abrechnung |
| Lange CLAUDE.md mit Workflows | hoher Grundverbrauch in `/context` | Abläufe in Skills auslagern |
| Viele MCP-Server dauerhaft aktiv | große Ausgaben, viele Tool-Namen | `/mcp` aufräumen, `MAX_MCP_OUTPUT_TOKENS` bewusst setzen |
| `/compact` statt `/clear` beim Themenwechsel | Kompaktierung kostet selbst Tokens | bei neuem Thema `/clear` |
| Opus als Default für alles | hohe Kosten bei Routine | Sonnet als Default, Opus gezielt |

## Häufige Fragen

### Wie sehe ich, wie viele Tokens Claude Code verbraucht?

Mit `/usage` in der laufenden Sitzung, auch erreichbar als `/cost` oder `/stats`. Der Block Session zeigt Eingabe-, Ausgabe- und Cache-Tokens je Modell und eine Kostenschätzung; `/context` zeigt, wofür der Kontext belegt ist.

### Was ist der Unterschied zwischen /cost und /usage?

Keiner, `/cost` und `/stats` sind Aliase von `/usage`. Auf Abos zeigt der Befehl zusätzlich die Auslastung der Planlimits und eine Aufschlüsselung nach Skills, Subagents, Plugins und MCP-Servern.

### Warum ist mein Claude-Code-Limit so schnell erreicht?

Meist wegen langer Sitzungen: Claude Code schickt bei jeder Anfrage den ganzen Verlauf mit, nach Pausen fällt der Cache weg, und Subagents, Teams oder `/loop`-Aufgaben senden eigene Anfragen. `/usage` markiert Verhaltensweisen, die über 10 % des Verbrauchs ausmachen, mit einem Tipp.

### Spart /compact Tokens?

Ja für die folgenden Anfragen, weil der Verlauf danach kürzer ist, aber die Kompaktierung selbst ist eine große Anfrage. Für einen echten Neustart ohne Bezug zum Vorherigen ist `/clear` günstiger, es kostet nichts.

### Ist ccusage ein offizielles Tool?

Nein, ccusage ist ein Community-Werkzeug und nicht von Anthropic. Die offiziellen Wege sind `/usage`, die Statuszeile, die Claude Console, die Analytics-Ansichten für Team und Enterprise sowie OpenTelemetry.

### Wie begrenze ich die Kosten eines automatisierten Laufs?

Mit `--max-budget-usd <betrag>` und `--max-turns <n>` im Headless-Modus (`claude -p`). Im Agent SDK heißen die Optionen `maxBudgetUsd` und `maxTurns` (TypeScript) bzw. `max_budget_usd` und `max_turns` (Python).

## Weiterlesen

- [Claude Code Kosten: Abo, API, Budgets](./claude-code-kosten.md)
- [Claude Code Statusline](./claude-code-statusline.md)
- [Claude Code Subagents](./claude-code-subagents.md)
- [Claude Code Skills](./claude-code-skills.md)
- [CLAUDE.md](./claude-md.md)
- Kostenrichtlinie für Teams: [`../rollout/kostenrichtlinie.md`](../rollout/kostenrichtlinie.md)
