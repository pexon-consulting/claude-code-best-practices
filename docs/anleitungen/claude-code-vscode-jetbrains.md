# Claude Code VS Code und JetBrains: IDE-Integration einrichten

Claude Code verbindest du mit VS Code über die Extension `anthropic.claude-code` aus dem Marketplace (ab VS Code 1.94.0). Sie bringt eine eigene Kopie der CLI mit und öffnet Claude in einem Panel. Für IntelliJ, PyCharm, WebStorm und andere JetBrains-IDEs installierst du die CLI und das Plugin "Claude Code [Beta]" aus dem JetBrains Marketplace und startest `claude` im Terminal der IDE. Aus einem externen Terminal verbindest du dich in beiden Fällen mit `/ide`.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- VS Code: Extension installieren, Spark-Icon oben rechts im Editor klicken, anmelden. Die CLI im PATH brauchst du dafür nicht.
- JetBrains: Das Plugin startet `claude` im integrierten Terminal und bringt keine eigene CLI mit. Ohne `claude` im PATH erscheint "Cannot launch Claude Code".
- Beide nutzen `~/.claude/settings.json` gemeinsam mit der CLI, deine Regeln, Hooks und MCP-Server gelten also überall.
- Die IDE teilt Auswahl, offene Datei und Diagnosen über einen lokalen MCP-Server namens `ide`. Eine `Read`-deny-Regel hält zum Beispiel `.env` aus diesem Kontext heraus.
- Für Bedrock, Agent Platform, Foundry oder ein LLM-Gateway schaltest du in VS Code "Disable Login Prompt" ein.

## VS Code oder JetBrains: was ist anders?

| Punkt | VS Code (Extension) | JetBrains (Plugin) |
| --- | --- | --- |
| Oberfläche | grafisches Panel, optional Terminal-Modus | CLI im integrierten Terminal |
| CLI nötig | nein, die Extension bringt eine eigene Kopie mit | ja, `claude` muss im PATH liegen |
| Version | Extension-Version = gebündelte CLI-Version | eigene CLI-Installation |
| Öffnen | `Cmd+Esc` (Mac) / `Ctrl+Esc` (Windows, Linux) | `Cmd+Esc` (Mac) / `Ctrl+Esc` (Windows, Linux) |
| Dateiverweis einfügen | `Option+K` / `Alt+K` | `Cmd+Option+K` / `Alt+Ctrl+K` |
| Diffs | eigener Diff-Viewer mit Annahme je Änderung (ab v2.1.275) | Diff-Viewer der IDE, umschaltbar mit `/config` |
| Werkzeuge für das Modell | `mcp__ide__getDiagnostics`, `mcp__ide__executeCode` (Jupyter) | nur `mcp__ide__getDiagnostics` |
| Andere Editoren | Cursor, Devin Desktop, Kiro über Open VSX | IntelliJ IDEA, PyCharm, Android Studio, WebStorm, PhpStorm, GoLand |

Die VS-Code-Extension kann nicht alles, was die CLI kann: Sie bietet nur einen Teil der Befehle und Skills, keinen `!`-Shortcut für Bash und keine Tab-Vervollständigung. Checkpoints und `/mcp` gibt es auch im Panel. Brauchst du eine reine CLI-Funktion, startest du `claude` im integrierten Terminal; dafür musst du die CLI einmal [separat installieren](./claude-code-installieren.md).

## Beispiele für VS Code und JetBrains

### Beispiel 1: VS-Code-Extension installieren

In VS Code öffnest du mit `Cmd+Shift+X` (Mac) oder `Ctrl+Shift+X` (Windows, Linux) die Extensions-Ansicht, suchst nach "Claude Code" und klickst auf Install. Direkt installieren geht über diese Links:

```text
vscode:extension/anthropic.claude-code
cursor:extension/anthropic.claude-code
```

