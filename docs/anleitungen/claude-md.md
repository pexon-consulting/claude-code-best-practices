# CLAUDE.md: Aufbau, Beispiele und Best Practices für Teams

Eine CLAUDE.md ist eine Markdown-Datei im Projekt, die Claude Code zu Beginn jeder Sitzung liest: Sie enthält Build- und Testbefehle, Konventionen, den Projektaufbau und feste Regeln, die Claude sonst jedes Mal neu erklärt bekommen müsste. Anthropic empfiehlt, jede CLAUDE.md unter 200 Zeilen zu halten, weil lange Dateien Kontext kosten und schlechter befolgt werden. Alles, was nur für einen Teil des Codes gilt, gehört in `.claude/rules/`, alles, was zwingend passieren muss, in einen Hook.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Die Projekt-CLAUDE.md liegt unter `./CLAUDE.md` oder `./.claude/CLAUDE.md` und wird mit Git im Team geteilt.
- Claude Code hängt alle gefundenen CLAUDE.md-Dateien vom Dateisystem-Root bis zum Arbeitsverzeichnis aneinander, keine Datei überschreibt eine andere.
- Unter 200 Zeilen bleiben, konkret und prüfbar formulieren, Widersprüche vermeiden.
- `@pfad`-Imports binden weitere Dateien ein (maximal 4 Hops tief), sparen aber keinen Kontext.
- Block-HTML-Kommentare `<!-- ... -->` werden vor dem Einlesen entfernt und eignen sich für Notizen an Menschen.
- Der `#`-Kurzbefehl zum schnellen Speichern wurde in v2.0.70 entfernt; heute sagt man "add this to CLAUDE.md" oder öffnet `/memory`.

## Was gehört in eine CLAUDE.md?

Die Doku formuliert es so: Schreib in die CLAUDE.md, was du sonst immer wieder erklären würdest. Gute Anlässe sind:

- Claude macht denselben Fehler zum zweiten Mal.
- Ein Code-Review findet etwas, das Claude über diese Codebasis hätte wissen müssen.
- Du tippst dieselbe Korrektur wie in der letzten Sitzung.
- Eine neue Kollegin bräuchte denselben Kontext, um loszulegen.

Hinein gehören Fakten, die in jeder Sitzung gelten: Befehle, Konventionen, Projektlayout, "immer X"-Regeln. Mehrschrittige Abläufe gehören in [Skills](./claude-code-skills.md), Regeln für einen Teilbereich in [Rules mit `paths`](./claude-code-rules.md).

| Gehört hinein | Gehört woandershin |
| --- | --- |
| Build-, Test- und Lint-Befehle | Abläufe mit vielen Schritten: Skill |
| Namens- und Commit-Konventionen | Regeln nur für `src/api/`: `.claude/rules/` mit `paths` |
| Wo was liegt, wenn es nicht offensichtlich ist | Verbote, die sicher greifen müssen: `permissions.deny` oder Hook |
| Bekannte Fallen und deren Grund | Persönliche Vorlieben: `CLAUDE.local.md` oder `~/.claude/CLAUDE.md` |

Konkret schlägt vage. Die Doku gibt diese Beispiele:

- "Use 2-space indentation" statt "Format code properly"
- "Run `npm test` before committing" statt "Test your changes"
- "API handlers live in `src/api/handlers/`" statt "Keep files organized"

Wichtig: CLAUDE.md ist Kontext, keine erzwungene Konfiguration. Claude Code liefert sie als User-Message nach dem System-Prompt aus. Was technisch verhindert werden muss, regelst du über [Permissions](./claude-code-permissions.md) oder [Hooks](./claude-code-hooks.md).

## Wo liegt die CLAUDE.md? Speicherorte im Überblick

