# Claude Code vs Codex und Cursor: Unterschiede für Teams

Claude Code vs Codex vs Cursor ist vor allem eine Frage der Bedienform und des Betriebs: Claude Code ist ein Agent, der im Terminal, in IDE-Erweiterungen und in einer Desktop-App läuft, Codex ist der Coding-Agent von OpenAI, und Cursor ist ein Editor mit eingebauten KI-Funktionen. Für Teams zählen neben der Modellqualität die Konfigurationsdateien, die Erweiterbarkeit mit Hooks, Skills und MCP-Servern, der Betrieb über eigene Cloud-Konten und die Datenschutz-Optionen. Diese Seite vergleicht sachlich, ohne Preise und Benchmarks, und belegt Aussagen zu Claude Code mit der offiziellen Doku; zu Codex und Cursor stehen nur allgemeine Merkmale, die du in deren Doku nachprüfst.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- Claude Code arbeitet agentisch vom Terminal aus und ist zusätzlich in VS Code, Cursor, JetBrains und einer Desktop-App nutzbar; Cursor ist dagegen selbst der Editor.
- Claude Code liest CLAUDE.md und ab v2.1.277 auch AGENTS.md, wenn keine CLAUDE.md vorhanden ist; `/init` übernimmt vorhandene Cursor-Regeln.
- Mit `/import codex`, `/import gemini` oder `/import cursor` übernimmt Claude Code Anweisungsdateien, MCP-Server, Befehle, Subagents und Skills aus anderen Werkzeugen.
- Für Teams wichtig sind Managed Settings, Hooks und der Betrieb über Bedrock, Vertex AI, Foundry oder ein LLM-Gateway.
- Viele Teams nutzen mehrere Werkzeuge parallel; eine gemeinsame AGENTS.md hält die Regeln an einer Stelle.
- Prüft Datenschutz, Speicherfristen und Verträge für jedes Werkzeug einzeln und klärt sie mit dem Datenschutzbeauftragten.

## Wo liegen die Unterschiede in der Bedienung?

