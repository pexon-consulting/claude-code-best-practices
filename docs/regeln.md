# Prüfregeln von claude-team audit (CC001 bis CC051)

> Stand: 15.10.2026, geprüft gegen Claude Code 2.1.294 und die offizielle Doku unter [code.claude.com/docs](https://code.claude.com/docs/en/overview).

`claude-team audit` prüft ein Repository auf 36 Regeln in sieben Bereichen: CLAUDE.md, settings.json, Hooks, Secrets, MCP, Subagents und Skills, Git. Jede Regel hat eine feste ID. Die Meldungen im Terminal, im Markdown- und im SARIF-Bericht verlinken direkt auf den Abschnitt hier.

```bash
claude-team audit .                      # Text, Exit 1 bei Fehlern
claude-team audit . --schwelle warnung   # Exit 1 schon bei Warnungen
claude-team audit . --ignorieren CC019,CC020
claude-team regeln                       # alle Regeln als Liste
```

**Stufen:** `fehler` heißt, etwas ist kaputt oder ein Sicherheitsloch. `warnung` heißt, es funktioniert, ist aber riskant oder wirkungslos. `hinweis` ist eine Empfehlung. Standard-Schwelle für den Exit-Code ist `fehler`.

## Übersicht

| ID | Stufe | Titel |
| --- | --- | --- |
| [CC001](#cc001) | warnung | Keine CLAUDE.md und keine AGENTS.md |
| [CC002](#cc002) | warnung | CLAUDE.md über 200 Zeilen |
| [CC003](#cc003) | hinweis | CLAUDE.md nennt keine Befehle |
| [CC004](#cc004) | fehler | @-Import zeigt auf fehlende Datei |
| [CC005](#cc005) | fehler | CLAUDE.local.md nicht in .gitignore |
| [CC006](#cc006) | hinweis | AGENTS.md wird neben CLAUDE.md nicht gelesen |
| [CC007](#cc007) | hinweis | Platzhalter {{...}} in CLAUDE.md nicht ausgefüllt |
| [CC010](#cc010) | fehler | settings.json ist kein gültiges JSON |
| [CC011](#cc011) | fehler | settings.local.json im Repo |
| [CC012](#cc012) | fehler | bypassPermissions als Standard oder nicht gesperrt |
| [CC013](#cc013) | fehler | Keine deny-Regel für .env |
| [CC014](#cc014) | warnung | Keine deny-Regel für Schlüsseldateien |
| [CC015](#cc015) | warnung | allow-Regel gibt zu viel frei |
| [CC016](#cc016) | warnung | Stern vor dem Unterbefehl |
| [CC017](#cc017) | warnung | Regel wird von Claude Code ignoriert |
| [CC018](#cc018) | warnung | Alle MCP-Server aus .mcp.json automatisch freigegeben |
| [CC019](#cc019) | hinweis | Telemetrie nicht abgeschaltet |
| [CC020](#cc020) | hinweis | Keine Hooks konfiguriert |
| [CC021](#cc021) | fehler | Hook-Skript fehlt |
| [CC022](#cc022) | fehler | Hook-Skript nicht ausführbar |
| [CC023](#cc023) | warnung | Hook mit relativem Pfad |
| [CC024](#cc024) | warnung | Unbekanntes Hook-Ereignis |
| [CC030](#cc030) | fehler | Zugangsschlüssel in einer Claude-Datei |
| [CC031](#cc031) | fehler | .mcp.json ist kein gültiges JSON |
| [CC032](#cc032) | fehler | Token im Klartext in .mcp.json |
| [CC033](#cc033) | warnung | MCP-Server ohne feste Version |
| [CC034](#cc034) | fehler | MCP-Server mit url, aber ohne type |
| [CC035](#cc035) | hinweis | MCP-Transport sse ist veraltet |
| [CC036](#cc036) | fehler | Geschützte Variable in Remote-MCP |
| [CC040](#cc040) | fehler | Subagent ohne name oder description |
| [CC041](#cc041) | fehler | Subagent mit bypassPermissions |
| [CC042](#cc042) | warnung | Skill ohne description |
| [CC043](#cc043) | hinweis | SKILL.md über 500 Zeilen |
| [CC044](#cc044) | hinweis | Subagent ohne tools-Liste |
| [CC050](#cc050) | fehler | .env im Repo oder nicht ignoriert |
| [CC051](#cc051) | warnung | Hook-Protokoll nicht ignoriert |

---

## CLAUDE.md

<a id="cc001"></a>
### CC001: Keine CLAUDE.md und keine AGENTS.md

**Stufe:** warnung

Ohne CLAUDE.md startet jede Sitzung ohne Projektwissen. Claude rät dann Testbefehle, Ordnerstruktur und Konventionen und liegt dabei oft daneben. Claude Code lädt `CLAUDE.md` und `.claude/CLAUDE.md` im Projekt automatisch. `AGENTS.md` liest es nur, wenn keine CLAUDE.md existiert.

**Lösung:** `claude-team einrichten` legt eine Vorlage mit erkannten Befehlen an. Alternativ `/init` in Claude Code. Anleitung: [CLAUDE.md schreiben](anleitungen/claude-md.md).

<a id="cc002"></a>
### CC002: CLAUDE.md über 200 Zeilen

**Stufe:** warnung

Anthropic empfiehlt, jede CLAUDE.md unter 200 Zeilen zu halten. Die Datei landet in jeder Sitzung vollständig im Kontext. Lange Dateien kosten Tokens und verwässern die Regeln, die wirklich zählen.

**Lösung:** Bereichsregeln nach `.claude/rules/` verschieben und mit `paths` nur für passende Dateien laden:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API-Regeln
- Jeder Endpunkt validiert die Eingabe mit zod.
```

Anleitung: [Claude Code Rules](anleitungen/claude-code-rules.md).

<a id="cc003"></a>
### CC003: CLAUDE.md nennt keine Befehle

**Stufe:** hinweis

Die wichtigste Information für einen Coding-Agent ist, wie er baut, testet und lintet. Fehlt das, probiert Claude Befehle aus oder lässt Tests weg. Die Regel sucht nach typischen Werkzeugen wie `npm`, `pytest`, `make`, `cargo` oder `go` am Zeilenanfang, in Listen oder in Backticks.

**Lösung:**

```markdown
## Befehle
- Installieren: `pnpm install`
- Tests: `pnpm test` (einzeln: `pnpm test -- src/auth`)
- Lint: `pnpm lint`
```

<a id="cc004"></a>
### CC004: @-Import zeigt auf fehlende Datei

**Stufe:** fehler

CLAUDE.md kann andere Dateien mit `@pfad` einbinden, bis zu vier Ebenen tief. Zeigt ein Import ins Leere, lädt Claude Code ihn still nicht. Niemand merkt, dass die Architektur-Doku fehlt. Die Regel ignoriert Importe in Codeblöcken und Codespans (die wertet auch Claude Code nicht aus) und npm-Scopes wie `@types/node`.

**Lösung:** Pfad korrigieren oder Import entfernen. Relative Pfade gelten relativ zur importierenden Datei.

<a id="cc005"></a>
### CC005: CLAUDE.local.md nicht in .gitignore

**Stufe:** fehler

`CLAUDE.local.md` ist für persönliche Notizen gedacht: eigene Sandbox-URLs, Testzugänge, Vorlieben. Ohne Eintrag in `.gitignore` landet sie beim nächsten `git add -A` im Repo.

**Lösung:**

```gitignore
CLAUDE.local.md
```

<a id="cc006"></a>
### CC006: AGENTS.md wird neben CLAUDE.md nicht gelesen

**Stufe:** hinweis

Seit Claude Code 2.1.277 liest Claude Code `AGENTS.md` nur, wenn es keine CLAUDE.md gibt. Wer beide pflegt (etwa für Codex und Claude Code), hat Regeln in AGENTS.md, die Claude nie sieht.

**Lösung:** In CLAUDE.md eine Zeile `@AGENTS.md` aufnehmen. Dann pflegt das Team die gemeinsamen Regeln an einer Stelle. Anleitung: [AGENTS.md und CLAUDE.md](anleitungen/agents-md.md).

<a id="cc007"></a>
### CC007: Platzhalter {{...}} in CLAUDE.md nicht ausgefüllt

**Stufe:** hinweis

`claude-team einrichten` setzt erkannte Befehle in die CLAUDE.md ein. Was es nicht erkennt, bleibt als Platzhalter stehen, etwa `{{EIN_SATZ_WAS_DAS_PROJEKT_TUT}}`, `{{LINT}}` oder `{{START}}`. Claude liest den Platzhalter wörtlich und rät dann.

**Lösung:** Jeden Platzhalter durch den echten Wert ersetzen oder die Zeile löschen. Platzhalter in Codeblöcken zählen nicht.

---

## settings.json

<a id="cc010"></a>
### CC010: settings.json ist kein gültiges JSON

**Stufe:** fehler

Settings-Dateien sind striktes JSON. Ein Kommentar oder ein Komma zu viel, und Claude Code meldet einen Settings-Fehler und überspringt die Datei. Dann gelten auch die deny-Regeln nicht.

**Lösung:** Mit `python3 -m json.tool .claude/settings.json` testen. Der Schlüssel `$schema` mit `https://json.schemastore.org/claude-code-settings.json` gibt im Editor Autovervollständigung.

<a id="cc011"></a>
### CC011: settings.local.json im Repo

**Stufe:** fehler

`.claude/settings.local.json` enthält persönliche Freigaben, die sich beim Arbeiten ansammeln, etwa "immer erlauben" für einen Befehl. Im Repo gelten sie plötzlich für alle. Claude Code trägt die Datei beim Anlegen in die globale Git-Ignore-Datei ein. Das schützt aber nicht, wenn jemand sie von Hand anlegt oder schon committet hat.

**Lösung:**

```bash
git rm --cached .claude/settings.local.json
echo ".claude/settings.local.json" >> .gitignore
```

<a id="cc012"></a>
### CC012: bypassPermissions als Standard oder nicht gesperrt

**Stufe:** fehler (bei `defaultMode: bypassPermissions`), hinweis (wenn der Modus nur nicht gesperrt ist)

`bypassPermissions` entspricht `--dangerously-skip-permissions`: Claude führt jeden Befehl ohne Rückfrage aus. Seit 2.1.257 ignoriert Claude Code diesen Wert aus Projekt- und Local-Settings, ältere Versionen nicht. Und ohne `disableBypassPermissionsMode` kann jede Person den Modus per Flag einschalten.

**Lösung:**

```json
{
  "permissions": {
    "defaultMode": "default",
    "disableBypassPermissionsMode": "disable"
  }
}
```

Unternehmensweit gehört die Sperre in die Managed Settings. Anleitung: [dangerously-skip-permissions](anleitungen/claude-code-dangerously-skip-permissions.md).

<a id="cc013"></a>
### CC013: Keine deny-Regel für .env

**Stufe:** fehler

Ohne deny-Regel darf Claude `.env` lesen. Der Inhalt steht dann im Kontext, im lokalen Transkript und geht an den Modellanbieter. Ein Dateiname ohne Pfad wie `Read(.env)` gilt in jeder Ordnertiefe.

**Lösung:**

```json
{
  "permissions": {
    "deny": ["Read(.env)", "Read(.env.*)", "Read(!.env.example)", "Edit(.env)", "Edit(.env.*)"]
  }
}
```

Die `!`-Zeile nimmt `.env.example` wieder aus. Sie wirkt nur hinter der Regel, die sie einschränkt, und nur in derselben Datei. Die Vorlage ergänzt einen Hook, der auch `cat .env` und `printenv` abfängt.

<a id="cc014"></a>
### CC014: Keine deny-Regel für Schlüsseldateien

**Stufe:** warnung

Private Schlüssel, Zertifikate und Terraform-State enthalten oft Zugangsdaten. Die Regel sucht nach deny-Regeln für `*.pem`, `*.key`, `id_rsa`, `id_ed25519` oder `secrets/`.

**Lösung:**

```json
{
  "permissions": {
    "deny": ["Read(**/*.pem)", "Read(**/*.key)", "Read(**/id_rsa*)", "Read(**/id_ed25519*)", "Read(**/*.tfstate)", "Read(secrets/**)"]
  }
}
```

<a id="cc015"></a>
### CC015: allow-Regel gibt zu viel frei

**Stufe:** warnung

`Bash`, `Bash(*)`, `Edit` oder `Bash(python3 *)` erlauben fast alles ohne Rückfrage. Bei Interpretern und Netzwerkwerkzeugen (`python`, `node`, `curl`, `ssh`, `docker`, `git`) ist der Stern ein Freibrief: `python3 -c "..."` kann alles.

**Lösung:** Konkrete Unterbefehle freigeben:

```json
{
  "permissions": {
    "allow": ["Bash(git status *)", "Bash(git diff *)", "Bash(npm run lint)", "Bash(ruff check *)"]
  }
}
```

<a id="cc016"></a>
### CC016: Stern vor dem Unterbefehl

**Stufe:** warnung

`Bash(git * main)` sieht eng aus, erlaubt aber jeden Git-Unterbefehl samt Optionen, etwa `git -c core.fsmonitor=... status main`. Der Stern gehört hinter den Unterbefehl.

**Lösung:** `Bash(git log * main)` oder `Bash(git checkout main)` statt `Bash(git * main)`.

<a id="cc017"></a>
### CC017: Regel wird von Claude Code ignoriert

**Stufe:** warnung

Einige Regeln sehen gültig aus, wirken aber nie:

| Regel | Problem | Richtig |
| --- | --- | --- |
| `Write(docs/**)` | Pfadregeln wirken nur für Read und Edit | `Edit(docs/**)` |
| `Glob(src/**)` | dito | `Read(src/**)` |
| `MultiEdit(...)`, `NotebookEdit(...)` | dito | `Edit(...)` |
| `Bash(git:* push)` | `:*` wirkt nur am Ende | `Bash(git push *)` |
| `Bash(command:rm *)` | Parameterregeln gibt es nicht für das Hauptfeld | `Bash(rm *)` |
| `mcp__*` in allow | Tool-Glob in allow nur hinter einem Servernamen | `mcp__github__*` |

Seit 2.1.210 warnt Claude Code beim Start vor wirkungslosen Pfadregeln. Das Audit findet sie schon im Pull Request.

<a id="cc018"></a>
### CC018: Alle MCP-Server aus .mcp.json automatisch freigegeben

**Stufe:** warnung

`enableAllProjectMcpServers: true` startet jeden Server, der in `.mcp.json` steht, ohne Nachfrage. Ein Pull Request, der einen neuen Server einträgt, läuft dann beim nächsten Start auf jedem Rechner.

**Lösung:** Server namentlich freigeben:

```json
{
  "enabledMcpjsonServers": ["github", "postgres"]
}
```

<a id="cc019"></a>
### CC019: Telemetrie nicht abgeschaltet

**Stufe:** hinweis

Claude Code sendet standardmäßig Nutzungsmetriken und Fehlerberichte, wenn es direkt mit der Anthropic-API arbeitet. Für viele Datenschutzbeauftragte ist das ein Punkt in der Freigabe. Diese beiden Variablen dürfen auch in Projekt-Settings stehen, weil sie Telemetrie abschalten und nicht einschalten.

**Lösung:**

```json
{
  "env": {
    "DISABLE_TELEMETRY": "1",
    "DISABLE_ERROR_REPORTING": "1"
  }
}
```

`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` schaltet zusätzlich automatische Updates ab und steht deshalb nicht in der Vorlage. Anleitung: [Claude Code DSGVO](anleitungen/claude-code-dsgvo.md).

---

## Hooks

<a id="cc020"></a>
### CC020: Keine Hooks konfiguriert

**Stufe:** hinweis

CLAUDE.md ist eine Bitte, ein Hook ist eine Regel. Was wirklich nicht passieren darf (Secrets lesen, Kundendaten in den Code, `git push --force`), sollte ein Hook abfangen.

**Lösung:** `claude-team einrichten` legt sieben getestete Hooks an. Anleitung: [Claude Code Hooks](anleitungen/claude-code-hooks.md).

<a id="cc021"></a>
### CC021: Hook-Skript fehlt

**Stufe:** fehler

Die settings.json verweist auf ein Skript, das es nicht gibt. Claude Code meldet dann bei jedem Aufruf einen Hook-Fehler, und der Schutz fällt still aus: Ein Hook, der nicht startet, blockiert nichts.

**Lösung:** Pfad korrigieren oder Eintrag entfernen. Die Regel erkennt die Shell-Form (`"command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/x.py\""`) und die Exec-Form mit `args`.

<a id="cc022"></a>
### CC022: Hook-Skript nicht ausführbar

**Stufe:** fehler

Ein Skript, das direkt ohne Interpreter gestartet wird, braucht das Ausführungsrecht. Fehlt es, schlägt der Hook fehl und die Aktion läuft durch.

**Lösung:** `chmod +x .claude/hooks/check.sh` und committen (Git speichert das Bit), oder mit Interpreter aufrufen: `"command": "bash \"${CLAUDE_PROJECT_DIR}/.claude/hooks/check.sh\""`.

<a id="cc023"></a>
### CC023: Hook mit relativem Pfad

**Stufe:** warnung

`python3 .claude/hooks/x.py` gilt relativ zum aktuellen Arbeitsordner. Wechselt Claude mit `cd` in einen Unterordner, findet die Shell das Skript nicht mehr. `CLAUDE_PROJECT_DIR` bleibt dagegen über die ganze Sitzung gleich.

**Lösung:** `"command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/x.py\""`. In der Shell-Form gehört die Variable in Anführungszeichen.

<a id="cc024"></a>
### CC024: Unbekanntes Hook-Ereignis

**Stufe:** warnung

Ein Tippfehler wie `PreToolUsage` oder `postToolUse` fällt nicht auf. Der Hook läuft einfach nie. Die Regel kennt alle 33 Ereignisse aus der Doku, von `SessionStart` bis `PostModelSwitch`.

---

## Secrets

<a id="cc030"></a>
### CC030: Zugangsschlüssel in einer Claude-Datei

**Stufe:** fehler

Die Regel durchsucht CLAUDE.md, CLAUDE.local.md, AGENTS.md, .mcp.json und alles unter `.claude/` nach echten Tokens: AWS, GitHub, GitLab, Slack, Anthropic, OpenAI, Google, Stripe, Azure, JWT, private Schlüssel und URLs mit Passwort. Platzhalter wie `${TOKEN}`, `<token>` oder Werte mit `example` zählen nicht. Die Meldung zeigt den Wert nur maskiert.

**Lösung:** Schlüssel beim Anbieter widerrufen (er ist kompromittiert, sobald er in Git stand), neu ausstellen, als Umgebungsvariable setzen und in der Datei nur `${NAME}` referenzieren.

---

## MCP

<a id="cc031"></a>
### CC031: .mcp.json ist kein gültiges JSON

**Stufe:** fehler

Mit kaputtem JSON lädt Claude Code keinen der Projekt-Server.

<a id="cc032"></a>
### CC032: Token im Klartext in .mcp.json

**Stufe:** fehler

`.mcp.json` wird committet. Ein Token in `env` oder `headers` steht damit im Repo. Die Regel meldet Werte unter Namen wie `token`, `secret`, `password`, `api_key`, `auth` und jeden `Bearer`-Header ohne Variable.

**Lösung:** Claude Code ersetzt `${VAR}` und `${VAR:-standard}` beim Laden:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_MCP_TOKEN}" }
    }
  }
}
```

<a id="cc033"></a>
### CC033: MCP-Server ohne feste Version

**Stufe:** warnung

`npx -y paket` oder `uvx paket` lädt bei jedem Start die neueste Version. Wird das Paket kompromittiert, läuft der Schadcode beim nächsten Start auf jedem Entwicklerrechner, mit den Rechten der Person.

**Lösung:** Version pinnen: `@modelcontextprotocol/server-postgres@0.6.2` bei npx, `mcp-server-git==0.6.2` bei uvx. Updates bewusst per Pull Request.

<a id="cc034"></a>
### CC034: MCP-Server mit url, aber ohne type

**Stufe:** fehler

Ein Eintrag mit `url`, aber ohne `type`, gilt als stdio-Server ohne Befehl und wird übersprungen.

**Lösung:** `"type": "http"` ergänzen.

<a id="cc035"></a>
### CC035: MCP-Transport sse ist veraltet

**Stufe:** hinweis

Die Doku führt `sse` als veraltet. Die meisten Server bieten inzwischen Streamable HTTP an.

**Lösung:** Auf `"type": "http"` wechseln, wenn der Server es unterstützt.

<a id="cc036"></a>
### CC036: Geschützte Variable in Remote-MCP

**Stufe:** fehler

`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `AWS_BEARER_TOKEN_BEDROCK` und `NPM_TOKEN` liest Claude Code in `url` und `headers` von Remote-Servern als leer. So kann eine fremde `.mcp.json` keine Zugangsdaten an einen beliebigen Server schicken. Wer sie trotzdem einträgt, bekommt eine Anmeldung ohne Token.

**Lösung:** Eigene Variable für den MCP-Server anlegen, z.B. `${MEIN_DIENST_TOKEN}`.

---

## Subagents und Skills

<a id="cc040"></a>
### CC040: Subagent ohne name oder description

**Stufe:** fehler

`name` und `description` sind im Frontmatter von `.claude/agents/*.md` Pflicht. Fehlen sie, lädt Claude Code den Subagent nicht.

```markdown
---
name: code-reviewer
description: Bewertet Änderungen auf Fehler, Sicherheit und Lesbarkeit. Nach jeder größeren Änderung einsetzen.
tools: Read, Grep, Glob, Bash
---
```

<a id="cc041"></a>
### CC041: Subagent mit bypassPermissions

**Stufe:** fehler

`permissionMode: bypassPermissions` im Frontmatter lässt diesen Subagent ohne jede Rückfrage arbeiten, auch wenn die Hauptsitzung vorsichtig eingestellt ist.

**Lösung:** Zeile entfernen oder `acceptEdits` nutzen, wenn der Agent nur Dateien bearbeiten soll.

<a id="cc042"></a>
### CC042: Skill ohne description

**Stufe:** warnung

Claude entscheidet anhand der `description`, wann ein Skill passt. Ohne sie greift Claude auf den ersten Absatz zurück, und der Skill wird selten oder zur falschen Zeit geladen.

**Lösung:** In einem Satz was und wann: `description: Erstellt Release Notes aus den Commits seit dem letzten Tag. Nutzen, wenn ein Release vorbereitet wird.`

<a id="cc043"></a>
### CC043: SKILL.md über 500 Zeilen

**Stufe:** hinweis

Anthropic empfiehlt, SKILL.md unter 500 Zeilen zu halten. Details, Beispiele und Referenzen gehören in Zusatzdateien im Skill-Ordner, die Claude nur bei Bedarf liest.

<a id="cc044"></a>
### CC044: Subagent ohne tools-Liste

**Stufe:** hinweis

Ohne `tools` erbt ein Subagent alle Werkzeuge der Hauptsitzung, inklusive MCP-Servern. Ein Review-Agent braucht keine Schreibrechte.

**Lösung:** `tools: Read, Grep, Glob` für reine Leser, `Bash` nur, wenn der Agent Tests starten soll.

---

## Git

<a id="cc050"></a>
### CC050: .env im Repo oder nicht ignoriert

**Stufe:** fehler

Eine getrackte `.env` ist kompromittiert, auch wenn das Repo privat ist. Eine nicht ignorierte `.env` landet beim nächsten `git add -A` im Repo. `.env.example`, `.env.sample`, `.env.template` und `.env.dist` sind erlaubt.

**Lösung:**

```bash
git rm --cached .env
echo ".env" >> .gitignore
# Schlüssel aus der Datei beim Anbieter widerrufen und neu ausstellen
```

<a id="cc051"></a>
### CC051: Hook-Protokoll nicht ignoriert

**Stufe:** warnung

Der Protokoll-Hook der Vorlage schreibt unter `.claude/protokoll/` mit, welches Werkzeug wann lief. Das ist für die eigene Nachvollziehbarkeit gedacht und gehört nicht ins Repo.

**Lösung:** `.claude/protokoll/` in `.gitignore`. `claude-team einrichten` trägt das ein.

---

## Regeln in der CI

```yaml
- uses: pexon-consulting/claude-code-best-practices@v0.2.0
  with:
    schwelle: warnung
    sarif: true
```

Mit `sarif: true` erscheinen die Befunde als Code-Scanning-Hinweise direkt im Pull Request. Dafür braucht der Job `permissions: security-events: write`. Details: [Claude Code Review mit GitHub Actions](anleitungen/claude-code-review-github-actions.md).

[Zurück zur Übersicht](../README.md)