| Ebene | Pfad | Gilt für | Geteilt |
| --- | --- | --- | --- |
| Managed Policy | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`, Linux und WSL: `/etc/claude-code/CLAUDE.md`, Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | alle Nutzer der Maschine | per IT verteilt, nicht ausschließbar |
| Managed als Setting | Key `claudeMd` in Managed Settings | wie oben | nur in Managed Settings wirksam |
| Nutzer | `~/.claude/CLAUDE.md` | du, alle Projekte | nein |
| Projekt | `./CLAUDE.md` oder `./.claude/CLAUDE.md` | alle im Repo | ja, über Git |
| Lokal | `./CLAUDE.local.md` | du, dieses Projekt | nein, in `.gitignore` eintragen |
| Unterordner | `<ordner>/CLAUDE.md` | Arbeit in diesem Ordner | ja |

So lädt Claude Code die Dateien:

- CLAUDE.md und CLAUDE.local.md im Arbeitsverzeichnis und in allen Ordnern darüber werden beim Start geladen.
- Dateien in Unterordnern lädt Claude Code erst, wenn Claude dort eine Datei liest, schreibt oder bearbeitet. Sie erscheinen nicht unter "Memory files" in `/context`, beim Laden zeigt das Terminal eine `Loaded`-Zeile.
- Innerhalb eines Ordners kommt `CLAUDE.local.md` nach `CLAUDE.md`. Weiter oben liegende Dateien stehen im Kontext vor den näheren.
- Dateien bis 4 MiB werden ganz geladen, größere übersprungen.
- Nach `/compact` liest Claude Code die CLAUDE.md im Projekt-Root neu von der Platte.

Ob eine Datei wirklich geladen ist, zeigt `/context` unter **Memory files**. Mit `/memory` öffnest du die Dateien im Editor.

## Wie lang darf eine CLAUDE.md sein?

Die offizielle Empfehlung lautet unter 200 Zeilen pro Datei. Ist eine Datei länger, warnt Claude Code beim Start und in `/status`. Es gibt außerdem eine Warnung, wenn viele einzeln kurze Dateien zusammen ein Gesamtlimit überschreiten; dabei zählt jede CLAUDE.md, jede Regeldatei und jeder `@`-Import einzeln.

Wenn die Datei wächst:

1. Bereichsregeln nach `.claude/rules/` mit `paths` verschieben. Sie laden nur, wenn Claude passende Dateien anfasst.
2. Abläufe ("so machst du ein Release") in einen Skill auslagern.
3. Streichen, was Claude aus dem Code selbst ableiten kann, etwa Verzeichnisbäume oder Abhängigkeitslisten.
4. `/doctor prompt-audit` laufen lassen (ab v2.1.283). Claude sucht dann veraltete Anweisungen, Verweise auf nicht vorhandene Dateien und Widersprüche und schlägt Änderungen vor, ohne selbst etwas zu ändern.

## @-Imports: andere Dateien einbinden

Mit `@pfad/zur/datei` bindet eine CLAUDE.md weitere Dateien ein. Regeln laut Doku:

- Relative Pfade gelten relativ zur importierenden Datei, nicht zum Arbeitsverzeichnis. Absolute Pfade und `@~/...` gehen auch.
- Imports dürfen selbst importieren, maximal 4 Hops tief.
- Leerzeichen im Pfad mit Backslash escapen: `@Design\ Docs/api-conventions.md`. Pfade in Anführungszeichen werden gar nicht importiert.
- In Code-Spans und Codeblöcken wird nicht importiert. `` `@README` `` bleibt Text.
- Imports sparen keinen Kontext, sie werden beim Start mitgeladen.
- Zeigt ein Import aus einer Projektdatei nach außerhalb des Arbeitsverzeichnisses, fragt Claude Code einmal pro Projekt nach einer Freigabe.

```markdown
See @README for project overview and @package.json for available npm commands.

