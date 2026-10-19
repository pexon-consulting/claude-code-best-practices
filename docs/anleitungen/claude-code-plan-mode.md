# Claude Code Plan Mode: erst planen, dann ändern lassen

Den Claude Code Plan Mode aktivierst du mit `Shift+Tab`, bis die Statusleiste `⏸ plan mode on` zeigt, mit `/plan` vor einem einzelnen Prompt oder beim Start mit `claude --permission-mode plan`. Claude liest dann Dateien, führt erkundende Befehle aus und schreibt einen Plan, ändert aber keinen Quellcode, bis du den Plan freigibst. Sinnvoll ist das, wenn der Lösungsweg unklar ist, die Änderung mehrere Dateien betrifft oder du den Code nicht kennst.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- Plan Mode ist ein Permission Mode: Claude darf lesen und erkunden, Edits bleiben bis zur Freigabe gesperrt.
- Du kommst mit `Shift+Tab`, `/plan` oder `--permission-mode plan` hinein und mit erneutem `Shift+Tab` ohne Freigabe wieder heraus.
- Bei der Freigabe wählst du, wie es weitergeht: mit Auto Mode, mit Rückfrage bei jedem Edit oder weiterplanen.
- `Ctrl+G` öffnet den Plan im Texteditor, damit du ihn vor der Umsetzung direkt anpassen kannst.
- Das Modell `opusplan` nutzt Opus im Plan Mode und Sonnet bei der Umsetzung.
- Mit `ultrathink` im Prompt bekommst du für einen Turn gründlicheres Nachdenken, mit `/effort` stellst du die Denktiefe für die Sitzung ein.

## Wie aktiviere ich den Plan Mode?

| Weg | Wirkung |
| --- | --- |
| `Shift+Tab` drücken, bis `⏸ plan mode on` erscheint | Wechsel in der laufenden Sitzung |
| `/plan` oder `/plan fix the auth bug` | Plan Mode für diesen Prompt, optional mit Beschreibung |
| `claude --permission-mode plan` | Start im Plan Mode, funktioniert auch mit `claude -p` |
| `"permissions": { "defaultMode": "plan" }` | jede Terminal-Sitzung im Projekt startet im Plan Mode |
| VS Code: `claudeCode.initialPermissionMode` auf `plan` | Start im Plan Mode in der Extension |

Zur Reihenfolge von `Shift+Tab`: Ab v2.1.283 ist Auto Mode im Terminal der eingebaute Start, sofern dein Modell ihn unterstützt. Von dort führt der erste Druck zu Manual, der zweite zu acceptEdits, der dritte zu plan. Startest du in Manual, sind es zwei Drücke. Unter Windows gibt es zusätzlich `Alt+M`, wenn die Konsole kein VT-Input aktiviert hat.

Die VS-Code-Extension liest den Start-Modus nicht aus den Projekt-Settings. Dort setzt du `claudeCode.initialPermissionMode` in deinen VS-Code-Nutzereinstellungen.

## Was darf Claude im Plan Mode?

| Aktion | Im Plan Mode |
| --- | --- |
| Dateien lesen, suchen | ja |
| Nur-Lese-Befehle wie `ls`, `git log`, `grep` | ja |
| Andere Shell-Befehle | Klassifikator prüft, wenn Auto Mode verfügbar und `useAutoModeDuringPlan` an ist (Standard); sonst Rückfrage |
| Quellcode bearbeiten | nein, erst nach Freigabe |
| Den Plan schreiben | ja, als Datei unter `~/.claude/plans` oder `plansDirectory` |

Für die Recherche nutzt Claude den eingebauten Plan-Subagent. So bleibt die Ausgabe der Erkundung in einem eigenen Kontextfenster, und das Hauptgespräch bleibt schlank.

Eine Ausnahme: In interaktiven Terminal-Sitzungen, die mit verfügbarem Bypass gestartet wurden (etwa mit `--allow-dangerously-skip-permissions`), setzt Claude Code die Sperren des Plan Mode nicht durch. Claude soll dann zwar nur planen, ein versuchter Edit läuft aber ohne Rückfrage. In `claude -p`, im Agent SDK und im Chat der VS-Code-Extension bleiben die Sperren bestehen.

## Wie gebe ich einen Plan frei?

Ist der Plan fertig, zeigt Claude ihn und fragt, wie es weitergehen soll:

| Option | Was danach passiert |
| --- | --- |
| Yes, and use auto mode | Freigabe, Umsetzung im Auto Mode; heißt "Yes, auto-accept edits", wenn Auto Mode nicht verfügbar ist |
| Yes, manually approve edits | Freigabe, jeder Edit wird einzeln bestätigt |
| No, keep planning | Claude bleibt im Plan Mode, du sagst, was sich ändern soll |

