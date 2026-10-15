# Claude Code Plugins: Marketplace einrichten und Plugins im Team verteilen

Ein Claude Code Plugin installierst du mit zwei Befehlen: zuerst den Marketplace bekannt machen (`claude plugin marketplace add owner/repo`), dann das Plugin installieren (`claude plugin install name@marketplace`). Einen eigenen Team-Marketplace betreibst du als Git-Repo mit einer Datei `.claude-plugin/marketplace.json`, die deine Plugins auflistet. Über `extraKnownMarketplaces` und `enabledPlugins` in `.claude/settings.json` bekommt jedes Teammitglied die Plugins automatisch angeboten.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Ein Plugin bündelt Skills, Subagents, Hooks, MCP-Server und weitere Bausteine in einem Ordner und lässt sich versioniert verteilen.
- Das Manifest `.claude-plugin/plugin.json` ist optional. Wenn es existiert, ist nur `name` Pflicht.
- Die Präfixe `claude-`, `anthropic-` und `cc-plugin-` sind für Plugin-Namen reserviert. Deshalb heißt das Plugin dieses Repos `team-basis`.
- Ein Marketplace ist ein Repo mit `.claude-plugin/marketplace.json`. Pflicht sind `name`, `owner` und `plugins`.
- Für die Organisation steuerst du mit `strictKnownMarketplaces` in Managed Settings, aus welchen Quellen Plugins kommen dürfen.
- `claude plugin validate --strict` gehört in die CI, damit kaputte Manifeste nicht im Team landen.

## Wie installiere ich ein Claude Code Plugin?

Im Terminal:

```bash
claude plugin marketplace add pexon-consulting/claude-code-best-practices
claude plugin install team-basis@claude-code-best-practices
```

In einer laufenden Sitzung geht dasselbe mit `/plugin marketplace add` und `/plugin install`, danach lädt `/reload-plugins` die Änderungen. `/plugin` öffnet die Übersicht. In `claude -p` gibt es `/plugin` nicht, dort nimmst du die Shell-Befehle.

`claude plugin install` installiert standardmäßig im Scope `user`. Mit `--scope project` landet der Eintrag in `.claude/settings.json` und gilt für alle im Repo, mit `--scope local` nur für dich in diesem Repo. Bei Konflikten gilt local vor project vor user.

## Die wichtigsten Plugin-Befehle

| Befehl | Zweck |
| --- | --- |
| `claude plugin marketplace add <quelle>` | Marketplace hinzufügen: `owner/repo`, `owner/repo#ref`, Git-URL, `./pfad` oder URL einer `marketplace.json` |
| `claude plugin marketplace list` | bekannte Marketplaces anzeigen |
| `claude plugin marketplace update [name]` | Marketplace aktualisieren |
| `claude plugin marketplace remove <name>` | Marketplace entfernen |
| `claude plugin install <name>@<marketplace>` | Plugin installieren, `--scope user\|project\|local` |
| `claude plugin install <name> --marketplace <quelle>` | Marketplace und Plugin in einem Schritt (ab v2.1.292) |
| `claude plugin list` | installierte Plugins |
| `claude plugin enable` / `disable` | Plugin ein- oder ausschalten |
| `claude plugin update <name>@<marketplace>` | ein Plugin aktualisieren, wirkt nach Neustart |
| `claude plugin uninstall` | Plugin entfernen |
| `claude plugin details <name>` | Bestandteile eines Plugins und geschätzte Token-Kosten |
| `claude plugin validate <pfad> [--strict]` | Manifest und Frontmatter prüfen |
| `claude plugin init <name>` | neues Plugin unter `~/.claude/skills/<name>/` anlegen, lädt ab der nächsten Sitzung |
| `claude --plugin-dir ./mein-plugin` | Plugin für eine Sitzung lokal laden, zum Entwickeln |

## Wie ist ein Plugin aufgebaut?

Nur das Manifest liegt in `.claude-plugin/`. Alle anderen Ordner liegen im Plugin-Root.

