# Claude Code Permissions: Berechtigungen mit allow, ask und deny festlegen

Claude Code Permissions legst du in der settings.json mit drei Listen fest: `allow` erlaubt einen Befehl dauerhaft ohne Rückfrage, `ask` fragt immer nach und `deny` verbietet ihn. Geprüft wird immer in der Reihenfolge deny, dann ask, dann allow, und die erste passende Regel entscheidet. Wie viel Claude ohne Rückfrage tun darf, bestimmst du zusätzlich mit dem Permission Mode, etwa Auto Mode oder acceptEdits.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Eine Regel hat die Form `Werkzeug` oder `Werkzeug(Muster)`, zum Beispiel `Bash(npm run test *)` oder `Read(./.env)`.
- deny schlägt ask, ask schlägt allow. Ein `allow` kann keine Ausnahme aus einem `deny` herausschneiden.
- Bei Bash-Regeln gehört der Stern hinter den Unterbefehl und mit Leerzeichen davor: `Bash(git diff *)`, nicht `Bash(git * diff)`.
- Pfadregeln wirken nur für `Read` und `Edit`. Eine Regel wie `Write(...)` ignoriert Claude Code; nimm `Edit(...)`, das gilt für alle Werkzeuge, die Dateien ändern.
- Die Regeln setzt Claude Code durch, nicht das Modell. Eine Anweisung in der CLAUDE.md ersetzt keine `deny`-Regel.
- Bash-Regeln sind keine Sicherheitsgrenze. Für echten Schutz kommen Sandbox oder Hooks dazu.

## Wie erlaube ich einen Befehl dauerhaft?

Drei Wege führen zum gleichen Ergebnis:

1. **In der Rückfrage:** "Yes, and don't ask again for: npm test \*" speichert die Regel in `.claude/settings.local.json` am Root des Git-Repos. Das gilt für Bash-Befehle, WebFetch-Domains und WebSearch. Freigaben für Dateiänderungen gelten nur bis zum Ende der Sitzung.
2. **Mit `/permissions`:** Der Dialog listet alle Regeln mit der Datei, aus der sie stammen, und lässt dich Regeln hinzufügen oder entfernen. Seit v2.1.234 gilt eine Änderung ab dem nächsten Werkzeugaufruf, auch mitten im Turn.
3. **Direkt in der settings.json:** für Team-Regeln in `.claude/settings.json`, für dich in `~/.claude/settings.json`.

```json
{
  "permissions": {
    "allow": ["Bash(npm run test *)", "Bash(npm run lint)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"]
  }
}
```

Was ohne Regel passiert, zeigt die Tabelle für den Manual-Modus:

| Werkzeug | Rückfrage | "Don't ask again" gilt |
| --- | --- | --- |
| Lesen, Grep | nein, im Arbeitsordner und zusätzlichen Ordnern | entfällt |
| Bash | ja, außer eingebauten Nur-Lese-Befehlen | dauerhaft pro Repo und Befehl |
| Dateien ändern | ja | bis Sitzungsende |
| WebFetch | ja, außer vorab freigegebenen Doku-Domains | dauerhaft pro Repo und Domain |
| WebSearch | ja | dauerhaft pro Repo |

Nur-Lese-Befehle wie `ls`, `cat`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `diff` und lesende `git`-Befehle fragen nie nach. Diese Liste ist nicht konfigurierbar.

## In welcher Reihenfolge gelten deny, ask und allow?

| Schritt | Liste | Wirkung |
| --- | --- | --- |
| 1 | `deny` | passt eine Regel, wird blockiert |
| 2 | `ask` | passt eine Regel, wird nachgefragt, auch wenn ein `allow` passt |
| 3 | `allow` | passt eine Regel, läuft die Aktion ohne Rückfrage |
| 4 | keine | der Permission Mode entscheidet |

