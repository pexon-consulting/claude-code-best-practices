# Claude Code Review: automatische Reviews mit GitHub Actions

Claude Code Review in GitHub Actions läuft über die offizielle Action `anthropics/claude-code-action@v1`: Du installierst die Claude GitHub App, legst das Secret `ANTHROPIC_API_KEY` oder `CLAUDE_CODE_OAUTH_TOKEN` an und kopierst einen Workflow, der bei jedem Pull Request das Review-Plugin oder einen eigenen `prompt` ausführt. Ohne `prompt` reagiert Claude nur auf `@claude` in Kommentaren, mit `prompt` läuft es automatisch; `--max-turns` und `--allowedTools` in `claude_args` begrenzen Kosten und Rechte.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

## Das Wichtigste in Kürze

- Die Action heißt `anthropics/claude-code-action` und wird mit dem Major-Tag `@v1` eingebunden; `@beta` ist abgelöst.
- Am schnellsten geht das Setup mit `/install-github-app` in Claude Code, das nur mit github.com-Repos funktioniert und Admin-Rechte im Repo braucht.
- Ohne `prompt` läuft die Action im interaktiven Modus und wartet auf `@claude`, mit `prompt` im Automationsmodus bei jedem passenden Ereignis.
- `claude_args` nimmt jedes CLI-Argument an, im Review-Workflow vor allem `--max-turns`, `--model` und `--allowedTools`.
- Lokal prüfst du denselben Diff vorher mit `/code-review` (Alias `/review`) und `/security-review`, für eigene Skripte nutzt du `claude -p`.
- Die Team-Basis des Repos (Settings, Hooks, MCP) prüft zusätzlich die Action `pexon-consulting/claude-code-best-practices@v0.2.0` und lädt die Befunde als SARIF zu GitHub Code Scanning hoch.

## Welche Review-Varianten gibt es?

Mehrere Produkte tragen den Namen Claude Code. Für Reviews sind diese vier relevant:

| Variante | Wo sie läuft | Wann sinnvoll |
| --- | --- | --- |
| `anthropics/claude-code-action@v1` | dein GitHub-Actions-Runner | volle Kontrolle über Prompt, Modell, Trigger und Rechte |
| Code Review (verwalteter Dienst) | bei Anthropic, ein Owner schaltet ihn für die Organisation ein | Review jedes PR ohne eigene Workflow-Datei |
| `/code-review` und `/security-review` | in deiner lokalen Sitzung | vor dem Push, zählt wie normale Nutzung gegen Abo oder API |
| `claude -p` in eigenen Skripten | überall, wo die CLI läuft | eigene Prüfungen, GitLab, Jenkins, pre-commit |

Diese Anleitung behandelt vor allem die Action und die lokalen Befehle. Für GitLab gibt es eine eigene Doku-Seite unter https://code.claude.com/docs/en/gitlab-ci-cd; `/code-review --comment` kann Befunde ab v2.1.257 über die `glab`-CLI an einen GitLab Merge Request schreiben.

## Wie richte ich Claude Code in GitHub Actions ein?

### Schnell mit /install-github-app

1. GitHub CLI installieren und mit `gh auth login` anmelden. Claude Code prüft das und warnt, wenn `gh` fehlt.
2. Im Repo `claude` starten und `/install-github-app` eingeben.
3. Claude Code installiert die Claude GitHub App und legt ein Secret an: `ANTHROPIC_API_KEY` für einen API-Schlüssel oder `CLAUDE_CODE_OAUTH_TOKEN` für ein Abo-Token.
4. Claude Code pusht einen Branch mit den gewählten Workflows (`claude.yml`, optional `claude-code-review.yml`) und öffnet den Pull Request im Browser. Mergen, fertig.

Mit Esc brichst du ab; ein laufender Schritt wird noch beendet. Mit **Skip for now** installierst du nur die App und holst Workflow und Secret später nach. Den Review-Workflow einer älteren Version aktualisierst du, indem du `/install-github-app` erneut startest und **Update workflow file with latest version** wählst.

### Manuell