```text
team-basis/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── commit/SKILL.md
│   └── handoff/SKILL.md
├── agents/
│   └── code-reviewer.md
├── hooks/
│   └── hooks.json
├── scripts/
│   └── secrets_schutz.py
└── .mcp.json
```

| Baustein | Ort |
| --- | --- |
| Manifest | `.claude-plugin/plugin.json` |
| Skills | `skills/<name>/SKILL.md` |
| Commands (alt, Skills bevorzugen) | `commands/*.md` |
| Subagents | `agents/*.md` |
| Hooks | `hooks/hooks.json` |
| MCP-Server | `.mcp.json` |
| LSP-Server | `.lsp.json` |
| Output Styles | `output-styles/` |
| Programme im PATH des Bash-Tools | `bin/` |
| Einstellungen | `settings.json` (nur `agent` und `subagentStatusLine` wirken) |

Eine `CLAUDE.md` im Plugin-Root lädt Claude Code nicht als Kontext. Skills aus Plugins rufst du mit Präfix auf, z.B. `/team-basis:commit`. Subagents aus Plugins ignorieren `hooks`, `mcpServers` und `permissionMode` im Frontmatter.

## plugin.json: die Felder

| Feld | Pflicht | Bedeutung |
| --- | --- | --- |
| `name` | ja | kebab-case, keine Leerzeichen, kein `@` oder `:`, nicht mit `claude-`, `anthropic-` oder `cc-plugin-` beginnen |
| `version` | nein | Versionsnummer |
| `description` | nein | kurze Beschreibung |
| `author` | nein | Objekt, darin `name` Pflicht, dazu `email` und `url` |
| `homepage`, `repository`, `license`, `keywords` | nein | Metadaten |
| `displayName` | nein | Anzeigename |
| `defaultEnabled` | nein | ob das Plugin aktiv startet, solange der Nutzer nichts festlegt, Standard `true` |
| `dependencies` | nein | andere Plugins, die mitgebraucht werden |
| `userConfig` | nein | Werte, die Claude Code beim Aktivieren abfragt |
| `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles` | nein | abweichende Pfade oder Inline-Definitionen |

## Pfade im Plugin: ${CLAUDE_PLUGIN_ROOT}

| Variable | Wert |
| --- | --- |
| `${CLAUDE_PLUGIN_ROOT}` | Ordner der installierten Plugin-Version, ändert sich bei jedem Update, nicht hineinschreiben |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/<id>/`, bleibt bei Updates erhalten |
| `${CLAUDE_PROJECT_DIR}` | Projektordner |

In Hook-Befehlen setzt du die Variable in Anführungszeichen, weil Pfade Leerzeichen enthalten können: `"\"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.sh"`.

## Beispiele

### Beispiel 1: plugin.json für ein Team-Plugin

```json
{
  "name": "team-basis",
  "version": "0.1.0",
  "description": "Schutz-Hooks, Commit- und Handoff-Skill und ein Review-Agent für alle Repos im Team",
  "author": { "name": "Plattform-Team", "email": "plattform@example.com" },
  "license": "MIT",
  "keywords": ["hooks", "skills", "review"]
}
```

### Beispiel 2: Hooks im Plugin

`hooks/hooks.json` hat dasselbe Format wie der Block `hooks` in der [settings.json](./claude-code-settings-json.md), mit einem äußeren Schlüssel `hooks`.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Write|Bash",
        "hooks": [
          { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}\"/scripts/secrets_schutz.py", "timeout": 10 }
        ]
      }
    ]
  }
}
```

Wie solche Hooks aufgebaut sind, zeigt die Anleitung zu [Claude Code Hooks](./claude-code-hooks.md).

### Beispiel 3: eigener Team-Marketplace

Die Datei `.claude-plugin/marketplace.json` in einem Repo deiner Organisation. Ein Plugin liegt im selben Repo, ein zweites kommt aus einem eigenen Repo mit fester Version.

```json
{
  "name": "team-plugins",
  "owner": { "name": "Plattform-Team", "email": "plattform@example.com" },
  "description": "Freigegebene Claude-Code-Plugins für alle Teams",
  "plugins": [
    {
      "name": "team-basis",
      "source": "./plugins/team-basis",
      "description": "Schutz-Hooks und Basis-Skills"
    },
    {
      "name": "formatter",
      "source": { "source": "github", "repo": "your-org/formatter", "ref": "v2.0.0" },
      "description": "Formatiert Dateien nach jeder Änderung"
    }
  ]
}
```

