# Claude Code Hooks: Secrets und personenbezogene Daten automatisch blockieren

Claude Code Hooks sind Skripte, die Claude Code bei festen Ereignissen automatisch startet, zum Beispiel vor jedem Tool-Aufruf (`PreToolUse`). Um zu verhindern, dass Claude eine `.env` liest oder personenbezogene Daten in Code und Befehle übernimmt, registrierst du in `.claude/settings.json` einen `PreToolUse`-Hook für `Read|Edit|Write|Grep|Glob|Bash`, der den Dateipfad oder Inhalt aus dem JSON auf stdin prüft und `permissionDecision: "deny"` zurückgibt. Anders als eine Anweisung in der CLAUDE.md läuft ein Hook jedes Mal, unabhängig davon, ob das Modell sich an Regeln hält.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

Diese Anleitung erklärt Technik und Einstellungen. Sie ist keine Rechtsberatung. Datenschutz, Verträge und Mitbestimmung klärst du mit Datenschutzbeauftragtem, Rechtsabteilung und Betriebsrat. Angaben zu Regionen und Datenverarbeitung der Anbieter können sich ändern; maßgeblich sind deren aktuelle Dokumentation und Verträge.

## Das Wichtigste in Kürze

- Hooks stehen unter dem Schlüssel `hooks` in einer settings.json und haben drei Ebenen: Ereignis, Matcher-Gruppe und Handler.
- Claude Code schickt jedem Hook ein JSON-Objekt auf stdin und wertet Exit-Code und stdout aus.
- Exit 2 blockiert, Exit 1 blockiert nicht, und JSON mit `permissionDecision` steuert `PreToolUse` fein (allow, deny, ask, defer).
- Ein `deny` aus einem `PreToolUse`-Hook gilt auch im Modus `bypassPermissions`, ein `allow` hebelt aber keine deny-Regel aus.
- Command-Hooks laufen mit deinen vollen Benutzerrechten, deshalb gehören nur geprüfte Skripte ins Repo.
- Die Vorlage in diesem Repo bringt sieben fertige Hooks mit: Secrets, deutsche PII mit Prüfziffern, gefährliche Befehle, Protokoll, Formatieren, Sitzungsstart und Tests vor dem Stopp.
- Die Hooks prüfen Prompts, Shell-Befehle, Dateipfade und neu geschriebenen Code, nicht den Inhalt gelesener Dateien. Was sie nicht abdecken, steht unter [Was die Hooks nicht abdecken](#was-die-hooks-nicht-abdecken).

## Wo werden Claude Code Hooks konfiguriert?

Hooks gehören in eine settings.json. Hooks aus mehreren Ebenen werden zusammengeführt, nicht ersetzt. Ein identischer Handler, der in mehreren Dateien steht, läuft nur einmal.

| Ort | Gültigkeit | Teilbar |
| --- | --- | --- |
| `~/.claude/settings.json` | alle eigenen Projekte | nein |
| `.claude/settings.json` | ein Projekt | ja, ins Repo committen |
| `.claude/settings.local.json` | ein Projekt | nein, gehört in `.gitignore` |
| Managed Settings | ganze Organisation | ja, durch die Administration |
| Plugin `hooks/hooks.json` | solange das Plugin aktiv ist | ja |
| Skill-Frontmatter | ab Aufruf des Skills bis zum Ende der Sitzung | ja |
| Subagent-Frontmatter | solange der Subagent läuft, `Stop` wird dort zu `SubagentStop` | ja |

Der Aufbau ist immer gleich: Ereignis, darunter eine Liste von Matcher-Gruppen, darin die Handler.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PROJECT_DIR}\"/.claude/hooks/block-rm.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Änderungen an Settings-Dateien erkennt Claude Code normalerweise ohne Neustart. Mit `/hooks` öffnest du eine Liste aller aktiven Hooks samt Herkunft. Die Liste ist nur zum Ansehen, bearbeitet wird in den Dateien.

## Alle Hook-Ereignisse im Überblick

Die Doku nennt 33 Ereignisse. "Kann blocken" heißt: Exit 2 oder eine JSON-Entscheidung hält die Aktion an.