# Additional Instructions
- git workflow @docs/git-instructions.md
- @~/.claude/my-project-instructions.md
```

Ein Import auf eine fehlende Datei wird still ignoriert. Das CLI aus diesem Repo meldet das als [CC004](../regeln.md#cc004).

## HTML-Kommentare für Notizen an Menschen

Block-HTML-Kommentare entfernt Claude Code, bevor der Inhalt in den Kontext geht. Sie kosten also keine Tokens. Kommentare in Codeblöcken bleiben erhalten, und wer die Datei mit dem Read-Tool öffnet, sieht sie weiterhin.

```markdown
<!-- Pflege: Team Plattform. Befehle bei jedem Wechsel des Build-Tools prüfen. -->
## Befehle
- `make test` vor jedem Commit
```

## CLAUDE.md erstellen mit /init

`/init` analysiert die Codebasis und schreibt eine erste CLAUDE.md mit Befehlen, Testanweisungen und erkannten Konventionen. Gibt es schon eine Datei, macht `/init` Verbesserungsvorschläge, statt zu überschreiben. Dabei liest es auch `.cursor/rules/`, `.cursorrules` und `.github/copilot-instructions.md` mit ein.

Mit gesetzter Variable `CLAUDE_CODE_NEW_INIT=1` startet ein interaktiver Ablauf in mehreren Phasen: Er fragt, ob CLAUDE.md, Skills und Hooks eingerichtet werden sollen, erkundet den Code mit einem Subagent, stellt Rückfragen und zeigt einen Vorschlag, bevor Dateien entstehen.

```bash
CLAUDE_CODE_NEW_INIT=1 claude
# in der Sitzung:
# /init
```

Danach von Hand nachschärfen: Was Claude nicht selbst entdecken kann (Fallen, Gründe, Team-Absprachen), ist der wertvollste Teil.

## Was wurde aus dem #-Kurzbefehl?

Früher speicherte eine Zeile, die mit `#` begann, eine Notiz direkt in die CLAUDE.md. Der Changelog von v2.0.70 (15.12.2025) sagt: "Removed # shortcut for quick memory entry (tell Claude to edit your CLAUDE.md instead)". Heute gilt:

- "remember ..." landet in der [Auto Memory](./claude-code-memory.md).
- "add this to CLAUDE.md" lässt Claude die CLAUDE.md bearbeiten.
- `/memory` öffnet die Datei im Editor.

## Beispiele

Alle Beispiele sind vollständige Dateien. Passe Befehle und Pfade an dein Projekt an.

### Beispiel 1: Python-Backend (FastAPI, uv, pytest)

Für ein Backend mit Datenbank-Migrationen und strengem Typcheck.

````markdown
# Bestell-API

REST-API für Bestellungen. FastAPI, PostgreSQL, SQLAlchemy 2, Alembic.

## Befehle

```bash
uv sync                      # Abhängigkeiten installieren
uv run pytest -q             # alle Tests, vor jedem Commit
uv run pytest tests/api -q   # nur API-Tests
uv run ruff check . --fix    # Lint
uv run ruff format .         # Format
uv run mypy src              # Typcheck, muss grün sein
uv run uvicorn app.main:app --reload   # lokal starten
```

## Aufbau

- `src/app/api/` Router, ein Modul pro Ressource
- `src/app/services/` Geschäftslogik, keine HTTP-Objekte hier
- `src/app/db/` Modelle und Session
- `migrations/` Alembic-Revisionen
- `tests/` gleiche Struktur wie `src/app/`

## Konventionen

- Typ-Hinweise überall, auch bei Rückgabewerten.
- Pydantic-Modelle für Ein- und Ausgabe, nie ORM-Objekte zurückgeben.
- Fehler als `HTTPException` nur im Router, im Service eigene Exceptions.
- Neue Funktion heißt neuer Test. Bugfix: erst ein Test, der den Fehler zeigt.

## Grenzen

- Migrationen nur als neue Revision: `uv run alembic revision -m "..."`. Nie eine bestehende Revision ändern.
- Keine echten Kundendaten in Tests. Muster-IBAN `DE89 3704 0044 0532 0130 00`, Mails an `@example.com`.
- Keine neue Abhängigkeit ohne Rückfrage.

## Fallen

- Tests brauchen eine lokale Datenbank: `docker compose up -d db`.
- `uv run` statt `python`, sonst fehlt die virtuelle Umgebung.
````

### Beispiel 2: TypeScript-Frontend (React, Vite, pnpm)

Für ein Frontend mit Komponententests und End-to-End-Tests.

````markdown
# Kundenportal

Single-Page-App für Kunden. React 19, TypeScript strict, Vite, TanStack Query.

## Befehle

```bash
pnpm install          # Abhängigkeiten
pnpm dev              # lokal auf Port 5173
pnpm test             # Vitest, vor jedem Commit
pnpm test:e2e         # Playwright, vor jedem Merge
pnpm lint             # ESLint
pnpm typecheck        # tsc --noEmit, muss grün sein
```