Als Quelle gehen außerdem `url`, `git-subdir`, `npm`, `archive` (ab v2.1.224) und `command` (ab v2.1.229). Die Namen `claude-plugins-official`, `claude-code-plugins` und weitere offizielle Namen sind für Marketplaces reserviert.

### Beispiel 4: Plugins im Repo vorgeben

In `.claude/settings.json` des Projekts. Wer das Repo öffnet und dem Ordner vertraut, bekommt den Marketplace registriert und das Plugin angeboten.

```json
{
  "extraKnownMarketplaces": {
    "team-plugins": {
      "source": { "source": "github", "repo": "your-org/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "team-basis@team-plugins": true
  }
}
```

Zwei Einschränkungen: `extraKnownMarketplaces` greift nur in vertrauten Ordnern, in nicht vertrauten ignoriert Claude Code den Eintrag ohne Meldung. Und Plugins, die im Marketplace auf eine externe Quelle zeigen, muss jeder einmal selbst installieren: `claude plugin install <name>@<marketplace> --scope project`. Plugins mit relativem Pfad im Marketplace-Repo laden direkt.

### Beispiel 5: Quellen für die ganze Organisation festlegen

In den Managed Settings. Erlaubt sind nur der offizielle Marketplace, alle Repos deiner GitHub-Organisation (Wildcard ab v2.1.223) und Skills aus `.claude/skills/`. `disableSideloadFlags` sperrt zusätzlich `--plugin-dir`.

```json
{
  "strictKnownMarketplaces": [
    { "source": "github", "repo": "anthropics/claude-plugins-official" },
    { "source": "github", "repo": "your-org/*" },
    { "source": "skills-dir" }
  ],
  "extraKnownMarketplaces": {
    "team-plugins": {
      "source": { "source": "github", "repo": "your-org/claude-plugins" }
    }
  },
  "enabledPlugins": {
    "team-basis@team-plugins": true
  },
  "disableSideloadFlags": true
}
```

Eine leere Liste `"strictKnownMarketplaces": []` sperrt alle Quellen, auch den offiziellen Marketplace. Die Allowlist registriert selbst nichts, dafür braucht es den Eintrag in `extraKnownMarketplaces`. Eine Vorlage für Managed Settings liegt unter [vorlagen/managed-settings.json](../../vorlagen/managed-settings.json).

### Beispiel 6: Plugin in der CI prüfen

Ein GitHub-Actions-Job, der Marketplace und Plugin bei jedem Pull Request validiert. `--strict` lässt den Job auch bei Warnungen scheitern.

```yaml
name: plugins-validieren
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g @anthropic-ai/claude-code@2.1.294
      - run: claude plugin validate . --strict
      - run: claude plugin validate ./plugins/team-basis --strict
```

Lokal meldet ein gültiges Plugin `✔ Validation passed` und endet mit Exit-Code 0.

## Schritt für Schritt: eigenes Team-Plugin veröffentlichen

1. Repo `your-org/claude-plugins` anlegen.
2. Plugin-Ordner `plugins/team-basis/` mit `.claude-plugin/plugin.json` und den Bausteinen anlegen, siehe Beispiel 1 und 2.
3. Lokal testen: `claude --plugin-dir ./plugins/team-basis`, dann `/team-basis:commit` aufrufen.
4. `.claude-plugin/marketplace.json` im Repo-Root schreiben, siehe Beispiel 3.
5. Beides prüfen: `claude plugin validate . --strict` und `claude plugin validate ./plugins/team-basis --strict`.
6. CI-Job aus Beispiel 6 einrichten, dann pushen.
7. Selbst testen: `claude plugin marketplace add your-org/claude-plugins` und `claude plugin install team-basis@team-plugins`.
8. In den Projekt-Repos `extraKnownMarketplaces` und `enabledPlugins` eintragen (Beispiel 4) oder organisationsweit über Managed Settings (Beispiel 5).
9. Kontrolle: in einer neuen Sitzung `/plugin` öffnen. In der CI zeigt `claude -p --output-format stream-json --verbose` die geladenen Plugins im `init`-Ereignis.

