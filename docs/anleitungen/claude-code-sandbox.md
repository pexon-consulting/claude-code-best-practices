# Claude Code Sandbox: isoliert arbeiten mit Devcontainer und Docker

Claude Code startest du in einer Sandbox auf zwei Arten: Die eingebaute Sandbox schaltest du in der Sitzung mit `/sandbox` oder mit `"sandbox": {"enabled": true}` in der settings.json ein, dann laufen Shell-Befehle unter Seatbelt (macOS) oder bubblewrap (Linux, WSL 2). Für eine komplett abgeschottete Umgebung nimmst du einen Devcontainer mit dem Feature `ghcr.io/anthropics/devcontainer-features/claude-code:1.0` oder einen eigenen Docker-Container. Die eingebaute Sandbox kapselt nur Bash-, PowerShell- und Monitor-Befehle, ein Container dagegen den ganzen Prozess samt Hooks und MCP-Servern.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Die eingebaute Sandbox ist standardmäßig aus. `/sandbox` öffnet das Panel, auf Linux und WSL 2 brauchst du vorher `bubblewrap` und `socat`.
- Sie isoliert Bash-, PowerShell- und Monitor-Befehle samt Kindprozessen. Read, Edit, Write, WebFetch, Hooks und lokale MCP-Server laufen außerhalb.
- Schreiben ist auf das Arbeitsverzeichnis begrenzt, Netzwerk läuft über einen Proxy mit anfangs leerer Domain-Liste. Lesen darf sie standardmäßig fast alles, auch `~/.ssh`.
- Ein Devcontainer isoliert die ganze Entwicklungsumgebung und ist der empfohlene Ort für `--dangerously-skip-permissions`.
- Unter nativem Windows gibt es keine eingebaute Sandbox, dort hilft ein Container, eine VM oder WSL 2.

## Welche Isolierung passt?

