# Claude Code Rules: modulare Regeln in .claude/rules statt einer riesigen CLAUDE.md

Claude Code Rules sind Markdown-Dateien im Ordner `.claude/rules/`, mit denen du Projektregeln auf mehrere Dateien aufteilst. Eine Regel ohne Frontmatter lädt bei jedem Start wie die CLAUDE.md. Eine Regel mit `paths`-Frontmatter lädt erst, wenn Claude eine passende Datei liest oder bearbeitet, und spart so Kontext. Damit bleibt die CLAUDE.md unter den empfohlenen 200 Zeilen, und Testregeln, API-Regeln oder Migrationsregeln stehen nur dann im Kontext, wenn sie gebraucht werden.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Alle `.md`-Dateien unter `.claude/rules/` werden rekursiv gefunden, Unterordner wie `frontend/` oder `backend/` sind erlaubt.
- `paths` ist das einzige Frontmatter-Feld, das Claude Code in einer Regel auswertet; alle anderen Felder werden still ignoriert.
- Eine Regel mit `paths` lädt, sobald Claude eine passende Datei per Read, Write oder Edit anfasst oder mit `cat` oder `head` liest.
- Brace-Expansion wie `src/**/*.{ts,tsx}` ist erlaubt, mit einem Budget von 1.000 erweiterten Mustern und 4 MiB pro Regel.
- Persönliche Regeln für alle Projekte liegen in `~/.claude/rules/` und laden vor den Projektregeln.
- In Monorepos blendet `claudeMdExcludes` fremde CLAUDE.md-Dateien und Regelordner aus.

## Wie teile ich Projektregeln auf mehrere Dateien auf?

Lege für jedes Thema eine Datei mit sprechendem Namen in `.claude/rules/` an. Die Doku zeigt diesen Aufbau:

```text
your-project/
├── .claude/
│   ├── CLAUDE.md           # Main project instructions
│   └── rules/
│       ├── code-style.md   # Code style guidelines
│       ├── testing.md      # Testing conventions
│       └── security.md     # Security requirements
```

Zwei Arten von Regeln:

| Art | Frontmatter | Lädt | Typischer Inhalt |
| --- | --- | --- | --- |
| Immer aktiv | keins | beim Start, gleiche Priorität wie `.claude/CLAUDE.md` | Code-Stil, Commit-Regeln, Sicherheitsgrundsätze |
| Bereichsregel | `paths` mit Globs | wenn Claude eine passende Datei anfasst | Testregeln, API-Konventionen, Migrationen |

Rules sind trotzdem Kontext und keine Durchsetzung. Für Abläufe, die nur bei Bedarf gebraucht werden, sind [Skills](./claude-code-skills.md) besser: Sie laden erst, wenn du sie aufrufst oder Claude sie für relevant hält.

## paths-Frontmatter: Regeln an Dateien binden

Das Frontmatter steht zwischen zwei `---`-Zeilen am Dateianfang. `paths` nimmt eine YAML-Liste oder einen kommagetrennten String. Claude Code entfernt das Frontmatter, bevor die Regel in den Kontext geht.

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

Typische Muster aus der Doku:

| Muster | Trifft |
| --- | --- |
| `**/*.ts` | alle TypeScript-Dateien in jedem Ordner |
| `src/**/*` | alle Dateien unter `src/` |
| `*.md` | Markdown-Dateien im Projekt-Root |
| `src/components/*.tsx` | React-Komponenten in genau diesem Ordner |

Wann eine Bereichsregel lädt:

- Claude nutzt Read, Write oder Edit auf einer passenden Datei.
- Claude liest eine passende Datei mit einem Bash-Befehl, der als Lesen zählt, etwa `cat` oder `head` auf eine einzelne Datei.
- Das klappt auch über einen symbolisch verlinkten Pfad zum Projektordner.

Wenn das YAML zwischen den Markern nicht parst, ignoriert Claude Code das Frontmatter und lädt die Regel, als hätte sie kein `paths`. Den Parse-Fehler zeigt `claude --debug`.

## Brace-Expansion und das Budget

Mehrere Endungen in einem Muster schreibst du mit geschweiften Klammern:

```markdown
---
paths:
  - "src/**/*.{ts,tsx}"
  - "lib/**/*.ts"
  - "tests/**/*.test.ts"
---
```