## Sicherheit

- Ein Plugin kann Hooks und MCP-Server mitbringen, die auf deinem Rechner Befehle ausführen. Installiere nur Plugins aus Quellen, deren Code du prüfen kannst.
- Feste Versionen (`ref` auf einen Tag) machen Updates nachvollziehbar.
- Für private Marketplace-Repos braucht jeder Nutzer Lesezugriff. In der CI richtest du einen Git-Credential-Helper ein, auf GitHub Actions z.B. mit `GH_TOKEN` und `gh auth setup-git`.
- `strictPluginOnlyCustomization` in Managed Settings lässt Skills, Subagents, Hooks und MCP-Server nur noch aus Plugins, Managed Settings und den eingebauten Quellen zu.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Plugin-Name mit `claude-` | Validierung schlägt fehl | anderen Namen wählen, z.B. `team-basis` |
| Skills in `.claude-plugin/skills/` | Skills fehlen | nur `plugin.json` gehört in `.claude-plugin/` |
| `CLAUDE.md` im Plugin | Anweisungen wirken nicht | Inhalt in einen Skill verschieben |
| externe Quelle im Marketplace | `Plugin "<name>" is enabled in project settings but isn't installed` | `claude plugin install <name>@<marketplace> --scope project` |
| Ordner nicht vertraut | Marketplace erscheint nicht | Workspace-Trust bestätigen |
| in `${CLAUDE_PLUGIN_ROOT}` gespeichert | Daten nach Update weg | `${CLAUDE_PLUGIN_DATA}` nutzen |
| `/plugin` in `claude -p` | Befehl unbekannt | `claude plugin ...` in der Shell |

## Häufige Fragen

### Was ist der Unterschied zwischen einem Plugin und einem Skill?

Ein Skill ist eine einzelne Fähigkeit mit `SKILL.md`. Ein Plugin ist ein Paket, das mehrere Skills, Subagents, Hooks und MCP-Server zusammen ausliefert und über einen Marketplace versioniert verteilt wird.

### Brauche ich eine plugin.json?

Nein, das Manifest ist optional. Ohne Manifest nimmt Claude Code die Standardordner. Für Name, Version und Beschreibung im Marketplace solltest du es trotzdem anlegen.

### Wie aktualisiere ich ein Plugin?

Mit `claude plugin update <name>@<marketplace>` oder in der Sitzung über `/plugin`, Reiter Installed, Update now. Einen Befehl für alle Plugins auf einmal gibt es nicht. Über den Reiter Marketplaces aktualisierst du alle Plugins eines Marketplace zusammen.

### Kann ich Plugins für alle Mitarbeitenden erzwingen?

Ja. In den Managed Settings setzt `enabledPlugins` mit `true` ein Plugin auf allen Rechnern aktiv. Mit `false` sperrst du es in jedem Scope und blendest es aus.

### Wie installiere ich das Plugin dieses Repos?

`claude plugin marketplace add pexon-consulting/claude-code-best-practices` und danach `claude plugin install team-basis@claude-code-best-practices`. Es bringt die Schutz-Hooks und Skills aus der Vorlage mit.

## Weiterlesen

- [Claude Code Skills](./claude-code-skills.md): Skills schreiben, die ein Plugin ausliefert
- [Claude Code Subagents](./claude-code-subagents.md): Agenten für das Plugin
- [Claude Code Hooks](./claude-code-hooks.md): Schutz-Hooks im Plugin
- [Claude Code MCP](./claude-code-mcp.md): MCP-Server im Plugin
- [Claude Code Enterprise](./claude-code-enterprise.md): Managed Settings für die Organisation
- Offizielle Doku: [Plugins](https://code.claude.com/docs/en/plugins/overview), [Marketplace-Referenz](https://code.claude.com/docs/en/plugins/marketplace-reference), [Plugins in der Organisation](https://code.claude.com/docs/en/plugins/org)