Die Doku zu [Sandbox environments](https://code.claude.com/docs/en/sandbox-environments) vergleicht sechs Ansätze:

| Ansatz | Was isoliert wird | Docker nötig | Aufwand |
| --- | --- | --- | --- |
| Eingebaute Bash-Sandbox | Bash-, PowerShell- und Monitor-Befehle mit Kindprozessen | nein | gering auf macOS, niedrig auf Linux und WSL 2 |
| Sandbox Runtime | der ganze Claude-Code-Prozess inklusive Datei-Tools, MCP-Servern und Hooks | nein | niedrig |
| Devcontainer | ganze Entwicklungsumgebung | ja | mittel |
| Eigener Container | ganze Entwicklungsumgebung | ja | mittel bis hoch |
| Virtuelle Maschine | ganzes Betriebssystem | nein | hoch |
| Cloud-Sitzungen | ganzes Betriebssystem, bei Anthropic gehostet | nein | keiner, braucht ein Claude-Abo |

Faustregeln aus derselben Seite: Für weniger Rückfragen im Alltag reicht die Bash-Sandbox. Für unbeaufsichtigte Läufe mit `--dangerously-skip-permissions` oder Auto Mode nimmst du einen Devcontainer, einen anderen Container, eine VM oder die Sandbox Runtime. Ein fremdes, nicht vertrauenswürdiges Repository gehört in eine eigene VM oder eine Cloud-Sitzung. Für ein Team kopierst du einen vorkonfigurierten Devcontainer ins Repo.

## Was die eingebaute Sandbox abdeckt

| Bereich | Standard |
| --- | --- |
| Schreiben | Arbeitsverzeichnis, temporäres Verzeichnis des Nutzers, mit `/add-dir` hinzugefügte Ordner |
| Lesen | fast der ganze Rechner, auch `~/.ssh` |
| Netzwerk | nur über den Sandbox-Proxy, `allowedDomains` startet leer, neue Domains fragt Claude Code an |
| Umgebungsvariablen | werden vererbt |
| Außerhalb der Sandbox | Read, Edit, Write, WebFetch, WebSearch (die folgen den Berechtigungsregeln), Hooks, lokale MCP-Server, Plugin-Monitore, LSP-Server, Statusline, `apiKeyHelper`, `!`-Befehle, `excludedCommands` |

Es gibt zwei Modi: Auto-allow führt Befehle in der Sandbox ohne Rückfrage aus, Regular permissions fragt weiter wie gewohnt. Scheitert ein Befehl in der Sandbox, kann Claude ihn mit `dangerouslyDisableSandbox` außerhalb wiederholen und fragt dich dann. Mit `allowUnsandboxedCommands: false` gibt es diesen Ausweg nicht mehr.

Subagents nutzen dieselbe Sandbox-Konfiguration wie die Hauptsitzung.

## Beispiele

### Beispiel 1: Sandbox einschalten und prüfen

Auf Linux und WSL 2 zuerst die Pakete:

```bash
sudo apt-get install bubblewrap socat
```

Dann in der Sitzung `/sandbox` aufrufen, im Tab Mode einen Modus wählen und mit zwei Testbefehlen prüfen. Lass Claude diese Befehle ausführen:

```bash
touch ~/sandbox-probe
curl --noproxy '*' https://example.com
```

Der erste Befehl muss mit `Operation not permitted` (macOS) oder `Read-only file system` (Linux, WSL 2) scheitern, der zweite mit `Could not resolve host`. Fragt Claude, ob es den Befehl außerhalb der Sandbox wiederholen soll, lehnst du ab. Den im Panel gewählten Modus speichert Claude Code in `.claude/settings.local.json`, also nur für dich und dieses Projekt.

### Beispiel 2: Sandbox für eine einzelne Sitzung

Zum Ausprobieren, ohne Dateien zu ändern.

```bash
claude --settings '{"sandbox": {"enabled": true, "allowUnsandboxedCommands": false}}'
```

### Beispiel 3: Netzwerk und Schreibrechte für das Projekt freigeben

Für ein Node-Projekt, das von GitHub und npm lädt und in `/tmp/build` baut. In `.claude/settings.json`:

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "allowWrite": ["/tmp/build"],
      "denyRead": ["~/"],
      "allowRead": ["."]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"]
    }
  }
}
```

`denyRead` mit `~/` und `allowRead` mit `.` sperrt das Home-Verzeichnis und lässt nur das Projekt lesbar. Ein `.` in `.claude/settings.json` meint die Projektwurzel; in `~/.claude/settings.json` würde es `~/.claude` meinen. Mehrere Settings-Ebenen werden bei diesen Listen zusammengeführt, nicht ersetzt.

### Beispiel 4: Zugangsdaten vor Befehlen in der Sandbox verbergen

Damit ein Befehl in der Sandbox weder AWS-Schlüssel noch das GitHub-Token lesen kann:

```json
{
  "sandbox": {
    "enabled": true,
    "credentials": {
      "files": [
        { "path": "~/.aws/credentials", "mode": "deny" },
        { "path": "~/.ssh", "mode": "deny" }
      ],
      "envVars": [
        { "name": "GITHUB_TOKEN", "mode": "deny" },
        { "name": "NPM_TOKEN", "mode": "deny" }
      ]
    }
  }
}
```

Zusätzlich gibt es den Modus `mask`, bei dem der Proxy das echte Token nur an freigegebene Hosts weiterreicht. `mask` wirkt aber nur aus Nutzer-, Managed- oder CLI-Settings, nicht aus dem Repo.

### Beispiel 5: Docker-Befehle aus der Sandbox nehmen

`docker` funktioniert nicht in der Sandbox. Gezielte Ausnahmen:

```json
{
  "sandbox": {
    "enabled": true,
    "excludedCommands": ["docker compose *"]
  }
}
```

Das Muster muss mit ` *` enden, und jeder Befehl in einer Kette muss passen: `npm ci && docker compose build` bleibt in der Sandbox. Ein Skript, das intern `docker` aufruft, passt nicht. Ausgenommene Befehle laufen mit deinen vollen Rechten.

### Beispiel 6: Claude Code im Devcontainer

Die kleinste Variante von `.devcontainer/devcontainer.json`:

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/anthropics/devcontainer-features/claude-code:1.0": {}
  }
}
```

Danach in VS Code "Dev Containers: Rebuild Container". Das Feature installiert die CLI und die VS-Code-Extension. `:1.0` fixiert nur das Installationsskript, nicht die Version von Claude Code; das Feature installiert immer das neueste Release. Stoppt der Build mit `Failed to install Node.js and npm`, ergänzt du vor dem Claude-Feature `"ghcr.io/devcontainers/features/node:1": {}`.

### Beispiel 7: Devcontainer mit Login, der einen Rebuild übersteht

