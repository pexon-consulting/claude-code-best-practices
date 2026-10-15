# Claude Code Skills: eigene Skills erstellen, testen und im Team teilen

Claude Code Skills sind Ordner mit einer Datei `SKILL.md`, die Anweisungen für eine wiederkehrende Aufgabe enthält und per `/name` oder automatisch durch Claude geladen wird. Einen Skill für ein Projekt legst du unter `.claude/skills/<name>/SKILL.md` an, einen persönlichen unter `~/.claude/skills/<name>/SKILL.md`. Den Kopf bildet ein YAML-Frontmatter mit `description`, darunter folgen die Anweisungen in Markdown.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Ein Skill ist ein Ordner mit `SKILL.md`, der Ordnername wird zum Befehl `/name`.
- Die `description` entscheidet, wann Claude einen Skill von selbst lädt. Sie sollte deshalb die Wörter enthalten, die Menschen tatsächlich tippen.
- Mit `disable-model-invocation: true` startet nur ein Mensch den Skill, das ist Pflicht für Commits, Deployments und alles mit Nebenwirkungen.
- Seit v2.1.3 sind Slash-Commands und Skills zusammengeführt, `.claude/commands/*.md` funktioniert weiter, für Neues sind Skills besser.
- Die Doku empfiehlt höchstens 500 Zeilen pro `SKILL.md`, Details gehören in Zusatzdateien im selben Ordner.
- Im Team verteilst du Skills über das Repo (`.claude/skills/`), über ein Plugin oder über Managed Settings.

## Wo liegt die SKILL.md?

| Ort | Pfad | Gilt für |
| --- | --- | --- |
| Enterprise | `.claude/skills/<name>/SKILL.md` im Managed-Settings-Verzeichnis | alle Nutzer auf verwalteten Rechnern |
| Persönlich | `~/.claude/skills/<name>/SKILL.md` | alle eigenen Projekte auf diesem Rechner |
| Projekt | `.claude/skills/<name>/SKILL.md` | dieses Repository, wird mit committet |
| Verschachtelt | `<unterordner>/.claude/skills/<name>/SKILL.md` | Sitzungen in diesem Unterordner, z.B. im Monorepo |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | überall, wo das Plugin aktiv ist, Aufruf als `/plugin-name:skill-name` |
| claude.ai-Konto | synchronisiert nach `~/.claude/skills/synced/` (ab v2.1.273) | dein Konto |

Bei gleichem Namen gilt: Enterprise vor persönlich vor Projekt. Ein Skill schlägt eine Datei in `.claude/commands/` mit gleichem Namen. Die Ordnernamen `synced` und `anthropic-skills` sind reserviert. Änderungen in bestehenden Skill-Ordnern lädt Claude Code live nach. Einen ganz neuen Skill-Ordner machst du mit `/reload-skills` bekannt.

## Wie sieht eine SKILL.md aus?

Zwischen den `---`-Markern am Dateianfang steht das Frontmatter, danach der Inhalt. Das kleinste sinnvolle Beispiel:

```markdown
---
name: tests-schreiben
description: Schreibt fehlende Unit-Tests für geänderte Dateien. Nutzen, wenn nach Tests, Testabdeckung oder pytest gefragt wird.
---

Lies `git diff --name-only` und schreibe für jede geänderte Funktion ohne Test einen Test im bestehenden Stil.
Führe danach die Tests aus und berichte das Ergebnis in drei Sätzen.
```

Das Frontmatter muss in Zeile 1 beginnen, sonst wird die ganze Datei als Inhalt gelesen. Ist das YAML kaputt, lädt der Skill ohne Felder: `/name` geht dann noch, aber Claude findet ihn nicht automatisch.

## Frontmatter-Felder im Überblick

Alle Felder sind optional, empfohlen ist `description`. Unbekannte Felder ignoriert Claude Code ohne Fehlermeldung, Tippfehler fallen also nicht auf.

