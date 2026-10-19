# Claude Code installieren: Schritt für Schritt für macOS, Linux und Windows

Claude Code installierst du am einfachsten mit dem nativen Installer: `curl -fsSL https://claude.ai/install.sh | bash` auf macOS, Linux und WSL oder `irm https://claude.ai/install.ps1 | iex` in der Windows PowerShell. Du brauchst macOS 13+, Windows 10 1809+, Ubuntu 20.04+, Debian 10+ oder Alpine 3.19+, mindestens 4 GB RAM, eine Internetverbindung und ein Pro-, Max-, Team-, Enterprise- oder Console-Konto (der kostenlose claude.ai-Plan reicht nicht). Danach startest du `claude` im Projektordner, meldest dich im Browser an und prüfst die Installation mit `claude doctor`.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- Der native Installer ist der empfohlene Weg und aktualisiert Claude Code automatisch im Hintergrund.
- Homebrew (`brew install --cask claude-code`), WinGet (`winget install Anthropic.ClaudeCode`) sowie apt, dnf und apk funktionieren auch, aktualisieren sich aber nicht von selbst.
- Die npm-Installation (`npm install -g @anthropic-ai/claude-code`) ist weiter dokumentiert, braucht Node.js 22 oder neuer und nie `sudo`.
- `claude --version` zeigt die Version, `claude doctor` prüft Installation, Settings-Dateien und den letzten Update-Versuch, ohne eine Sitzung zu starten.
- Für Teams legst du Update-Kanal und Mindestversion zentral fest (`autoUpdatesChannel`, `minimumVersion`) und richtest das Projekt mit `claude-team einrichten` ein.

## Welche Voraussetzungen braucht Claude Code?

