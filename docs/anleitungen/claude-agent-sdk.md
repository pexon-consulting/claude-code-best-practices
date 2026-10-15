# Claude Agent SDK: eigene Agenten auf Basis von Claude Code bauen

Das Claude Agent SDK ist eine Bibliothek für Python und TypeScript, die die Agentenschleife von Claude Code in eigene Anwendungen bringt: mit eingebauten Tools, Rechten, Sitzungen, Hooks, Subagents und MCP-Servern. Früher hieß es Claude Code SDK; die Pakete heißen jetzt `@anthropic-ai/claude-agent-sdk` für TypeScript und `claude-agent-sdk` für Python. Für einfache Skripte und CI reicht oft der Headless-Modus der CLI (`claude -p`), das SDK lohnt sich, wenn du Nachrichten, Rechte und Kosten im eigenen Code steuern willst.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Das SDK führt das Claude-Code-Binary aus, es ist im Paket enthalten; du brauchst Node.js 18+ oder Python 3.10+.
- Authentifizierung über `ANTHROPIC_API_KEY` oder Bedrock, Vertex AI, Foundry und Claude Platform on AWS; das SDK lädt keine `.env`-Dateien selbst.
- Drittanbieter dürfen ohne vorherige Zustimmung keinen claude.ai-Login und keine claude.ai-Limits für ihre Produkte anbieten.
- Seit v0.1.0 nutzt das SDK einen minimalen System-Prompt; den von Claude Code bekommst du über das Preset `claude_code`.
- `claude -p` mit `--output-format json`, `--json-schema`, `--max-turns` und `--max-budget-usd` deckt viele Automatisierungen ohne eigenen Code ab.
- `--bare` ist laut Doku der empfohlene Modus für Skripte und SDK-Aufrufe und soll künftig Standard für `-p` werden.

## Was ist der Unterschied zwischen Claude Code und dem Claude Agent SDK?

Die Doku grenzt vier Werkzeuge ab:

| Du willst | Nutze | Was du bekommst |
| --- | --- | --- |
| die Agentenschleife von Claude Code in eine eigene Python- oder TypeScript-Anwendung einbetten | Agent SDK | eine Bibliothek, die das Claude-Code-Binary ausführt, mit Tools, Rechten, Sitzungen und Hooks |
| interaktiv entwickeln oder einmalige Aufgaben im Terminal | Claude Code CLI | die Terminal-Oberfläche für den Alltag |
| die Claude API direkt aus eigenem Code aufrufen | Client SDK | direkter API-Zugriff, die Tool-Schleife schreibst du selbst |
| den Agenten von Anthropic betreiben lassen | Managed Agents | gehostete Agentenschleife mit Sandbox |

Für andere Sprachen als Python und TypeScript empfiehlt die Doku, die CLI als Unterprozess mit `-p` und `--output-format json` aufzurufen.

### Claude Code SDK heißt jetzt Claude Agent SDK

| Vorher | Jetzt |
| --- | --- |
| `@anthropic-ai/claude-code` (als SDK) | `@anthropic-ai/claude-agent-sdk` |
| Python `claude-code-sdk`, Import `claude_code_sdk` | `claude-agent-sdk`, Import `claude_agent_sdk` |
| `ClaudeCodeOptions` | `ClaudeAgentOptions` |

Zwei Verhaltensänderungen beim Umstieg:

- **System-Prompt:** Seit v0.1.0 ist er minimal. Den Prompt von Claude Code bekommst du mit `systemPrompt: { type: "preset", preset: "claude_code" }`.
- **Einstellungsquellen:** `settingSources` lädt standardmäßig alle Quellen, also auch CLAUDE.md und `.claude/settings.json` des Projekts. Mit `settingSources: []` läuft der Agent isoliert; in Python wirkt die leere Liste erst in Versionen nach 0.1.59.

### Namen und Lizenz

Für eigene Produkte erlaubt sind Namen wie "Claude Agent" oder "<Name> Powered by Claude", nicht aber "Claude Code" oder eine Nachahmung des Claude-Code-Brandings. Es gelten die Commercial Terms von Anthropic.

## Wie nutze ich Claude Code headless mit claude -p?

Viele Automatisierungen brauchen keine eigene Anwendung:

