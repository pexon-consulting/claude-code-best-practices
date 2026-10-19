# Claude Code Security: Sicherheitsregeln für Teams und Unternehmen

Claude Code Security heißt im Unternehmen: Der Agent arbeitet mit den Rechten des Entwicklers, also begrenzt du technisch, welche Dateien er lesen, welche Befehle er ausführen und welche Hosts er erreichen darf. Die wichtigsten Risiken sind Secrets im Kontext, Prompt Injection über Dateien, Webseiten und MCP-Server, zerstörerische Befehle, die Lieferkette von MCP-Servern und Datenabfluss über WebFetch oder `curl`. Dagegen helfen mehrere Schichten: deny-Regeln, Hooks, Sandbox mit Netz-Allowlist, Devcontainer, Managed Settings und Review.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

Diese Anleitung erklärt Technik und Einstellungen. Sie ist keine Rechtsberatung. Datenschutz, Verträge und Mitbestimmung klärst du mit Datenschutzbeauftragtem, Rechtsabteilung und Betriebsrat. Angaben zu Regionen und Datenverarbeitung der Anbieter können sich ändern; maßgeblich sind deren aktuelle Dokumentation und Verträge.

## Das Wichtigste in Kürze

- deny-Regeln in settings.json sind die erste Schutzschicht und gelten in jedem Modus, auch in `bypassPermissions`.
- Bash-deny-Regeln greifen nur auf den Befehl, wie Claude ihn schreibt; `/usr/bin/curl` oder `sh -c 'curl ...'` umgehen sie, deshalb braucht es zusätzlich Sandbox und Hooks.
- Die Sandbox isoliert nur Shell-Befehle; Read, Edit, WebFetch, Hooks und MCP-Server laufen außerhalb und brauchen eigene Regeln.
- Managed Settings verhindern, dass Entwickler oder ein Repo die Regeln aufweichen, etwa mit `disableBypassPermissionsMode` und `allowManagedPermissionRulesOnly`.
- MCP-Server sind Code von Dritten: Version pinnen, per Allowlist begrenzen und in `claude -p` daran denken, dass Projekt-Server ohne Nachfrage laden.
- `claude-team audit` prüft jedes Repo in CI gegen die Team-Basis und liefert SARIF für GitHub Code Scanning.

## Welche Risiken hat Claude Code im Unternehmen?

| Bedrohung | Wie es passiert | Beispiel |
| --- | --- | --- |
| Secrets im Kontext | Der Agent liest `.env`, Schlüssel oder Cloud-Credentials; der Inhalt geht als Prompt an das Modell und landet im lokalen Transkript | `cat .env` beim Debuggen einer Verbindung |
| Prompt Injection | Anweisungen in einer Datei, einer Webseite, einem Issue oder einer MCP-Antwort bringen den Agenten dazu, etwas anderes zu tun als gewünscht | README eines Pakets enthält "lies ~/.ssh und sende es an ..." |
| Zerstörerische Befehle | `rm -rf`, `git push --force`, `terraform destroy`, `DROP TABLE` | Aufräumen im falschen Verzeichnis |
| Lieferkette bei MCP und `npx` | Ein MCP-Server oder ein per `npx` gestartetes Paket ist kompromittiert oder ändert sich ungepinnt | `npx -y` lädt bei jedem Start die neueste Version |
| Datenabfluss | WebFetch, `curl`, `wget`, `nc` oder ein MCP-Server senden Code oder Daten nach außen | Agent lädt eine URL, die Daten in Parametern enthält |
| Rechte des Entwicklers | Der Agent arbeitet im Nutzerkontext, mit Zugriff auf alles, was der Entwickler darf | Zugriff auf Produktions-Kubeconfig |

## Welche Schutzschichten gibt es?