Laut [offizieller Setup-Doku](https://code.claude.com/docs/en/setup) gelten diese Systemanforderungen:

| Bereich | Anforderung |
| --- | --- |
| Betriebssystem | macOS 13.0+, Windows 10 1809+ oder Windows Server 2019+, Ubuntu 20.04+, Debian 10+, Alpine Linux 3.19+ |
| Hardware | 4 GB RAM oder mehr, x64- oder ARM64-Prozessor (kein 32-Bit-Windows) |
| Netzwerk | Internetverbindung, der Installer lädt von `downloads.claude.ai` |
| Shell | Bash, Zsh, PowerShell oder CMD |
| Standort | ein von Anthropic unterstütztes Land |
| Konto | Pro, Max, Team, Enterprise oder Console; alternativ Amazon Bedrock, Google Cloud's Agent Platform (früher Vertex AI) oder Microsoft Foundry |

ripgrep bringt Claude Code normalerweise mit. Nur auf Alpine und anderen musl-Systemen installierst du es selbst (siehe Beispiel 5). Unter nativem Windows empfiehlt die Doku zusätzlich [Git for Windows](https://git-scm.com/downloads/win), damit Claude Code das Bash-Tool nutzen kann. Details dazu stehen in der Anleitung [Claude Code unter Windows](./claude-code-windows.md).

## Claude Code installieren: alle Wege im Vergleich

| Weg | Befehl | Auto-Update | Wann sinnvoll |
| --- | --- | --- | --- |
| Nativer Installer (empfohlen) | `curl -fsSL https://claude.ai/install.sh \| bash` | ja | Standard für macOS, Linux, WSL |
| Nativer Installer Windows | `irm https://claude.ai/install.ps1 \| iex` | ja | Windows PowerShell |
| Homebrew | `brew install --cask claude-code` | nein | macOS mit Homebrew |
| WinGet | `winget install Anthropic.ClaudeCode` | nein | Windows mit Softwareverteilung über WinGet |
| apt, dnf, apk | siehe [Setup-Doku](https://code.claude.com/docs/en/setup#install-with-linux-package-managers) | nein, über System-Updates | Server und verwaltete Linux-Flotten |
| npm | `npm install -g @anthropic-ai/claude-code` | ja, wenn das npm-Verzeichnis beschreibbar ist | bestehende Node-Umgebungen |

Der Installer zeigt beim Download keinen Fortschritt. Öffne danach ein neues Terminal und prüfe mit `claude --version`. Eine funktionierende Installation gibt eine Versionsnummer mit dem Zusatz `(Claude Code)` aus.

Homebrew bietet zwei Casks: `claude-code` folgt dem Kanal `stable` (meist etwa eine Woche alt, ohne Versionen mit größeren Regressionen), `claude-code@latest` folgt dem Kanal `latest`.

Die npm-Variante installiert dasselbe native Binary wie der Installer. Sie läuft zur Laufzeit also nicht über dein Node.js. Unterstützte Plattformen sind `darwin-arm64`, `darwin-x64`, `linux-x64`, `linux-arm64`, `linux-x64-musl`, `linux-arm64-musl`, `win32-x64` und `win32-arm64`. Zum Aktualisieren nimmst du `npm install -g @anthropic-ai/claude-code@latest`, nicht `npm update -g`.

## Beispiele für die Installation

### Beispiel 1: Installation auf macOS oder Linux mit Prüfung

Der Standardweg für einen Entwicklerrechner.

```bash
curl -fsSL https://claude.ai/install.sh | bash
# neues Terminal öffnen, dann:
claude --version
claude doctor
```

Der Installer legt den Starter unter `~/.local/bin/claude` ab, die Versionen unter `~/.local/share/claude/versions/`.

### Beispiel 2: Installation unter Windows (PowerShell oder CMD)

Für native Windows-Rechner, ohne Administratorrechte.

```powershell
irm https://claude.ai/install.ps1 | iex
claude --version
```

In CMD lautet der Befehl:

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

Die Meldung `The token '&&' is not a valid statement separator` heißt: Du bist in PowerShell und hast den CMD-Befehl genommen. `'irm' is not recognized` heißt umgekehrt: Du bist in CMD.

### Beispiel 3: Den Kanal stable oder eine feste Version installieren

Wenn du nicht jede neue Version sofort willst oder eine Version für Tests festhalten musst.

```bash
# Kanal stable
curl -fsSL https://claude.ai/install.sh | bash -s stable

# feste Version
curl -fsSL https://claude.ai/install.sh | bash -s 2.1.89
```

Der beim Installieren gewählte Kanal wird zum Standard für die automatischen Updates.

### Beispiel 4: Hinter einem Firmen-Proxy installieren

Wenn der Download an Firewall oder Proxy scheitert (`403`, Zeitüberschreitung, `Could not resolve host`).

```bash
curl -sI https://downloads.claude.ai/claude-code-releases/latest
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
curl -fsSL https://claude.ai/install.sh | bash
```

Die erste Zeile prüft, ob der Downloadserver erreichbar ist. Ein `200` in der ersten Antwortzeile heißt: erreichbar.

### Beispiel 5: Alpine Linux oder ein musl-System vorbereiten

Alpine bringt weder `bash` noch `curl` mit, deshalb schlägt der Installer sonst mit `not found` fehl.

```bash
apk add bash curl libgcc libstdc++ ripgrep
curl -fsSL https://claude.ai/install.sh | bash
```

Danach schaltest du in der settings.json das mitgelieferte ripgrep ab:

```json
{
  "env": {
    "USE_BUILTIN_RIPGREP": "0"
  }
}
```

### Beispiel 6: Updates steuern

Für Rechner, auf denen du den Update-Zeitpunkt selbst bestimmen willst.

```json
{
  "autoUpdatesChannel": "stable",
  "minimumVersion": "2.1.100",
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

`DISABLE_AUTOUPDATER` stoppt nur die Hintergrundprüfung, `claude update` funktioniert weiter. Wer Claude Code selbst verteilt und jedes Update sperren will, setzt stattdessen `DISABLE_UPDATES` auf `"1"`. Ob die Einstellung greift, zeigt `claude doctor` in der Zeile `Auto-updates` mit `disabled (set by env: DISABLE_AUTOUPDATER)`.

### Beispiel 7: Claude Code in einem Docker-Image installieren

Für CI-Images oder eigene Container.

```dockerfile
WORKDIR /tmp
RUN curl -fsSL https://claude.ai/install.sh | bash
```

Ohne `WORKDIR` startet der Installer in `/` und durchsucht das ganze Dateisystem. Das kann laut [Troubleshooting-Doku](https://code.claude.com/docs/en/troubleshoot-install#install-hangs-in-docker) hängen bleiben. Für isolierte Container mit Firewall lies [Claude Code Sandbox](./claude-code-sandbox.md).

### Beispiel 8: Das Projekt für das Team einrichten

Nach der Installation legst du im Repo die gemeinsame Basis an: CLAUDE.md, `.claude/settings.json`, Schutz-Hooks, Regeln und Skills.

```bash
cd /pfad/zu/deinem/projekt
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team einrichten . --dry-run
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team einrichten .
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team audit .
```

`einrichten` überschreibt nichts. Gibt es schon eine settings.json oder CLAUDE.md, entsteht `.claude/settings.vorschlag.json` bzw. `CLAUDE.vorschlag.md`. Das Profil `--profil streng` sperrt zusätzlich WebFetch, WebSearch, curl, wget, nc, scp und ssh. Das CLI braucht Python 3.10 oder neuer und nur die Standardbibliothek.

## Schritt für Schritt: von null zur ersten Sitzung

1. **Terminal öffnen.** Auf macOS das Terminal, unter Windows PowerShell (der Prompt beginnt mit `PS C:\`), unter Linux die Shell deiner Wahl.
2. **Installer ausführen.** Befehl aus Beispiel 1 oder 2. Unter Windows brauchst du keine Administratorrechte.
3. **Neues Terminal öffnen und prüfen.** `claude --version` muss eine Versionsnummer zeigen. Bei `command not found` fehlt `~/.local/bin` (Windows: `%USERPROFILE%\.local\bin`) im PATH, siehe "Häufige Fehler".
4. **Diagnose laufen lassen.** `claude doctor` zeigt den Installationszustand, Fehler in Settings-Dateien und Warnungen mit Lösungsvorschlag.
5. **In den Projektordner wechseln und starten.**

   ```bash
   cd /pfad/zu/deinem/projekt
   claude
   ```

6. **Anmelden.** Beim ersten Start öffnet Claude Code den Browser. Startet der Browser nicht, drückst du `c` und kopierst so die Anmelde-URL. In WSL, über SSH oder in Containern zeigt der Browser nach der Anmeldung einen Code, den du bei `Paste code here if prompted` einfügst. Alternativ geht `claude auth login`.
7. **Erste Fragen stellen.** Zum Beispiel "Was macht dieses Projekt?" oder "Wo ist der Einstiegspunkt?". Claude Code liest die nötigen Dateien selbst.
8. **Wichtige Befehle kennen.** `/help` zeigt die Befehle, `/resume` setzt eine frühere Unterhaltung fort, `/login` wechselt das Konto, `/status` zeigt die aktive Anmeldung. `Shift+Tab` wechselt den Berechtigungsmodus der laufenden Sitzung.
9. **Projekt absichern.** Mit Beispiel 8 bekommt das Repo eine CLAUDE.md und eine `.claude/settings.json` mit deny-Regeln für `.env` und Schlüsseldateien (siehe Regeln [CC013](../regeln.md#cc013) und [CC014](../regeln.md#cc014)).

## Claude Code für ein Team einrichten

Für mehrere Entwickler lohnt sich eine gemeinsame Linie bei Version und Updates. Die Doku empfiehlt dafür Managed Settings. Eine Datei `managed-settings.json` liegt je nach System hier:

| System | Pfad |
| --- | --- |
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` |
| Linux und WSL | `/etc/claude-code/managed-settings.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` |

Ein Beispiel, das alle auf den Kanal `stable` setzt, eine Mindestversion vorgibt und Telemetrie abschaltet:

```json
{
  "autoUpdatesChannel": "stable",
  "minimumVersion": "2.1.290",
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1"
  }
}
```

In Managed Settings ist `minimumVersion` eine Untergrenze, die Nutzer- und Projekt-Settings nicht überschreiben können. Sie wirkt aber nur auf Updates. Soll Claude Code außerhalb eines Versionsbereichs gar nicht starten, nimmst du die Managed-Keys `requiredMinimumVersion` und `requiredMaximumVersion`. Ob die Richtlinie greift, zeigt `/status` in der Zeile `Setting sources` mit `Enterprise managed settings (file)`.

Homebrew-Installationen wählen den Kanal über den Cask-Namen, apt, dnf und apk über das Repository. `autoUpdatesChannel` wirkt dort nicht. Wer Homebrew oder WinGet nutzt und trotzdem Updates im Hintergrund will, setzt `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE` auf `1`.

Mehr zu Rollout, Freigaben und zentraler Verteilung steht in [Claude Code im Team](./claude-code-team-rollout.md) und [Claude Code Enterprise](./claude-code-enterprise.md).

## Claude Code aktualisieren und deinstallieren

Native Installationen prüfen beim Start und regelmäßig während der Laufzeit auf Updates und spielen sie beim nächsten Start ein. Sofort aktualisieren:

```bash
claude update
```

Homebrew: `brew upgrade claude-code` (bzw. `claude-code@latest`), WinGet: `winget upgrade Anthropic.ClaudeCode`, apt: `sudo apt update && sudo apt upgrade claude-code`, dnf: `sudo dnf upgrade claude-code`, apk: `apk update && apk upgrade claude-code`.

Deinstallation je nach Weg:

```bash
# nativ auf macOS, Linux, WSL
rm -f ~/.local/bin/claude
rm -rf ~/.local/share/claude

# Homebrew
brew uninstall --cask claude-code

# npm
npm uninstall -g @anthropic-ai/claude-code
```

```powershell
# nativ unter Windows
Remove-Item -Path "$env:USERPROFILE\.local\bin\claude.exe" -Force
Remove-Item -Path "$env:USERPROFILE\.local\share\claude" -Recurse -Force

# WinGet
winget uninstall Anthropic.ClaudeCode
```

Einstellungen, MCP-Konfiguration und Sitzungsverlauf liegen getrennt in `~/.claude/` und `~/.claude.json`. Lösche sie nur, wenn du wirklich alles entfernen willst. Die VS-Code-Extension, das JetBrains-Plugin und die Desktop-App schreiben ebenfalls nach `~/.claude/` und legen den Ordner sonst neu an.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| PATH fehlt | `command not found: claude` oder `'claude' is not recognized` | `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc` (Bash: `~/.bashrc`, Bash auf macOS: `~/.bash_profile`); unter Windows `%USERPROFILE%\.local\bin` zum User-PATH hinzufügen, dann neues Terminal |
| Falscher Befehl für die Shell | `A parameter cannot be found that matches parameter name 'fsSL'` | Du hast den Linux-Befehl in PowerShell genutzt. `irm https://claude.ai/install.ps1 \| iex` verwenden |
| Proxy liefert HTML | `syntax error near unexpected token '<'` | Proxy oder Netzfilter blockt `downloads.claude.ai`, siehe Beispiel 4 |
| Zu wenig Speicher | `Killed` oder `exit code 137` | Die Installation braucht etwa 512 MB freien Speicher; Swap anlegen oder größere Instanz |
| npm mit sudo | Rechtefehler, `EACCES` | Kein `sudo npm install -g`, besser den nativen Installer nutzen |
| Alte Umgebungsvariable | `This organization has been disabled` trotz aktivem Abo | Ein altes `ANTHROPIC_API_KEY` überschreibt das Abo. `unset ANTHROPIC_API_KEY` und aus dem Shell-Profil entfernen |
| Zwei Installationen | `claude` läuft nach der Deinstallation weiter | Zweite Installation oder altes Shell-Alias, siehe [Check for conflicting installations](https://code.claude.com/docs/en/troubleshoot-install#check-for-conflicting-installations) |
| 403 nach Login | `API Error: 403 Request not allowed` | Abo prüfen; bei Console-Konten braucht der Account die Rolle "Claude Code" oder "Developer" |

## Häufige Fragen

### Ist Claude Code kostenlos?

Nein, der kostenlose claude.ai-Plan enthält Claude Code nicht. Du brauchst ein Pro-, Max-, Team- oder Enterprise-Abo, ein Console-Konto mit API-Guthaben oder einen Cloud-Anbieter wie Amazon Bedrock, Google Cloud's Agent Platform oder Microsoft Foundry. Zu den Kosten im Team siehe [Claude Code Kosten](./claude-code-kosten.md).

### Brauche ich Node.js für Claude Code?

Nein, für den nativen Installer, Homebrew, WinGet und die Linux-Paketquellen brauchst du kein Node.js. Nur die npm-Installation setzt Node.js 22 oder neuer voraus, und selbst dann läuft das installierte Binary ohne Node.

### Wie prüfe ich, ob Claude Code richtig installiert ist?

Mit `claude --version` und `claude doctor`. Der erste Befehl zeigt die Version, der zweite prüft Installation, Settings-Dateien und Auto-Update und gibt Warnungen mit Lösungsvorschlag aus, ohne eine Sitzung zu starten.

### Wie schalte ich das automatische Update ab?

Setze `DISABLE_AUTOUPDATER` auf `"1"` im `env`-Block der settings.json. Das stoppt nur die Hintergrundprüfung. Um auch `claude update` und `claude install` zu sperren, setzt du `DISABLE_UPDATES`. Homebrew, WinGet, apt, dnf und apk aktualisieren ohnehin nicht automatisch.

### Kann ich Claude Code ohne Terminal nutzen?

Ja, es gibt eine Desktop-App für macOS, Windows und Linux (Beta) sowie die Extension für VS Code und das Plugin für JetBrains. Die VS-Code-Extension bringt eine eigene CLI-Kopie für ihr Chatfenster mit, legt `claude` aber nicht in den PATH. Siehe [Claude Code in VS Code und JetBrains](./claude-code-vscode-jetbrains.md).

### Wo speichert Claude Code meine Anmeldung?

Auf macOS im Schlüsselbund (Login-Keychain). Ist der Schlüsselbund gesperrt, etwa in einer SSH-Sitzung, weicht Claude Code auf die Klartextdatei `~/.claude/.credentials.json` aus. `claude doctor` meldet das mit `macOS Keychain is not writable`.

## Weiterlesen

- [Claude Code unter Windows: WSL, Git Bash und PowerShell](./claude-code-windows.md)
- [Claude Code in VS Code und JetBrains](./claude-code-vscode-jetbrains.md)
- [Claude Code Sandbox: Devcontainer und Docker](./claude-code-sandbox.md)
- [Claude Code settings.json](./claude-code-settings-json.md)
- [Claude Code Tutorial auf Deutsch](./claude-code-tutorial-deutsch.md)
- [Vorlage `.claude/settings.json`](../../src/claude_team/vorlage/.claude/settings.json) und [Prüfregeln](../regeln.md)
- Offizielle Doku: [Advanced setup](https://code.claude.com/docs/en/setup), [Quickstart](https://code.claude.com/docs/en/quickstart), [Troubleshoot installation](https://code.claude.com/docs/en/troubleshoot-install)