## Aufbau

- `src/features/<feature>/` Komponenten, Hooks und Tests eines Features zusammen
- `src/shared/ui/` wiederverwendbare Komponenten, keine Fachlogik
- `src/api/` generierter API-Client, nicht von Hand ändern

## Konventionen

- Nur Funktionskomponenten, Props als `type`, nicht `interface`.
- Server-Daten über TanStack Query, kein `useEffect` mit `fetch`.
- Texte über `t("key")` aus `src/i18n/`, keine festen Strings in Komponenten.
- Tests mit Testing Library: nach Rolle und Text suchen, nicht nach CSS-Klassen.

## Grenzen

- `src/api/` wird mit `pnpm generate:api` erzeugt. Änderungen dort gehen verloren.
- Keine neuen UI-Bibliotheken ohne Rückfrage.

## Fallen

- `pnpm`, nicht `npm`. Die Lock-Datei ist `pnpm-lock.yaml`.
- Playwright braucht einmal `pnpm exec playwright install`.
````

### Beispiel 3: Monorepo mit Wurzel-Datei und Paket-Dateien

Im Monorepo hält die Wurzel-CLAUDE.md nur das Gemeinsame. Jedes Paket bekommt eine eigene, kurze CLAUDE.md, die Claude Code erst lädt, wenn Claude dort arbeitet.

````markdown
# Plattform-Monorepo

pnpm-Workspace mit Turborepo. Pakete unter `apps/` und `packages/`.

## Befehle

```bash
pnpm install                       # alles installieren
pnpm turbo run test --filter=...[origin/main]   # nur geänderte Pakete testen
pnpm turbo run build --filter=web  # ein Paket bauen
```

## Aufbau

- `apps/web/` Next.js-Frontend, eigene CLAUDE.md
- `apps/api/` Node-Backend, eigene CLAUDE.md
- `packages/ui/` gemeinsame Komponenten
- `packages/config/` ESLint- und TS-Konfiguration für alle

## Regeln für alle Pakete

- Abhängigkeiten zwischen Paketen nur über `workspace:*`.
- Änderungen an `packages/config/` betreffen alle: vorher Plan zeigen.
- Commits mit Scope: `feat(web): ...`, `fix(api): ...`.

@docs/architektur.md
````

Dazu die Paketdatei `apps/api/CLAUDE.md`:

````markdown
# apps/api

Express-Backend. Tests mit Vitest, Datenbank über Prisma.

```bash
pnpm --filter api test
pnpm --filter api prisma migrate dev --name <name>
```

- Prisma-Schema nur in `prisma/schema.prisma` ändern, danach Migration erzeugen.
- Handler geben immer `{ data }` oder `{ error }` zurück.
````

Wer in einem großen Monorepo arbeitet, kann fremde CLAUDE.md-Dateien mit `claudeMdExcludes` ausblenden. Das steht in der Anleitung zu [Rules](./claude-code-rules.md).

### Beispiel 4: Infrastruktur mit Terraform

Bei Infrastruktur zählt vor allem, was Claude nie tun darf. Die harten Verbote stehen zusätzlich als `deny`- oder `ask`-Regel in der settings.json.

````markdown
# Infrastruktur

Terraform für AWS, Umgebungen `dev`, `stage`, `prod`. State in S3 mit DynamoDB-Lock.

## Befehle

```bash
terraform -chdir=envs/dev init
terraform -chdir=envs/dev plan -out=plan.tfplan
terraform fmt -recursive
tflint --recursive
```

## Aufbau

- `modules/` wiederverwendbare Module, eines pro Baustein
- `envs/<umgebung>/` Wurzelmodule, nur Modulaufrufe und Variablen

## Arbeitsweise

- Nur `plan`, nie `apply`. `apply` macht ein Mensch nach Review.
- Jede Änderung an `envs/prod/` braucht einen Plan-Output im PR.
- Neue Ressourcen bekommen die Tags `team`, `kostenstelle`, `umgebung`.
- Provider-Versionen fest pinnen, keine `>=`-Angaben.

## Grenzen

- `*.tfstate` und `*.tfvars` mit Geheimnissen nicht lesen.
- Keine Zugangsdaten in Code. Geheimnisse kommen aus dem Secrets Manager.
- `terraform destroy` und `terraform state rm` nie ausführen.

