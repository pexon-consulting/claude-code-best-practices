# Claude Code Windows: Installation mit WSL, Git Bash und PowerShell

Claude Code läuft nativ unter Windows 10 1809+ und Windows Server 2019+, du brauchst also kein WSL: `irm https://claude.ai/install.ps1 | iex` in PowerShell genügt, ohne Administratorrechte. Git for Windows ist optional, liefert aber Git Bash für das Bash-Tool; ohne Git Bash führt Claude Code Befehle über das PowerShell-Tool aus. WSL 2 brauchst du nur, wenn du Linux-Toolchains nutzt oder die eingebaute Sandbox willst, denn die läuft unter nativem Windows nicht.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- Nativ unter Windows installierst du mit PowerShell (`irm https://claude.ai/install.ps1 | iex`), CMD oder WinGet (`winget install Anthropic.ClaudeCode`).
- Mit Git for Windows nutzt Claude Code Git Bash für Shell-Befehle, ohne Git for Windows das PowerShell-Tool.
- Die eingebaute Sandbox läuft nur auf macOS, Linux und WSL 2; unter nativem Windows laufen Befehle ohne Sandbox.
- In WSL installierst und startest du `claude` im WSL-Terminal mit dem Linux-Installer, nicht aus PowerShell.
- Managed Settings liegen unter Windows in `C:\Program Files\ClaudeCode\managed-settings.json` oder in der Registry unter `HKLM\SOFTWARE\Policies\ClaudeCode`.

## Läuft Claude Code nativ unter Windows oder brauche ich WSL?