| Merkmal | Claude Code | Codex | Cursor |
| --- | --- | --- | --- |
| Grundform | Agent im Terminal (CLI) | Coding-Agent von OpenAI, unter anderem als CLI | Editor (Fork von VS Code) mit KI-Funktionen |
| IDE | Erweiterung für VS Code und Cursor, Plugin für JetBrains | laut Anbieter auch als IDE-Erweiterung | ist selbst die IDE |
| Weitere Oberflächen | Desktop-App, Web | laut Anbieter auch in der Cloud | laut Anbieter auch CLI und [Cloud Agents](https://cursor.com/docs/cli/overview) |
| Headless und CI | `claude -p`, GitHub Actions, Agent SDK | laut Anbieter Ausführung ohne Oberfläche möglich | laut Anbieter über die CLI ohne Oberfläche möglich |

Die Spalten für Codex und Cursor beschreiben allgemein bekannte Merkmale. Funktionsumfang und Namen ändern sich schnell; prüf den aktuellen Stand in der Doku der Anbieter.

Claude Code und Cursor schließen sich nicht aus: Die Claude-Code-Erweiterung `anthropic.claude-code` läuft auch in Cursor. Siehe [Claude Code in VS Code und JetBrains](./claude-code-vscode-jetbrains.md).

## Welche Konfigurationsdateien nutzen die Werkzeuge?

| Zweck | Claude Code | Codex | Cursor |
| --- | --- | --- | --- |
| Projektanweisungen | CLAUDE.md, AGENTS.md ab v2.1.277 | AGENTS.md | `.cursor/rules`, ältere `.cursorrules` |
| Bereichsregeln | `.claude/rules/` mit `paths` | in der Doku des Anbieters prüfen | Regeln in `.cursor/rules` |
| Einstellungen | `.claude/settings.json`, Managed Settings | eigene Konfigurationsdatei | Editor-Einstellungen |

So liest Claude Code Anweisungen laut Doku:

- Gibt es eine AGENTS.md und keine CLAUDE.md oder CLAUDE.local.md im Arbeitsverzeichnis oder darüber, liest Claude die AGENTS.md (ab v2.1.277).
- Gibt es beide, liest Claude nur die CLAUDE.md.
- Importiert die CLAUDE.md die AGENTS.md mit `@AGENTS.md`, gelten beide. Das ist der robuste Weg, weil Claude AGENTS.md in manchen Sitzungen nicht direkt lesen kann.

`/init` berücksichtigt beim Erstellen der CLAUDE.md vorhandene `.cursor/rules`, `.cursorrules` und `.github/copilot-instructions.md`. Mehr in [AGENTS.md](./agents-md.md) und [CLAUDE.md](./claude-md.md).

## Wie erweiterbar sind die Werkzeuge?

Claude Code bietet laut Doku diese Erweiterungspunkte:

| Erweiterung | Was sie tut |
| --- | --- |
| Hooks | Befehle zu festen Zeitpunkten, etwa vor einem Tool-Aufruf oder am Sitzungsende, mit der Möglichkeit zu blockieren |
| Skills | Anweisungen und Skripte, die bei Bedarf oder über `/name` laden |
| Subagents | spezialisierte Helfer mit eigenem Kontext, eigenen Tools und eigenem Modell |
| MCP-Server | Anbindung externer Werkzeuge und Datenquellen |
| Plugins | Bündel aus Skills, Subagents, Hooks und MCP-Servern, verteilt über Marketplaces |
| Agent SDK | dieselbe Agentenschleife als Bibliothek für Python und TypeScript |

MCP ist ein offener Standard, den auch andere Werkzeuge unterstützen; die Einbindung unterscheidet sich je Werkzeug. Skills im Format `SKILL.md` aus diesem Repo funktionieren für Claude Code und Codex; Cursor liest laut [Doku](https://cursor.com/docs/context/skills) ebenfalls `SKILL.md` und lädt dafür auch `.claude/skills/`. Für Hooks und Plugins bei Codex und Cursor prüfst du die jeweilige Doku.

## Wie betreibe ich die Werkzeuge im Unternehmen?

Für Claude Code beschreibt die Doku diese Wege:

- Anmeldung über Abo (Pro, Max, Team, Enterprise), Claude Console (API), Amazon Bedrock, Google Vertex AI oder Microsoft Foundry.
- Ein LLM-Gateway über `ANTHROPIC_BASE_URL` und `ANTHROPIC_AUTH_TOKEN` für zentrale Schlüssel, Budgets und Protokolle.
- Managed Settings für Rechte, erlaubte Modelle (`availableModels`) und Richtlinien, die Nutzer nicht überschreiben können.
- OpenTelemetry für Nutzungs- und Kostenmetriken im eigenen Monitoring.

Bei Codex und Cursor laufen Abrechnung und Verwaltung über die Konten der jeweiligen Anbieter; welche Cloud-Anbindungen, Admin-Richtlinien und Regionen verfügbar sind, klärst du direkt mit dem Anbieter.

## Was gilt beim Datenschutz?

Für Claude Code laut Doku (Stand 15.10.2026):

- Bei kommerziellen Konten (Team, Enterprise, API, Cloud-Anbieter) trainiert Anthropic keine Modelle mit Code oder Prompts, außer der Kunde hat zugestimmt.
- Bei Free, Pro und Max entscheidet eine Einstellung, ob Daten für das Training genutzt werden; die Speicherdauer beträgt dann 5 Jahre, sonst 30 Tage.
- Kommerzielle Konten haben standardmäßig 30 Tage Speicherdauer. Zero Data Retention gibt es nur für geeignete Enterprise-Organisationen, freigeschaltet durch das Account-Team.
- Über Bedrock, Vertex AI oder Foundry laufen Anfragen über das Cloud-Konto; es gelten die Bedingungen des Cloud-Anbieters.
- Telemetrie und nicht notwendigen Datenverkehr schaltest du mit `DISABLE_TELEMETRY` bzw. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` ab.

Für Codex und Cursor gelten die Datenschutzbedingungen der Anbieter. Das ist keine Rechtsberatung; klärt Auftragsverarbeitung, Speicherorte und Fristen mit dem Datenschutzbeauftragten. Siehe [Claude Code DSGVO](./claude-code-dsgvo.md).

## Beispiele für den Vergleich

### Beispiel 1: Eine AGENTS.md für alle Werkzeuge, eingebunden in CLAUDE.md

Wenn Teile des Teams Codex und andere Claude Code nutzen. Datei `CLAUDE.md`:

```markdown
@AGENTS.md

## Nur für Claude Code

- Für Commits den Skill /commit nutzen.
- Im Plan Mode beginnen, wenn mehr als zwei Dateien betroffen sind.
```

Gemeinsame Regeln stehen in `AGENTS.md`, Claude-spezifische Ergänzungen darunter.

### Beispiel 2: Konfiguration aus Cursor oder Codex übernehmen

Wenn du von einem anderen Werkzeug umsteigst oder beide parallel pflegst.

```text
/import cursor --dry-run
/import cursor
/import codex --dry-run
```

`--dry-run` zeigt, was übernommen würde. `/import` gibt es ab v2.1.213.

### Beispiel 3: Neue CLAUDE.md aus vorhandenen Regeln

Wenn ein Repo schon `.cursor/rules` oder `.github/copilot-instructions.md` hat.

```text
/init
```

Claude liest die vorhandenen Regeln und erstellt daraus eine CLAUDE.md. Danach kürzen: Die Doku empfiehlt unter 200 Zeilen.

### Beispiel 4: Skills für Claude Code und Codex installieren

Wenn beide Werkzeuge dieselben Abläufe nutzen sollen.

```bash
npx skills add pexon-consulting/claude-code-best-practices
```

### Beispiel 5: Gleiche Leitplanken in Claude Code erzwingen

Wenn Geheimnisse in keinem Werkzeug gelesen werden dürfen. Auszug aus `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  },
  "env": {
    "DISABLE_TELEMETRY": "1"
  }
}
```

Für Codex und Cursor setzt du die entsprechenden Ausschlüsse in deren Konfiguration. Siehe Prüfregel [CC013](../regeln.md#cc013).

### Beispiel 6: Claude Code in Cursor nutzen

Wenn das Team bei Cursor als Editor bleibt und Claude Code als Agent ergänzt.

```text
cursor:extension/anthropic.claude-code
```

Diesen Link öffnest du im Browser, Cursor zeigt dann die Erweiterung zur Installation an; alternativ suchst du in der Erweiterungsansicht nach "Claude Code". Ohne Erweiterung startest du `claude` im Terminal von Cursor.

## Schritt für Schritt: Werkzeugwahl im Team

1. Anforderungen sammeln: Terminal oder Editor, CI-Nutzung, Cloud-Konto, Datenschutzvorgaben, Admin-Kontrolle.
2. Entscheidungstabelle unten durchgehen und 1-2 Kandidaten wählen.
3. Datenschutz und Verträge je Kandidat mit dem Datenschutzbeauftragten klären, siehe [`../rollout/freigabe-paket.md`](../rollout/freigabe-paket.md).
4. Gemeinsame AGENTS.md anlegen, damit Regeln werkzeugunabhängig bleiben.
5. Pilot mit einer kleinen Gruppe und echten Aufgaben, nicht mit Demos; siehe [`../rollout/pilotplan.md`](../rollout/pilotplan.md).
6. Nach dem Pilot entscheiden: ein Werkzeug als Standard oder bewusste Kombination.

## Fazit als Entscheidungstabelle

| Wenn du ... | dann passt eher |
| --- | --- |
| agentisch im Terminal arbeiten und automatisieren wollt (Skripte, CI, SDK) | Claude Code |
| über Bedrock, Vertex AI oder Foundry abrechnen müsst | Claude Code, die Anbindung ist dokumentiert |
| zentrale Richtlinien per Managed Settings und Hooks durchsetzen wollt | Claude Code |
| einen Editor mit integrierten KI-Funktionen als Hauptwerkzeug wollt | Cursor, optional mit der Claude-Code-Erweiterung |
| schon auf OpenAI-Verträge und -Modelle festgelegt seid | Codex, Stand beim Anbieter prüfen |
| mehrere Werkzeuge parallel zulasst | gemeinsame AGENTS.md plus `/import` |

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Regeln in drei Dateien doppelt pflegen | Widersprüche zwischen Werkzeugen | AGENTS.md als Quelle, in CLAUDE.md importieren |
| AGENTS.md neben CLAUDE.md ohne Import | Claude liest AGENTS.md nicht | `@AGENTS.md` in die CLAUDE.md |
| Vergleich nur nach Demos | Enttäuschung im Alltag | Pilot mit echten Aufgaben |
| Datenschutz nur für ein Werkzeug geprüft | Lücke bei Parallelnutzung | jedes Werkzeug einzeln freigeben |
| Benchmarks als Entscheidungsgrundlage | Ergebnis passt nicht zum eigenen Code | eigene Aufgaben messen |

## Häufige Fragen

### Ist Claude Code besser als Codex?

Das hängt von deinen Anforderungen ab, nicht von einer pauschalen Rangliste. Claude Code bringt dokumentierte Erweiterungspunkte (Hooks, Skills, Subagents, Plugins, MCP-Server), Managed Settings und den Betrieb über Bedrock, Vertex AI und Foundry mit. Für Codex prüfst du den aktuellen Funktionsumfang bei OpenAI und vergleichst beide mit deinen eigenen Aufgaben.

### Kann ich Claude Code in Cursor nutzen?

Ja, die Erweiterung `anthropic.claude-code` läuft in VS Code und in Cursor. Alternativ startest du `claude` im integrierten Terminal.

### Liest Claude Code AGENTS.md?

Ja, ab v2.1.277, wenn im Arbeitsverzeichnis und darüber keine CLAUDE.md oder CLAUDE.local.md liegt. Gibt es beide, bindest du AGENTS.md mit `@AGENTS.md` in die CLAUDE.md ein.

### Wie wechsle ich von Cursor zu Claude Code?

Mit `/import cursor` übernimmt Claude Code Anweisungsdateien, MCP-Server, Befehle, Subagents und Skills; mit `--dry-run` siehst du vorher, was übernommen wird. `/init` berücksichtigt vorhandene `.cursor/rules`.

### Welches Werkzeug ist datenschutzfreundlicher?

Das lässt sich nicht pauschal beantworten. Für Claude Code sind Training, Speicherfristen und Zero Data Retention dokumentiert; für die anderen Werkzeuge gelten deren Bedingungen. Keine Rechtsberatung; klärt das mit dem Datenschutzbeauftragten.

## Weiterlesen

- [AGENTS.md](./agents-md.md)
- [CLAUDE.md](./claude-md.md)
- [Claude Code in VS Code und JetBrains](./claude-code-vscode-jetbrains.md)
- [Claude Code Enterprise](./claude-code-enterprise.md)
- [Claude Code DSGVO](./claude-code-dsgvo.md)
- [Claude Code LLM-Gateway](./claude-code-llm-gateway.md)