1. Die Claude GitHub App unter https://github.com/apps/claude im Repo installieren. Die Action nutzt davon Contents, Issues und Pull requests, jeweils lesen und schreiben.
2. Ein Secret anlegen: `ANTHROPIC_API_KEY` (Schlüssel aus der Claude Console) oder `CLAUDE_CODE_OAUTH_TOKEN` (lokal mit `claude setup-token` erzeugt, für Pro, Max, Team und Enterprise).
3. Die Vorlage `examples/claude.yml` aus dem Repo der Action nach `.github/workflows/` kopieren. Bei OAuth-Token die Zeile `anthropic_api_key` durch `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}` ersetzen.

Für eine ganze Organisation installierst du die App einmal auf Organisationsebene und legst das Secret als Organisations-Secret ab. Dort gehört ein API-Schlüssel hin, kein OAuth-Token, weil das Token an das Abo der Person gebunden ist, die `claude setup-token` ausgeführt hat. Ganz ohne langlebiges Secret geht es mit Workload Identity Federation über OIDC (Inputs `anthropic_federation_rule_id`, `anthropic_organization_id`, optional `anthropic_service_account_id` und `anthropic_workspace_id`, Recht `id-token: write`).

Wichtig für die Freigabe: Die offizielle App bekommt beim Installieren ihr komplettes Rechte-Set, darunter Actions, Checks, Workflows und Repository hooks mit Schreibrecht. GitHub erlaubt keine Teilmenge. Wer nur die drei nötigen Rechte vergeben will, legt eine eigene GitHub App an; die deckt dann aber nur die Action ab, nicht den verwalteten Code-Review-Dienst.

## Interaktiver Modus und Automationsmodus

| Modus | Auslöser | Ergebnis landet |
| --- | --- | --- |
| interaktiv (kein `prompt`) | `@claude` in Issue- oder PR-Kommentar, PR-Review oder Titel und Text eines neuen Issues | als Kommentar am Issue oder PR |
| Automation (mit `prompt`) | jedes GitHub-Ereignis, auch `schedule` | im Log des Workflow-Laufs, außer der Prompt lässt Claude mit einem passenden Tool kommentieren |

In beiden Modi prüft die Action vor dem Start zwei Dinge. Erstens braucht der auslösende Nutzer bei Issue- und PR-Ereignissen Schreibrecht im Repo; Ausnahmen setzt du mit `allowed_non_write_users` plus eigenem `github_token`. Zweitens lehnt sie Bots ab, außer sie stehen in `allowed_bots`. Das verhindert Schleifen, in denen sich Bots gegenseitig auslösen.

Ein Detail für reine Text-Prompts im Automationsmodus: Claude hat dann weder Shell noch GitHub-API, bis du die Tools mit `--allowedTools` in `claude_args` oder mit einer `permissions.allow`-Regel im Input `settings` freigibst. Ruft der Prompt einen Skill auf, gelten dessen `allowed-tools` aus dem Frontmatter.

## Die wichtigsten Inputs

| Input | Zweck |
| --- | --- |
| `prompt` | Text oder Skill-Aufruf wie `/review-checkliste`; ohne ihn interaktiver Modus |
| `claude_args` | CLI-Argumente, z. B. `--max-turns 5 --model claude-sonnet-5` |
| `anthropic_api_key` | API-Schlüssel für die Claude API |
| `claude_code_oauth_token` | Abo-Token aus `claude setup-token` |
| `github_token` | eigenes Token für GitHub; fehlt es, authentifiziert sich die Action als Claude GitHub App |
| `plugin_marketplaces`, `plugins` | Plugins vor dem Lauf installieren, je Zeile ein Eintrag |
| `settings` | Claude-Code-Settings als JSON-String oder Pfad zu einer Datei |
| `trigger_phrase` | Auslösewort, Default `@claude` |
| `use_bedrock`, `use_vertex`, `use_foundry` | Inferenz über Amazon Bedrock, Google Cloud's Agent Platform (Vertex AI) oder Microsoft Foundry |