Beides geht. Die [Setup-Doku](https://code.claude.com/docs/en/setup#set-up-on-windows) stellt drei Varianten gegenüber:

| Variante | Voraussetzung | Sandbox | Wann sinnvoll |
| --- | --- | --- | --- |
| Natives Windows | keine; Git for Windows optional | nicht unterstützt | Windows-Projekte und Windows-Werkzeuge (.NET, PowerShell-Skripte) |
| WSL 2 | WSL 2 aktiviert | unterstützt | Linux-Toolchains, Befehle in der Sandbox |
| WSL 1 | WSL 1 aktiviert | nicht unterstützt | nur wenn WSL 2 nicht verfügbar ist |

Faustregel: Liegen deine Projekte und Werkzeuge in Windows, nimm die native Installation. Arbeitest du mit Linux-Werkzeugen, Docker-Compose-Stacks oder willst du Befehle per [Sandbox](./claude-code-sandbox.md) isolieren, nimm WSL 2. Claude Code unterstützt kein 32-Bit-Windows.

## Shell-Werkzeuge unter Windows: Git Bash oder PowerShell

Unter nativem Windows entscheidet Git for Windows, wie Claude Code Befehle ausführt:

| Situation | Was Claude Code nutzt |
| --- | --- |
| Ohne Git for Windows | das PowerShell-Tool für alle Shell-Befehle |
| Mit Git for Windows | Git Bash für das Bash-Tool und das Monitor-Tool; das PowerShell-Tool zusätzlich |
| Mit Git for Windows und claude.ai- oder Console-Konto | PowerShell-Tool standardmäßig an |
| Mit Git for Windows und Bedrock, Agent Platform oder Foundry | PowerShell-Tool nur mit `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` |
| Weder Git Bash noch PowerShell gefunden | Fehler `Claude Code on Windows requires either Git for Windows (for bash) or PowerShell` |

Ohne gesetzte Variable sucht Claude Code `bash.exe` zuerst in `C:\Program Files\Git` und `C:\Program Files (x86)\Git`, danach über das `git` im PATH (dort `bin\bash.exe`). Ein `git`, das im Startordner liegt oder darunter in einem Pfad mit `node_modules`, `.venv` oder `env`, wird übersprungen, damit kein vom Projekt mitgeliefertes Programm läuft.

Mit `CLAUDE_CODE_USE_POWERSHELL_TOOL=0` schaltest du das PowerShell-Tool aus. Auf Linux, macOS und WSL kannst du es mit `1` einschalten, dann muss `pwsh` im PATH liegen.

## Beispiele für Claude Code unter Windows

### Beispiel 1: Native Installation in PowerShell

Der Standardweg für einen Windows-Rechner.

```powershell
irm https://claude.ai/install.ps1 | iex
claude --version
claude doctor
```

Danach liegt `claude.exe` unter `%USERPROFILE%\.local\bin\`. Öffne für `claude --version` ein neues Terminal.

### Beispiel 2: Installation in CMD oder mit WinGet

Wenn PowerShell gesperrt ist oder die Softwareverteilung über WinGet läuft.

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

```powershell
winget install Anthropic.ClaudeCode
winget upgrade Anthropic.ClaudeCode
```

WinGet-Installationen aktualisieren sich nicht selbst. Mit `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1` führt Claude Code das Upgrade im Hintergrund aus. Weil Windows die laufende `claude.exe` sperrt, kann das Upgrade scheitern; dann zeigt Claude Code den manuellen Befehl.

### Beispiel 3: Git Bash fest einstellen

Wenn Git installiert ist, Claude Code es aber nicht findet, etwa bei einer portablen Git-Installation.

```powershell
where.exe git
```

Den gefundenen Pfad trägst du als `bin\bash.exe` in `%USERPROFILE%\.claude\settings.json` ein:

```json
{
  "env": {
    "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe"
  }
}
```

Claude Code akzeptiert nur eine Datei namens `bash.exe`, `sh.exe`, `bash` oder `sh`. Der Starter `git-bash.exe` wird ignoriert; dann sucht Claude Code wie ohne Variable und schreibt eine Warnung, die du mit `--debug` siehst.

### Beispiel 4: Installation in WSL 2

Für Linux-Werkzeuge und die Sandbox.

```powershell
wsl -l -v
```

Zeigt die Spalte `VERSION` eine `1`, stellst du die Distribution um:

```powershell
wsl --set-version Ubuntu 2
```

Danach im WSL-Terminal den Linux-Installer und die Sandbox-Pakete:

```bash
curl -fsSL https://claude.ai/install.sh | bash
sudo apt-get install bubblewrap socat
claude
```

WSL braucht kein Git for Windows. Ersetze `Ubuntu` durch den Namen deiner Distribution.

### Beispiel 5: Login aus WSL, wenn der Browser nicht aufgeht

In WSL 2 öffnet sich der Browser auf Windows, und der Rücksprung erreicht Claude Code oft nicht. Nach der Anmeldung zeigt der Browser einen Code, den du bei `Paste code here if prompted` einfügst. Öffnet sich gar kein Browser, setzt du den Pfad zum Windows-Browser:

```bash
export BROWSER="/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
claude
```

Klappt das Einfügen im Prompt nicht, nimm `claude auth login`. Der Befehl liest den Code von der Standardeingabe. In Windows Terminal hilft oft auch Rechtsklick oder `Shift+Insert` zum Einfügen.

### Beispiel 6: Claude Code mit JetBrains unter WSL 2 verbinden

Wenn `/ide` die Meldung `No available IDEs detected` zeigt. Ursache ist meist das NAT-Netz von WSL 2 oder die Windows-Firewall. In WSL ermittelst du die Adresse mit `hostname -I` und leitest daraus das Subnetz ab (aus `172.21.123.45` wird `172.21.0.0/16`). Dann in einer Administrator-PowerShell:

```powershell
New-NetFirewallRule -DisplayName "Allow WSL2 Internal Traffic" -Direction Inbound -Protocol TCP -Action Allow -RemoteAddress 172.21.0.0/16 -LocalAddress 172.21.0.0/16
```

Unter Windows 11 22H2 oder neuer geht alternativ gespiegeltes Netzwerk in `%USERPROFILE%\.wslconfig`, danach `wsl --shutdown`:

```ini
[wsl2]
networkingMode=mirrored
```

Im JetBrains-Plugin trägst du als Claude command `wsl -d Ubuntu -- bash -lic "claude"` ein. Mehr dazu in [Claude Code in VS Code und JetBrains](./claude-code-vscode-jetbrains.md).

### Beispiel 7: PATH unter Windows reparieren

Wenn `claude` nach der Installation nicht gefunden wird.

```powershell
Test-Path "$env:USERPROFILE\.local\bin\claude.exe"
$currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
[Environment]::SetEnvironmentVariable('PATH', "$currentPath;$env:USERPROFILE\.local\bin", 'User')
```

Danach das Terminal neu starten. Läuft das Terminal in einem Editor, musst du den Editor neu starten, denn er vererbt seinen eigenen PATH.

## Schritt für Schritt: Claude Code unter Windows einrichten

1. **Variante wählen.** Natives Windows für Windows-Projekte, WSL 2 für Linux-Werkzeuge und Sandbox (Tabelle oben).
2. **Optional Git for Windows installieren.** Von [git-scm.com/downloads/win](https://git-scm.com/downloads/win), bei der Installation "Add to PATH" wählen und das Terminal neu starten.
3. **Die richtige PowerShell öffnen.** Im Startmenü `Windows PowerShell`, nicht `Windows PowerShell (x86)`. Die x86-Variante läuft als 32-Bit-Prozess und löst `Claude Code does not support 32-bit Windows` aus.
4. **Installer ausführen.** Beispiel 1 (PowerShell) oder Beispiel 2 (CMD, WinGet). Kein Administrator nötig.
5. **Neues Terminal öffnen und prüfen.** `claude --version` und `claude doctor`. Bei `'claude' is not recognized` hilft Beispiel 7.
6. **Projekt öffnen und anmelden.** `cd C:\pfad\zum\projekt`, dann `claude`, Anmeldung im Browser.
7. **Shell prüfen.** Frag Claude "Welche Shell nutzt du für Befehle?" oder sieh in `claude --debug` nach. Fehlt Git Bash, setze den Pfad wie in Beispiel 3.
8. **Projekt-Basis anlegen.** Mit `claude-team einrichten` bekommt das Repo CLAUDE.md, `.claude/settings.json` und Schutz-Hooks:

   ```powershell
   uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.2.0 claude-team einrichten . --dry-run
   ```

   Die Hooks der Vorlage starten mit `python3`. Prüfe unter Windows, dass `python3` im PATH liegt, sonst laufen sie nicht.

   Ohne Git Bash führt Claude Befehle über das PowerShell-Tool aus. Ein Hook mit `"matcher": "Bash"` greift dann nicht, deshalb steht in der Vorlage `"Bash|PowerShell"`. Eigene Hooks für Befehle brauchst du ebenso mit beiden Namen.

## Pfade unter Windows

| Was | Pfad |
| --- | --- |
| Programm (nativer Installer) | `%USERPROFILE%\.local\bin\claude.exe` |
| Versionen | `%USERPROFILE%\.local\share\claude` |
| Nutzer-Einstellungen | `%USERPROFILE%\.claude\settings.json` |
| Nutzer-Status, MCP-Server, Projekt-Vertrauen | `%USERPROFILE%\.claude.json` |
| Downloads des Installers | `%USERPROFILE%\.claude\downloads` |
| Managed Settings (Datei) | `C:\Program Files\ClaudeCode\managed-settings.json` und `managed-settings.d\` |
| Managed Settings (Registry) | `HKLM\SOFTWARE\Policies\ClaudeCode`, Wert `Settings` (REG_SZ oder REG_EXPAND_SZ, JSON) |
| Nutzer-Registry (kein Admin-Pfad) | `HKCU\SOFTWARE\Policies\ClaudeCode` |
| Daten der VS-Code-Extension | `%APPDATA%\Code\User\globalStorage\anthropic.claude-code` |

Den alten Pfad `C:\ProgramData\ClaudeCode\managed-settings.json` liest Claude Code nicht mehr. Der HKCU-Schlüssel ist vom Nutzer beschreibbar und zählt deshalb nicht als Administrator-Quelle: Claude Code nutzt ihn nur, wenn keine HKLM- oder Datei-Richtlinie vorhanden ist.

In JSON-Dateien schreibst du Backslashes doppelt (`C:\\Program Files\\Git\\bin\\bash.exe`).

## Managed Settings für Windows und WSL

Für eine Windows-Flotte verteilst du die Richtlinie per Intune, Group Policy oder ein anderes Werkzeug als Datei unter `C:\Program Files\ClaudeCode\` oder als HKLM-Wert. Ein Beispiel für `managed-settings.json`, das den Bypass-Modus sperrt, Telemetrie abschaltet und WSL dieselbe Richtlinie lesen lässt:

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  },
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1"
  },
  "wslInheritsWindowsSettings": true
}
```

WSL liest sonst nur `/etc/claude-code/managed-settings.json`, und dieser Ordner ist unter WSL vom Nutzer beschreibbar. Mit `wslInheritsWindowsSettings` (ab v2.1.282, nur aus HKLM oder einer Datei unter `C:\Program Files\ClaudeCode\`) gilt die Windows-Richtlinie auch in WSL. Auf nativem Windows hat der Key keine Wirkung.

Achtung bei Sandbox-Pflicht: Setzt die Richtlinie `sandbox.enabled` zusammen mit `sandbox.failIfUnavailable`, beendet sich Claude Code auf nativen Windows-Rechnern beim Start. Verteile die Sandbox-Einstellungen dann nur auf macOS- und Linux-Rechner oder lass Windows-Nutzer in WSL 2 oder einem Container arbeiten.

Projekt-Settings (`.claude/settings.json`) dürfen im `env`-Block einige Windows-Variablen nicht setzen, darunter `SystemRoot`, `ComSpec`, `ProgramData`, `LOCALAPPDATA`, `PATHEXT`, `PSModulePath` und die `ProgramFiles`-Familie. Claude Code verwirft sie und meldet das in `claude --debug`. Solche Werte gehören in die Shell, die Nutzer-Settings oder Managed Settings.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| CMD-Befehl in PowerShell | `The token '&&' is not a valid statement separator` | `irm https://claude.ai/install.ps1 \| iex` verwenden |
| PowerShell-Befehl in CMD | `'irm' is not recognized` | PowerShell öffnen oder den CMD-Befehl aus Beispiel 2 nehmen |
| Linux-Befehl in PowerShell | `A parameter cannot be found that matches parameter name 'fsSL'` oder `'bash' is not recognized` | Windows-Installer verwenden |
| 32-Bit-PowerShell | `Claude Code does not support 32-bit Windows` | `[Environment]::Is64BitOperatingSystem` prüfen; bei `True` die PowerShell ohne x86 öffnen |
| Datei gesperrt | `The process cannot access the file ... because it is being used by another process` | Andere Installer-Fenster schließen, Virenscan abwarten, `Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\downloads"`, Installer erneut starten |
| claude.exe nach Update weg | `'claude' is not recognized` direkt nach einem Update | Neueste `claude.exe.old.*` in `%USERPROFILE%\.local\bin` zurück in `claude.exe` umbenennen oder neu installieren |
| npm-Skripte gesperrt | `running scripts is disabled on this system` | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, `claude.cmd` nutzen oder den nativen Installer |
| Desktop-App statt CLI | `claude` öffnet die Desktop-App | Ältere Claude Desktop registriert ein `Claude.exe` in `WindowsApps`; Desktop-App aktualisieren |
| WSL 1 | `cannot execute binary file: Exec format error` | Distribution mit `wsl --set-version <DistroName> 2` auf WSL 2 umstellen |
| Windows-Node in WSL | `exec: node: not found` nach npm-Installation | `which node` zeigt `/mnt/c/...`; Node in WSL selbst installieren oder nativen Installer nutzen |
| Endpoint-Schutz blockt | Git Bash trotz korrektem Pfad nicht genutzt | AppLocker, Gruppenrichtlinie oder EDR prüfen; `claude.exe`, `cmd.exe` und `bash.exe` freigeben lassen |
| Firmen-Zertifikat | `CRYPT_E_NO_REVOCATION_CHECK` oder `SSL/TLS secure channel` | Siehe [TLS or SSL connection errors](https://code.claude.com/docs/en/troubleshoot-install#tls-or-ssl-connection-errors) |

## Häufige Fragen

### Brauche ich Administratorrechte für Claude Code unter Windows?

Nein, der native Installer läuft ohne Administratorrechte und installiert nach `%USERPROFILE%\.local\bin`. Administratorrechte brauchst du nur, um Managed Settings unter `C:\Program Files\ClaudeCode\` oder in HKLM abzulegen.

### Ist Git for Windows Pflicht?

Nein, Git for Windows ist optional. Ohne Git Bash führt Claude Code Befehle über das PowerShell-Tool aus. Mit Git Bash stehen das Bash-Tool und das Monitor-Tool zur Verfügung, was bei Bash-Skripten und Unix-Werkzeugen hilft.

### Gibt es die Sandbox unter Windows?

Nicht unter nativem Windows, dort laufen Shell-Befehle ohne Sandbox. Die Sandbox läuft in WSL 2 mit `bubblewrap` und `socat`. Unter WSL 1 meldet Claude Code `Sandboxing requires WSL2`. Alternativ isolierst du Claude Code in einem Devcontainer, siehe [Claude Code Sandbox](./claude-code-sandbox.md).

### Kann ich Claude Code in WSL und in Windows gleichzeitig nutzen?

Ja, das sind zwei getrennte Installationen mit eigenen Einstellungen: In WSL liegen sie unter `~/.claude` der Linux-Umgebung, unter Windows in `%USERPROFILE%\.claude`. Starte `claude` jeweils im passenden Terminal.

### Wie verteile ich Claude Code an viele Windows-Rechner?

Mit WinGet (`winget install Anthropic.ClaudeCode`) oder deiner Softwareverteilung, dazu eine `managed-settings.json` unter `C:\Program Files\ClaudeCode\` oder den HKLM-Wert `Settings`. `/status` zeigt in der Zeile `Setting sources`, ob die Richtlinie geladen wurde.

### Welche Windows-Version brauche ich?

Windows 10 ab Version 1809 oder Windows Server 2019 und neuer, jeweils 64 Bit, mit mindestens 4 GB RAM. Für gespiegeltes WSL-Netzwerk brauchst du Windows 11 22H2 oder neuer.

## Weiterlesen

- [Claude Code installieren: alle Wege](./claude-code-installieren.md)
- [Claude Code Sandbox: Devcontainer und Docker](./claude-code-sandbox.md)
- [Claude Code in VS Code und JetBrains](./claude-code-vscode-jetbrains.md)
- [Claude Code Enterprise: Managed Settings](./claude-code-enterprise.md)
- [Claude Code settings.json](./claude-code-settings-json.md)
- [Prüfregeln, z.B. CC012 zu bypassPermissions](../regeln.md#cc012)
- [Claude Code Tutorial auf Deutsch: die erste Stunde mit Claude Code](./claude-code-tutorial-deutsch.md)
- Offizielle Doku: [Set up on Windows](https://code.claude.com/docs/en/setup#set-up-on-windows), [Troubleshoot installation](https://code.claude.com/docs/en/troubleshoot-install), [Managed settings](https://code.claude.com/docs/en/managed-settings)