Wie genau eine Regel ist, spielt keine Rolle. Ein `deny` aus irgendeiner Ebene lässt sich nicht aufheben, auch nicht mit `--allowedTools`. Steht ein Werkzeug pauschal in `deny`, etwa `Bash`, `Bash(*)` oder `mcp__*`, entfernt Claude Code es ganz aus dem Kontext. Die Listen aller Ebenen werden zusammengeführt, siehe [settings.json](./claude-code-settings-json.md).

## Wie schreibe ich Bash-Regeln richtig?

| Regel | Passt auf | Passt nicht auf |
| --- | --- | --- |
| `Bash(npm run build)` | genau `npm run build` | `npm run build --prod` |
| `Bash(npm run test *)` | `npm run test`, `npm run test -- --watch` | `npm run lint` |
| `Bash(ls *)` | `ls -la` | `lsof` |
| `Bash(ls*)` | `ls -la` und `lsof` | |
| `Bash(git diff:*)` | wie `Bash(git diff *)` | |
| `Bash(git:* push)` | nichts Sinnvolles, `:` wird wörtlich gelesen | `git push` |

Die Regeln dazu:

- Der Stern passt auf beliebigen Text, auch auf Leerzeichen.
- Ein abschließendes ` *` passt auch auf den Befehl ohne Argumente.
- Das Leerzeichen vor dem Stern begrenzt das Wort. `Bash(ls *)` passt nicht auf `lsof`.
- `:*` ist nur am Ende gleichbedeutend mit ` *`.
- Ein Stern vor dem Unterbefehl ist riskant: `Bash(git * main)` passt auch auf `git push origin main`. Claude Code warnt beim Start bei solchen `allow`-Regeln.
- Bei verketteten Befehlen mit `&&`, `||`, `;` oder `|` muss ein `allow` jeden Teil abdecken. `deny` und `ask` greifen, wenn irgendein Teil passt.
- Vor dem Abgleich entfernt Claude Code Hüllbefehle wie `timeout`, `time`, `nice`, `nohup`, `stdbuf` und ein bloßes `xargs`. `Bash(npm test *)` passt also auch auf `timeout 30 npm test`. Nicht entfernt werden `npx`, `docker exec`, `devbox run`, `direnv exec` und `mise exec`.
- Befehle hinter `watch`, `setsid`, `ionice`, `flock` sowie `find` mit `-exec` oder `-delete` lassen sich nicht über ein Präfix freigeben.

Bash-Regeln vergleichen Text. `/usr/bin/curl`, `sh -c "..."` oder `git -C . push` umgehen eine Regel, die nur `curl` oder `git push` nennt. Wer Befehle wirklich sperren will, nutzt zusätzlich [Sandbox](./claude-code-sandbox.md) oder einen [PreToolUse-Hook](./claude-code-hooks.md).

## Wie funktionieren Pfadregeln für Read und Edit?

Read- und Edit-Regeln folgen der gitignore-Syntax. Der Anfang des Pfads entscheidet, worauf er sich bezieht:

| Muster | Bedeutung | Beispiel |
| --- | --- | --- |
| `//pfad` | absoluter Pfad ab Wurzel | `Read(//Users/alice/secrets/**)` |
| `~/pfad` | ab Home-Ordner | `Read(~/.aws/**)` |
| `/pfad` | relativ zur Settings-Quelle (Projekt: Arbeitsordner, Nutzer-Settings: `~/.claude/`) | `Edit(/src/**/*.ts)` |
| `pfad` oder `./pfad` | relativ zum aktuellen Ordner | `Read(.env)` |

Achtung: `/Users/alice/file` ist kein absoluter Pfad, sondern relativ zur Settings-Quelle. Für absolute Pfade braucht es zwei Schrägstriche.

Weitere Regeln:

- Ein Dateiname ohne Pfad passt in jeder Tiefe: `Read(.env)` trifft auch `config/.env`.
- `src/**` passt als `allow` nur auf `src` im aktuellen Ordner, als `deny` in jeder Tiefe.
- Ein `deny` für `Read` blockiert auch `Edit` (ab v2.1.208) und `Write` (ab v2.1.228) auf denselben Pfad, aber nicht `NotebookEdit`.
- Pfadregeln für `Write`, `NotebookEdit`, `Glob` und `MultiEdit` werden ignoriert, mit einer Warnung beim Start (ab v2.1.210). Nimm `Edit(...)`.
- Ein Read-deny wirkt auf die eingebauten Werkzeuge, auf `@`-Erwähnungen und auf Bash-Befehle wie `cat`, `head`, `tail`, `sed` und Umleitungen, aber nicht auf `grep -r` oder eigene Skripte.
- Eine `.claudeignore`-Datei hat keine Wirkung.

## WebFetch, MCP und Subagents

| Regel | Wirkung |
| --- | --- |
| `WebFetch(domain:example.com)` | genau diese Domain |
| `WebFetch(domain:*.example.com)` | Subdomains, nicht `example.com` selbst |
| `mcp__github` oder `mcp__github__*` | alle Werkzeuge des MCP-Servers `github` |
| `mcp__github__create_issue` | genau ein Werkzeug |
| `Agent(Explore)` | ein bestimmter Subagent |
| `Agent(model:opus)` in `deny` oder `ask` | Subagents mit diesem Modell |
| `Bash(run_in_background:true)` in `deny` oder `ask` | Hintergrund-Befehle |

`*` und `mcp__*` in `allow` überspringt Claude Code. Ein Stern bei MCP wirkt in `allow` nur nach einem festen `mcp__<server>__`.

## Welche Permission Modes gibt es?

| Modus | Was ohne Rückfrage läuft | Gedacht für |
| --- | --- | --- |
| `default` (Manual) | nur Lesen | sensible Arbeit, Einstieg |
| `acceptEdits` | Lesen, Datei-Edits und `mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed` im Arbeitsordner | Code, den du danach prüfst |
| `plan` | nur Lesen und Erkunden | Planen vor dem Ändern, siehe [Plan Mode](./claude-code-plan-mode.md) |
| `auto` | alles, ein Klassifikator prüft im Hintergrund | lange Aufgaben mit weniger Rückfragen |
| `dontAsk` | nur vorab erlaubte Werkzeuge, alles andere wird abgelehnt | CI und gesperrte Umgebungen |
| `bypassPermissions` | alles ohne Prüfung | isolierte Container, siehe [dangerously-skip-permissions](./claude-code-dangerously-skip-permissions.md) |

Den Modus wechselst du mit `Shift+Tab`; die Statusleiste zeigt den aktiven Modus, etwa `⏵⏵ accept edits on`. Ab v2.1.283 ist Auto Mode im Terminal und in VS Code der eingebaute Start, sofern dein Modell ihn unterstützt. Vom Auto Mode führt der erste Druck auf `Shift+Tab` zu Manual, dann zu acceptEdits, dann zu plan. `dontAsk` ist nicht im Zyklus, sondern nur per `--permission-mode dontAsk` oder `defaultMode` erreichbar.

Den Start-Modus legst du so fest:

- für eine Sitzung mit `claude --permission-mode plan`
- dauerhaft mit `permissions.defaultMode` in der settings.json
- `auto` und `bypassPermissions` als `defaultMode` wirken nicht aus Projekt- oder lokalen Settings, nur aus deinen Nutzer-Settings, `--settings` oder Managed Settings

In jedem Modus gilt: `ask`-Regeln werden nie automatisch freigegeben, `deny`-Regeln gelten auch in `bypassPermissions`, und `rm` auf kritische Pfade wie Home oder Arbeitsordner fragt immer nach. Schreibzugriffe auf geschützte Pfade wie `.git`, `.claude`, `.vscode`, `.mcp.json` oder `.bashrc` gibt keine `allow`-Regel frei: In Manual und acceptEdits fragt Claude Code nach, im Auto Mode entscheidet der Klassifikator, in `dontAsk` werden sie abgelehnt, und nur `bypassPermissions` lässt sie ohne Prüfung zu.