| Flag | Wirkung |
| --- | --- |
| `-p "<prompt>"` | Print-Modus: eine Aufgabe, Ausgabe, Ende |
| `--output-format text\|json\|stream-json` | `json` liefert `result`, `session_id`, `total_cost_usd` und Kosten je Modell |
| `--verbose --include-partial-messages` | nötig bzw. sinnvoll für `stream-json` |
| `--json-schema '<schema>'` | strukturierte Ausgabe im Feld `structured_output` |
| `--bare` | überspringt Hooks, Skills, Befehle, Subagents, Plugins, MCP-Server, Auto Memory und CLAUDE.md |
| `--max-turns <n>` | begrenzt die Zahl der Runden, Fehler bei Erreichen |
| `--max-budget-usd <betrag>` | stoppt bei geschätzten Kosten über dem Betrag |
| `--permission-mode <modus>` | etwa `acceptEdits`, `plan`, `auto`, `dontAsk` |
| `--permission-prompts none` | lehnt alles ab, was eine Rückfrage bräuchte (ab v2.1.259) |
| `--allowedTools "<liste>"` | Tools ohne Rückfrage, etwa `"Read,Bash(git diff *)"` |
| `--continue`, `--resume <id>` | Sitzung fortsetzen |

Hinweise:

- `--max-turns` erscheint in `claude --help` von 2.1.294 nicht, ist aber in der CLI-Referenz dokumentiert.
- Bei `--allowedTools` ist das Leerzeichen vor `*` wichtig: `Bash(git diff *)` erlaubt Befehle, die mit `git diff ` beginnen.
- `--bare` braucht `ANTHROPIC_API_KEY` oder einen `apiKeyHelper`, weil der OAuth-Login nicht gelesen wird. Was du brauchst, lädst du explizit: `--append-system-prompt`, `--settings`, `--mcp-config`, `--agents`, `--plugin-dir`.
- Ohne `--bare` führt `claude -p` die Hooks aus `.claude/settings.json` aus und verbindet die Server aus `.mcp.json`, auch in Ordnern, denen du nie vertraut hast. In fremden Repos also `--bare` nutzen.
- Exit-Code 0 bei Erfolg, sonst ungleich 0; Stdin ist auf 10 MB begrenzt.

## Wie baue ich einen ersten Agenten mit dem SDK?

Installation:

```bash
npm install @anthropic-ai/claude-agent-sdk
npm install -D tsx
```

```bash
uv add claude-agent-sdk
```

oder `pip install claude-agent-sdk` in einer virtuellen Umgebung. Schlüssel setzen:

```bash
export ANTHROPIC_API_KEY=<dein-api-key>
```

Wichtige Optionen:

| TypeScript | Python | Zweck |
| --- | --- | --- |
| `allowedTools` | `allowed_tools` | Tools ohne Rückfrage |
| `permissionMode` | `permission_mode` | Rechtemodus, etwa `"acceptEdits"` |
| `systemPrompt` | `system_prompt` | eigener System-Prompt oder Preset |
| `maxTurns` | `max_turns` | Rundenlimit |
| `maxBudgetUsd` | `max_budget_usd` | Kostenlimit pro Aufruf |
| `model` | `model` | Modell |
| `cwd` | `cwd` | Arbeitsverzeichnis |
| `settingSources` | `setting_sources` | welche Einstellungen geladen werden |
| `mcpServers` | `mcp_servers` | MCP-Server |

Die Ergebnisnachricht (`type === "result"` in TypeScript, `ResultMessage` in Python) enthält `subtype` (`"success"`, `"error_max_turns"`, `"error_max_budget_usd"` und weitere), `result`, `session_id`, `num_turns` und `total_cost_usd`. Der Kostenwert ist eine Schätzung auf Client-Seite, keine Abrechnung; in Python ist das Feld optional.

## Beispiele

### Beispiel 1: Minimaler Agent in TypeScript

Wenn ein Agent Fehler in einer Datei finden und beheben soll. Datei `agent.ts`, nach dem Quickstart der Doku:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Prüfe utils.py auf Fehler, die zu Abstürzen führen. Behebe gefundene Fehler.",
  options: {
    allowedTools: ["Read", "Edit", "Glob"],
    permissionMode: "acceptEdits"
  }
})) {
  if (message.type === "assistant" && message.message?.content) {
    for (const block of message.message.content) {
      if ("text" in block) {
        console.log(block.text);
      } else if ("name" in block) {
        console.log(`Tool: ${block.name}`);
      }
    }
  } else if (message.type === "result") {
    console.log(`Fertig: ${message.subtype}`);
  }
}
```

Starten mit `npx tsx agent.ts`. Nutzt dein Projekt CommonJS, benenne die Datei `agent.mts`.

### Beispiel 2: Minimaler Agent in Python

Dasselbe in Python, Datei `agent.py`:

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


async def main():
    async for message in query(
        prompt="Prüfe utils.py auf Fehler, die zu Abstürzen führen. Behebe gefundene Fehler.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"Fertig: {message.subtype}")


asyncio.run(main())
```