Ohne Volume musst du dich nach jedem Rebuild neu anmelden. Diese Variante speichert `~/.claude` je Projekt und schaltet Telemetrie und Auto-Update ab:

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/anthropics/devcontainer-features/claude-code:1.0": {}
  },
  "mounts": [
    "source=claude-code-config-${devcontainerId},target=/home/node/.claude,type=volume"
  ],
  "containerEnv": {
    "CLAUDE_CONFIG_DIR": "/home/node/.claude",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

Ersetze `/home/node` durch das Home-Verzeichnis des `remoteUser` deines Containers. `${devcontainerId}` sorgt für ein eigenes Volume je Projekt. `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` schaltet auch die Feature-Flag-Abfrage ab, Remote Control geht im Container dann nicht. In GitHub Codespaces legst du `CLAUDE_CODE_OAUTH_TOKEN` aus `claude setup-token` als Codespaces-Secret ab.

### Beispiel 8: Eigenes Docker-Image mit fester Version und Richtlinie

Für reproduzierbare Builds installierst du eine feste Version per npm in deinem Dockerfile, statt das Feature zu nutzen:

```dockerfile
RUN npm install -g @anthropic-ai/claude-code@2.1.294
RUN mkdir -p /etc/claude-code
COPY managed-settings.json /etc/claude-code/managed-settings.json
```

Das Basisimage muss Node.js 22 oder neuer mitbringen, sonst installierst du es vorher. Die `managed-settings.json` daneben:

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable",
    "deny": ["Read(./.env)", "Read(./.env.*)"]
  },
  "env": {
    "DISABLE_AUTOUPDATER": "1",
    "DISABLE_TELEMETRY": "1"
  }
}
```

Achtung: Wer Schreibrechte am Repo hat, kann den `COPY`-Schritt ändern. Eine Richtlinie, die niemand im Repo umgehen kann, kommt über Server-managed Settings oder MDM.

## Schritt für Schritt: Sandbox für ein Team

1. **Ansatz wählen.** Bash-Sandbox für den Alltag, Devcontainer für unbeaufsichtigte Läufe und ein einheitliches Team-Setup.
2. **Abhängigkeiten installieren.** Linux und WSL 2: `bubblewrap` und `socat`. macOS braucht nichts, Windows nativ geht nicht.
3. **Sandbox im Projekt einschalten.** `sandbox.enabled` und die nötigen Domains in `.claude/settings.json` (Beispiel 3).
4. **Zugangsdaten sperren.** `credentials.files` und `credentials.envVars` (Beispiel 4) und die deny-Regeln der [Vorlage](../../src/claude_team/vorlage/.claude/settings.json) für `.env`, `~/.aws`, `~/.ssh` und `~/.kube`.
5. **Ausnahmen klein halten.** Nur einzelne `excludedCommands`, keine breiten Domains.
6. **Testen.** Die Probe-Befehle aus Beispiel 1, danach `/sandbox` und den Tab Dependencies auf Linux.
7. **Pflicht machen, wenn nötig.** In Managed Settings:

   ```json
   {
     "sandbox": {
       "enabled": true,
       "failIfUnavailable": true,
       "allowUnsandboxedCommands": false
     }
   }
   ```

   `failIfUnavailable` lässt Claude Code nicht starten, wenn die Sandbox fehlt, statt ohne zu laufen. Mit diesen drei Werten ist die Sandbox ab v2.1.285 "admin-required": Claude Code ignoriert dann lockernde Einträge wie `excludedCommands` und `allowedDomains` aus `.claude/settings.json` und `.claude/settings.local.json`. Auf nativen Windows-Rechnern beendet sich Claude Code mit dieser Richtlinie, verteile sie deshalb nur an macOS und Linux.

8. **Im Repo prüfen.** `claude-team audit .` meldet unter anderem einen fehlenden Schutz vor dem Bypass-Modus ([CC012](../regeln.md#cc012)) und fehlende deny-Regeln ([CC013](../regeln.md#cc013), [CC014](../regeln.md#cc014)).

## Grenzen der Sandbox

- **Breite Domains.** `github.com` in `allowedDomains` erlaubt auch, Daten dorthin hochzuladen. Ohne `network.tlsTerminate` schaut der Proxy nicht in TLS-Verbindungen; über Domain Fronting lässt sich die Liste umgehen.
- **Unix-Sockets.** `allowUnixSockets` für `/var/run/docker.sock` gibt praktisch Zugriff auf den Host.
- **Lesen.** Standardmäßig darf ein Befehl in der Sandbox fast alles lesen. Sperre Home und Schlüssel mit `denyRead` oder `credentials`.
- **Bypass.** Für `--dangerously-skip-permissions` reicht die Bash-Sandbox allein nicht, denn Datei-Tools, Hooks und MCP-Server laufen außerhalb. Dafür nimmst du einen Container, eine VM oder die Sandbox Runtime.
- **Container.** Auch im Devcontainer kann eine Sitzung mit Bypass alles im Container lesen und senden, auch die Zugangsdaten in `~/.claude`. Mounte `~/.ssh` nicht in den Container und kombiniere den Bypass mit einer Egress-Firewall wie `init-firewall.sh` aus dem [Referenz-Container](https://github.com/anthropics/claude-code/tree/main/.devcontainer).

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Pakete fehlen | `/sandbox` meldet fehlende Abhängigkeiten | `sudo apt-get install bubblewrap socat` |
| WSL 1 | `Sandboxing requires WSL2` | Distribution mit `wsl --set-version <DistroName> 2` umstellen |
| Container ohne Rechte | `Can't mount proc on /newroot/proc: Operation not permitted` | `enableWeakerNestedSandbox` setzen oder den Container selbst als Grenze nutzen |
| Docker in der Sandbox | `docker`-Befehle scheitern | `excludedCommands` mit `docker compose *` (Beispiel 5) |
| Werkzeug ignoriert Proxy | Datenbank-Client oder `ssh` erreicht freigegebenen Host nicht | Befehl über `excludedCommands` ausnehmen und mit einer `ask`-Regel absichern |
| TLS-Fehler auf macOS | `gh`, `gcloud` oder `terraform` scheitern an der Zertifikatsprüfung | Muster wie `gh *` in `excludedCommands` |
| Panel gesperrt | `Sandbox settings are overridden by a higher-priority configuration` | Managed Settings legen die Sandbox fest, Änderungen über den Admin |
| Bypass als root | Claude Code lehnt `--dangerously-skip-permissions` ab | `remoteUser` im Devcontainer auf einen normalen Nutzer setzen |