## Fallen

- `envs/prod/` nutzt ein anderes AWS-Profil als `dev`.
- Module sind versioniert über Git-Tags, nicht über Branches.
````

Passende Regeln in `.claude/settings.json`: `"Read(**/*.tfstate)"` in `deny` und `"Bash(terraform apply *)"` in `ask`, wie in der [Team-Vorlage](../../src/claude_team/vorlage/.claude/settings.json).

### Beispiel 5: Persönliche CLAUDE.local.md

Für eigene Notizen, die nicht ins Repo gehören. Die Datei muss in `.gitignore` stehen.

```markdown
# Meine Notizen (nicht committen)

- Meine lokale Datenbank läuft auf Port 5433, nicht 5432.
- Test-Account: test-user@example.com
- Antworten bitte auf Deutsch.
```

```bash
echo "CLAUDE.local.md" >> .gitignore
```

Wer mit mehreren Git-Worktrees arbeitet, hat die ignorierte `CLAUDE.local.md` nur im Worktree, in dem sie angelegt wurde. Für alle Worktrees besser ein Import aus dem Home-Verzeichnis: `@~/.claude/my-project-instructions.md`.

### Beispiel 6: Zentrale Anweisungen per Managed Settings

Für IT-Abteilungen, die eine Anweisung auf alle Rechner verteilen. Der Key `claudeMd` wirkt nur in Managed Settings.

```json
{
  "claudeMd": "Always run `make lint` before committing.\nNever push directly to main."
}
```

## Schritt für Schritt: CLAUDE.md für ein bestehendes Projekt

1. Im Projekt-Root `claude` starten und `/init` eingeben. Den Vorschlag lesen, nicht blind übernehmen.
2. Befehle prüfen: Jeder Befehl muss so im Terminal funktionieren. Fehlende Befehle ergänzen.
3. Abschnitte anlegen: Befehle, Aufbau, Konventionen, Grenzen, Fallen. Kurze Stichpunkte statt Fließtext.
4. Alles streichen, was Claude aus dem Code ablesen kann.
5. Bereichsregeln in `.claude/rules/` verschieben, zum Beispiel Testregeln mit `paths: ["tests/**"]`.
6. Harte Verbote zusätzlich als `deny`-Regel in `.claude/settings.json` eintragen.
7. `CLAUDE.local.md` in `.gitignore` aufnehmen, falls jemand eine anlegt.
8. Neue Sitzung starten, `/context` aufrufen und prüfen, ob die Datei unter **Memory files** steht.
9. Mit dem Prüf-CLI testen:

```bash
uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team audit .
```

Wer bei null anfängt, nimmt die [Vorlage aus diesem Repo](../../src/claude_team/vorlage/CLAUDE.md). `claude-team einrichten . --dry-run` zeigt, was angelegt würde, und füllt die Befehle aus `package.json`, `pyproject.toml` oder `Makefile`. Eine vorhandene CLAUDE.md wird nie überschrieben, stattdessen entsteht `CLAUDE.vorschlag.md`.

## Was prüft claude-team audit?