| Ereignis | Wann es feuert | Kann blocken | Matcher filtert auf |
| --- | --- | --- | --- |
| `SessionStart` | Sitzung startet oder wird fortgesetzt | nein | `startup`, `resume`, `clear`, `compact`, `fork` |
| `Setup` | nur bei `--init-only`, `-p --init` oder `-p --maintenance` | nein | `init`, `maintenance` |
| `InstructionsLoaded` | CLAUDE.md oder `.claude/rules/*.md` wird geladen | nein | Ladegrund |
| `UserPromptSubmit` | Prompt abgeschickt, vor der Verarbeitung | ja | kein Matcher |
| `UserPromptExpansion` | Slash-Befehl wird zu einem Prompt erweitert | ja | Befehlsname |
| `MessageDisplay` | Antworttext wird angezeigt | nein | kein Matcher |
| `PreToolUse` | vor jedem Tool-Aufruf | ja | Toolname |
| `PermissionRequest` | ein Berechtigungsdialog würde erscheinen | ja, nur per JSON | Toolname |
| `PermissionDenied` | Auto Mode lehnt einen Tool-Aufruf ab | nein, nur `retry` | Toolname |
| `PostToolUse` | nach einem erfolgreichen Tool-Aufruf | nein, Rückmeldung an Claude möglich | Toolname |
| `PostToolUseFailure` | Tool ist fehlgeschlagen | nein | Toolname |
| `PostToolBatch` | alle parallelen Tool-Aufrufe eines Batches sind fertig | ja | kein Matcher |
| `Notification` | Claude Code sendet eine Benachrichtigung | nein | `permission_prompt`, `idle_prompt` und weitere |
| `SubagentStart` | ein Subagent startet | nein | Agent-Typ |
| `SubagentStop` | ein Subagent ist fertig | ja | Agent-Typ |
| `TaskCreated` | Task wird angelegt | ja | kein Matcher |
| `TaskCompleted` | Task wird als erledigt markiert | ja | kein Matcher |
| `Stop` | Claude ist mit der Antwort fertig (nicht bei Abbruch durch dich) | ja | kein Matcher |
| `StopFailure` | Turn endet durch einen API-Fehler | nein | Fehlertyp |
| `TeammateIdle` | ein Teammate in einem Agent Team wartet | ja | kein Matcher |
| `ConfigChange` | Settings-, Policy- oder Skill-Datei ändert sich | ja, außer `policy_settings` | Quelle |
| `CwdChanged` | Arbeitsverzeichnis wechselt | nein | kein Matcher |
| `DirectoryAdded` | `/add-dir` fügt einen Ordner hinzu | nein | Herkunft |
| `FileChanged` | eine beobachtete Datei ändert sich | nein | wörtliche Dateinamen |
| `WorktreeCreate` | ein Worktree wird erstellt, ersetzt das Git-Standardverhalten | ja | kein Matcher |
| `WorktreeRemove` | ein vom Hook erstellter Worktree wird entfernt | ja | kein Matcher |
| `PreCompact` | vor der Compaction | ja | `manual`, `auto` |
| `PostCompact` | nach der Compaction | nein | `manual`, `auto` |
| `PreModelSwitch` | vor einem Modellwechsel (ab v2.1.251) | ja | Name des Zielmodells |
| `PostModelSwitch` | nach einem Modellwechsel (ab v2.1.251) | nein | Name des Zielmodells |
| `Elicitation` | ein MCP-Server fragt eine Eingabe an | ja | MCP-Servername |
| `ElicitationResult` | nach deiner Antwort auf eine Elicitation | ja | MCP-Servername |
| `SessionEnd` | Sitzung endet | nein | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` |

Bei Ereignissen ohne Matcher wird ein gesetzter `matcher` stillschweigend ignoriert.

## Was bekommt ein Hook auf stdin?

Jeder Hook erhält ein JSON-Objekt auf stdin. Diese Felder sind fast immer dabei:

| Feld | Bedeutung |
| --- | --- |
| `session_id` | ID der Sitzung |
| `transcript_path` | Pfad zum Verlauf als JSONL, kann hinterherhinken |
| `cwd` | aktuelles Arbeitsverzeichnis, folgt `cd` und Worktrees |
| `hook_event_name` | Name des Ereignisses |
| `permission_mode` | `default`, `plan`, `acceptEdits`, `auto`, `dontAsk` oder `bypassPermissions`, nicht bei jedem Ereignis |
| `prompt_id` | ID des aktuellen Prompts, fehlt bis zur ersten Eingabe |
| `agent_id`, `agent_type` | nur in Subagents oder mit `--agent` |

Dazu kommen Felder je Ereignis. `PreToolUse` liefert `tool_name`, `tool_input` und `tool_use_id`, `PostToolUse` zusätzlich `tool_response` und `duration_ms`, `UserPromptSubmit` liefert `prompt`, `Stop` liefert `stop_hook_active` und `last_assistant_message`, `SessionStart` liefert `source`. Für `Read`, `Edit` und `Write` ist `tool_input.file_path` immer ein absoluter Pfad.

```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/projekt/transcript.jsonl",
  "cwd": "/home/user/projekt",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test", "description": "Run test suite", "timeout": 120000, "run_in_background": false },
  "tool_use_id": "toolu_01ABC"
}
```

## Exit-Code 0, 2 oder etwas anderes: was passiert?

Das Ergebnis hängt von Exit-Code und stdout zusammen ab.

| stdout | Exit 0 | Exit 2 | anderer Exit-Code |
| --- | --- | --- | --- |
| gültiges JSON-Objekt | Erfolg, die Felder wirken | blockiert, ein `allow` im JSON hebt das nicht auf | Exit-Code wird ignoriert, die Felder entscheiden |
| ungültiges JSON | nicht blockierender Fehler | blockiert, stderr ist der Grund | nicht blockierender Fehler |
| Text oder leer | Erfolg | blockiert, stderr ist der Grund | nicht blockierender Fehler |

- Exit 1 blockiert nicht. Wer eine Regel durchsetzen will, nimmt Exit 2 oder JSON.
- Bei Exit 0 landet Klartext auf stdout meist nur im Debug-Log. Ausnahmen sind `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart` und `PostModelSwitch`: Dort wird der Text Kontext für Claude.
- stderr bei Exit 0 sieht Claude nie.
- Ein Hook, der nicht startet (falscher Pfad, nicht ausführbar), ist ein nicht blockierender Fehler. Die Aktion läuft weiter. Ab v2.1.295 lässt sich das mit `"onFailure": "block"` umdrehen.
- Ein Timeout bei `PreToolUse` blockiert nicht. Der Aufruf geht in den normalen Berechtigungsablauf.

## JSON-Ausgabe: permissionDecision, decision und additionalContext

Für feinere Entscheidungen gibt der Hook mit Exit 0 genau ein JSON-Objekt auf stdout aus, sonst nichts.

### PreToolUse: allow, deny, ask oder defer

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": ".env enthält Zugangsdaten und ist für Claude gesperrt."
  }
}
```