Auto Mode und Bypass lassen sich organisationsweit sperren: `permissions.disableAutoMode: "disable"` und `permissions.disableBypassPermissionsMode: "disable"`, am besten in den Managed Settings.

## Beispiele

### Beispiel 1: Node-Projekt mit Tests und Lint

Routinebefehle ohne Rückfrage, Veröffentlichen mit Rückfrage.

```json
{
  "permissions": {
    "allow": ["Bash(npm run test *)", "Bash(npm run lint *)", "Bash(npm run build *)", "Bash(git status *)", "Bash(git diff *)"],
    "ask": ["Bash(git push *)", "Bash(npm publish *)"],
    "deny": ["Read(.env)", "Read(.env.*)", "Edit(.env)", "Edit(.env.*)"]
  }
}
```

### Beispiel 2: Python-Projekt

```json
{
  "permissions": {
    "allow": ["Bash(pytest *)", "Bash(python -m pytest *)", "Bash(ruff check *)", "Bash(ruff format *)"],
    "deny": ["Read(**/*.pem)", "Read(**/*.key)", "Read(**/id_rsa*)", "Read(**/id_ed25519*)", "Read(secrets/**)"]
  }
}
```

### Beispiel 3: Cloud-Zugangsdaten im Home-Ordner sperren

Gehört in `~/.claude/settings.json`, damit es in jedem Projekt gilt.

```json
{
  "permissions": {
    "deny": ["Read(~/.aws/**)", "Read(~/.ssh/**)", "Read(~/.kube/**)", "Read(~/.config/gcloud/**)", "Read(~/.azure/**)", "Read(~/.netrc)", "Read(~/.docker/config.json)"]
  }
}
```

### Beispiel 4: Infrastruktur nur mit Rückfrage

```json
{
  "permissions": {
    "allow": ["Bash(terraform plan *)", "Bash(terraform validate *)", "Bash(kubectl get *)"],
    "ask": ["Bash(terraform apply *)", "Bash(kubectl apply *)", "Bash(kubectl delete *)", "Bash(helm upgrade *)"],
    "deny": ["Read(**/*.tfstate)", "Read(**/*.tfstate.*)", "Bash(terraform destroy *)"]
  }
}
```

### Beispiel 5: Web-Zugriff auf bestimmte Domains begrenzen

```json
{
  "permissions": {
    "allow": ["WebFetch(domain:docs.python.org)", "WebFetch(domain:*.example.com)", "mcp__github__get_issue"],
    "ask": ["mcp__github__create_issue"],
    "deny": ["WebSearch"]
  }
}
```

### Beispiel 6: Automatischer Lauf in der CI

`dontAsk` lehnt alles ab, was nicht ausdrücklich erlaubt ist.

```bash
claude -p "run the test suite" --permission-mode dontAsk --allowedTools "Bash(npm test)" "Read"
```

### Beispiel 7: Team startet im Plan Mode

```json
{
  "permissions": {
    "defaultMode": "plan"
  }
}
```

## Schritt für Schritt: Regeln für ein Team aufsetzen