Starten mit `uv run agent.py` bzw. `python agent.py`.

### Beispiel 3: Kosten eines Aufrufs ausgeben (Python)

Wenn du den Verbrauch pro Aufruf protokollieren willst.

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    async for message in query(
        prompt="Fasse dieses Projekt in fünf Sätzen zusammen",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep"],
            max_turns=10,
            max_budget_usd=1.00,
        ),
    ):
        if isinstance(message, ResultMessage):
            print(f"Status: {message.subtype}")
            print(f"Geschätzte Kosten: ${message.total_cost_usd or 0}")


asyncio.run(main())
```

`total_cost_usd` enthält auch die Kosten von Subagents. Ein Lauf, der das Budget reißt, endet mit `subtype` `error_max_budget_usd`.

### Beispiel 4: System-Prompt von Claude Code im SDK nutzen (TypeScript)

Wenn sich der Agent wie Claude Code verhalten, aber keine lokalen Einstellungen laden soll.

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Schreib Docstrings für alle Funktionen in utils.py",
  options: {
    systemPrompt: { type: "preset", preset: "claude_code" },
    settingSources: [],
    allowedTools: ["Read", "Edit"],
    permissionMode: "acceptEdits",
    maxTurns: 8
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

`settingSources: []` verhindert, dass CLAUDE.md, Hooks oder Rechte aus dem Arbeitsverzeichnis und `~/.claude` geladen werden.

### Beispiel 5: Strukturierte Ausgabe mit der CLI

Wenn ein Skript eine maschinenlesbare Antwort braucht.

```bash
claude --bare -p "Nenne die Hauptfunktionen in auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}' \
  | jq '.structured_output'
```

Ist das Schema ungültig, endet `claude` mit `Error: --json-schema is not a valid JSON Schema`.

### Beispiel 6: Sitzung über mehrere Aufrufe fortsetzen

Wenn ein Ablauf in Schritten läuft.

```bash
session_id=$(claude -p "Starte ein Review der Änderungen in src/" --output-format json | jq -r '.session_id')
claude -p "Prüfe jetzt zusätzlich die Datenbankabfragen" --resume "$session_id"
```

### Beispiel 7: Unbeaufsichtigter Lauf ohne Rückfragen

Wenn ein geplanter Job niemanden zum Bestätigen hat.

```bash
claude -p "Aktualisiere die Versionsangaben der Abhängigkeiten und führe die Tests aus" \
  --permission-mode auto \
  --permission-prompts none \
  --max-turns 20 \
  --max-budget-usd 3.00