| Regel | Stufe | Befund | Lösung |
| --- | --- | --- | --- |
| [CC001](../regeln.md#cc001) | warnung | Weder CLAUDE.md noch AGENTS.md im Projekt | Datei mit `/init` oder der Vorlage anlegen |
| [CC002](../regeln.md#cc002) | warnung | CLAUDE.md hat mehr als 200 Zeilen | Teile nach `.claude/rules/` oder in Skills verschieben |
| [CC003](../regeln.md#cc003) | hinweis | Keine Build- oder Testbefehle erkennbar | Abschnitt "Befehle" mit echten Befehlen ergänzen |
| [CC004](../regeln.md#cc004) | fehler | `@`-Import zeigt auf eine fehlende Datei | Pfad korrigieren, relativ zur importierenden Datei |
| [CC005](../regeln.md#cc005) | fehler | `CLAUDE.local.md` steht nicht in `.gitignore` | Eintrag in `.gitignore` ergänzen |
| [CC006](../regeln.md#cc006) | hinweis | AGENTS.md liegt neben CLAUDE.md und wird nicht gelesen | `@AGENTS.md` in die CLAUDE.md schreiben, siehe [AGENTS.md](./agents-md.md) |

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Datei über 200 Zeilen | Warnung beim Start, Regeln werden ignoriert | Kürzen, Bereichsregeln mit `paths` auslagern |
| Vage Regeln ("sauberen Code schreiben") | Claude verhält sich uneinheitlich | Prüfbare Anweisung mit Befehl oder Pfad |
| Zwei Dateien widersprechen sich | Claude wählt mal so, mal so | Nutzer-, Projekt- und Unterordner-Dateien abgleichen |
| Sicherheitsregel nur in der CLAUDE.md | Claude liest `.env` trotzdem | `deny`-Regel in settings.json, siehe [Permissions](./claude-code-permissions.md) |
| `@`-Import in Backticks | Datei wird nicht geladen | Backticks entfernen |
| Pfad mit Leerzeichen in Anführungszeichen | Import fehlt | Leerzeichen mit Backslash escapen |
| CLAUDE.md und AGENTS.md nebeneinander | AGENTS.md wird nicht gelesen | `@AGENTS.md` importieren |
| Notiz mit `#` am Zeilenanfang | Nichts wird gespeichert | "add this to CLAUDE.md" sagen oder `/memory` |

## Häufige Fragen

### Wie lang sollte eine CLAUDE.md maximal sein?

Unter 200 Zeilen pro Datei, so lautet die Empfehlung in der offiziellen Doku. Längere Dateien verbrauchen mehr Kontext und werden schlechter befolgt. Claude Code warnt beim Start und in `/status`, wenn eine Datei zu lang ist.

### Muss die CLAUDE.md im Projekt-Root liegen?

Nein, `./CLAUDE.md` und `./.claude/CLAUDE.md` funktionieren beide. Dazu kommen Dateien in Unterordnern, die Claude Code lädt, sobald Claude dort Dateien anfasst, und Dateien in Ordnern oberhalb des Arbeitsverzeichnisses, die beim Start geladen werden.

### Liest Claude Code auch eine AGENTS.md?

Ja, ab v2.1.277, aber standardmäßig nur, wenn keine CLAUDE.md und keine CLAUDE.local.md da ist. Wer beide Dateien hat, schreibt `@AGENTS.md` in die CLAUDE.md. Details stehen in der Anleitung [AGENTS.md und CLAUDE.md](./agents-md.md).

### Warum hält sich Claude nicht an meine CLAUDE.md?

Meist ist die Datei nicht geladen, zu lang, zu vage oder widersprüchlich. Prüfe mit `/context`, ob sie unter **Memory files** steht, formuliere konkreter und entferne Widersprüche. Was sicher passieren muss, gehört in einen Hook oder eine Permission-Regel, denn die CLAUDE.md ist nur Kontext.

### Sparen @-Imports Kontext?

Nein. Importierte Dateien werden beim Start vollständig mitgeladen. Imports helfen beim Ordnen. Kontext sparen nur Regeln mit `paths`, Unterordner-Dateien und Skills, weil sie erst bei Bedarf laden.

### Sollte die CLAUDE.md auf Deutsch oder Englisch geschrieben sein?

Beides funktioniert, die Doku schreibt dazu keine Sprache vor. Wichtiger ist eine einheitliche Sprache im Team und dass Befehle, Pfade und Bezeichner genau so dastehen, wie sie im Code heißen.

## Weiterlesen

- [Claude Code Rules: modulare Regeln in .claude/rules](./claude-code-rules.md)
- [AGENTS.md und CLAUDE.md gemeinsam nutzen](./agents-md.md)
- [Claude Code Memory: Kontext, /compact und Sitzungen](./claude-code-memory.md)
- [Claude Code settings.json mit Team-Vorlage](./claude-code-settings-json.md)
- [Claude Code Skills](./claude-code-skills.md)
- Vorlage: [CLAUDE.md](../../src/claude_team/vorlage/CLAUDE.md), Prüfregeln: [CC001 bis CC006](../regeln.md#cc001)
- Offizielle Doku: [How Claude remembers your project](https://code.claude.com/docs/en/memory)