Mit `"showClearContextOnPlanAccept": true` kommt eine Option dazu, die den Plan freigibt und den Planungskontext leert. Das hilft bei langen Erkundungen, denn die Umsetzung startet dann nur mit dem Plan.

Nach der Freigabe verlässt die Sitzung den Plan Mode. Für den nächsten Plan wieder `Shift+Tab` oder `/plan`. Der Plan liegt als Datei auf der Platte und wird nach einer Komprimierung mit `/compact` neu eingelesen, er geht also nicht verloren.

## Wann lohnt sich der Plan Mode?

Die Doku von Anthropic empfiehlt vier Phasen: erkunden, planen, umsetzen, committen. Die ersten beiden laufen im Plan Mode.

| Lohnt sich | Lohnt sich nicht |
| --- | --- |
| der Lösungsweg ist unklar | Tippfehler korrigieren |
| die Änderung betrifft mehrere Dateien | eine Log-Zeile ergänzen |
| du kennst den Code nicht | eine Variable umbenennen |
| es geht um Architektur, Migration, Sicherheit | du kannst den Diff in einem Satz beschreiben |

Planen kostet Zeit und Tokens. Lässt sich die Änderung in einem Satz beschreiben, ist der direkte Weg meist besser.

## opusplan, ultrathink und Effort

**opusplan** ist ein Modell-Alias: Im Plan Mode arbeitet Opus, bei der Umsetzung Sonnet. Welche Modelle genau dahinterstehen, steuern `ANTHROPIC_DEFAULT_OPUS_MODEL` und `ANTHROPIC_DEFAULT_SONNET_MODEL`. Setzen kannst du ihn mit `/model opusplan`, `claude --model opusplan` oder `"model": "opusplan"`.

**ultrathink** ist ein Schlüsselwort im Prompt. Es fordert für diesen einen Turn gründlicheres Nachdenken an, ohne die Effort-Einstellung der Sitzung zu ändern. Andere Formulierungen wie "think hard" oder "think more" erkennt Claude Code nicht als Schlüsselwort, sie gehen als normaler Text ans Modell.

**Effort** legt fest, wie viel Claude nachdenkt. Die Stufen sind `low`, `medium`, `high`, `xhigh` und `max`; welche verfügbar sind und welche Standard ist, hängt vom Modell ab. Einstellen lässt sich das so:

| Weg | Wirkung |
| --- | --- |
| `/effort` | Schieberegler; `/effort high` setzt direkt, `/effort auto` löscht die gespeicherte Stufe |
| `/effort status` | zeigt die aktive Stufe |
| `claude --effort high` | für eine Sitzung |
| `CLAUDE_CODE_EFFORT_LEVEL` | Umgebungsvariable mit Stufe oder `auto` |
| `effortLevel` in der settings.json | dauerhafter Wert (`low` bis `xhigh`, nicht `max`) |

`max` gilt nur für die laufende Sitzung, außer du setzt es über die Umgebungsvariable. Organisationen können mit `maxEffortLevel` eine Obergrenze festlegen.

## Beispiele für den Plan Mode

### Beispiel 1: Neues Feature erst erkunden und planen

Start im Plan Mode, dann zwei Prompts in der Sitzung.

```bash
claude --permission-mode plan
```

```text
Lies src/auth und erkläre, wie Sessions und Login funktionieren.
Ich will Google OAuth ergänzen. Welche Dateien müssen sich ändern, wie sieht der Ablauf aus? Erstelle einen Plan.
```

### Beispiel 2: Plan für einen einzelnen Prompt

Aus einer normalen Sitzung heraus, ohne den Modus dauerhaft zu wechseln.

```text
/plan Migriere die Tabelle orders auf das neue Statusfeld, ohne bestehende Daten zu verlieren
```

### Beispiel 3: Projekt startet immer im Plan Mode

Für `.claude/settings.json` in einem Repo mit heiklem Code. Wirkt für Terminal-Sitzungen, nicht für die VS-Code-Extension.

```json
{
  "permissions": {
    "defaultMode": "plan"
  }
}
```

### Beispiel 4: Opus plant, Sonnet setzt um

Für `~/.claude/settings.json` oder das Projekt. Der Planungskontext wird bei Freigabe geleert, Pläne landen im Repo.

```json
{
  "model": "opusplan",
  "showClearContextOnPlanAccept": true,
  "plansDirectory": "./plans"
}
```

### Beispiel 5: Plan ohne Interaktion erzeugen