Jede Klammergruppe vervielfacht die Zahl der Muster: `src/*.{ts,tsx}` ergibt zwei, `{a,b}/{c,d}/*.{ts,tsx}` ergibt acht. Damit das begrenzt bleibt, teilt sich die ganze `paths`-Liste einer Regel ein Budget von 1.000 erweiterten Mustern und 4 MiB. Muster ohne Klammern zählen nicht mit. Ein Muster, das das Budget sprengen würde, nutzt Claude Code unerweitert, und die wörtlichen Klammern treffen dann keine Datei. Vor v2.1.217 konnte eine Liste mit vielen Klammergruppen den Start blockieren.

Eckige Klammern leiten in Glob-Syntax eine Zeichenklasse wie `[abc]` ein. Ein Muster wie `photos [2024/**` ist ungültig und trifft nichts. Für ein wörtliches `[` escapest du: `photos \[2024/**`.

## Regeln teilen: Symlinks und ~/.claude/rules

**Symlinks:** `.claude/rules/` unterstützt symbolische Links, Kreise werden erkannt. So pflegt ein Team einen gemeinsamen Regelsatz und verlinkt ihn in mehrere Projekte:

```bash
ln -s ~/shared-claude-rules .claude/rules/shared
ln -s ~/company-standards/security.md .claude/rules/security.md
```

Zeigt der Link nach außerhalb des Arbeitsverzeichnisses, behandelt Claude Code ihn wie einen externen `@`-Import: Die Regeln laden erst nach einer Freigabe, die einmal pro Projekt beim Start abgefragt wird, und danach nur die Regeln ohne `paths`. Links auf Netzwerkpfade wie `\\server\share`, `/net` oder `/Network` folgt Claude Code gar nicht.

**Nutzerregeln:** Persönliche Regeln in `~/.claude/rules/` gelten in jedem Projekt auf deinem Rechner und brauchen keine Freigabe. Sie laden vor den Projektregeln. Keine Seite überschreibt die andere; bei einem Widerspruch kann Claude beiden folgen, also beide Sätze widerspruchsfrei halten.

```text
~/.claude/rules/
├── preferences.md    # Your personal coding preferences
└── workflows.md      # Your preferred workflows
```

## claudeMdExcludes für Monorepos

In großen Monorepos lädt Claude Code CLAUDE.md-Dateien aus übergeordneten Ordnern, die für dein Team nicht passen. Mit `claudeMdExcludes` schließt du Dateien per Pfad oder Glob aus. Die Muster gelten gegen absolute Pfade.

- Setzbar in jeder Settings-Ebene: Nutzer, Projekt, lokal, Managed. Die Listen werden zusammengeführt.
- Eine Managed-CLAUDE.md lässt sich nicht ausschließen.
- Regeln, die über einen Symlink erreichbar sind, schließt ein Muster auf den Pfad unter `.claude/rules/` oder auf das Link-Ziel aus (vor v2.1.239 nur auf das Ziel).

Weitere Grenzen:

- Wer Claude Code mit `--setting-sources` ohne `project` startet, bekommt keine Projektregeln.
- Ordner aus `--add-dir` liefern ihre Regeln nur mit `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`.

## Beispiele

### Beispiel 1: Testregeln

Lädt nur, wenn Claude an Tests arbeitet. Das ist die Regel aus der [Vorlage dieses Repos](../../src/claude_team/vorlage/.claude/rules/tests.md).

```markdown
---
paths:
  - "tests/**/*"
  - "**/*.test.{ts,tsx,js}"
  - "**/test_*.py"
---

# Regeln für Tests

- Ein Test prüft ein Verhalten. Name sagt, was erwartet wird: `test_leere_liste_ergibt_null`.
- Keine echten Personendaten. Muster-IBAN `DE89 3704 0044 0532 0130 00`, Mails an `@example.com`.
- Kein Netzwerk in Unit-Tests. Externe Dienste mocken.
- Einen fehlschlagenden Test nie löschen oder auf skip setzen, um grün zu werden. Ursache melden.
```

### Beispiel 2: API-Regeln für ein Backend

Für Handler und Router. Der kommagetrennte String ist eine erlaubte Alternative zur Liste.