1. `/permissions` öffnen und ansehen, welche Regeln schon gelten und woher sie kommen.
2. Zuerst `deny` schreiben: `.env`, Schlüsseldateien, Zugangsdaten, `sudo`, `curl ... | sh`.
3. Dann `ask` für alles mit Wirkung nach außen: Push, Publish, Deploy.
4. Zuletzt `allow` für die Befehle, die täglich laufen, jeweils mit festem Unterbefehl.
5. Prüfen: `claude-team audit .` meldet zu breite Regeln, Sterne vor dem Unterbefehl und wirkungslose Regeln.
6. Eine Woche nutzen und die Rückfragen beobachten. Was dauernd kommt und harmlos ist, wandert nach `allow`.
7. Regeln, die eine Person allein braucht, in `.claude/settings.local.json` lassen.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| `allow: ["Bash"]` oder `Bash(python *)` | Claude darf praktisch alles ([CC015](../regeln.md#cc015)) | feste Unterbefehle freigeben |
| `Bash(git * main)` | passt auch auf `git push origin main` ([CC016](../regeln.md#cc016)) | Stern hinter den Unterbefehl |
| `Write(src/**)` | Regel ohne Wirkung, Warnung beim Start ([CC017](../regeln.md#cc017)) | `Edit(src/**)` |
| `Bash(git:* push)` | passt nie | `Bash(git push *)` |
| `Read(/Users/alice/.env)` | greift nicht | `Read(//Users/alice/.env)` |
| Kein deny für `.env` | Zugangsdaten landen im Kontext ([CC013](../regeln.md#cc013)) | `Read(.env)` und `Read(.env.*)` sperren |
| Ausnahme per `allow` aus einem `deny` | bleibt blockiert | `deny` enger fassen |

## Häufige Fragen

### Wie aktiviere ich Auto Accept in Claude Code?

Mit dem Modus `acceptEdits`: `Shift+Tab` drücken, bis die Statusleiste `⏵⏵ accept edits on` zeigt, oder `claude --permission-mode acceptEdits` starten. Claude bearbeitet dann Dateien im Arbeitsordner ohne Rückfrage, andere Bash-Befehle fragen weiter nach.

### Was ist der Auto Mode in Claude Code?

Im Auto Mode läuft alles ohne Rückfrage, und ein Klassifikator prüft jede Aktion im Hintergrund. Ab v2.1.283 ist er im Terminal und in VS Code der eingebaute Start-Modus, sofern dein Modell ihn unterstützt. Organisationen schalten ihn mit `permissions.disableAutoMode: "disable"` ab.

### Warum fragt Claude trotz allow-Regel nach?

Meist greift eine `ask`-Regel aus einer anderen Ebene, denn ask schlägt allow. Weitere Gründe: Ein Teil eines verketteten Befehls ist nicht abgedeckt, die Aktion schreibt in einen geschützten Pfad, oder du hast den Vertrauensdialog für den Ordner noch nicht bestätigt. `/permissions` zeigt alle Regeln mit Herkunft.

### Schützt eine deny-Regel zuverlässig?

Für Read und Edit mit den eingebauten Werkzeugen ja. Bash-Regeln vergleichen dagegen Text und lassen sich mit anderen Schreibweisen umgehen, und ein Read-deny erfasst kein `grep -r`. Für harte Grenzen kommen Sandbox und Hooks dazu.

### Wo speichert "Yes, and don't ask again" die Regel?

In `.claude/settings.local.json` am Root des Git-Repos, auch bei Worktrees im Haupt-Checkout. Die Regel gilt dann für alle künftigen Sitzungen im Repo, eine `ask`-Regel aus der Projektdatei schlägt sie aber weiterhin.

## Weiterlesen

- [Claude Code settings.json](./claude-code-settings-json.md)
- [Claude Code dangerously-skip-permissions](./claude-code-dangerously-skip-permissions.md)
- [Claude Code Plan Mode](./claude-code-plan-mode.md)
- [Claude Code Sandbox](./claude-code-sandbox.md)
- [Claude Code Sicherheit](./claude-code-sicherheit.md)
- Vorlage: [.claude/settings.json](../../src/claude_team/vorlage/.claude/settings.json), Prüfregeln [CC012 bis CC017](../regeln.md#cc012)
- Offizielle Doku: [Permissions](https://code.claude.com/docs/en/permissions), [Permission modes](https://code.claude.com/docs/en/permission-modes)