Die vollständige Liste steht in der Konfigurationsreferenz der Action: https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md#inputs

Häufige Werte für `claude_args`: `--max-turns` (begrenzt die Zahl der Runden), `--model`, `--mcp-config`, `--allowedTools` (Alias `--allowed-tools`, kommagetrennt), `--append-system-prompt` und `--debug`.

## Beispiele für Claude Code Review

### Beispiel 1: Auf @claude in Kommentaren reagieren

Die Grundform, wenn Entwickler Claude gezielt im PR oder Issue ansprechen sollen.

```yaml
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          claude_args: "--max-turns 5"
```

`id-token: write` braucht die Standard-Authentifizierung über die GitHub App, `actions: read` erlaubt Claude, CI-Ergebnisse am PR zu lesen. Typische Kommentare: `@claude erkläre, warum der Test in auth.spec.ts fehlschlägt` oder `@claude setze die Änderung aus diesem Issue um und öffne einen PR`.

### Beispiel 2: Jeden Pull Request automatisch reviewen (offizielles Plugin)

Für Teams, die bei jedem PR ein Review mit Inline-Kommentaren wollen.

```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize, ready_for_review, reopened]
concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true
jobs:
  review:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    permissions:
      contents: read
      pull-requests: read
      issues: read
      id-token: write
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          plugin_marketplaces: "https://github.com/anthropics/claude-code.git"
          plugins: "code-review@claude-code-plugins"
          prompt: "/code-review:code-review --comment ${{ github.repository }}/pull/${{ github.event.pull_request.number }}"
          claude_args: '--allowedTools "mcp__github_inline_comment__create_inline_comment"'
```

`--comment` sorgt dafür, dass das Review am PR erscheint, als Inline-Kommentar je Befund oder als ein Sammelkommentar ohne Befund. Die Zeile `claude_args` muss bleiben: Die Action startet den MCP-Server für Inline-Kommentare nur, wenn `--allowedTools` ihn nennt. Claude überspringt Entwürfe, geschlossene PRs, triviale oder automatische PRs und PRs, die schon einen Claude-Kommentar haben. Auf öffentlichen Repos gibt GitHub Forks keine Secrets, das Review läuft dann nur für Branches im selben Repo.

### Beispiel 3: Eigener Review-Prompt mit Leitplanken

Wenn du Kriterien, Modell und Rechte selbst festlegen willst, statt das Plugin zu nutzen.

```yaml
name: Claude Review mit Leitplanken
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]
concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true
jobs:
  review:
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
      pull-requests: read
      issues: read
      id-token: write
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Prüfe den Pull Request ${{ github.repository }}/pull/${{ github.event.pull_request.number }}.
            Vergleiche den Branch mit origin/${{ github.event.pull_request.base.ref }}.
            Melde nur Fehler, Sicherheitslücken und fehlende Tests, keinen Stil.
            Schreibe zu jedem Befund einen Inline-Kommentar an die betroffene Zeile.
            Halte dich an die Regeln aus CLAUDE.md.
          claude_args: |
            --model claude-sonnet-5
            --max-turns 8
            --allowedTools "Read,Grep,Glob,Bash(git diff *),Bash(git log *),mcp__github_inline_comment__create_inline_comment"
```

`timeout-minutes` und `concurrency` sind normale GitHub-Funktionen und verhindern hängende oder doppelte Läufe. Das Leerzeichen in `Bash(git diff *)` ist Absicht: Ohne es würde die Regel auch `git diff-index` treffen.

### Beispiel 4: Einen Review-Skill aus dem eigenen Repo ausführen

Wenn die Review-Checkliste versioniert im Repo unter `.claude/skills/review-checkliste/SKILL.md` liegt.

```yaml
name: Review nach Team-Checkliste
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: read
      pull-requests: read
      id-token: write
    steps:
      - uses: actions/checkout@v6
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "/review-checkliste"
          claude_args: "--max-turns 6"
```

Der Checkout muss vor der Action stehen, sonst findet der Runner die Skill-Dateien nicht. Welche Tools der Skill ohne Rückfrage nutzt, regelt sein Frontmatter-Feld `allowed-tools`.

