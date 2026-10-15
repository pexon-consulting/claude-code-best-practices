# Claude Code Statusline: Modell, Kontext und Kosten in der Statuszeile anzeigen

Eine eigene Claude Code Statusline richtest du über das Feld `statusLine` in `~/.claude/settings.json` ein: Es zeigt auf ein Skript, das Sitzungsdaten als JSON über stdin bekommt und eine Zeile Text ausgibt. Der schnellste Weg ist `/statusline` mit einer Beschreibung in normaler Sprache, Claude Code schreibt dann Skript und Einstellung selbst. So siehst du Modell, Kontextfüllung, Git-Branch und geschätzte Kosten ständig am unteren Rand.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Die Statusline ist ein beliebiges Programm. Es liest JSON von stdin und schreibt Text nach stdout.
- Sie läuft lokal und verbraucht keine API-Tokens.
- `context_window.used_percentage` zeigt, wie voll das Kontextfenster ist. Es zählt nur Eingabe-Tokens.
- `cost.total_cost_usd` ist eine Schätzung von Claude Code, nicht deine Rechnung, und beginnt nach `/clear` wieder bei 0.
- Das Skript muss mit Exit-Code 0 enden und schnell sein, sonst bleibt die Zeile leer oder veraltet.
- In einem Ordner, dem du nicht vertraust, bleibt die Statusline leer, weil sie wie ein Hook einen Shell-Befehl ausführt.

## Wie richte ich eine eigene Statusline ein?

### Mit /statusline

```text
/statusline zeige Modellname und Kontext in Prozent mit Fortschrittsbalken
```

Claude Code legt ein Skript in `~/.claude/` an und trägt es in die Einstellungen ein. Bestätige die Rückfragen zum Schreiben der Dateien. Ohne Argument übernimmt `/statusline` die Gestaltung deines Shell-Prompts. Entfernen geht mit `/statusline delete`.

### Von Hand

In `~/.claude/settings.json` (für dich) oder in den Projekt-Settings:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 2
  }
}
```

| Feld | Bedeutung |
| --- | --- |
| `type` | immer `"command"` |
| `command` | Pfad zum Skript oder ein Shell-Befehl |
| `padding` | zusätzlicher Abstand in Zeichen, Standard 0 |
| `refreshInterval` | Skript zusätzlich alle N Sekunden ausführen, mindestens 1 |
| `hideVimModeIndicator` | blendet `-- INSERT --` aus, wenn dein Skript den Vim-Modus selbst zeigt |

## Wann wird die Statusline aktualisiert?

Das Skript läuft beim Start und Fortsetzen einer Sitzung und danach bei:

- einer neuen Antwort von Claude,
- dem Ende von `/compact`,
- einem Wechsel des Berechtigungsmodus oder des Vim-Modus,
- einer Änderung am `command`,
- Ablauf von `refreshInterval`, wenn gesetzt,
- Ablauf eines Rate-Limit-Fensters oder des Prompt-Caches.

Claude Code wartet 300 ms, bis Änderungen zur Ruhe kommen, und startet das Skript dann einmal. Kommt ein neues Ereignis, während das Skript noch läuft, bricht Claude Code den alten Lauf ab. Ist die Sitzung untätig, etwa während Hintergrund-Subagents arbeiten, hält `refreshInterval` die Anzeige aktuell.

## Welche Daten bekommt das Skript?

| Feld | Inhalt |
| --- | --- |
| `model.id`, `model.display_name` | Modell-ID und Anzeigename |
| `workspace.current_dir` | aktueller Arbeitsordner, auch als `cwd` |
| `workspace.project_dir` | Ordner, in dem Claude Code gestartet wurde |
| `workspace.repo.owner`, `workspace.repo.name` | Repo aus dem Remote `origin` |
| `cost.total_cost_usd` | geschätzte Kosten der Sitzung in USD |
| `cost.total_duration_ms` | Laufzeit der Sitzung |
| `cost.total_lines_added`, `cost.total_lines_removed` | geänderte Zeilen |
| `context_window.used_percentage` | belegter Kontext in Prozent |
| `context_window.remaining_percentage` | freier Kontext in Prozent |
| `context_window.context_window_size` | Größe des Fensters, 200000 oder 1000000 |
| `context_window.total_input_tokens` | Eingabe-Tokens im Kontext |
| `context_window.current_usage` | Tokens nach Art: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` |
| `exceeds_200k_tokens` | ob die letzte Antwort über 200.000 Tokens lag |
| `effort.level` | aktuelle Effort-Stufe |
| `fast_mode` | ob Fast Mode an ist |
| `rate_limits.five_hour.used_percentage` | Verbrauch im 5-Stunden-Fenster, nur Pro und Max |
| `rate_limits.seven_day.used_percentage` | Verbrauch im 7-Tage-Fenster, nur Pro und Max |
| `session_id`, `session_name` | Sitzungs-ID und Name |
| `transcript_path` | Pfad zum Transcript |
| `version` | Version von Claude Code |
| `output_style.name` | aktiver Ausgabestil |
| `vim.mode` | Vim-Modus, wenn aktiv |
| `agent.name` | Agent, wenn die Sitzung mit `--agent` läuft |