| Wert | Wirkung |
| --- | --- |
| `allow` | überspringt die Rückfrage, deny- und ask-Regeln aus den Settings gelten trotzdem |
| `deny` | blockiert den Aufruf, Claude sieht `permissionDecisionReason` |
| `ask` | zeigt dir die Rückfrage mit dem Grund |
| `defer` | wirkt nur mit `-p` und nur, wenn der Turn genau einen Tool-Aufruf hat |

Melden mehrere Hooks verschiedene Entscheidungen, gilt `deny` vor `defer` vor `ask` vor `allow`. Mit `updatedInput` kann ein Hook die Eingabe ersetzen, dabei immer das komplette Objekt mitschicken. Das alte top-level `decision` mit `approve` oder `block` ist für `PreToolUse` veraltet.

### UserPromptSubmit, Stop und PostToolUse: decision block

Diese Ereignisse nutzen ein top-level `decision`:

```json
{
  "decision": "block",
  "reason": "Personenbezogene Daten gefunden. Der Prompt wurde nicht gesendet."
}
```

Bei `UserPromptSubmit` wird der Prompt verworfen. Bei `Stop` arbeitet Claude weiter und bekommt `reason` als nächste Anweisung. Bei `PostToolUse` ist das Tool schon gelaufen, der Grund geht als Rückmeldung an Claude.

### additionalContext: Kontext mitgeben

`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse` und `Stop` können über `hookSpecificOutput.additionalContext` Text in den Kontext legen. Ein Beispiel zeigt der Hook `sitzungsstart.py` weiter unten. `additionalContext` und `systemMessage` sind auf je 10.000 Zeichen begrenzt. Längeren Text schreibt Claude Code in eine Datei und gibt nur Pfad und Vorschau weiter. Universell gibt es außerdem `continue: false` mit `stopReason` (stoppt Claude komplett) und `systemMessage` (Warnung an dich).

## Stop-Hooks ohne Endlosschleife: stop_hook_active und die 8er-Kappe

Ein Stop-Hook, der blockt, schickt Claude zurück an die Arbeit. Damit daraus keine Schleife wird, steht im Eingabe-JSON `stop_hook_active: true`, wenn Claude bereits wegen eines Stop-Hooks weiterarbeitet. Prüfe dieses Feld und lass den Stopp dann durch. Zusätzlich beendet Claude Code den Turn nach acht Fortsetzungen in Folge ohne Tool-Aufruf dazwischen trotzdem. Die Grenze lässt sich mit `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` ändern.

## matcher, if, timeout und ${CLAUDE_PROJECT_DIR}

Der `matcher` wird je nach Zeichen unterschiedlich ausgewertet:

| matcher | Auswertung | Beispiel |
| --- | --- | --- |
| `"*"`, `""` oder weggelassen | trifft alles | jedes Tool |
| nur Buchstaben, Ziffern, `_`, `-`, Leerzeichen, `,`, `\|` | exakte Namen, getrennt durch `\|` oder `,` | `Bash`, `Edit\|Write` |
| jedes andere Zeichen | JavaScript-RegExp, nicht verankert | `^Notebook`, `mcp__github__.*` |

- `Edit.*` trifft auch `NotebookEdit`. Für genau `Edit` nimm `^Edit$`.
- `mcp__memory` ohne `.*` trifft kein einziges Tool. Richtig ist `mcp__memory__.*`.
- Matcher unterscheiden Groß- und Kleinschreibung.

Das Feld `if` filtert genauer mit genau einer Berechtigungsregel, etwa `"if": "Bash(git *)"`. Es wirkt nur bei `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest` und `PermissionDenied`. Bei anderen Ereignissen läuft ein Hook mit `if` nie. Für harte Grenzen ist `if` nicht gedacht, dafür gibt es Permissions.

`timeout` steht in Sekunden. Standard sind 600 Sekunden für `command`, `http` und `mcp_tool`, aber 30 Sekunden bei `UserPromptSubmit`, 30 Sekunden für `prompt` und 60 Sekunden für `agent`. Alle `SessionEnd`-Hooks teilen sich 1,5 Sekunden, ein größerer `timeout` hebt das Budget auf höchstens 60 Sekunden.

`CLAUDE_PROJECT_DIR` zeigt auf den Projektordner beim Start der Sitzung und bleibt auch nach `cd` gleich. Nutze ihn für Skriptpfade, dann läuft der Hook aus jedem Unterordner. In der Shell-Form gehört die Variable in doppelte Anführungszeichen. Mit `args` startet die Exec-Form ohne Shell, dann sind keine Anführungszeichen nötig:

```json
{
  "type": "command",
  "command": "python3",
  "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/secrets_schutz.py"],
  "timeout": 10
}
```

Die Exec-Form passt immer, wenn ein Pfad-Platzhalter vorkommt. Die Shell-Form brauchst du für Pipes oder `&&`. Unter Windows muss `command` in der Exec-Form eine echte ausführbare Datei sein, `.cmd`- und `.bat`-Dateien gehen nur in der Shell-Form.

## Welche Hook-Typen gibt es?