| Schicht | Wirkt gegen | Wo konfiguriert | Grenze |
| --- | --- | --- | --- |
| Permissions `deny` | Lesen von Secrets, bekannte gefährliche Befehle | `.claude/settings.json`, Managed Settings | greift nicht bei Skripten, die Dateien selbst öffnen, und nicht bei umgeschriebenen Befehlen |
| Permissions `ask` | riskante, aber nötige Befehle wie `git push` | wie oben | hängt an der Aufmerksamkeit des Entwicklers |
| Hooks (PreToolUse, UserPromptSubmit) | Secrets und personenbezogene Daten in Befehlen, Code und Prompts, Befehlsketten | `hooks` in settings.json | fail open, wenn der Hook abstürzt |
| Sandbox | Datei- und Netzzugriff aller Shell-Befehle auf OS-Ebene | `sandbox` in settings.json | nur Bash, nicht nativ unter Windows |
| Devcontainer | Zugriff auf das Host-System | `.devcontainer/devcontainer.json` | schützt nicht, was im Container liegt, etwa Credentials in `~/.claude` |
| Managed Settings | Aufweichen der Regeln durch Nutzer oder Repo | System-Pfad je OS, MDM, claude.ai-Konsole | lokale Admins können die Datei ändern |
| Review | logische Fehler, Schwachstellen im erzeugten Code | `/security-review`, Pull Requests | ersetzt keine technische Sperre |
| Audit in CI | fehlende oder zu offene Konfiguration im Repo | `claude-team audit`, GitHub Action | prüft Dateien, nicht das Laufzeitverhalten |

## Secrets mit deny-Regeln und Hooks schützen

deny-Regeln blocken die Datei-Tools und von Claude Code erkannte Befehle wie `cat`, `head`, `tail`, `sed` und `tee` sowie Umleitungen wie `< file`. Ein Python- oder Node-Skript, das Dateien selbst öffnet, erfassen sie nicht. Ein Dateiname ohne Pfad wirkt in jeder Tiefe: `Read(.env)` entspricht `Read(**/.env)`.

```json
{
  "permissions": {
    "deny": [
      "Read(.env)",
      "Read(.env.*)",
      "Read(!.env.example)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Read(**/id_rsa*)",
      "Read(**/id_ed25519*)",
      "Read(~/.aws/**)",
      "Read(~/.ssh/**)",
      "Read(~/.kube/**)",
      "Edit(.env)",
      "Edit(.env.*)",
      "Bash(printenv *)",
      "Bash(env)"
    ]
  }
}
```

Ein `!`-Muster in einer deny-Liste nimmt Pfade aus den davor stehenden Regeln derselben Quelle wieder heraus. Hier bleibt `.env.example` lesbar. Ein `!`-Muster ganz am Anfang der Liste wirkt nicht.