`used_percentage` rechnet nur mit Eingabe: `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`. `current_usage` ist vor dem ersten API-Aufruf und direkt nach `/compact` `null`. `/context` kann etwas höher liegen, weil es Nachrichten seit der letzten Antwort schätzt. Viele Felder fehlen am Anfang einer Sitzung, deshalb brauchst du immer Standardwerte wie `// 0` in jq.

## Beispiele

### Beispiel 1: Einzeiler mit jq

Ohne eigenes Skript, direkt in der settings.json:

```json
{
  "statusLine": {
    "type": "command",
    "command": "jq -r '\"[\\(.model.display_name)] \\(.context_window.used_percentage // 0)% context\"'"
  }
}
```

Ausgabe etwa: `[Opus] 42% context`.

### Beispiel 2: Modell und Kontext mit Fortschrittsbalken

`~/.claude/statusline.sh`, braucht `jq`:

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)

BAR_WIDTH=10
FILLED=$((PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR=""
[ "$FILLED" -gt 0 ] && printf -v FILL "%${FILLED}s" && BAR="${FILL// /▓}"
[ "$EMPTY" -gt 0 ] && printf -v PAD "%${EMPTY}s" && BAR="${BAR}${PAD// /░}"

echo "[$MODEL] $BAR $PCT%"
```

Danach `chmod +x ~/.claude/statusline.sh` und den Pfad in `command` eintragen.

### Beispiel 3: Git-Branch mit Farben

Grün für vorgemerkte, gelb für geänderte Dateien. `\033[32m` ist grün, `\033[33m` gelb, `\033[0m` setzt zurück.

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
GREEN='\033[32m'
YELLOW='\033[33m'
RESET='\033[0m'

if git rev-parse --git-dir > /dev/null 2>&1; then
  BRANCH=$(git branch --show-current 2>/dev/null)
  STAGED=$(git diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
  MODIFIED=$(git diff --numstat 2>/dev/null | wc -l | tr -d ' ')
  GIT_STATUS=""
  [ "$STAGED" -gt 0 ] && GIT_STATUS="${GREEN}+${STAGED}${RESET}"
  [ "$MODIFIED" -gt 0 ] && GIT_STATUS="${GIT_STATUS}${YELLOW}~${MODIFIED}${RESET}"
  echo -e "[$MODEL] ${DIR##*/} | $BRANCH $GIT_STATUS"
else
  echo "[$MODEL] ${DIR##*/}"
fi
```

In großen Repos kann `git diff` bremsen. Die offizielle Doku zeigt dafür eine Variante, die das Ergebnis einige Sekunden in einer Datei pro `session_id` zwischenspeichert.

### Beispiel 4: Kosten und Dauer

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

COST_FMT=$(printf '$%.2f' "$COST")
DURATION_SEC=$((DURATION_MS / 1000))
MINS=$((DURATION_SEC / 60))
SECS=$((DURATION_SEC % 60))

echo "[$MODEL] $COST_FMT | ${MINS}m ${SECS}s"
```

Der Betrag ist eine Schätzung zum Listenpreis. Was wirklich abgerechnet wird, zeigt `/usage` oder die Abrechnung deines Anbieters, mehr in [Claude Code Kosten](./claude-code-kosten.md).

### Beispiel 5: Python-Skript mit Tokens und Fenstergröße

Ohne `jq`, nur mit der Standardbibliothek. Gut, wenn im Team nicht überall `jq` installiert ist.

```python
#!/usr/bin/env python3
import json
import sys

data = json.load(sys.stdin)
model = data.get("model", {}).get("display_name", "?")
ctx = data.get("context_window", {})
pct = int(ctx.get("used_percentage") or 0)
used = ctx.get("total_input_tokens") or 0
size = ctx.get("context_window_size") or 200000
effort = data.get("effort", {}).get("level", "")

line = f"[{model}] {pct}% ({used // 1000}k von {size // 1000}k)"
if effort:
    line += f" | effort {effort}"
print(line)
```

### Beispiel 6: Rate Limits für Pro und Max

`// empty` sorgt dafür, dass nichts erscheint, wenn die Felder fehlen.

```bash
#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
FIVE_H=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
WEEK=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

LIMITS=""
[ -n "$FIVE_H" ] && LIMITS="5h: $(printf '%.0f' "$FIVE_H")%"
[ -n "$WEEK" ] && LIMITS="${LIMITS:+$LIMITS }7d: $(printf '%.0f' "$WEEK")%"

[ -n "$LIMITS" ] && echo "[$MODEL] | $LIMITS" || echo "[$MODEL]"
```

### Beispiel 7: Windows mit PowerShell

Unter Windows führt Claude Code den Befehl über Git Bash aus, wenn es installiert ist, sonst über PowerShell. Pfade schreibst du mit Schrägstrichen nach vorn, sonst verschluckt Git Bash die Backslashes.

```json
{
  "statusLine": {
    "type": "command",
    "command": "powershell -NoProfile -File C:/Users/username/.claude/statusline.ps1"
  }
}
```

## Schritt für Schritt: Skript testen und einbinden

1. Skript unter `~/.claude/statusline.sh` speichern, z.B. Beispiel 2.
2. Ausführbar machen: `chmod +x ~/.claude/statusline.sh`.
3. Mit Testdaten prüfen:

   ```bash
   echo '{"model":{"display_name":"Opus"},"workspace":{"current_dir":"/home/user/project"},"context_window":{"used_percentage":25},"session_id":"test-session-abc"}' | ~/.claude/statusline.sh
   ```

4. `statusLine` in `~/.claude/settings.json` eintragen. Claude Code lädt die Einstellung beim Speichern neu.
5. Bleibt die Zeile leer, `claude --debug` starten. Das Log zeigt stderr des Skripts und den Exit-Code beim ersten Lauf.

## Was das Skript ausgeben darf

- Mehrere Zeilen: jedes `echo` oder `print` wird eine eigene Zeile.
- Farben über ANSI-Codes, wenn das Terminal sie kann.
- Klickbare Links über OSC-8-Sequenzen, z.B. in iTerm2, Kitty und WezTerm. Terminal.app kann das nicht.
- Für die Breite liest du `COLUMNS` und `LINES`. `tput cols` funktioniert nicht, weil Claude Code die Ausgabe abfängt.
- Kurz halten: Lange Ausgaben werden abgeschnitten oder umbrochen.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Skript nicht ausführbar | Zeile bleibt leer | `chmod +x` |
| Ausgabe nach stderr | Zeile bleibt leer | nach stdout schreiben |
| Exit-Code ungleich 0 | Zeile bleibt leer | Fehler abfangen, immer mit 0 enden |
| kein Standardwert für `null` | `--` oder leere Werte | `// 0` in jq, `or 0` in Python |
| Ordner nicht vertraut | Debug-Log: `Status line command skipped: workspace trust not accepted` | Trust-Dialog bestätigen |
| `disableAllHooks` oder `allowManagedHooksOnly` gesetzt | eigene Statusline verschwindet | nur eine Statusline aus Managed Settings läuft |
| Backslashes im Windows-Pfad | Befehl schlägt still fehl | `C:/Users/...` schreiben |
| langsames Skript | Anzeige hängt hinterher | Ergebnisse zwischenspeichern |

## Häufige Fragen

### Kostet die Statusline Tokens?

Nein. Das Skript läuft lokal und schickt nichts an die API.

### Wie zeige ich das Kontextfenster in Prozent an?

Mit dem Feld `context_window.used_percentage`, etwa per jq-Einzeiler aus Beispiel 1. Für den freien Rest gibt es `remaining_percentage`.

### Warum stimmt der Kontextwert nicht mit /context überein?

Die Statusline nutzt die Zahlen der letzten API-Antwort. `/context` schätzt zusätzlich die Nachrichten seit dieser Antwort und liegt deshalb bis zur nächsten Antwort etwas höher.

### Kann ich die Statusline im Team vorgeben?

Ja, über die Projekt-Settings oder Managed Settings. Das Skript muss dann auf jedem Rechner am angegebenen Pfad liegen. Ein Python-Skript wie in Beispiel 5 vermeidet, dass alle `jq` installieren müssen.

### Gibt es fertige Statuslines?

Ja, die offizielle Doku nennt die Community-Projekte [ccstatusline](https://github.com/sirmalloc/ccstatusline) und [starship-claude](https://github.com/martinemde/starship-claude). Prüfe fremde Skripte vor dem Einsatz, sie laufen mit deinen Rechten.

## Weiterlesen

- [Claude Code Usage und Tokens](./claude-code-usage-tokens.md): Kontext und Verbrauch verstehen
- [Claude Code Kosten](./claude-code-kosten.md): Schätzung und echte Abrechnung
- [Claude Code settings.json](./claude-code-settings-json.md): wo `statusLine` steht
- [Claude Code Befehle](./claude-code-befehle.md): `/statusline`, `/context` und `/usage`
- Offizielle Doku: [Statusline](https://code.claude.com/docs/en/statusline)