Für ein Review oder eine CI-Aufgabe: Claude erstellt nur einen Plan und ändert nichts. Die Sperren des Plan Mode gelten in `claude -p` immer.

```bash
claude -p "Erstelle einen Plan, wie wir die Logging-Bibliothek austauschen. Liste betroffene Dateien und Risiken." --permission-mode plan
```

### Beispiel 6: Schwierige Frage mit mehr Denktiefe

`ultrathink` für einen Turn, `/effort` für den Rest der Sitzung.

```text
ultrathink: Warum tritt die Race Condition im Checkout nur unter Last auf? Plane einen Fix mit Test.
```

```text
/effort xhigh
```

### Beispiel 7: Sitzung mit hoher Denktiefe im Plan Mode starten

```bash
claude --permission-mode plan --effort high --model opusplan
```

## Schritt für Schritt: Erkunden, planen, umsetzen

1. Mit `claude --permission-mode plan` starten oder `Shift+Tab` drücken, bis `⏸ plan mode on` erscheint.
2. Claude den relevanten Code lesen und erklären lassen. Rückfragen stellen, bis das Verständnis passt.
3. Einen Plan anfordern, mit konkreter Aufgabe und Randbedingungen, etwa "ohne neue Abhängigkeiten".
4. Den Plan prüfen. Mit `Ctrl+G` im Editor anpassen oder "No, keep planning" wählen und Änderungen nennen.
5. Freigeben: "Yes, manually approve edits" für heiklen Code, "Yes, and use auto mode" für Routine.
6. Claude umsetzen lassen und gegen den Plan prüfen, inklusive Tests.
7. Committen lassen und einen Pull Request öffnen.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Plan Mode für Kleinigkeiten | viel Zeit und Tokens für einen Einzeiler | direkt umsetzen lassen |
| Plan ungeprüft freigegeben | Umsetzung geht in die falsche Richtung | Plan lesen, mit `Ctrl+G` anpassen |
| `defaultMode: "plan"` wirkt in VS Code nicht | Extension startet in einem anderen Modus | `claudeCode.initialPermissionMode` setzen |
| Mit verfügbarem Bypass geplant | Claude ändert Dateien schon während der Planung | ohne `--allow-dangerously-skip-permissions` starten |
| "think hard" statt `ultrathink` | keine spürbare Wirkung | `ultrathink` oder `/effort` nutzen |
| `effortLevel: "max"` in der settings.json | Wert wird nicht übernommen | `max` per `/effort` oder `CLAUDE_CODE_EFFORT_LEVEL` |

## Häufige Fragen

### Wie aktiviere ich den Plan Mode in Claude Code?

Mit `Shift+Tab`, bis die Statusleiste `⏸ plan mode on` zeigt, oder mit `/plan` vor einem Prompt. Beim Start geht es mit `claude --permission-mode plan`, dauerhaft mit `"defaultMode": "plan"` in der settings.json.

### Wie verlasse ich den Plan Mode?

Indem du den Plan freigibst oder erneut `Shift+Tab` drückst. Mit `Shift+Tab` verlässt du den Modus ohne Freigabe, und Claude setzt nichts um.

### Kann Claude im Plan Mode Dateien ändern?

Quellcode nicht, nur die eigene Plan-Datei. Shell-Befehle prüft der Klassifikator oder du per Rückfrage. Ausnahme sind interaktive Terminal-Sitzungen mit verfügbarem Bypass, dort sind die Sperren nicht aktiv.

### Was ist ultrathink?

Ein Schlüsselwort, das du in den Prompt schreibst. Claude denkt dann für diesen Turn gründlicher nach, die Effort-Einstellung der Sitzung bleibt gleich.

### Was ist opusplan?

Ein Modell-Alias, der im Plan Mode Opus und bei der Umsetzung Sonnet verwendet. Der Wechsel passiert automatisch mit dem Verlassen des Plan Mode, du musst das Modell nicht von Hand umstellen.

### Wo speichert Claude Code den Plan?

Standardmäßig unter `~/.claude/plans`. Mit `plansDirectory` legst du einen Ordner relativ zum Projekt-Root fest, etwa `./plans`.

## Weiterlesen

- [Claude Code Permissions und Permission Modes](./claude-code-permissions.md)
- [Claude Code Workflow](./claude-code-workflow.md)
- [Claude Code Memory: Kontext und /compact](./claude-code-memory.md)
- [Claude Code Subagents](./claude-code-subagents.md)
- [Claude Code Kosten](./claude-code-kosten.md)
- Offizielle Doku: [Permission modes](https://code.claude.com/docs/en/permission-modes), [Model configuration](https://code.claude.com/docs/en/model-config), [Best practices](https://code.claude.com/docs/en/best-practices)