Der Hook `secrets_schutz.py` aus der [Vorlage](../../src/claude_team/vorlage/.claude/hooks/secrets_schutz.py) ergänzt das: Er sperrt zusätzlich `gh auth token` und blockt neuen Code mit Tokens von AWS, GitHub, GitLab, Slack, Anthropic, OpenAI, Google, Stripe und Azure, mit JWTs und mit URLs, die ein Passwort enthalten. `befehle_schutz.py` prüft jeden Teil einer Befehlskette und sperrt `rm -rf` auf `/`, `~`, `.` und `*`, `git push --force` ohne `-with-lease`, `--no-verify`, `curl ... | sh`, `chmod 777`, `mkfs` und `dd`.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Write|MultiEdit|NotebookEdit|Grep|Glob|Bash|PowerShell",
        "hooks": [
          { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/secrets_schutz.py\"", "timeout": 10 }
        ]
      },
      {
        "matcher": "Bash|PowerShell",
        "hooks": [
          { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/befehle_schutz.py\"", "timeout": 10 }
        ]
      }
    ]
  }
}
```

Credentials in Umgebungsvariablen schützt `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`: Claude Code entfernt sie aus der Umgebung von Bash-Befehlen, Hooks und stdio-MCP-Servern. GitHub-Tokens und Proxy-Einstellungen bleiben laut Doku erhalten, die Erkennung läuft über Name oder Form des Werts. Nutze es als zusätzliche Schicht, nicht als einzige.

## Prompt Injection und Datenabfluss begrenzen

Prompt Injection lässt sich nicht zuverlässig erkennen. Die Doku empfiehlt deshalb, Permissions und Sandbox zu kombinieren, weil die Sandbox auch dann greift, wenn eine Injection die Entscheidung des Modells umgeht. Praktisch heißt das: Begrenze, was ein manipulierter Agent erreichen kann.

1. **Netzwerk-Werkzeuge sperren** und für erlaubte Ziele WebFetch mit Domain-Regel nutzen.
2. **Sandbox mit Netz-Allowlist** aktivieren, damit auch umgeschriebene Befehle nur freigegebene Hosts erreichen.
3. **MCP-Server begrenzen**, besonders solche, die externe Inhalte holen.

```json
{
  "permissions": {
    "deny": ["Bash(curl *)", "Bash(wget *)", "Bash(nc *)", "WebSearch"],
    "allow": ["WebFetch(domain:docs.python.org)", "WebFetch(domain:*.github.com)"]
  },
  "sandbox": {
    "enabled": true,
    "allowUnsandboxedCommands": false,
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org", "pypi.org"]
    }
  }
}
```

Hinweise zur Sandbox laut [Sandboxing](https://code.claude.com/docs/en/sandboxing):

- Sie läuft unter macOS, Linux und WSL2, nicht nativ unter Windows.
- Ohne `allowedDomains` ist im Sandbox-Netz nichts freigegeben; neue Hosts behandelt Claude Code dann nach dem Permission-Modus.
- `allowUnsandboxedCommands: false` verhindert, dass Claude einen gescheiterten Befehl außerhalb der Sandbox wiederholt.
- `failIfUnavailable: true` lässt Claude Code nicht starten, wenn die Sandbox fehlt, statt ungeschützt weiterzulaufen.
- Credential-Dateien schützt `sandbox.credentials`; eine eingebaute Liste gibt es nicht.

```json
{
  "sandbox": {
    "enabled": true,
    "credentials": {
      "files": [{ "path": "~/.aws/credentials", "mode": "deny" }],
      "envVars": [{ "name": "GITHUB_TOKEN", "mode": "deny" }]
    }
  }
}
```

## MCP-Server und Lieferkette absichern

MCP-Server laufen als eigener Prozess oder als entfernter Dienst. Was sie verarbeiten, fällt nicht unter Zero Data Retention und nicht unter die Sandbox. Regeln für das Team:

- Feste Versionen statt `@latest` oder ungepinntem `npx -y` (Prüfregel [CC033](../regeln.md#cc033)).
- Keine Tokens im Klartext in `.mcp.json`, sondern `${VARIABLE}` (Prüfregel [CC032](../regeln.md#cc032)).
- `enableAllProjectMcpServers` nicht setzen (Prüfregel [CC018](../regeln.md#cc018)).
- In `claude -p`, im Agent SDK und in Cloud-Sessions laden Projekt-Server aus `.mcp.json` ohne Nachfrage. In CI deshalb `--strict-mcp-config` mit einer eigenen `--mcp-config` oder `--bare` nutzen.
- Unternehmensweit per Allowlist und Denylist in den Managed Settings begrenzen; die Denylist gilt immer.

```json
{
  "allowManagedMcpServersOnly": true,
  "allowedMcpServers": [
    { "serverUrl": "https://mcp.example.com/*" },
    { "serverCommand": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "."] }
  ],
  "deniedMcpServers": [
    { "serverName": "filesystem-alt" }
  ]
}
```

Ein `serverCommand`-Eintrag muss exakt passen, inklusive aller Argumente. Wenn du die Paketversion im Befehl pinnst, etwa `@modelcontextprotocol/server-filesystem@<version>`, muss derselbe Text in der Allowlist stehen.

## Bypass-Modus und Auto-Modus zentral steuern

`--dangerously-skip-permissions` bietet laut Doku keinen Schutz gegen Prompt Injection. In Managed Settings sperrst du den Modus für alle; Claude Code lehnt das Flag dann ab und ignoriert `permissionMode: bypassPermissions` in Subagent-Definitionen.

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  },
  "disableAutoMode": "disable"
}
```

`disableAutoMode` entfernt den Auto-Modus aus dem `Shift+Tab`-Wechsel. Ob du ihn sperrst, ist eine Abwägung: Der Auto-Modus prüft Aktionen mit einem Klassifikator und ist laut Doku die Alternative zu weniger Rückfragen ohne Bypass.

## Devcontainer für unbeaufsichtigte Läufe

