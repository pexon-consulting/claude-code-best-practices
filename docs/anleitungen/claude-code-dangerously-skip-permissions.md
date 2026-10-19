# Claude Code dangerously-skip-permissions: YOLO-Modus sicher in Sandbox und Container

`claude --dangerously-skip-permissions` startet Claude Code im Modus `bypassPermissions`: Claude führt jeden Werkzeugaufruf sofort aus, ohne Rückfrage und ohne die meisten Sicherheitsprüfungen, auch Schreibzugriffe auf `.git` oder `.claude`. Vertretbar ist das laut Anthropic nur in isolierten Umgebungen wie Containern, VMs oder Dev Containern, in denen Claude Code keinen Schaden anrichten kann, also ohne Zugangsdaten vom Host, als normaler Nutzer statt root und mit begrenztem Netz. Für weniger Rückfragen auf dem eigenen Rechner ist Auto Mode die vorgesehene Alternative.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- `--dangerously-skip-permissions` ist gleichbedeutend mit `--permission-mode bypassPermissions`, umgangssprachlich "YOLO-Modus".
- Der Modus schützt nicht gegen Prompt Injection: Eine präparierte Datei oder Webseite kann Claude zu beliebigen Befehlen bringen.
- `deny`-Regeln gelten auch in diesem Modus, `allow`-Regeln sind wirkungslos, `ask`-Regeln fragen weiter nach.
- Als root oder mit `sudo` verweigert Claude Code den Start auf Linux und macOS, außer in einer erkannten Sandbox.
- Organisationen sperren den Modus mit `permissions.disableBypassPermissionsMode: "disable"` in den Managed Settings.
- Auto Mode und acceptEdits reduzieren Rückfragen, ohne die Prüfungen ganz abzuschalten.

## Was macht --dangerously-skip-permissions genau?

| Ohne Flag (Manual) | Mit Flag (bypassPermissions) |
| --- | --- |
| Bash-Befehle fragen nach, außer Nur-Lese-Befehlen und `allow`-Regeln | alle Bash-Befehle laufen sofort |
| Datei-Edits fragen nach | alle Edits laufen sofort |
| Schreibzugriffe auf geschützte Pfade fragen immer nach | laufen ohne Rückfrage |
| `allow`-Regeln geben Befehle frei | wirkungslos, weil ohnehin alles läuft |
| `deny`-Regeln blockieren | blockieren weiterhin |
| `ask`-Regeln fragen nach | fragen weiterhin nach |

Auch in diesem Modus fragt Claude Code bei einigen Aktionen nach: bei ausdrücklichen `ask`-Regeln, bei `rm` und `rmdir` auf kritische Pfade wie Wurzel, Home oder Arbeitsordner, bei `AskUserQuestion` und bei MCP-Werkzeugen, die eine Interaktion verlangen. In `claude -p` werden diese wenigen Aufrufe abgelehnt statt nachgefragt.

Weitere Eigenschaften laut Doku:

- Beim ersten interaktiven Start zeigt Claude Code einen Warndialog. Wer zustimmt, bekommt `skipDangerousModePermissionPrompt: true` in `~/.claude/settings.json`; wer ablehnt, beendet Claude Code. In `claude -p` erscheint kein Dialog.
- In den Modus kommst du nur, wenn er beim Start aktiviert war. Mitten in einer normalen Sitzung lässt er sich nicht einschalten.
- `--allow-dangerously-skip-permissions` nimmt den Modus nur in den `Shift+Tab`-Zyklus auf, ohne ihn zu aktivieren.
- Mit `--restricted` verweigert Claude Code den Modus (ab v2.1.248).
- In Cloud-Sitzungen wird `defaultMode: "bypassPermissions"` aus Settings-Dateien still ignoriert.
- In interaktiven Terminal-Sitzungen mit verfügbarem Bypass setzt Claude Code die Sperren des Plan Mode nicht durch. Claude soll dann zwar nur planen, ein versuchter Edit läuft aber ohne Rückfrage.

## Welche Risiken hat der YOLO-Modus?

| Risiko | Beispiel | Gegenmaßnahme |
| --- | --- | --- |
| Prompt Injection | eine README in einer Abhängigkeit fordert Claude auf, Zugangsdaten zu senden | kein Netz außer Allowlist, keine Secrets im Container |
| Datenabfluss | Claude liest `~/.aws/credentials` oder `.env` und schickt sie per `curl` weg | Host-Secrets nicht mounten, kurzlebige Tokens |
| Zerstörung | `rm -rf` auf einen gemounteten Ordner, Force-Push | nur Repo-Kopie mounten, Branch-Schutz im Git-Server |
| Manipulation der Konfiguration | Claude ändert `.claude/settings.json`, Hooks oder `.git/hooks` | Wegwerf-Container, Änderungen vor dem Merge prüfen |
| Zugangsdaten von Claude Code | Anmeldedaten unter `~/.claude` im Container | eigenen Account oder API-Schlüssel mit Limit für den Container |