| `type` | Was passiert | Standard-Timeout |
| --- | --- | --- |
| `command` | Shell-Befehl, Eingabe als JSON auf stdin | 600 s |
| `http` | POST des Eingabe-JSON an `url` | 600 s |
| `mcp_tool` | ruft ein Tool auf einem konfigurierten MCP-Server auf | 600 s |
| `prompt` | einmalige Bewertung durch ein Modell, Antwort `{"ok": true}` oder `{"ok": false, "reason": "..."}` | 30 s |
| `agent` | Subagent mit Tools bis zu 50 Turns, laut Doku experimentell | 60 s |

Nicht jedes Ereignis kennt alle Typen. `SessionStart` und `Setup` erlauben nur `command` und `mcp_tool`, `PermissionRequest` alle außer `agent`. Für Schutzregeln ist `command` die robuste Wahl, weil das Ergebnis deterministisch ist. `async: true` (nur bei `command`) startet einen Hook im Hintergrund, er kann dann aber nichts mehr entscheiden.

## Die sieben Hooks der Vorlage

Die [Vorlage](../../src/claude_team/vorlage/.claude/settings.json) in diesem Repo bringt sieben Hooks in Python 3.10+ mit, nur mit Standardbibliothek. Sie liegen unter `.claude/hooks/` und werden über `.claude/schutz.json` eingestellt. Stürzt ein Hook selbst ab, lässt er die Aktion durch (fail open), damit ein kaputter Hook niemanden aussperrt. Die deny-Regeln in der settings.json sind deshalb die erste Schutzschicht, die Hooks die zweite.

So sind sie in der [settings.json der Vorlage](../../src/claude_team/vorlage/.claude/settings.json) eingetragen (gekürzt):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/sitzungsstart.py\"", "timeout": 10 } ] }
    ],
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/pii_schutz.py\"", "timeout": 10 } ] }
    ],
    "PreToolUse": [
      { "matcher": "Read|Edit|Write|MultiEdit|NotebookEdit|Grep|Glob|Bash|PowerShell", "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/secrets_schutz.py\"", "timeout": 10 } ] },
      { "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash|PowerShell", "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/pii_schutz.py\"", "timeout": 10 } ] },
      { "matcher": "Bash|PowerShell", "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/befehle_schutz.py\"", "timeout": 10 } ] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write|MultiEdit", "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/format_nach_edit.py\"", "timeout": 30 } ] },
      { "matcher": "*", "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/protokoll.py\"", "timeout": 5 } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/stopp_tests.py\"", "timeout": 600 } ] }
    ]
  }
}
```

Die Einstellungen stehen in [`.claude/schutz.json`](../../src/claude_team/vorlage/.claude/schutz.json):

```json
{
  "secrets": { "modus": "deny", "pfade_ausnehmen": [] },
  "pii": { "modus": "deny", "kontakte_ab": 5, "pfade_ausnehmen": ["tests/fixtures/**"] },
  "befehle": { "modus": "deny", "fragen_bei": ["git push", "npm publish", "terraform apply", "kubectl delete", "helm upgrade"] },
  "protokoll": { "aktiv": false, "ordner": ".claude/protokoll", "aufbewahrung_tage": 30 },
  "stopp": { "befehl": "" }
}
```

`modus` kennt `deny`, `ask` und `aus`. Alle Tests unten laufen im Projektordner, die Ausgaben sind echt.

### 1. secrets_schutz.py: .env, Schlüssel und Tokens sperren

[secrets_schutz.py](../../src/claude_team/vorlage/.claude/hooks/secrets_schutz.py) läuft vor `Read`, `Edit`, `Write`, `MultiEdit`, `NotebookEdit`, `Grep`, `Glob` und `Bash`. Er sperrt `.env` und `.env.*`, Schlüsseldateien wie `*.pem`, `*.key` und `id_rsa`, Cloud-Credentials unter `.aws`, `.ssh`, `.kube`, `.azure` und `.config/gcloud` sowie Terraform-State. In Bash- und PowerShell-Befehlen blockt er `env`, `printenv`, `export`, `declare -x`, `gh auth token` und jeden Befehl, der einen solchen Pfad nennt, auch in Interpreter-Code wie `python3 -c "open('.env')"`. Platzhalter wie `cat .e*v` löst er gegen den Arbeitsordner auf, und `grep -r` über einen Ordner mit `.env` blockt er, solange kein `--exclude` gesetzt ist. Nur `ls`, `test`, `stat` und `touch` dürfen solche Pfade nennen, weil sie keinen Inhalt ausgeben. Pfade, die erst zur Laufzeit entstehen (Variablen, `$(...)`, Base64), erkennt er nicht. Neuer Code mit Tokens (AWS, GitHub, GitLab, Slack, Anthropic, OpenAI, Google, Stripe, Azure, JWT, URL mit Passwort) wird ebenfalls blockiert. `.env.example`, `.env.sample` und `*.pub` bleiben erlaubt, Platzhalter wie `${API_KEY}` oder `<dein-token>` auch.

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"Read","tool_input":{"file_path":"'"$PWD"'/.env"}}' \
  | python3 .claude/hooks/secrets_schutz.py
```

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": ".env enthält Zugangsdaten und ist für Claude gesperrt. Für Beispiele .env.example verwenden."}}
```

Derselbe Test mit `.env.example` gibt nichts aus und endet mit Exit 0, die Aktion ist also erlaubt.

### 2. pii_schutz.py: deutsche personenbezogene Daten mit Prüfziffern

[pii_schutz.py](../../src/claude_team/vorlage/.claude/hooks/pii_schutz.py) läuft bei `UserPromptSubmit` und vor `Edit`, `Write`, `MultiEdit`, `NotebookEdit` und `Bash`. Er blockt nur Werte mit gültiger Prüfziffer, damit Fehlalarme selten bleiben:

| Datum | Prüfverfahren | Reaktion |
| --- | --- | --- |
| IBAN | ISO 13616, Mod 97 | blockieren |
| Steuer-ID | ISO 7064 Mod 11,10 plus Ziffernregel | blockieren |
| Sozialversicherungsnummer | Prüfziffer der Deutschen Rentenversicherung | blockieren |
| Kreditkarte | Luhn | blockieren |
| USt-IdNr. | ISO 7064 Mod 11,10 | Rückfrage |
| ab 5 verschiedenen E-Mail-Adressen oder Telefonnummern | Zählung | Rückfrage |

Er prüft den Prompt und das, was ein Tool neu schreiben oder ausführen würde (`content`, `new_string`, `command`). Den Inhalt von Dateien, die Claude liest, sieht er nicht. Verbreitete Beispielwerte wie die Beispiel-IBAN `DE89 3704 0044 0532 0130 00` oder die Testkarten 4111 und 4012 sind erlaubt. Ordner mit Testdaten nimmst du über `pii.pfade_ausnehmen` aus.

```bash
echo '{"hook_event_name":"UserPromptSubmit","prompt":"Testdaten mit DE89 3704 0044 0532 0130 00"}' \
  | python3 .claude/hooks/pii_schutz.py; echo "exit=$?"