### Beispiel 5: Täglicher Bericht per Zeitplan

Für einen Morgenbericht über Commits und offene Issues, ohne Checkout.

```yaml
name: Tagesbericht
on:
  schedule:
    - cron: "0 6 * * 1-5"
jobs:
  report:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
      issues: read
      id-token: write
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Fasse die Commits von gestern und die offenen Issues auf Deutsch zusammen."
          claude_args: |
            --model claude-sonnet-5
            --max-turns 4
            --allowedTools "mcp__github__list_commits,mcp__github__list_issues"
```

GitHub führt Zeitpläne nur vom Default-Branch aus und schaltet sie in öffentlichen Repos nach 60 Tagen ohne Aktivität ab. Der Bericht steht im Log des Laufs.

### Beispiel 6: Inferenz über Amazon Bedrock in der EU

Für Teams, die Modellaufrufe über das eigene AWS-Konto laufen lassen müssen.

```yaml
name: Claude über Bedrock
permissions:
  contents: write
  pull-requests: write
  issues: write
  id-token: write
on:
  issue_comment:
    types: [created]
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v6
      - name: AWS-Zugang per OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
          aws-region: eu-central-1
      - uses: anthropics/claude-code-action@v1
        with:
          use_bedrock: "true"
          claude_args: "--model eu.anthropic.claude-sonnet-4-6 --max-turns 5"
```

Statt eines API-Schlüssels tauscht der Workflow sein OIDC-Token gegen kurzlebige AWS-Zugangsdaten; im Repo liegt nur die Rollen-ARN als Secret. Die Modell-ID mit Präfix `eu.` vorher in der eigenen Bedrock-Konsole prüfen. Ohne `github_token` nutzt die Action die offizielle Claude GitHub App. Vertex AI (`use_vertex`) und Foundry (`use_foundry`) funktionieren nach demselben Muster, siehe https://code.claude.com/docs/en/github-actions-cloud-providers. Achtung bei öffentlichen Repos: Die Zugangs-Schritte laufen, bevor die Action das Schreibrecht des Kommentators prüft.

### Beispiel 7: Team-Basis mit claude-team audit prüfen (SARIF)

Für jedes Repo, in dem Claude Code genutzt wird: Die Action dieses Repos prüft CLAUDE.md, `.claude/settings.json`, Hooks, `.mcp.json`, Subagents und Skills gegen die Team-Basis.

```yaml
name: Claude-Code-Basis
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
  security-events: write
jobs:
  audit:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v6
      - uses: pexon-consulting/claude-code-best-practices@v0.2.0
        with:
          pfad: .
          schwelle: fehler
          sarif: true
```