| Feld | Bedeutung |
| --- | --- |
| `name` | Befehlsname im `/`-Menü, Standard ist der Ordnername |
| `description` | was der Skill tut und wann, Grundlage für die automatische Auswahl |
| `when_to_use` | zusätzliche Auslöser, wird an `description` angehängt |
| `argument-hint` | Hinweis in der Autovervollständigung, z.B. `[issue-nummer]` |
| `arguments` | benannte Positionsargumente für `$name`, als Liste oder durch Leerzeichen getrennt |
| `disable-model-invocation` | `true`: nur manueller Aufruf, Beschreibung steht nicht im Kontext |
| `user-invocable` | `false`: nur Claude ruft auf, nicht im `/`-Menü |
| `allowed-tools` | Tools ohne Rückfrage, nur für den Turn, der den Skill aufruft |
| `disallowed-tools` | Tools, die während des Skills entfernt werden |
| `model` | Modell für den Rest des Turns, oder `inherit` |
| `effort` | `low`, `medium`, `high`, `xhigh` oder `max` |
| `context` | `fork`: läuft in einem eigenen Subagent |
| `agent` | Subagent-Typ bei `context: fork` |
| `background` | nur mit `fork`, `false` wartet auf das Ergebnis (ab v2.1.218) |
| `hooks` | Hooks, die ab dem Aufruf bis zum Ende der Sitzung gelten |
| `paths` | Globs, die das automatische Laden auf passende Dateien begrenzen |
| `shell` | `bash` (Standard) oder `powershell` für `!`-Befehle |
| `metadata` | freie Map für eigene Werkzeuge |
| `license`, `compatibility` | aus der Agent-Skills-Spezifikation, werden nicht ausgewertet |

`description` und `when_to_use` zusammen werden in der Skill-Liste nach 1.536 Zeichen abgeschnitten. Die ganze Liste darf etwa 1 % des Kontextfensters belegen. Den wichtigsten Anwendungsfall deshalb an den Anfang der `description` stellen. Boolesche Felder akzeptieren ab v2.1.218 auch `yes`, `no`, `on`, `off`, `1` und `0`.

## Wann ruft Claude einen Skill auf?

| Frontmatter | Du rufst auf | Claude ruft auf | Im Kontext |
| --- | --- | --- | --- |
| Standard | ja | ja | Beschreibung immer, Inhalt beim Aufruf |
| `disable-model-invocation: true` | ja | nein | Beschreibung nicht |
| `user-invocable: false` | nein | ja | Beschreibung immer |

- `/name` am Anfang der Nachricht führt den Skill direkt aus. Mitten im Text gilt `/name` nur als Erlaubnis, Claude entscheidet dann selbst.
- Mehrere Skills lassen sich am Anfang stapeln (der erste plus bis zu fünf weitere): `/tests-schreiben /commit fix login` gibt den Rest als Argument an alle.
- Ein geladener Skill bleibt im Kontext. Nach einer Auto-Compaction hängt Claude Code je Skill die ersten 5.000 Tokens wieder an, zusammen höchstens 25.000 Tokens. Wichtige Anweisungen gehören deshalb nach oben.
- Regeln, die jedes Mal gelten müssen, gehören in einen [Hook](./claude-code-hooks.md), nicht nur in einen Skill.

## Argumente: $ARGUMENTS, $0 und benannte Platzhalter

| Platzhalter | Bedeutung |
| --- | --- |
| `$ARGUMENTS` | alles nach dem Skill-Namen; fehlt ein Platzhalter, hängt Claude Code `ARGUMENTS: <wert>` an |
| `$ARGUMENTS[0]` oder `$0` | erstes Argument, die Zählung beginnt bei 0 |
| `$1` | zweites Argument |
| `$name` | benanntes Argument aus `arguments` |
| `${CLAUDE_SKILL_DIR}` | Ordner der SKILL.md, für mitgelieferte Skripte |
| `${CLAUDE_PROJECT_DIR}` | Projektordner |
| `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` | Sitzungs-ID und Effort-Stufe |

Argumente mit Leerzeichen setzt du in Anführungszeichen: `/migration "users tabelle" postgres` macht `$0` zu `users tabelle`. Ein Dollarzeichen vor einer Ziffer im Fließtext schreibst du als `\$1.00`.

## Dynamischer Kontext mit !`befehl`