```

Die Beispiel-IBAN gibt keine Ausgabe und `exit=0`. Ersetzt du sie durch eine andere IBAN mit gültiger Prüfziffer (`<gültige-iban>`), blockt der Hook den Prompt und zeigt den Wert nur maskiert:

```json
{"decision": "block", "reason": "Personenbezogene Daten gefunden: IBAN DE12****************90. Durch Testdaten ersetzen (z.B. die verbreitete Beispiel-IBAN DE89 3704 0044 0532 0130 00). Der Prompt wurde nicht gesendet."}
```

Wichtig: Der blockierte Prompt geht nicht an das Modell. Laut Doku kann er aber trotzdem lokal im Transcript und in der Prompt-History landen. Ein Hook ersetzt also keine Schulung, keine Daten in den Chat zu kopieren.

### 3. befehle_schutz.py: gefährliche Befehle stoppen

[befehle_schutz.py](../../src/claude_team/vorlage/.claude/hooks/befehle_schutz.py) läuft vor `Bash` und `PowerShell` und prüft jeden Teil einer Befehlskette, also auch `cd /tmp && rm -rf ~`, dazu den Inhalt von `bash -c "..."`, `eval` und `$(...)`. Globale Git-Optionen wie `git -C repo` oder `git -c x=y` stören die Erkennung nicht. Text in Commit-Nachrichten (`-m "..."`) zählt nicht als Befehl. Permission-Regeln wie `Bash(rm -rf *)` greifen dagegen nur am Anfang eines Befehls.

| Stufe | Befehle |
| --- | --- |
| sperren | `rm -rf` auf `/`, `~`, `~/*`, `.` oder `*`, `git push --force`, `-f` und `+branch` (ohne `-with-lease`), `--no-verify`, `curl ... \| sh`, `bash <(curl ...)`, `sh -c "$(curl ...)"`, `chmod 777`, `mkfs`, `dd` auf Geräte |
| nachfragen | `rm -r`, `git reset --hard`, `git clean -f`, `git branch -D`, `sudo`, `DROP TABLE`, `terraform destroy` und alles aus `befehle.fragen_bei` |

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git reset --hard HEAD~1"}}' \
  | python3 .claude/hooks/befehle_schutz.py
```

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "Riskanter Befehl (git reset --hard verwirft lokale Änderungen). Bitte bestätigen."}}
```

### 4. protokoll.py: Tool-Nutzung nachvollziehen

[protokoll.py](../../src/claude_team/vorlage/.claude/hooks/protokoll.py) ist standardmäßig aus. Mit `"aktiv": true` läuft er nach jedem Tool (`PostToolUse` mit `*`) und schreibt je Tag eine JSON-Lines-Datei nach `.claude/protokoll/`. Gespeichert werden Zeit, die ersten 8 Zeichen der Sitzungs-ID, Tool, Datei, Befehl und Dauer. Im Befehl ersetzt er Tokens, IBAN, Steuer-ID, Sozialversicherungsnummer, Kartennummern und E-Mail-Adressen durch Platzhalter, Heredoc-Inhalte (ab `<<`) speichert er nicht. Dateiinhalte werden nie gespeichert. Dateien, die älter als `aufbewahrung_tage` sind (Standard 30), löscht er beim nächsten Schreiben. Das Protokoll zeichnet auf, wer wann welchen Befehl ausgeführt hat; im Team schaltest du es erst nach Absprache mit Betriebsrat und Datenschutz ein. Der Ordner gehört in `.gitignore` (Regel [CC051](../regeln.md#cc051)).

```json
{"zeit": "2026-10-15T20:41:19+00:00", "sitzung": "abc12345", "ereignis": "PostToolUse", "tool": "Bash", "modus": "", "befehl": "pytest -q", "dauer_ms": 812}
```

### 5. format_nach_edit.py: nach jeder Änderung formatieren

[format_nach_edit.py](../../src/claude_team/vorlage/.claude/hooks/format_nach_edit.py) läuft nach `Edit`, `Write` und `MultiEdit`. Er nutzt nur Formatter, die schon da sind: `ruff format` oder `black` für Python, `prettier` aus `node_modules/.bin` für JS, TS, JSON, CSS, Markdown und YAML, `gofmt`, `rustfmt` und `terraform fmt`. Fehlt ein Formatter, passiert nichts.

### 6. sitzungsstart.py: Git-Stand als Kontext

[sitzungsstart.py](../../src/claude_team/vorlage/.claude/hooks/sitzungsstart.py) läuft bei `SessionStart` und gibt Branch, Zahl offener Änderungen und die letzten drei Commits als `additionalContext` mit. Auf `main` oder `master` kommt ein Hinweis, vor Änderungen einen Branch anzulegen.

```json
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Git-Branch: main\nOffene Änderungen: 1 Dateien\nHinweis: Du bist auf dem Hauptbranch. Vor Änderungen einen Feature-Branch anlegen."}}
```

### 7. stopp_tests.py: erst fertig, wenn die Tests grün sind

[stopp_tests.py](../../src/claude_team/vorlage/.claude/hooks/stopp_tests.py) läuft bei `Stop`. Ist in `schutz.json` ein `stopp.befehl` gesetzt (zum Beispiel `pytest -q` oder `npm test && npm run lint`) und zeigt Git offene Änderungen, führt der Hook den Befehl in der Shell aus; Ketten mit `&&` und `|` gehen also. Nach `claude-team einrichten` ist der Befehl leer, der Hook also aus, bis du ihn einträgst. Schlägt er fehl, antwortet der Hook mit `decision: block` und den letzten 40 Zeilen der Ausgabe. Ist `stop_hook_active` gesetzt, läuft er nicht noch einmal. Leerer Befehl heißt aus.

```json
{"decision": "block", "reason": "'pytest -q' schlägt fehl (Exit 1). Bitte beheben, bevor du fertig meldest.\n\n<letzte 40 Zeilen>"}
```

## Beispiele für Claude Code Hooks

### Beispiel 1: Minimaler Bash-Hook gegen rm -rf

Für den Einstieg: ein Skript, das `rm -rf` per JSON ablehnt. Braucht `jq`.

```bash
#!/bin/bash
# .claude/hooks/block-rm.sh
COMMAND=$(jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "rm -rf ist per Hook gesperrt."
    }
  }'
else
  exit 0
fi
```

```bash
chmod +x .claude/hooks/block-rm.sh
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf build"}}' | .claude/hooks/block-rm.sh
```

Eingetragen wird er wie im ersten JSON-Block dieser Anleitung mit `"matcher": "Bash"`.

### Beispiel 2: Minimaler Python-Hook, der .env per Exit 2 sperrt

Ohne `jq` und ohne JSON-Ausgabe: Exit 2 blockt, stderr ist der Grund für Claude.

```python
#!/usr/bin/env python3
"""PreToolUse-Hook: sperrt .env und .env.*, erlaubt .env.example."""
import json
import sys
from pathlib import Path

daten = json.load(sys.stdin)
pfad = (daten.get("tool_input") or {}).get("file_path", "")
name = Path(pfad).name

if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
    print(f"{name} enthält Zugangsdaten und ist gesperrt. Nutze .env.example.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
```

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Read|Edit|Write", "hooks": [ { "type": "command", "command": "python3", "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/env_sperre.py"] } ] }
    ]
  }
}
```

### Beispiel 3: Dateien nach jeder Änderung mit Prettier formatieren

Aus der offiziellen Doku, für JavaScript- und TypeScript-Projekte:

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write", "hooks": [ { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" } ] }
    ]
  }
}
```

### Beispiel 4: Wichtigen Kontext nach der Compaction erneut einspielen

Ein `SessionStart`-Hook mit Matcher `compact` läuft nach jeder Zusammenfassung. Klartext auf stdout wird Kontext.

```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "compact", "hooks": [ { "type": "command", "command": "echo 'Erinnerung: Tests mit pytest -q, keine echten Kundendaten in Fixtures.' && git log --oneline -5" } ] }
    ]
  }
}
```

### Beispiel 5: Desktop-Benachrichtigung, wenn Claude auf dich wartet

Für lange Aufgaben: `Notification` meldet sich, wenn Claude eine Freigabe braucht. Auf macOS mit `osascript`, unter Linux mit `notify-send 'Claude Code' 'Claude wartet auf dich'`.

```json
{
  "hooks": {
    "Notification": [
      { "matcher": "permission_prompt|idle_prompt", "hooks": [ { "type": "command", "command": "osascript -e 'display notification \"Claude wartet auf dich\" with title \"Claude Code\"'" } ] }
    ]
  }
}
```

### Beispiel 6: Stop-Hook in Bash, der Tests erzwingt

Die kurze Variante von `stopp_tests.py`. Exit 2 bei `Stop` heißt: Claude arbeitet weiter, stderr ist die Anweisung.

```bash
#!/bin/bash
# .claude/hooks/tests-vor-stopp.sh
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0
fi
if ! AUSGABE=$(npm test 2>&1); then
  echo "Tests schlagen fehl. Bitte beheben:" >&2
  echo "$AUSGABE" | tail -n 30 >&2
  exit 2
fi
exit 0
```

### Beispiel 7: Prompt-Hook prüft, ob alles erledigt ist

Ein `prompt`-Hook fragt ein Modell. Bei `{"ok": false}` arbeitet Claude mit dem Grund weiter.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Prüfe, ob alle Aufgaben erledigt sind: $ARGUMENTS. Wenn nicht, antworte mit {\"ok\": false, \"reason\": \"was noch fehlt\"}.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Beispiel 8: Branch bei jedem Prompt mitgeben

Bei `UserPromptSubmit` wird Klartext auf stdout zu Kontext. Praktisch, wenn du oft zwischen Branches wechselst.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "echo \"Aktueller Branch: $(git branch --show-current)\"" } ] }
    ]
  }
}
```

## Schritt für Schritt: Schutz-Hooks ins eigene Projekt bringen

1. Vorschau ansehen, ohne etwas zu schreiben: `uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team einrichten . --dry-run`
2. Einrichten: denselben Befehl ohne `--dry-run`. Hooks, `.claude/schutz.json` und settings.json landen im Projekt. Gibt es schon eine settings.json, entsteht `.claude/settings.vorschlag.json` zum Zusammenführen.
3. Alternativ als Plugin: `claude plugin marketplace add pexon-consulting/claude-code-best-practices` und `claude plugin install team-basis@claude-code-best-practices`.
4. In `.claude/schutz.json` den Testbefehl unter `stopp.befehl` eintragen (mehrere Schritte mit `&&`) und bei Bedarf `pfade_ausnehmen` für Testdaten setzen. Das Protokoll bleibt aus, bis ihr es im Team abgestimmt habt.
5. Jeden Hook einmal per Pipe testen, wie oben gezeigt.
6. Claude Code im Projekt starten, den Workspace-Trust-Dialog annehmen und mit `/hooks` prüfen, ob alle Einträge erscheinen.
7. Probe aufs Exempel: Claude bitten, `.env` zu lesen. Claude muss die Sperre mit dem Grund aus dem Hook melden.
8. Mit `claude-team audit .` prüfen, ob Hook-Skripte fehlen, nicht ausführbar sind oder relative Pfade nutzen (Regeln [CC020](../regeln.md#cc020) bis [CC024](../regeln.md#cc024)).
9. `.claude/settings.json`, `.claude/schutz.json` und `.claude/hooks/` committen, `.claude/protokoll/` in `.gitignore` eintragen.

## Hooks testen und debuggen

- **Per Pipe:** `echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./mein-hook.sh` und danach `echo $?` für den Exit-Code.
- **`/hooks`:** zeigt alle konfigurierten Hooks mit Quelle (User, Projekt, Local, Plugin, Sitzung). Erscheint ein Hook nicht, ist die settings.json ungültig oder liegt am falschen Ort.
- **`claude --debug`:** schreibt das Debug-Log nach `~/.claude/debug/<sitzung>.txt`, nicht ins Terminal. Mit `claude --debug-file /tmp/claude.log` legst du den Ort fest und liest in einem zweiten Terminal mit `tail -f /tmp/claude.log` mit. In der laufenden Sitzung schaltet `/debug` das Logging ein.
- **Typische Zeilen im Log:** `Hook output does not start with {, treating as plain text` (etwas schreibt vor dem JSON auf stdout), `Hook JSON output had unrecognized keys` (Feld auf der falschen Ebene).
- **`Ctrl+O`:** öffnet die Transcript-Ansicht. Dort siehst du Block-Meldungen und `hook error`-Hinweise.

## Was die Hooks nicht abdecken

Die Hooks sehen nur, was Claude Code tun will, nicht, was dabei herauskommt. Daraus ergeben sich feste Grenzen:

- **Gelesene Inhalte:** `pii_schutz.py` läuft vor dem Absenden eines Prompts und vor Edit, Write und Bash. Was Read, Grep oder ein Shell-Befehl als Ergebnis zurückgeben, sieht der Hook nicht; es geht direkt an das Modell. Liest Claude eine CSV mit Kundendaten, landen die Daten im Kontext. Datenordner sperrst du deshalb mit deny-Regeln wie `Read(./data/**)`; Claude Code wendet Read-Regeln laut Doku nach bestem Bemühen auch auf Grep und Glob an. Für eine Sperre, die auch Skripte und Unterprozesse trifft, braucht es die [Sandbox](./claude-code-sandbox.md).
- **Nur Kennungen mit Prüfziffer:** Erkannt werden IBAN, Steuer-ID, Sozialversicherungsnummer, Kreditkarte und USt-IdNr. in üblicher Schreibweise. Namen, Anschriften, Geburtsdaten, Gesundheitsdaten und Freitext erkennt kein Hook.
- **Umwege:** `secrets_schutz.py` und `befehle_schutz.py` arbeiten mit Mustern. Pfade oder Befehle, die erst zur Laufzeit entstehen (Variablen, `$(...)`, Base64, ein Skript, das selbst Dateien öffnet), erkennen sie nicht. Bei unbekannten Befehlen fragt Claude Code im Standardmodus trotzdem nach; mit breiten allow-Regeln, `acceptEdits` oder Auto Mode nicht immer.
- **Fail open:** Stürzt ein Hook ab oder fehlt `python3`, läuft die Aktion weiter.
- **Lokale Spuren:** Ein blockierter Prompt geht nicht an das Modell, kann aber lokal im Transcript und in der Prompt-History landen.

Hooks ergänzen deny-Regeln, Testdaten ohne Echtdaten und Schulung, sie ersetzen sie nicht. In einer DSFA oder TOM gehören sie deshalb nur mit diesen Grenzen hinein.

## Sicherheit: Hooks laufen mit deinen Rechten

- Command-Hooks laufen mit den vollen Rechten deines Benutzers. Prüfe Hooks aus fremden Repos, bevor du dem Ordner vertraust.
- Interaktiv hält Claude Code Hooks zurück, bis du den Workspace-Trust-Dialog annimmst. Mit `-p` und im Agent SDK gilt der Ordner als vertraut, Hooks aus einer fremden `.claude/settings.json` laufen also sofort.
- Vor `claude -p` auf fremden Repos hilft `--bare` (ohne Hooks, Skills, Plugins, MCP), `--settings '{"disableAllHooks": true}'` oder `--setting-sources user`.
- `disableAllHooks` in User-, Projekt- oder Local-Settings schaltet Hooks aus Managed Settings nicht ab. `allowManagedHooksOnly` in Managed Settings erlaubt nur noch zentrale Hooks.
- Validiere Eingaben, setze Variablen in Anführungszeichen (`"$VAR"`) und fange `..` in Pfaden ab.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Exit 1 statt Exit 2 | Aktion läuft trotz Fehlermeldung weiter | Exit 2 oder JSON mit `deny` nutzen |
| `permissionDecision` auf oberster Ebene | JSON wird still ignoriert | in `hookSpecificOutput` verschachteln |
| Shell-Profil schreibt auf stdout | JSON wirkt nicht | `echo` in `~/.zshrc` nur für interaktive Shells ausführen |
| relativer Skriptpfad | `command not found` in Unterordnern | `${CLAUDE_PROJECT_DIR}` nutzen ([CC023](../regeln.md#cc023)) |
| Skript nicht ausführbar | Hook läuft nicht, Aktion geht durch | `chmod +x` ([CC022](../regeln.md#cc022)) |
| Matcher `mcp__github` | Hook feuert nie | `mcp__github__.*` schreiben |
| Stop-Hook ohne `stop_hook_active` | Claude hört nicht auf, Warnung nach acht Runden | Feld prüfen und früh mit Exit 0 enden |
| Hook als einzige Sperre | kaputter Hook öffnet alles | zusätzlich deny-Regeln in der settings.json ([CC013](../regeln.md#cc013)) |

## Häufige Fragen

### Wie blockiere ich mit einem Hook, dass Claude Code die .env liest?

Mit einem `PreToolUse`-Hook für `Read|Edit|Write|Grep|Glob|Bash`, der den Dateinamen prüft und mit Exit 2 oder `permissionDecision: "deny"` antwortet. Ergänze immer die deny-Regeln `Read(.env)` und `Read(.env.*)` in der settings.json, damit die Sperre auch hält, wenn der Hook ausfällt.

### Was ist der Unterschied zwischen Exit 1 und Exit 2?

Exit 2 blockiert die Aktion, und stderr geht als Grund an Claude. Exit 1 gilt als nicht blockierender Fehler, die Aktion läuft weiter, und du siehst nur einen Hinweis.

### Greift ein Hook auch mit --dangerously-skip-permissions?

Ja. `PreToolUse`-Hooks laufen vor jeder Modus-Prüfung, ein `deny` blockt auch in `bypassPermissions`. Umgekehrt hebelt ein `allow` aus einem Hook keine deny-Regel aus den Settings aus.

### Warum wird mein Hook nicht ausgeführt?

Meist stimmt der Matcher nicht (Groß- und Kleinschreibung beachten), die settings.json ist ungültig, oder der Ordner ist noch nicht vertraut. Prüfe mit `/hooks`, ob der Hook erscheint, und mit `claude --debug-file /tmp/claude.log`, was passiert.

### Kann ein Hook den Prompt verändern?

Nein. `UserPromptSubmit` kann einen Prompt nur blockieren oder Kontext ergänzen, nicht ersetzen. Ein `PreToolUse`-Hook kann dagegen mit `updatedInput` die Eingabe eines Tools ändern.

### Brauche ich Python für die Hooks der Vorlage?

Ja, Python 3.10 oder neuer muss als `python3` im PATH liegen. Die Hooks nutzen nur die Standardbibliothek, es ist also nichts zu installieren.

## Weiterlesen

- [Claude Code Permissions](./claude-code-permissions.md): allow, ask und deny als erste Schutzschicht
- [Claude Code settings.json](./claude-code-settings-json.md): wo Hooks stehen und welche Datei gewinnt
- [Claude Code DSGVO](./claude-code-dsgvo.md): personenbezogene Daten im Unternehmen
- [Claude Code Sicherheit](./claude-code-sicherheit.md): Risiken im Team begrenzen
- [Claude Code Plugins](./claude-code-plugins.md): Hooks als Plugin im Team verteilen
- [Claude Code Review: automatische Reviews mit GitHub Actions](./claude-code-review-github-actions.md)
- Prüfregeln zu Hooks: [CC020](../regeln.md#cc020), [CC021](../regeln.md#cc021), [CC022](../regeln.md#cc022), [CC023](../regeln.md#cc023), [CC024](../regeln.md#cc024), [CC051](../regeln.md#cc051)
- Offizielle Doku: [Hooks reference](https://code.claude.com/docs/en/hooks) und [Hooks guide](https://code.claude.com/docs/en/hooks-guide)