Die Marketplace-Seite ist [marketplace.visualstudio.com](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code). Die Versionsnummer der Extension ist die Version der mitgelieferten CLI: Braucht eine Funktion v2.1.286, brauchst du Extension 2.1.286 oder neuer. Für andere VS-Code-Ableger gibt es die Extension in der [Open VSX Registry](https://open-vsx.org/extension/Anthropic/claude-code). Danach das Spark-Icon in der Editor-Leiste oben rechts anklicken. Es erscheint nur, wenn eine Datei offen ist.

### Beispiel 2: JetBrains-Plugin mit der CLI verbinden

Zuerst die CLI installieren und prüfen:

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version
```

Dann das Plugin [Claude Code [Beta]](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-) installieren und die IDE neu starten. Im Terminal der IDE im Projektordner:

```bash
claude
```

Alle Funktionen sind dann aktiv. Findet die IDE `claude` nicht, trägst du unter **Settings → Tools → Claude Code [Beta]** im Feld "Claude command" den vollen Pfad ein, zum Beispiel `/usr/local/bin/claude`. Unter WSL lautet der Eintrag `wsl -d Ubuntu -- bash -lic "claude"`.

### Beispiel 3: Aus einem externen Terminal verbinden

Wenn du Claude Code lieber in iTerm, Windows Terminal oder einem anderen Terminal nutzt:

```bash
cd /pfad/zum/projekt
claude
```

```text
/ide
```

Bei Erfolg meldet Claude Code etwa `Connected to IntelliJ IDEA.` Findet `/ide` eine laufende JetBrains-IDE ohne Plugin, installiert es das Plugin und bittet um einen Neustart der IDE. Starte Claude Code im selben Ordner wie das IDE-Projekt, damit beide dieselben Dateien sehen.

### Beispiel 4: .env und IDE-Diagnosen aus dem Kontext halten

Die IDE schickt bei jedem Prompt die markierten Zeilen und den Pfad der offenen Datei mit. Eine `Read`-deny-Regel verhindert das für sensible Dateien. Die Diagnose-Werkzeuge deckt sie nicht ab, die sperrst du mit Namen:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "mcp__ide__getDiagnostics",
      "mcp__claude-vscode__getDiagnostics"
    ]
  }
}
```

`mcp__claude-vscode__getDiagnostics` ist der Name, unter dem Hooks und Regeln das Diagnose-Werkzeug des VS-Code-Panels sehen. Für CLI und Panel nennst du beide Namen. Die `.env`-Regeln entsprechen der Prüfregel [CC013](../regeln.md#cc013).

### Beispiel 5: Extension-Einstellungen in VS Code

In den VS-Code-Nutzereinstellungen (`settings.json` von VS Code, nicht von Claude Code):

```json
{
  "claudeCode.preferredLocation": "sidebar",
  "claudeCode.autosave": true,
  "claudeCode.respectGitIgnore": true,
  "claudeCode.allowDangerouslySkipPermissions": false
}
```

`initialPermissionMode` liest VS Code nur aus den Nutzereinstellungen, Werte im Workspace ignoriert es. `allowDangerouslySkipPermissions` fügt den Bypass-Modus zur Auswahl hinzu; laut Doku nur in Sandboxes ohne Internet nutzen.

### Beispiel 6: VS Code über ein LLM-Gateway oder einen Cloud-Anbieter

Die Extension prüft Zugangsdaten vor dem Start nur aus ihrer eigenen Einstellung. Für ein Gateway trägst du die Variablen in die VS-Code-Nutzereinstellungen ein (Befehl "Preferences: Open User Settings (JSON)"):

```json
{
  "claudeCode.disableLoginPrompt": true,
  "claudeCode.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL", "value": "https://llm-gateway.example.com" },
    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "<dein-gateway-token>" }
  ]
}
```

Für Bedrock, Agent Platform oder Foundry reicht "Disable Login Prompt", die Anbieter-Variablen gehören dann in den `env`-Block von `~/.claude/settings.json`. Siehe [Bedrock](./claude-code-bedrock.md), [Vertex AI](./claude-code-vertex-ai.md), [Microsoft Foundry (Azure)](./claude-code-azure-foundry.md) und [LLM-Gateway](./claude-code-llm-gateway.md).

### Beispiel 7: Claude aus einem Link heraus öffnen

Die Extension reagiert auf `vscode://`-Links, zum Beispiel aus einer README oder einem Ticket:

```text
vscode://anthropic.claude-code/open?prompt=Erkl%C3%A4re%20die%20Projektstruktur
```

Der Prompt muss URL-kodiert sein. Er wird vorausgefüllt, aber nicht abgeschickt. GitHub zeigt solche Links nur als Text, deshalb stehen sie hier im Codeblock.

### Beispiel 8: Extension dauerhaft entfernen

Startest du `claude` im VS-Code-Terminal, installiert Claude Code die Extension neu. Zum dauerhaften Entfernen in `~/.claude/settings.json`:

```json
{
  "autoInstallIdeExtension": false
}
```

Alternativ setzt du `CLAUDE_CODE_IDE_SKIP_AUTO_INSTALL=1`. Die gespeicherten Extension-Daten löschst du je nach System:

```bash
# macOS
rm -rf ~/Library/"Application Support"/Code/User/globalStorage/anthropic.claude-code
# Linux
rm -rf ~/.config/Code/User/globalStorage/anthropic.claude-code
```

Unter Windows: `Remove-Item -Recurse -Force "$env:APPDATA\Code\User\globalStorage\anthropic.claude-code"`.

## Schritt für Schritt: IDE-Integration für ein Team

1. **IDE-Version prüfen.** VS Code 1.94.0 oder neuer (Help → About), bei JetBrains eine der unterstützten IDEs.
2. **Installieren.** VS Code: Beispiel 1. JetBrains: CLI und Plugin wie in Beispiel 2.
3. **Anmelden.** Beim ersten Öffnen fragt Claude Code nach dem Login. Ist `ANTHROPIC_API_KEY` in deiner Shell gesetzt, die IDE zeigt aber trotzdem den Login, hat sie deine Umgebung nicht geerbt: VS Code mit `code .` aus dem Terminal starten.
4. **Gemeinsame Einstellungen ins Repo.** `.claude/settings.json` mit deny-Regeln wie in Beispiel 4 gilt für CLI, VS Code und JetBrains gleich. Mit `"$schema": "https://json.schemastore.org/claude-code-settings.json"` bekommst du in VS Code Autovervollständigung.
5. **Berechtigungsmodus wählen.** Ab v2.1.283 startet die VS-Code-Extension standardmäßig im Modus Auto. In fremden Repos ist Manual sicherer, siehe unten.
6. **Diff-Ansicht einstellen.** In JetBrains in `/config` den Eintrag Diff tool auf `auto` (IDE) oder `terminal` setzen. Der Eintrag erscheint nur, wenn Claude Code mit der IDE verbunden ist.
7. **Remote Development beachten.** Bei JetBrains Remote Development installierst du das Plugin auf dem Remote-Host unter **Settings → Plugin (Host)**, nicht auf dem lokalen Rechner.
8. **Prüfen.** `claude-team audit .` meldet fehlende deny-Regeln und einen ungesperrten Bypass-Modus ([CC012](../regeln.md#cc012)).

## Sicherheit in der IDE

Beide Integrationen starten einen lokalen MCP-Server namens `ide`, mit dem sich die CLI automatisch verbindet. Er ist in `/mcp` ausgeblendet. Die Verbindung läuft unverschlüsselt über `ws://` auf `127.0.0.1` mit einem zufälligen Port; das Token liegt in einer Lock-Datei unter `~/.claude/ide/`. Wer eine `PreToolUse`-Hook-Allowlist für MCP-Werkzeuge pflegt, muss die `ide`-Werkzeuge kennen.

- **Jupyter in VS Code.** `mcp__ide__executeCode` fügt Code als neue Zelle ein und fragt jedes Mal per Quick Pick nach "Execute" oder "Cancel". Ein Allow-Eintrag erlaubt nur den Vorschlag, nicht die Ausführung.
- **IDE-Konfigurationsdateien.** Im Modus `acceptEdits` oder Auto darf Claude Dateien wie `.vscode/settings.json` oder `tasks.json` ändern, die die IDE selbst ausführen kann. Für fremden Code nimm den Modus Manual und in VS Code den Restricted Mode.
- **Netzwerk in JetBrains.** Die Option "Accept connections from all network interfaces" unter Networking (Advanced) macht den Port im lokalen Netz erreichbar, der Datenverkehr bleibt unverschlüsselt. Lass sie aus.
- **Selection Context.** VS Code schickt keinen markierten Text aus Dateien, die unter `files.exclude`, `search.exclude` oder `.gitignore` fallen, nur den Pfad. Verlass dich für Secrets trotzdem auf `Read`-deny-Regeln.

Mehr dazu in [Claude Code Sicherheit](./claude-code-sicherheit.md) und [Claude Code Permissions](./claude-code-permissions.md).

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Kein Spark-Icon | Icon fehlt in der Editor-Leiste | Eine Datei öffnen, VS Code-Version prüfen (1.94.0+), Extension aktiviert? |
| Tastenkürzel belegt | `Cmd+Esc` tut nichts auf macOS | Ab macOS Tahoe belegt das Game Overlay die Tasten; in den Systemeinstellungen abschalten |
| CLI fehlt für JetBrains | "Cannot launch Claude Code" oder "command not found" | CLI installieren, `claude --version` prüfen, Pfad im Feld "Claude command" eintragen |
| IDE nicht erkannt | `/ide` meldet "No available IDEs detected" | Plugin aktiv? IDE ganz neu starten; unter WSL 2 Firewall-Regel oder gespiegeltes Netzwerk, siehe [Claude Code unter Windows](./claude-code-windows.md) |
| ESC unterbricht nicht | ESC springt in JetBrains in den Editor | **Settings → Tools → Terminal**, "Move focus to the editor with Escape" abschalten |
| Login trotz API-Key | VS Code fragt nach Anmeldung | VS Code hat die Shell-Umgebung nicht geerbt; mit `code .` starten |
| `claude` im Terminal fehlt | Nach Installation der Extension gibt es kein `claude` | Die Extension legt `claude` nicht in den PATH; CLI separat installieren |
| Gateway in VS Code ignoriert | Login-Abfrage trotz `ANTHROPIC_BASE_URL` | Variablen in `claudeCode.environmentVariables` statt nur in `~/.claude/settings.json` |

## Häufige Fragen

### Funktioniert Claude Code in IntelliJ IDEA?

Ja, über das Plugin "Claude Code [Beta]" aus dem JetBrains Marketplace. Es funktioniert auch mit PyCharm, Android Studio, WebStorm, PhpStorm und GoLand. Die CLI musst du separat installieren, das Plugin startet `claude` im Terminal der IDE.

### Funktioniert die VS-Code-Extension auch in Cursor?

Ja. Die Extension läuft in Cursor und anderen VS-Code-Ablegern wie Devin Desktop oder Kiro. Für Cursor gibt es den Link `cursor:extension/anthropic.claude-code`, für andere Editoren die Open VSX Registry.

### Brauche ich für die VS-Code-Extension die CLI?

Nein, die Extension bringt eine eigene Kopie der CLI mit, deren Version der Extension-Version entspricht. Sie legt `claude` aber nicht in den PATH. Für `claude` im Terminal, `claude mcp add` oder JetBrains installierst du die CLI separat.

### Gelten meine CLAUDE.md und settings.json auch in der IDE?

Ja. Extension und Plugin nutzen dieselben Dateien wie die CLI: `~/.claude/settings.json`, die `.claude/settings.json` im Projekt und die CLAUDE.md. Gespräche aus der Extension kannst du in der CLI mit `claude --resume` fortsetzen.

### Wie verhindere ich, dass die IDE Secrets an Claude schickt?

Mit `Read`-deny-Regeln für die Pfade, etwa `Read(./.env)`. Eine passende Regel blockt sowohl den markierten Text als auch den Hinweis auf die offene Datei. Die Diagnose-Werkzeuge sperrst du zusätzlich mit Namen, wie in Beispiel 4.

### Geht die IDE-Integration mit Bedrock oder einem Gateway?

Ja. In VS Code schaltest du "Disable Login Prompt" ein und richtest den Anbieter in `~/.claude/settings.json` ein, ein Gateway zusätzlich über `claudeCode.environmentVariables`. Funktionen, die ein claude.ai-Konto brauchen, etwa Nutzungsbalken, Spracheingabe und Cloud-Sitzungen, fehlen dann.

## Weiterlesen

- [Claude Code installieren](./claude-code-installieren.md)
- [Claude Code unter Windows](./claude-code-windows.md)
- [Claude Code Permissions](./claude-code-permissions.md)
- [Claude Code settings.json](./claude-code-settings-json.md)
- [Claude Code MCP-Server](./claude-code-mcp.md)
- [Vorlage `.claude/settings.json`](../../src/claude_team/vorlage/.claude/settings.json)
- [Claude Code Tutorial auf Deutsch: die erste Stunde mit Claude Code](./claude-code-tutorial-deutsch.md)
- Offizielle Doku: [VS Code](https://code.claude.com/docs/en/vs-code), [JetBrains IDEs](https://code.claude.com/docs/en/jetbrains)