```markdown
---
paths: "src/api/**/*.py, src/schemas/**/*.py"
---

# API-Regeln

- Jeder Endpunkt validiert die Eingabe mit einem Pydantic-Modell.
- Fehlerantworten immer im Format `{"error": {"code": "...", "message": "..."}}`.
- Neue Endpunkte bekommen einen Eintrag in `docs/api.md` und einen Test in `tests/api/`.
- Keine Datenbankabfragen im Router, nur Aufrufe aus `src/services/`.
```

### Beispiel 3: Datenbank-Migrationen

Schützt vor dem häufigsten Fehler: eine bestehende Migration nachträglich ändern.

```markdown
---
paths:
  - "migrations/**/*"
  - "**/alembic/versions/*.py"
  - "prisma/migrations/**"
---

# Migrationen

- Bestehende Migrationen nie ändern. Jede Änderung ist eine neue Datei.
- Jede Migration hat einen funktionierenden Rückweg (`downgrade` bzw. `down`).
- Spalten erst nullable anlegen, befüllen, dann `NOT NULL` setzen, in getrennten Migrationen.
- Keine Daten löschen ohne ausdrückliche Freigabe im Prompt.
```

Wichtig: Wenn Migrationen technisch tabu sein sollen, kommt zusätzlich eine `ask`-Regel wie `"Edit(migrations/**)"` in die settings.json. Die Regel hier ist nur Kontext.

### Beispiel 4: Frontend-Komponenten

Für React-Komponenten mit Brace-Expansion über zwei Endungen.

```markdown
---
paths:
  - "src/components/**/*.{ts,tsx}"
  - "src/features/**/*.{ts,tsx}"
---

# Frontend-Regeln

- Nur Funktionskomponenten, Props als `type`.
- Barrierefreiheit: jedes interaktive Element ist per Tastatur bedienbar und hat einen zugänglichen Namen.
- Farben und Abstände nur aus `src/shared/theme.ts`, keine festen Pixelwerte.
- Neue Komponente heißt neue Story in `*.stories.tsx`.
```

### Beispiel 5: Sicherheitsregeln ohne paths

Gilt immer, deshalb ohne Frontmatter. Ergänzt die `deny`-Regeln in der settings.json, ersetzt sie aber nicht.

```markdown
# Sicherheit

- Keine Zugangsdaten, Tokens oder Passwörter in Code, Tests, Logs oder Commits.
- Neue Umgebungsvariablen in `.env.example` mit Platzhalterwert eintragen.
- SQL nur mit Parametern, nie mit String-Verkettung.
- Nutzereingaben vor der Ausgabe in HTML escapen.
- Bei Verdacht auf ein Sicherheitsproblem: stoppen und melden, nicht still beheben.
```

### Beispiel 6: Terraform und Infrastruktur

Lädt nur bei Infrastrukturdateien.

```markdown
---
paths:
  - "**/*.tf"
  - "**/*.tfvars"
---

# Terraform

- Nur `terraform plan`, nie `apply` oder `destroy`.
- Jede Ressource bekommt die Tags `team`, `kostenstelle`, `umgebung`.
- Provider-Versionen fest pinnen.
- Nach jeder Änderung `terraform fmt -recursive` ausführen.
```

### Beispiel 7: Fremde Team-Dateien im Monorepo ausblenden

Gehört in `.claude/settings.local.json`, damit der Ausschluss nur für dich gilt.

