---
name: hook-schreiben
description: "Einen eigenen Claude-Code-Hook schreiben und testen: PreToolUse, PostToolUse, UserPromptSubmit, Stop oder SessionStart, mit JSON auf stdin, permissionDecision deny oder ask, Eintrag in .claude/settings.json mit ${CLAUDE_PROJECT_DIR} und einem Test per Pipe. Nutzen, wenn eine Regel technisch durchgesetzt werden soll statt nur in CLAUDE.md zu stehen, z.B. bestimmte Befehle sperren, Dateien schützen oder nach jeder Änderung formatieren. Englisch: write a Claude Code hook, PreToolUse hook example."
license: MIT
---

# Hook schreiben

Teil von Claude Code Best Practices für Teams.

## Ablauf

1. Kläre in einem Satz, was der Hook verhindern oder erledigen soll, und wähle das Ereignis:
   - vor einem Werkzeug blocken oder nachfragen: `PreToolUse`
   - nach einer Änderung formatieren oder prüfen: `PostToolUse`
   - Prompt prüfen, bevor er an das Modell geht: `UserPromptSubmit`
   - verhindern, dass Claude zu früh fertig meldet: `Stop`
   - Kontext beim Start mitgeben: `SessionStart`
2. Schreibe das Skript nach `.claude/hooks/<name>.py`, nur mit Standardbibliothek. Gibt es `.claude/hooks/_hook.py` aus der Team-Vorlage, nutze `lies_eingabe`, `entscheide` und `ausfuehren` daraus.
3. Antwort für `PreToolUse` als JSON auf stdout, Exit 0:
   `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "<Grund für Claude>"}}`
   Erlaubt sind `allow`, `deny`, `ask` und `defer`. Für `UserPromptSubmit`, `PostToolUse` und `Stop` heißt es `{"decision": "block", "reason": "..."}`.
4. Der Hook muss bei eigenen Fehlern die Aktion durchlassen (Exit 0 ohne Ausgabe) und den Fehler nach stderr schreiben. Exit 1 blockt nichts. Wer blocken will, gibt JSON aus oder nutzt Exit 2 mit dem Grund auf stderr.
5. Bei `Stop` immer `stop_hook_active` auswerten. Ist es `true`, nichts tun, sonst entsteht eine Schleife.
6. Eintrag in `.claude/settings.json` mit festem Projektpfad:
   `{"type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/<name>.py\"", "timeout": 10}`
   unter `hooks.<Ereignis>[].hooks`, bei Werkzeug-Ereignissen mit `matcher`, z.B. `"Bash"` oder `"Edit|Write"`.
7. Teste ohne Claude per Pipe, je ein Fall, der greifen soll, und einer, der durchgehen soll:
   `echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"..."}}' | python3 .claude/hooks/<name>.py`
8. Schreibe die Fälle als pytest-Test, der das Skript mit `subprocess.run(..., input=json.dumps(eingabe))` startet.
9. Danach `claude-team audit .` (CC021 bis CC024 prüfen Pfad, Ausführbarkeit und Ereignisnamen) und in Claude Code `/hooks` öffnen, um zu sehen, ob der Hook geladen ist.

## Grenze

Hooks laufen mit den vollen Rechten der Person. Keine Netzwerkaufrufe, keine Ausgabe von Dateiinhalten oder Tokens in `reason`. Ein Hook ersetzt keine deny-Regel: Was Claude nie lesen darf, gehört zusätzlich unter `permissions.deny`. Referenz: https://code.claude.com/docs/en/hooks