## Häufige Fragen

### Ist die Sandbox in Claude Code standardmäßig an?

Nein. Du schaltest sie mit `/sandbox` oder `sandbox.enabled: true` ein. Für ein ganzes Team setzt du sie in Managed Settings, optional mit `failIfUnavailable`.

### Schützt die Sandbox auch vor dem Lesen von .env-Dateien?

Nur teilweise. Die Sandbox regelt Shell-Befehle, nicht das Read-Tool. Das Read-Tool sperrst du mit deny-Regeln wie `Read(./.env)` in der settings.json, Shell-Befehle zusätzlich mit `denyRead` oder `credentials`. Mehr in [Claude Code Sicherheit](./claude-code-sicherheit.md).

### Brauche ich für einen Devcontainer VS Code?

Nein, aber es ist der einfachste Weg. Das Feature folgt dem Dev-Container-Standard und funktioniert auch in GitHub Codespaces. Den Referenz-Container aus `anthropics/claude-code` öffnest du in VS Code mit "Dev Containers: Reopen in Container".

### Darf ich im Container --dangerously-skip-permissions nutzen?

Die Doku empfiehlt den Flag nur in einem Container, einer VM oder der Sandbox Runtime, mit einem normalen Nutzer statt root und mit begrenztem Netzwerk. Claude kann dann trotzdem alle Dateien im eingebundenen Workspace ändern. Wie du den Flag sperrst, steht in [dangerously-skip-permissions](./claude-code-dangerously-skip-permissions.md).

### Was ist die Sandbox Runtime?

Das npm-Paket `@anthropic-ai/sandbox-runtime` packt den ganzen Claude-Code-Prozess in dieselbe Seatbelt- oder bubblewrap-Isolierung, also auch Hooks und MCP-Server. Du startest es mit `npx @anthropic-ai/sandbox-runtime claude` und konfigurierst es in `~/.srt-settings.json`. Es ist eine Beta (Research Preview), das Format kann sich ändern.

### Kann ich die Sandbox unter Windows nutzen?

Nur in WSL 2. Unter nativem Windows laufen Befehle ohne Sandbox. Dort nimmst du einen Devcontainer, eine VM oder WSL 2, siehe [Claude Code unter Windows](./claude-code-windows.md).

## Weiterlesen

- [Claude Code Sicherheit](./claude-code-sicherheit.md)
- [Claude Code dangerously-skip-permissions](./claude-code-dangerously-skip-permissions.md)
- [Claude Code Permissions](./claude-code-permissions.md)
- [Claude Code installieren](./claude-code-installieren.md)
- [Vorlage `.claude/settings.json`](../../src/claude_team/vorlage/.claude/settings.json)
- Offizielle Doku: [Sandboxing](https://code.claude.com/docs/en/sandboxing), [Sandbox environments](https://code.claude.com/docs/en/sandbox-environments), [Development containers](https://code.claude.com/docs/en/devcontainer)