```json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

### Beispiel 8: Vendor-Ordner für alle ausschließen

In `.claude/settings.json` committet, damit kein CLAUDE.md aus eingebundenem Fremdcode geladen wird.

```json
{
  "claudeMdExcludes": ["**/vendor/**/CLAUDE.md"]
}
```

## Schritt für Schritt: eine zu lange CLAUDE.md aufteilen

1. Die CLAUDE.md durchgehen und jede Regel markieren: gilt sie überall oder nur für bestimmte Dateien?
2. Ordner anlegen: `mkdir -p .claude/rules`.
3. Für jedes Thema eine Datei anlegen, zum Beispiel `tests.md`, `api.md`, `migrations.md`.
4. Bereichsregeln mit `paths` versehen. Muster in Anführungszeichen setzen, damit YAML `*` und `{` nicht falsch liest.
5. Allgemeine Regeln ohne Frontmatter lassen oder in der CLAUDE.md behalten.
6. Die verschobenen Abschnitte aus der CLAUDE.md löschen.
7. Neue Sitzung starten und `/context` aufrufen: Regeln ohne `paths` müssen unter **Memory files** stehen.
8. Eine passende Datei lesen lassen ("Lies tests/test_export.py") und prüfen, ob die Bereichsregel jetzt geladen ist.
9. Mit `claude-team audit .` prüfen, ob die CLAUDE.md jetzt unter 200 Zeilen liegt ([CC002](../regeln.md#cc002)).

Zum Debuggen eignet sich der Hook `InstructionsLoaded`: Er feuert, wenn eine CLAUDE.md oder Regeldatei geladen wird, und liefert unter anderem `file_path`, `load_reason` (zum Beispiel `path_glob_match`) und `globs`. Details in der Anleitung zu [Hooks](./claude-code-hooks.md).

## Was passiert mit Regeln nach /compact?

Regeln ohne `paths` liest Claude Code nach einer Komprimierung neu von der Platte ein. Bereichsregeln dagegen landen beim Laden im Gesprächsverlauf und werden mit zusammengefasst. Sie laden erst wieder, wenn Claude die nächste passende Datei anfasst. Muss eine Regel sicher über `/compact` hinweg gelten, nimm das `paths` heraus oder verschiebe sie in die CLAUDE.md im Projekt-Root.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Weitere Frontmatter-Felder wie `description` | werden ignoriert, kein Fehler | nur `paths` nutzen |
| Kaputtes YAML im Frontmatter | Regel lädt immer statt nur bei passenden Dateien | `claude --debug`, Muster in Anführungszeichen |
| Zu viele Klammergruppen | Muster trifft keine Datei | Gruppen reduzieren, mehrere einfache Muster schreiben |
| Symlink auf Ordner außerhalb des Projekts | Regeln mit `paths` laden nicht | Regeln in `~/.claude/rules/` oder ins Projekt kopieren |
| Bereichsregel für Pflichtverhalten | gilt nach `/compact` nicht mehr | ohne `paths` anlegen oder Hook nutzen |
| Nutzer- und Projektregel widersprechen sich | Claude folgt mal der einen, mal der anderen | beide Sätze abgleichen |
| Regeln als Ersatz für deny-Regeln | Claude tut es trotzdem | Verbote in `permissions.deny` |

## Häufige Fragen

### Was ist der Unterschied zwischen CLAUDE.md und .claude/rules?

Eine Regel ohne `paths` verhält sich wie ein Teil der CLAUDE.md und lädt bei jedem Start. Der Vorteil von `.claude/rules/` sind die Bereichsregeln mit `paths`, die nur laden, wenn Claude passende Dateien anfasst, und die bessere Ordnung bei vielen Themen.

### Welche Frontmatter-Felder kennen Claude Code Rules?

Nur `paths`. Laut Doku ist es das einzige Feld, das Claude Code in einer Regel liest; alle anderen Felder werden ohne Fehlermeldung ignoriert.

### Funktionieren Rules auch in Unterordnern von .claude/rules?

Ja. Claude Code findet alle `.md`-Dateien unter `.claude/rules/` rekursiv, Unterordner wie `frontend/` oder `backend/` sind ausdrücklich vorgesehen.

### Wie teile ich Regeln zwischen mehreren Repos?

Entweder per Symlink in `.claude/rules/` oder über `~/.claude/rules/` für alle eigenen Projekte. Bei Symlinks nach außerhalb des Projekts fragt Claude Code einmal nach einer Freigabe und lädt dann nur Regeln ohne `paths`.

### Kann eine Regel etwas verbieten?

Nein, Regeln sind Anweisungen an das Modell und keine technische Sperre. Was sicher verhindert werden muss, gehört als `deny`-Regel in die settings.json oder in einen PreToolUse-Hook.

## Weiterlesen

- [CLAUDE.md: Aufbau, Beispiele und Best Practices](./claude-md.md)
- [AGENTS.md und CLAUDE.md](./agents-md.md)
- [Claude Code Skills](./claude-code-skills.md)
- [Claude Code Hooks](./claude-code-hooks.md)
- [Claude Code Permissions](./claude-code-permissions.md)
- Vorlage: [.claude/rules/tests.md](../../src/claude_team/vorlage/.claude/rules/tests.md)
- Offizielle Doku: [Organize rules with .claude/rules](https://code.claude.com/docs/en/memory)