Steht `` !`befehl` `` im Skill, führt Claude Code den Befehl aus, bevor der Skill an das Modell geht, und setzt die Ausgabe an diese Stelle. Für mehrere Zeilen gibt es einen Codeblock, der mit ` ```! ` beginnt.

- Schlägt ein Befehl fehl (Exit ungleich 0), bricht der ganze Skill-Aufruf ab. Hänge `|| true` an Befehle, die absichtlich mit Fehler enden können.
- Beim Rendern gibt es keine Rückfrage. Was keine allow-Regel hat, bricht mit `Shell command permission check failed` ab. Gib die Befehle deshalb in `allowed-tools` frei.
- `allowed-tools` wirkt auch in nie vertrauten Ordnern mit `-p`. Prüfe deshalb die `allowed-tools` fremder Skills, bevor du Claude Code in einem fremden Repo startest.
- Zentral abschalten lässt sich das mit `"disableSkillShellExecution": true`, sinnvoll in Managed Settings. Synchronisierte Skills aus claude.ai führen `!`-Befehle nie aus (ab v2.1.228).

## Zusatzdateien statt einer langen SKILL.md

Die Doku empfiehlt, eine `SKILL.md` unter 500 Zeilen zu halten (Regel [CC043](../regeln.md#cc043)). Lange Referenzen, Beispiele und Skripte liegen daneben und werden aus der SKILL.md verlinkt. Claude liest sie nur bei Bedarf. Skripte rufst du über `${CLAUDE_SKILL_DIR}` auf, dann stimmt der Pfad unabhängig vom Arbeitsordner.

```text
.claude/skills/review-checkliste/
├── SKILL.md
├── checkliste.md
├── beispiele.md
└── scripts/check.py
```

## Beispiele

### Beispiel 1: commit nach Conventional Commits

Der Skill aus der [Vorlage](../../src/claude_team/vorlage/.claude/skills/commit/SKILL.md), hier leicht gekürzt. Nur manuell aufrufbar, git-Befehle sind für den Turn freigegeben.

```markdown
---
name: commit
description: Staged die aktuellen Änderungen und schreibt eine Commit-Nachricht nach Conventional Commits. Nur aufrufen, wenn der Nutzer committen will.
disable-model-invocation: true
argument-hint: "[kurze Beschreibung]"
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git add *) Bash(git commit *) Bash(git log *)
---

## Stand

!`git status --short`

!`git log -5 --format=%s`

## Auftrag

1. Änderungen lesen (`git diff`, `git diff --staged`).
2. Gehören sie zu mehr als einem Thema, schlage getrennte Commits vor und frage nach.
3. Nur Dateien stagen, die zum Thema gehören. Nie `.env`, Schlüssel, Protokolle oder Build-Ordner.
4. Nachricht: `typ(bereich): was sich ändert` im Imperativ, höchstens 72 Zeichen.
5. Committen. Nicht pushen.

Hinweis des Nutzers: $ARGUMENTS
```

Aufruf: `/commit login-fehler behoben`.

### Beispiel 2: handoff vor /clear oder Feierabend

Aus der [Vorlage](../../src/claude_team/vorlage/.claude/skills/handoff/SKILL.md), gekürzt. Schreibt den Stand so auf, dass eine neue Sitzung ohne Kontextverlust weitermacht.

```markdown
---
name: handoff
description: Schreibt eine Übergabe der laufenden Arbeit nach docs/handoff.md, damit eine neue Sitzung oder ein Kollege ohne Kontextverlust weitermacht. Aufrufen vor /clear, vor Feierabend oder bei vollem Kontext.
disable-model-invocation: true
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git branch *)
---

## Stand

!`git branch --show-current`

!`git status --short`

## Auftrag

Schreibe `docs/handoff.md` neu mit den Abschnitten Ziel, Erledigt, Offen, Entscheidungen, Fallen und Prüfen.
Keine Secrets, keine Kundendaten. Höchstens 60 Zeilen.
```

### Beispiel 3: release-notes aus den letzten Commits

Für Teams, die Release Notes von Hand schreiben. Die Version kommt als Argument.

```markdown
---
name: release-notes
description: Schreibt Release Notes für eine neue Version aus den Commits seit dem letzten Tag. Nutzen beim Vorbereiten eines Releases.
disable-model-invocation: true
argument-hint: "[version]"
allowed-tools: Bash(git log *) Bash(git tag *) Bash(git describe *)
---

## Letzte Commits

!`git log -40 --format='%h %s'`

## Auftrag