Die Doku zum Dev Container sagt ausdrücklich: Mit `--dangerously-skip-permissions` verhindert ein Dev Container nicht, dass ein bösartiges Projekt alles abzieht, was im Container erreichbar ist, auch die Claude-Code-Anmeldedaten in `~/.claude`.

## Wann ist der Modus vertretbar?

Alle Bedingungen sollten erfüllt sein:

1. **Isolation:** Container, VM oder Dev Container, kein direkter Lauf auf dem Arbeitsrechner.
2. **Kein root:** Claude Code läuft als normaler Nutzer. Als root verweigert das Flag ohnehin den Start mit der Meldung `--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons`.
3. **Keine Host-Secrets:** kein gemountetes `~/.ssh`, keine Cloud-Credential-Dateien, keine produktiven `.env`-Dateien. Die Doku empfiehlt repo-bezogene oder kurzlebige Tokens.
4. **Begrenztes Netz:** ausgehender Verkehr nur zu einer Allowlist, etwa mit dem Firewall-Skript `init-firewall.sh` aus dem Referenz-Container von Anthropic.
5. **Wegwerfbar:** Der Container lässt sich jederzeit neu bauen, Ergebnisse gehen als Branch oder Pull Request raus und werden geprüft.

Typische Fälle: ein unbeaufsichtigter Lauf in einer CI-Pipeline, eine lange Refactoring-Aufgabe in einem Codespace, ein Experiment in einer frischen VM.

Nicht vertretbar: der eigene Laptop mit Zugriff auf Mails, Passwortmanager und Kundendaten, ein Server mit Produktionszugang, ein Container mit gemountetem Home-Ordner.

## Welche Alternativen gibt es?

| Modus | Rückfragen | Prüfung | Start |
| --- | --- | --- | --- |
| Auto Mode | kaum | ein Klassifikator prüft jede Aktion vor der Ausführung | `claude --permission-mode auto` oder `Shift+Tab` |
| acceptEdits | bei Bash-Befehlen außerhalb der Edit-Befehle | Edits und `mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed` im Arbeitsordner laufen sofort | `claude --permission-mode acceptEdits` |
| Sandbox mit Auto-Allow | wenige | Bash läuft isoliert mit Dateisystem- und Netzgrenzen | `"sandbox": { "enabled": true }` |
| gezielte `allow`-Regeln | nur für Unbekanntes | Regeln pro Befehl | siehe [Permissions](./claude-code-permissions.md) |
| dontAsk | keine, Unbekanntes wird abgelehnt | nur erlaubte Werkzeuge | `--permission-mode dontAsk` |

Auto Mode ist ab v2.1.283 im Terminal und in VS Code der eingebaute Start-Modus, wenn das Modell ihn unterstützt. Wer das Flag nur nutzt, weil die Rückfragen nerven, ist dort meist besser aufgehoben.

## Beispiele für `--dangerously-skip-permissions`

### Beispiel 1: Dev Container mit Claude Code als normaler Nutzer

Grundgerüst für `.devcontainer/devcontainer.json`. Das Feature installiert Claude Code; `remoteUser` sorgt dafür, dass es nicht als root läuft. Die Capabilities braucht nur, wer eine Firewall im Container betreibt.

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/anthropics/devcontainer-features/claude-code:1.0": {}
  },
  "remoteUser": "vscode",
  "runArgs": ["--cap-add=NET_ADMIN", "--cap-add=NET_RAW"]
}
```

Ein vollständiges Beispiel mit Firewall-Skript liegt im Ordner [`.devcontainer` von anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/.devcontainer). Es ist als Beispiel gedacht, nicht als gepflegtes Basis-Image.

### Beispiel 2: Unbeaufsichtigter Lauf im Container

So steht es in der Doku-Tabelle für vollautomatische Läufe; Voraussetzung sind Container, VM oder Sandbox-Runtime und ein Nutzer ohne root-Rechte.

```bash
claude -p "Run the test suite and fix failing tests in src/" --dangerously-skip-permissions
```

### Beispiel 3: Bypass organisationsweit sperren

In die Managed Settings (`managed-settings.json` oder MDM). Dann lehnt Claude Code das Flag ab und ignoriert auch `permissionMode: bypassPermissions` im Frontmatter von Subagents.

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  }
}
```

### Beispiel 4: deny-Regeln als letzte Sperre im Container

`deny` wirkt auch im Bypass. Für eine Container-Konfiguration, die trotz YOLO-Modus bestimmte Dinge nie zulässt:

```json
{
  "permissions": {
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(~/.aws/**)",
      "Bash(git push --force *)",
      "Bash(git push -f *)",
      "Bash(curl * | sh)"
    ]
  }
}
```

Bash-deny-Regeln vergleichen Text und lassen sich umgehen. Sie ersetzen keine Netz-Allowlist.

### Beispiel 5: Bypass nur bereithalten, im Plan Mode starten