Ein Devcontainer trennt den Agenten vom Host. Das Referenz-Setup im Repo `anthropics/claude-code` enthält eine Firewall (`init-firewall.sh`) und läuft als Nicht-root-Nutzer. Laut [Devcontainer](https://code.claude.com/docs/en/devcontainer) verhindert ein Container mit `--dangerously-skip-permissions` nicht, dass ein bösartiges Projekt alles abzieht, was im Container erreichbar ist, auch die Claude-Code-Credentials in `~/.claude`.

```json
{
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/anthropics/devcontainer-features/claude-code:1.0": {}
  },
  "containerEnv": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1"
  }
}
```

Das Basis-Image ist ein Beispiel; die Feature-ID stammt aus der Doku.

## Review: /security-review und automatische Prüfung

`/security-review` analysiert die Änderungen des aktuellen Branches gegen den Default-Branch von `origin` auf Schwachstellen wie Injection, Authentifizierungsfehler und Datenoffenlegung. Der Befehl braucht ein `origin`-Remote. Für Pull Requests gibt es von Anthropic die GitHub Action `anthropics/claude-code-security-review`; Details stehen in deren Repository. Ein Review findet Fehler im erzeugten Code, ersetzt aber keine Sperre in der Konfiguration.

## Beispiele für sichere Einstellungen

### Beispiel 1: Repo in CI gegen die Team-Basis prüfen

```yaml
name: Claude Code Audit
on: [pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v6
      - uses: pexon-consulting/claude-code-best-practices@v0.2.0
        with:
          pfad: .
          schwelle: fehler
          sarif: "true"
```

Für jedes Repo mit Claude-Code-Konfiguration; Befunde erscheinen in GitHub Code Scanning.

### Beispiel 2: Audit lokal als Markdown-Bericht

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team audit . --format markdown --out audit.md
```

Für die Freigabe durch die IT-Sicherheit, die einen lesbaren Bericht braucht.

### Beispiel 3: Sandbox als Pflicht in den Managed Settings

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "network": {
      "allowedDomains": ["github.com", "registry.npmjs.org"],
      "allowManagedDomainsOnly": true
    }
  }
}
```

Für Flotten aus macOS und Linux; unter nativem Windows startet Claude Code mit `failIfUnavailable` nicht.

### Beispiel 4: Nur Managed-Regeln zulassen

```json
{
  "allowManagedPermissionRulesOnly": true,
  "permissions": {
    "allow": ["Bash(git status *)", "Bash(git diff *)", "Bash(npm run test *)"],
    "deny": ["Read(.env)", "Read(~/.ssh/**)", "Bash(curl *)"]
  }
}
```

Für streng regulierte Umgebungen; Regeln aus Nutzer- und Projektdateien und `--allowedTools` werden ignoriert.

### Beispiel 5: Headless-Lauf in CI mit festen Grenzen

```bash
claude -p "Prüfe die Änderungen auf Sicherheitsprobleme" \
  --strict-mcp-config \
  --allowedTools "Read,Bash(git diff *)" \
  --permission-prompts none \
  --max-budget-usd 2
```

Für CI-Jobs ohne Projekt-MCP-Server und mit Kostengrenze; `--permission-prompts none` lehnt alles ab, was fragen würde (ab v2.1.259).

### Beispiel 6: Nur Hooks der Organisation zulassen

```json
{
  "allowManagedHooksOnly": true,
  "extraKnownMarketplaces": {
    "claude-code-best-practices": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-code-best-practices",
        "ref": "v0.2.0"
      }
    }
  },
  "enabledPlugins": {
    "team-basis@claude-code-best-practices": true
  }
}
```

Für Organisationen, die Hooks zentral über ein freigegebenes Plugin verteilen und alle anderen Hooks blocken wollen. `your-org/claude-code-best-practices` steht für einen geprüften Fork in der eigenen Organisation, gepinnt auf einen Tag; ein fremdes Repo ohne `ref` würde jede Änderung sofort auf alle Rechner bringen. Unter `allowManagedHooksOnly` laufen nur Managed Hooks und Hooks aus Plugins, die die Managed Settings per `enabledPlugins` erzwingen; Hooks aus Projekt-settings.json und Subagent-Frontmatter sind dann blockiert.

## Schritt für Schritt

1. Team-Basis ins Repo legen: `claude-team einrichten . --dry-run` prüfen, dann ohne `--dry-run`.
2. deny-Regeln für `.env`, Schlüssel und Cloud-Credentials kontrollieren (Prüfregeln [CC013](../regeln.md#cc013) und [CC014](../regeln.md#cc014)).
3. Hooks aktivieren und mit `/hooks` in einer Sitzung kontrollieren, dass sie geladen sind.
4. Sandbox mit Netz-Allowlist einschalten und mit einem Test wie `curl https://example.com` prüfen, dass der Zugriff gesperrt ist.
5. MCP-Server pinnen und in den Managed Settings auf eine Allowlist setzen.
6. `disableBypassPermissionsMode` und bei Bedarf `allowManagedPermissionRulesOnly` zentral verteilen, siehe [Claude Code Enterprise](./claude-code-enterprise.md).
7. `claude-team audit` als GitHub Action in jedes Repo.
8. `/security-review` vor jedem Merge größerer KI-Änderungen nutzen.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Nur `Bash(curl *)` gesperrt | `sh -c 'curl ...'` oder `/usr/bin/curl` funktioniert | Sandbox mit `allowedDomains` ergänzen |
| Pfadregel für `Write(...)` geschrieben | Warnung beim Start, Regel wirkt nicht | `Edit(...)` verwenden (Prüfregel [CC017](../regeln.md#cc017)) |
| `/secrets/**` in Nutzer-Settings | Regel greift auf `~/.claude/secrets`, nicht im Projekt | `~/`- oder `//`-Pfade oder Projekt-Settings nutzen |
| Sandbox ohne `allowUnsandboxedCommands: false` | gescheiterte Befehle laufen ungeschützt erneut | Wert auf `false` setzen |
| MCP-Server mit `@latest` | Verhalten ändert sich ohne Review | Version pinnen (Prüfregel [CC033](../regeln.md#cc033)) |
| Hook-Skript fehlt oder ist nicht ausführbar | Schutz greift still nicht | `claude-team audit` meldet [CC021](../regeln.md#cc021) und [CC022](../regeln.md#cc022) |

## Häufige Fragen

### Ist Claude Code sicher für den Unternehmenseinsatz?

Claude Code ist so sicher wie seine Konfiguration: Standardmäßig fragt es vor Änderungen und Befehlen, aber ohne deny-Regeln, Sandbox und Managed Settings kann der Agent alles lesen, was der Entwickler lesen darf. Mit den Schichten aus dieser Anleitung begrenzt du das technisch.

### Kann Claude Code meine .env-Datei lesen?

Ja, ohne Regel kann der Agent `.env` lesen, sobald du zustimmst oder ein Modus Lesen erlaubt. Eine deny-Regel `Read(.env)` plus der Hook `secrets_schutz.py` sperrt das für Datei-Tools und erkannte Befehle.

### Wie schütze ich mich vor Prompt Injection?

Verlass dich nicht darauf, Injection zu erkennen, sondern begrenze die Folgen: Netzwerkwerkzeuge sperren, Sandbox mit Netz-Allowlist, keine Secrets im Zugriff, MCP-Server nur nach Freigabe. Dann kann ein manipulierter Agent wenig Schaden anrichten.

### Schützt die Sandbox auch Read und WebFetch?

Nein, die Sandbox isoliert nur Shell-Befehle. Read, Edit, WebFetch, Hooks und MCP-Server steuerst du über Permissions und eigene Regeln.

### Was macht /security-review?

`/security-review` prüft die Änderungen des aktuellen Branches gegen den Default-Branch von `origin` auf Schwachstellen. Es braucht ein `origin`-Remote und ersetzt kein menschliches Review.

## Weiterlesen

- [Claude Code DSGVO](./claude-code-dsgvo.md)
- [Claude Code Permissions](./claude-code-permissions.md)
- [Claude Code Hooks](./claude-code-hooks.md)
- [Claude Code Sandbox](./claude-code-sandbox.md)
- [Claude Code MCP](./claude-code-mcp.md)
- [Claude Code Enterprise](./claude-code-enterprise.md)
- Vorlagen: [settings.json](../../src/claude_team/vorlage/.claude/settings.json), [schutz.json](../../src/claude_team/vorlage/.claude/schutz.json), [Freigabe-Paket](../rollout/freigabe-paket.md)
- [Claude Code Review: automatische Reviews mit GitHub Actions](./claude-code-review-github-actions.md)