`security-events: write` ist nötig, damit der SARIF-Bericht in GitHub Code Scanning landet. Der Job scheitert, wenn ein Befund die `schwelle` erreicht, etwa eine fehlende deny-Regel für `.env` ([CC013](../regeln.md#cc013)) oder ein Token im Klartext in `.mcp.json` ([CC032](../regeln.md#cc032)). Dieser Lauf braucht kein Modell und kostet keine Tokens.

### Beispiel 8: Migration von @beta auf @v1

Wenn ältere Workflows noch die Beta referenzieren. Vorher:

```yaml
- uses: anthropics/claude-code-action@beta
  with:
    mode: agent
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    direct_prompt: "Prüfe diesen Pull Request auf Fehler."
    max_turns: "5"
    model: claude-sonnet-5
    custom_instructions: "Antworte auf Deutsch."
```

Nachher:

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "Prüfe diesen Pull Request auf Fehler."
    claude_args: |
      --max-turns 5
      --model claude-sonnet-5
      --append-system-prompt "Antworte auf Deutsch."
```

Die Regeln: `@beta` wird `@v1`, `mode` entfällt (der Modus wird erkannt), `direct_prompt` heißt `prompt`, `max_turns` und `model` wandern in `claude_args`, `custom_instructions` wird `--append-system-prompt`. Details im Migration Guide der Action.

### Beispiel 9: Lokal reviewen, bevor der PR entsteht

Für Entwickler, die Befunde sehen wollen, bevor die CI Geld kostet.

```text
/code-review
/code-review main...mein-feature
/code-review 1234
/code-review low src/auth
/code-review --fix
/security-review
```

`/code-review` (Alias `/review`) läuft als Subagent im Hintergrund mit eigenem Kontextfenster und meldet die Befunde in der Sitzung. Ohne Ziel prüft es die Commits vor dem Upstream-Branch plus nicht committete Änderungen. `low` meldet nur die sichersten Befunde, ab `medium` wird die Abdeckung breiter. `--fix` wendet die Befunde an; diese Änderungen laufen außerhalb der Checkpoints, also mit Git zurücknehmen. `/security-review` vergleicht den Branch mit dem Default-Branch von `origin` und sucht Injection, Auth-Fehler und Datenabfluss; es braucht ein `origin`-Remote. Das Review liest deine CLAUDE.md, aber keine `REVIEW.md`.

### Beispiel 10: Eigenes Review-Skript mit claude -p

Für GitLab, Jenkins oder einen pre-push-Hook, wo die Action nicht läuft.

```bash
#!/usr/bin/env bash
# review.sh <pr-nummer>
set -euo pipefail
gh pr diff "$1" | claude --bare -p \
  --append-system-prompt "Du bist Security-Reviewer. Melde nur echte Schwachstellen mit Datei und Zeile." \
  --output-format json \
  --max-turns 3 \
  --max-budget-usd 1.00 \
  | jq -r '.result'
```

Der Diff kommt per Pipe, deshalb braucht Claude kein Bash-Recht zum Lesen. `--bare` lädt keine Hooks, Skills, MCP-Server und keine CLAUDE.md vom Rechner und braucht `ANTHROPIC_API_KEY` in der Umgebung. Der Exit-Code ist 0 bei Erfolg, sonst ungleich 0.

## Schritt für Schritt: automatisches Review für ein Team-Repo

1. CLAUDE.md mit Review-Kriterien anlegen oder schärfen ("Melde fehlende Tests für neue Endpunkte", "Kein SQL aus String-Verkettung"). Claude liest sie bei jedem Lauf, also kurz halten. Siehe [CLAUDE.md](./claude-md.md).
2. Lokal testen: `/code-review` im Feature-Branch ausführen und prüfen, ob die Befunde passen.
3. Claude GitHub App installieren und `ANTHROPIC_API_KEY` als Repo- oder Organisations-Secret anlegen.
4. Beispiel 2 oder 3 als `.github/workflows/claude-code-review.yml` committen.
5. `timeout-minutes`, `concurrency` und `--max-turns` setzen, damit kein Lauf ausufert.
6. Beispiel 7 als zweiten Workflow ergänzen, damit Änderungen an `.claude/settings.json`, Hooks oder `.mcp.json` die Team-Basis nicht unterlaufen.
7. Einen Test-PR öffnen und das Ergebnis im PR und im Actions-Log prüfen.
8. Nach zwei Wochen Kosten in der Claude Console ansehen und `--model` oder `--max-turns` nachjustieren. Siehe [Claude Code Kosten](./claude-code-kosten.md).

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| App nicht im Repo installiert | `@claude` bleibt ohne Antwort | App unter https://github.com/apps/claude installieren, Workflows im Repo aktivieren |
| Falsches Auslösewort | nichts passiert bei `/claude` oder `@claude-bot` | `@claude` als ganzes Wort schreiben oder `trigger_phrase` setzen |
| Kommentator ohne Schreibrecht | Lauf scheitert sofort | Schreibrecht geben oder `allowed_non_write_users` mit eigenem `github_token` |
| `github_token: ${{ secrets.GITHUB_TOKEN }}` gesetzt | CI startet nicht auf Claudes Commits | Zeile entfernen, dann nutzt die Action die App, oder ein eigenes App-Token übergeben |
| Review ohne `--comment` | Befunde nur im Log | `--comment` im Prompt und `claude_args` mit dem Inline-Kommentar-Tool |
| Text-Prompt ohne Tools | Claude kann weder Git noch GitHub nutzen | Tools mit `--allowedTools` freigeben |
| Kein Turn-Limit | lange Läufe, hohe Kosten | `--max-turns`, `timeout-minutes`, `concurrency` |
| OAuth-Token als Organisations-Secret | Verbrauch läuft über das Abo einer Person | API-Schlüssel aus der Claude Console nutzen |
| Noch `@beta` mit `direct_prompt` | Workflow-Fehler oder veraltetes Verhalten | auf `@v1` migrieren (Beispiel 8) |

## Häufige Fragen

### Wie lasse ich Claude Code Pull Requests automatisch prüfen?

Mit einem Workflow, der bei `pull_request` die Action `anthropics/claude-code-action@v1` mit `prompt` startet, am einfachsten mit dem Plugin `code-review@claude-code-plugins` und `--comment` wie in Beispiel 2. Ohne eigene Workflow-Datei geht es mit dem verwalteten Dienst Code Review, den ein Owner für die Organisation einschaltet.

### Was kostet ein Claude-Code-Review in GitHub Actions?

Jeder Lauf verbraucht GitHub-Actions-Minuten und Tokens; die Tokens hängen von Prompt-Länge, Antwort, Aufgabe und Größe der Codebasis ab. Aktuelle Preise stehen unter https://claude.com/platform/api. Mit OAuth-Token läuft der Verbrauch über das Claude-Abo statt über die API-Abrechnung. Präzise `@claude`-Anfragen, eine kurze CLAUDE.md, `--max-turns`, Timeouts und `concurrency` senken die Kosten.

### Brauche ich einen API-Schlüssel oder reicht mein Claude-Abo?

Beides geht: `ANTHROPIC_API_KEY` aus der Claude Console oder `CLAUDE_CODE_OAUTH_TOKEN`, das du mit `claude setup-token` erzeugst (Pro, Max, Team, Enterprise). Für Organisations-Secrets empfiehlt die Doku den API-Schlüssel, weil das Token am Abo einer Person hängt.

### Was ist der Unterschied zwischen /review und /code-review?

Seit v2.1.223 ist `/review` ein Alias von `/code-review`. Vorher war `/review` ein eigener Befehl für ein einfaches Lese-Review eines GitHub-PR. Beide nehmen heute dieselben Effort-Stufen und Flags wie `--fix` und `--comment`.

### Funktioniert Claude Code Review auch mit GitLab?

Ja, aber nicht mit `/install-github-app`, das nur github.com unterstützt. Für Pipelines gibt es die Anleitung GitLab CI/CD in der Doku, und lokal schreibt `/code-review --comment` ab v2.1.257 Befunde über `glab` an einen Merge Request. Ein eigenes Skript mit `claude -p` (Beispiel 10) läuft in jeder CI.

### Kann ich die Action ohne Daten an Anthropic direkt betreiben?

Du kannst die Inferenz mit `use_bedrock`, `use_vertex` oder `use_foundry` über dein eigenes Cloud-Konto leiten und dich per OIDC anmelden, ohne statische Cloud-Schlüssel im Repo. Welche Region und Vertragslage für dein Unternehmen passt, klärst du mit dem Datenschutzbeauftragten; siehe [Claude Code Bedrock](./claude-code-bedrock.md) und [Claude Code DSGVO](./claude-code-dsgvo.md).

## Weiterlesen

- [Claude Code Bedrock](./claude-code-bedrock.md)
- [Claude Code Kosten](./claude-code-kosten.md)
- [Claude Agent SDK und Headless-Modus](./claude-agent-sdk.md)
- [Claude Code Skills](./claude-code-skills.md)
- [Claude Code Sicherheit](./claude-code-sicherheit.md)
- Vorlage Review-Agent: [`.claude/agents/code-reviewer.md`](../../src/claude_team/vorlage/.claude/agents/code-reviewer.md)
- Prüfregeln: [CC013](../regeln.md#cc013), [CC032](../regeln.md#cc032)