Claude plant zuerst; bei der Freigabe des Plans bietet Claude Code dann "Yes, and switch to BYPASS PERMISSIONS (no further prompts) for this session" an.

```bash
claude --permission-mode plan --allow-dangerously-skip-permissions
```

### Beispiel 6: Weniger Rückfragen ohne Bypass

Auto Mode für eine Sitzung, oder acceptEdits, wenn nur Edits ohne Rückfrage laufen sollen.

```bash
claude --permission-mode auto
claude --permission-mode acceptEdits
```

### Beispiel 7: Sandbox statt Bypass

Bash-Befehle laufen isoliert und werden in der Sandbox ohne Rückfrage ausgeführt (`autoAllowBashIfSandboxed` ist Standard). Netz nur zu den freigegebenen Domains.

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "network": { "allowedDomains": ["registry.npmjs.org", "pypi.org"] }
  }
}
```

## Schritt für Schritt: YOLO-Modus im Dev Container einrichten

1. `.devcontainer/devcontainer.json` wie in Beispiel 1 anlegen und den Container neu bauen ("Dev Containers: Rebuild Container").
2. Prüfen, dass im Container nicht root aktiv ist: `whoami` darf nicht `root` ausgeben.
3. Keine Host-Ordner mit Zugangsdaten mounten. Für Cloud-Anbieter Zugangsdaten als Umgebungsvariablen oder Workload Identity übergeben.
4. Netz begrenzen, zum Beispiel mit dem Firewall-Skript aus dem Referenz-Container.
5. Claude Code im Container anmelden, möglichst mit einem eigenen Account oder Schlüssel mit Ausgabenlimit.
6. Erst interaktiv mit `claude --dangerously-skip-permissions` testen und den Warndialog bestätigen.
7. Ergebnisse als Branch pushen und per Pull Request prüfen. Branch-Schutz auf dem Git-Server verhindert Force-Pushes auf `main`.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Flag auf dem eigenen Laptop | Claude hat Zugriff auf alles, was du erreichst | Auto Mode oder Container |
| Start als root im Container | Meldung `cannot be used with root/sudo privileges` | `remoteUser` auf einen normalen Nutzer setzen |
| `~/.ssh` oder `~/.aws` gemountet | Zugangsdaten im Container lesbar | nicht mounten, kurzlebige Tokens |
| Mitten in der Sitzung Bypass gewünscht | Modus erscheint nicht in `Shift+Tab` | mit `--allow-dangerously-skip-permissions` starten |
| `defaultMode: "bypassPermissions"` in `.claude/settings.json` | Sitzung startet in Manual | in Nutzer-Settings oder per Flag ([CC012](../regeln.md#cc012) meldet das als Fehler) |
| Flag wird abgelehnt | Organisation hat Bypass gesperrt | Auto Mode nutzen oder Admin fragen |

## Häufige Fragen

### Was ist der YOLO-Modus in Claude Code?

So nennen viele den Start mit `--dangerously-skip-permissions`. Claude führt dann alle Werkzeugaufrufe ohne Rückfrage aus; nur `deny`-Regeln, `ask`-Regeln und Löschbefehle auf kritische Pfade halten ihn noch auf.

### Ist --dangerously-skip-permissions sicher?

Auf dem eigenen Rechner nicht. Der Modus schützt nicht gegen Prompt Injection oder ungewollte Aktionen. Vertretbar ist er in einem isolierten Container oder einer VM ohne Host-Secrets, als normaler Nutzer und mit begrenztem Netz.

### Wie sperre ich den Modus für mein Team?

Mit `"permissions": { "disableBypassPermissionsMode": "disable" }` in den Managed Settings. Der Key wirkt aus jeder Ebene, nur in den Managed Settings kann ihn aber niemand überschreiben.

### Was ist der Unterschied zu Auto Mode?

Im Auto Mode prüft ein Klassifikator jede Aktion vor der Ausführung und blockt riskante. Im Bypass gibt es diese Prüfung nicht. Beide sparen Rückfragen, aber nur Auto Mode behält eine Sicherheitsprüfung.

### Warum startet Claude Code mit dem Flag nicht?

Meist läuft der Prozess als root oder mit `sudo`; dann verweigert Claude Code den Start auf Linux und macOS. Andere Gründe sind eine Organisationssperre per `disableBypassPermissionsMode` oder ein Start mit `--restricted`.

## Weiterlesen

- [Claude Code Permissions: allow, ask und deny](./claude-code-permissions.md)
- [Claude Code Sandbox](./claude-code-sandbox.md)
- [Claude Code Sicherheit](./claude-code-sicherheit.md)
- [Claude Code Plan Mode](./claude-code-plan-mode.md)
- [Claude Code Enterprise](./claude-code-enterprise.md)
- Vorlagen: [managed-settings.json](../../vorlagen/managed-settings.json), Prüfregel [CC012](../regeln.md#cc012)
- Offizielle Doku: [Permission modes](https://code.claude.com/docs/en/permission-modes), [Development containers](https://code.claude.com/docs/en/devcontainer)