1. Finde mit `git describe --tags --abbrev=0` den letzten Tag und nimm nur Commits danach.
2. Gruppiere nach Neu (feat), Behoben (fix) und Sonstiges. chore und ci weglassen.
3. Schreibe für Anwender, nicht für Entwickler: was ändert sich für sie.
4. Überschrift: `## Version $0`. Schreibe das Ergebnis an den Anfang von `CHANGELOG.md`.
```

Aufruf: `/release-notes 1.4.0`.

### Beispiel 4: review-checkliste als Hintergrundwissen

Diesen Skill ruft nur Claude auf, wenn es um Reviews geht. Die eigentliche Liste steht in einer Zusatzdatei.

```markdown
---
name: review-checkliste
description: Team-Checkliste für Code-Reviews mit Punkten zu Sicherheit, Tests, Logging und personenbezogenen Daten. Laden, wenn Code geprüft, ein Pull Request bewertet oder ein Review geschrieben wird.
user-invocable: false
---

Wende bei jedem Review die Punkte aus [checkliste.md](checkliste.md) an.
Melde Befunde mit Datei und Zeile, sortiert nach muss, sollte, kann.
Nichts melden, was der Linter schon findet.
```

### Beispiel 5: migration mit benannten Argumenten

Für Datenbank-Migrationen mit festem Ablauf. `arguments` macht die Platzhalter lesbar.

```markdown
---
name: migration
description: Legt eine Datenbank-Migration mit Up- und Down-Schritt an und prüft sie lokal. Nutzen, wenn eine Tabelle oder Spalte geändert werden soll.
disable-model-invocation: true
argument-hint: "[tabelle] [beschreibung]"
arguments: [tabelle, beschreibung]
effort: high
---

Lege eine Migration für die Tabelle $tabelle an: $beschreibung

1. Lies die letzten drei Migrationen und übernimm deren Stil und Namensschema.
2. Schreibe Up und Down. Down muss Up vollständig zurücknehmen.
3. Keine Daten löschen ohne Rückfrage. Bei DROP oder Typänderung vorher fragen.
4. Führe die Migration lokal hoch und wieder runter und berichte das Ergebnis.
```

Aufruf: `/migration users "Spalte last_login als timestamp ergänzen"`.

### Beispiel 6: Recherche in einem eigenen Subagent

Mit `context: fork` läuft der Skill isoliert im Explore-Agent und liefert nur die Zusammenfassung zurück.

```markdown
---
name: recherche
description: Untersucht eine Frage zum Code gründlich und fasst das Ergebnis mit Dateiverweisen zusammen.
context: fork
agent: Explore
---

Untersuche $ARGUMENTS gründlich:

1. Relevante Dateien mit Glob und Grep finden.
2. Den Code lesen und verstehen.
3. Ergebnis mit konkreten Dateiverweisen zusammenfassen.
```

## Schritt für Schritt: ersten Skill anlegen und testen

1. Ordner anlegen: `mkdir -p .claude/skills/tests-schreiben`.
2. `SKILL.md` mit Frontmatter und Anweisungen schreiben, wie im Beispiel oben.
3. In der laufenden Sitzung `/reload-skills` ausführen, wenn der Ordner neu ist.
4. Mit `/skills` prüfen, ob der Skill in der Liste steht.
5. Direkt aufrufen: `/tests-schreiben`. Funktioniert das nicht, mit `claude plugin validate .claude/skills` das Frontmatter prüfen (ab v2.1.233) oder `/skill-doctor` nutzen (ab v2.1.252).
6. Automatische Auslösung testen: eine Bitte formulieren, die zur `description` passt, ohne den Namen zu nennen.
7. Löst der Skill zu oft aus, die `description` enger fassen oder `disable-model-invocation: true` setzen.
8. Mit `claude-team audit .` prüfen, ob jeder Skill eine `description` hat (Regel [CC042](../regeln.md#cc042)).
9. Den Ordner committen, damit das Team ihn bekommt.

## Skills im Team teilen

| Weg | Wie | Passt für |
| --- | --- | --- |
| Repo | `.claude/skills/` committen | ein Projekt, alle im Team |
| Plugin | Ordner `skills/` in einem Plugin, verteilt über einen Marketplace | viele Repos, versioniert |
| Managed Settings | im Managed-Settings-Verzeichnis | ganze Organisation |

Die Skills dieses Repos (`claude-code-audit`, `claude-code-einrichten`, `claude-md-schreiben`, `hook-schreiben`) installierst du mit:

```bash
npx skills add pexon-consulting/claude-code-best-practices
```

Claude Code folgt dem offenen Standard [Agent Skills](https://agentskills.io). Wer einen Skill auch in anderen Werkzeugen oder für den Upload nach claude.ai nutzen will, beschränkt das Frontmatter auf `name`, `description`, `license`, `compatibility`, `metadata` und `allowed-tools`. Alle anderen Felder sind Erweiterungen von Claude Code.

Einzelne Skills lassen sich über Berechtigungen steuern: `Skill(commit)` trifft genau einen Skill, `Skill(review *)` alle mit diesem Anfang. Eine deny-Regel auf `Skill` schaltet Skills ganz ab.

## Skills und alte Slash-Commands

Seit v2.1.3 (09.01.2026) sind Slash-Commands und Skills zusammengeführt. Dateien unter `.claude/commands/*.md` funktionieren weiter und kennen dasselbe Frontmatter außer `name` und `paths`. Unterordner werden mit `:` getrennt, aus `.claude/commands/frontend/component.md` wird `/frontend:component`. Für neue Befehle sind Skills besser, weil sie Zusatzdateien mitbringen können.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Frontmatter beginnt nicht in Zeile 1 | Felder werden ignoriert | `---` ganz an den Anfang |
| vage `description` | Claude nutzt den Skill nie | Suchwörter und Anwendungsfall nach vorn |
| Commit-Skill ohne `disable-model-invocation` | Claude committet ungefragt | Feld auf `true` setzen |
| `!`-Befehl ohne Freigabe | Skill bricht mit Permission-Fehler ab | Befehl in `allowed-tools` aufnehmen |
| `!`-Befehl endet mit Exit 1 | ganzer Skill bricht ab | `\|\| true` anhängen |
| `$1` für das erste Argument | falsches Argument eingesetzt | `$0` ist das erste, `$1` das zweite |
| neuer Ordner während der Sitzung | `/name` unbekannt | `/reload-skills` |

## Häufige Fragen

### Was ist der Unterschied zwischen Skills und Slash Commands?

Seit v2.1.3 sind beide dasselbe System. Ein Skill ist ein Ordner mit `SKILL.md` und optionalen Zusatzdateien, ein alter Command ist eine einzelne Datei in `.claude/commands/`. Beide erscheinen als `/name`.

### Wie verhindere ich, dass Claude einen Skill von selbst startet?

Setze `disable-model-invocation: true` ins Frontmatter. Dann startet der Skill nur, wenn du `/name` tippst, und seine Beschreibung belegt keinen Kontext.

### Wie lang darf eine SKILL.md sein?

Die Doku empfiehlt unter 500 Zeilen. Längere Referenzen gehören in Zusatzdateien im Skill-Ordner, die Claude bei Bedarf liest.

### Wo finde ich die eingebauten Skills?

`/skills` listet alle verfügbaren Skills. Eingebaut sind unter anderem `/code-review`, `/doctor`, `/loop` und `/simplify`.

### Was ist der Unterschied zwischen einem Skill und einem Subagent?

Ein Skill läuft standardmäßig im Hauptgespräch und bringt Anweisungen mit. Ein Subagent hat einen eigenen Kontext, eigene Tools und liefert nur eine Zusammenfassung zurück. Mit `context: fork` lässt sich ein Skill in einem Subagent ausführen.

### Kann ein Skill Tools sperren?

Ja, mit `disallowed-tools` für die Dauer des Skills. `allowed-tools` gibt dagegen nur frei und schränkt nichts ein.

## Weiterlesen

- [Claude Code Subagents](./claude-code-subagents.md): eigene Agenten mit eigenem Kontext
- [Claude Code Plugins](./claude-code-plugins.md): Skills versioniert im Team verteilen
- [Claude Code Befehle](./claude-code-befehle.md): eingebaute Slash Commands im Überblick
- [Claude Code Hooks](./claude-code-hooks.md): Regeln, die immer greifen müssen
- [CLAUDE.md](./claude-md.md): was in die Projektanweisungen gehört und was in einen Skill
- Vorlagen: [commit](../../src/claude_team/vorlage/.claude/skills/commit/SKILL.md), [handoff](../../src/claude_team/vorlage/.claude/skills/handoff/SKILL.md)
- Offizielle Doku: [Skills](https://code.claude.com/docs/en/skills)