```

Alles, was eine Rückfrage bräuchte, wird abgelehnt, statt zu warten. Erlaubnisregeln, `PermissionRequest`-Hooks und der Rechtemodus entscheiden weiterhin zuerst.

### Beispiel 8: Fehlertext an Claude weitergeben

Wenn ein Build-Log ausgewertet werden soll.

```bash
cat build-error.txt | claude -p "Erkläre kurz die Ursache dieses Build-Fehlers" > ursache.txt
```

## Schritt für Schritt: vom Skript zum SDK-Agenten

1. Aufgabe zuerst mit `claude -p` ausprobieren, mit `--max-turns` und `--max-budget-usd`.
2. In CI und fremden Repos `--bare` ergänzen und benötigte Einstellungen explizit mitgeben.
3. Für maschinenlesbare Antworten `--output-format json` und bei Bedarf `--json-schema` nutzen.
4. Braucht der Ablauf eigene Logik zwischen den Schritten, eigene Rechteprüfung oder Kostenprotokolle, auf das SDK umsteigen.
5. SDK installieren, `ANTHROPIC_API_KEY` oder Cloud-Anbieter setzen; `.env` selbst laden.
6. Mit dem Minimalbeispiel starten, `allowedTools` eng halten, `maxTurns` und `maxBudgetUsd` setzen.
7. `settingSources` bewusst wählen: `[]` für isolierte Agenten, Standard nur, wenn Projekt-Einstellungen gewollt sind.
8. Ergebnisnachricht auswerten: `subtype` prüfen, `total_cost_usd` protokollieren.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Alter Paketname `claude-code-sdk` | Import schlägt fehl oder alte Version | auf `claude-agent-sdk` und `ClaudeAgentOptions` umstellen |
| Schlüssel nur in `.env` | `Not logged in` oder `Invalid API key` | `.env` selbst laden, etwa mit `dotenv`, oder Variable exportieren |
| Erwartet, dass sich der Agent wie Claude Code verhält | anderes Verhalten seit v0.1.0 | Preset `claude_code` setzen |
| Projekt-Einstellungen ungewollt geladen | fremde Hooks oder Rechte greifen | `settingSources: []` |
| `-p` ohne `--bare` in fremdem Repo | Hooks und MCP-Server des Repos laufen | `--bare` nutzen |
| `--allowedTools "Bash(git diff*)"` ohne Leerzeichen | Regel greift breiter oder anders als gedacht | `Bash(git diff *)` |
| Kein Limit | lange, teure Läufe | `maxTurns` und `maxBudgetUsd` setzen |
| claude.ai-Login im eigenen Produkt | Verstoß gegen die Vorgaben | API-Schlüssel oder Cloud-Anbieter nutzen |

## Häufige Fragen

### Was ist der Unterschied zwischen Claude Code und dem Claude Agent SDK?

Claude Code ist die Anwendung für Terminal, IDE und Desktop. Das Agent SDK ist eine Bibliothek, die dieselbe Agentenschleife mit Tools, Rechten, Sitzungen und Hooks in deine Python- oder TypeScript-Anwendung bringt. Es führt dafür das gebündelte Claude-Code-Binary aus.

### Ist das Claude Code SDK dasselbe wie das Claude Agent SDK?

Ja, das Claude Code SDK wurde in Claude Agent SDK umbenannt. Die Pakete heißen jetzt `@anthropic-ai/claude-agent-sdk` und `claude-agent-sdk`, die Optionsklasse in Python `ClaudeAgentOptions`. Der Migrationsleitfaden steht unter https://code.claude.com/docs/en/agent-sdk/migration-guide.

### Brauche ich das SDK, oder reicht claude -p?

Für viele Skripte und CI-Jobs reicht `claude -p` mit `--output-format json`, `--max-turns` und `--max-budget-usd`. Das SDK lohnt sich, wenn du Nachrichten im Code verarbeiten, Rechte per Callback prüfen oder mehrere Aufrufe mit eigener Logik verbinden willst.

### Kann ich das SDK mit Bedrock oder Vertex AI nutzen?

Ja, über `CLAUDE_CODE_USE_BEDROCK=1`, `CLAUDE_CODE_USE_VERTEX=1` oder `CLAUDE_CODE_USE_FOUNDRY=1` plus die Zugangsdaten des Cloud-Anbieters. Für Claude Platform on AWS gibt es `CLAUDE_CODE_USE_ANTHROPIC_AWS=1` mit `ANTHROPIC_AWS_WORKSPACE_ID`.

### Darf ich mein Produkt "Claude Code" nennen?

Nein. Erlaubt sind Namen wie "Claude Agent" oder "<Name> Powered by Claude"; "Claude Code" und eine Nachahmung des Brandings sind nicht erlaubt. Es gelten die Commercial Terms von Anthropic.

### Laufen Agent Teams im SDK?

Nein. Teammitglieder gibt es nur in interaktiven Sitzungen; im SDK und in `claude -p` laufen benannte Subagents als normale Subagents. Siehe [Claude Code Agent Teams](./claude-code-agent-teams.md).

## Weiterlesen

- [Claude Code Review mit GitHub Actions](./claude-code-review-github-actions.md)
- [Claude Code Kosten](./claude-code-kosten.md)
- [Claude Code Usage und Tokens](./claude-code-usage-tokens.md)
- [Claude Code Subagents](./claude-code-subagents.md)
- [Claude Code Hooks](./claude-code-hooks.md)
- Offizielle Doku: https://code.claude.com/docs/en/agent-sdk/overview und https://code.claude.com/docs/en/headless
