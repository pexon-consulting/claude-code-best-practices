# Claude Code Workflow: Erkunden, Planen, Umsetzen, Committen

Der Claude Code Workflow, den die offizielle Doku empfiehlt, hat vier Phasen: im Plan Mode erkunden, einen Plan schreiben lassen, umsetzen und gegen Tests prüfen, dann committen. Der wichtigste Einzelhebel ist, Claude eine Möglichkeit zu geben, die eigene Arbeit zu prüfen, etwa mit Tests, Screenshots oder einem Prüfbefehl. Dazu kommen kleine Schritte, `/clear` zwischen Aufgaben und Subagents für Recherche, damit der Kontext sauber bleibt.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Erkunden und Planen trennen Recherche von Umsetzung; das verhindert, dass Claude das falsche Problem löst.
- Bei kleinen Änderungen, die sich in einem Satz beschreiben lassen, kannst du den Plan überspringen.
- Gib Claude ein Prüfkriterium: Tests, erwartete Ausgabe, Screenshot-Vergleich oder einen Stop-Hook.
- Der Kontext ist die knappste Ressource; `/clear` zwischen unabhängigen Aufgaben und nach zwei gescheiterten Korrekturen.
- Subagents erledigen Recherche in eigenem Kontext und halten die Hauptsitzung schlank.
- Ein zweiter Blick per Review-Subagent oder frischer Sitzung findet, was der Autor übersieht.

## Welcher Arbeitsablauf funktioniert mit Claude Code am besten?

### Phase 1: Erkunden im Plan Mode

Im Plan Mode liest Claude Dateien und beantwortet Fragen, ändert aber nichts. Wechseln mit Shift+Tab, bis unten `plan mode on` steht, oder direkt mit `claude --permission-mode plan`. Für eine einzelne Aufgabe reicht `/plan <beschreibung>`.

```text
Lies src/auth und erkläre, wie Sessions und Login funktionieren.
Schau auch, wie wir Umgebungsvariablen für Geheimnisse verwalten.
```

### Phase 2: Planen

Lass einen konkreten Plan schreiben. Mit Ctrl+G öffnest du ihn im Editor und kannst ihn direkt ändern, bevor Claude weitermacht.

```text
Ich will Google-OAuth ergänzen. Welche Dateien müssen sich ändern?
Wie läuft der Session-Ablauf? Schreib einen Plan.
```

### Phase 3: Umsetzen und prüfen

Zurück in den normalen Modus wechseln und Claude gegen den Plan arbeiten lassen:

```text
Setze den OAuth-Ablauf aus dem Plan um. Schreib Tests für den Callback-Handler,
führe die Testsuite aus und behebe alle Fehler.
```

### Phase 4: Committen

```text
Committe mit einer aussagekräftigen Nachricht und öffne einen PR.
```

Wann sich der Plan lohnt: wenn du unsicher über den Ansatz bist, wenn die Änderung mehrere Dateien betrifft oder wenn du den Code nicht kennst. Für einen Tippfehler, eine Logzeile oder eine umbenannte Variable lass Claude direkt arbeiten. Mehr in [Claude Code Plan Mode](./claude-code-plan-mode.md).

## Wie sorge ich dafür, dass Claude sein Ergebnis prüft?

Die Doku nennt das den wirkungsvollsten Einzelschritt: Ohne Prüfkriterium liefert Claude etwas, das richtig aussieht, und du bist die einzige Rückkopplung.

| Prüfweg | Wann | Beispiel-Prompt |
| --- | --- | --- |
| Tests zuerst | Logik mit klaren Ein- und Ausgaben | "Schreib zuerst Tests für validateEmail, dann die Funktion, bis alle grün sind." |
| Erwartete Ausgabe | Skripte, CLIs, Datenumwandlungen | "Lauf das Skript mit beispiel.csv, die Ausgabe muss 42 Zeilen haben." |
| Screenshot-Vergleich | UI-Änderungen | "[Bild einfügen] Setze dieses Design um, mach einen Screenshot und vergleiche." |
| `/verify` | Änderung am laufenden Produkt prüfen | `/verify` nach der Umsetzung |
| `/goal` | eine Bedingung, die über mehrere Turns gelten muss | `/goal alle Tests in tests/api sind grün` |
| Stop-Hook | jede Sitzung soll mit grünen Tests enden | siehe [Claude Code Hooks](./claude-code-hooks.md) |

Für Screenshots fügst du ein Bild per Kopieren und Einfügen oder Drag-and-drop in den Prompt ein. Damit Claude selbst Screenshots im Browser machen kann, braucht es eine Browser-Integration, etwa die Chrome-Erweiterung.

Ursachen statt Symptome adressieren: "Behebe die Ursache, unterdrücke den Fehler nicht."

## Wie halte ich den Kontext sauber?

- **`/clear` zwischen Aufgaben.** Unzusammenhängende Themen in einer Sitzung sind laut Doku das häufigste Fehlmuster.
- **Früh korrigieren.** Esc stoppt Claude mitten in der Arbeit, der Kontext bleibt erhalten. Esc Esc oder `/rewind` springt zu einem früheren Stand zurück; Änderungen über Bash-Befehle erfassen die Checkpoints nicht.
- **Zwei Korrekturen, dann neu.** Wenn du Claude zum zweiten Mal im selben Punkt korrigierst, `/clear` und mit einem besseren Prompt neu beginnen, der das Gelernte enthält.
- **Sitzungen benennen.** `/rename oauth-migration`, später `claude --continue` oder `claude --resume`.
- **Gezielt kompaktieren.** `/compact Fokus auf die API-Änderungen`.

Siehe auch [Claude Code Usage und Tokens](./claude-code-usage-tokens.md).

## Wann setze ich Subagents ein?

Recherche liest viele Dateien und füllt den Kontext. Ein Subagent erledigt das in eigenem Kontext und liefert nur die Zusammenfassung:

```text
Nutze Subagents, um herauszufinden, wie unser Auth-System Token-Refresh
behandelt und ob es eigene OAuth-Hilfsfunktionen gibt, die ich wiederverwenden sollte.
```

Nach der Umsetzung prüft ein Subagent mit frischem Blick:

```text
Nutze einen Subagent, um diesen Code auf Randfälle zu prüfen.
```

Für Pläne funktioniert ein Gegenreview: Ein Subagent liest PLAN.md und den Code und meldet nur Lücken, die beim Umsetzen wirklich etwas ändern. Mehr in [Claude Code Subagents](./claude-code-subagents.md).

## Beispiele

### Beispiel 1: Interview vor einer größeren Funktion

Wenn du die Anforderungen selbst noch nicht genau kennst.

```text
Ich will eine Exportfunktion für Rechnungen als CSV bauen. Interviewe mich
ausführlich mit dem AskUserQuestion-Tool: technische Umsetzung, Randfälle,
Datenschutz, Abwägungen. Keine offensichtlichen Fragen. Wenn alles geklärt ist,
schreib die vollständige Spezifikation nach SPEC.md.
```

Danach eine frische Sitzung starten und dort SPEC.md umsetzen lassen. So bleibt der Kontext frei für die Umsetzung.

### Beispiel 2: Testgetriebene Umsetzung

Wenn Logik klar prüfbar ist.

```text
Schreib Tests für die Funktion iban_pruefen in src/zahlung.py. Gültig ist
DE89 3704 0044 0532 0130 00, ungültig sind leere Zeichenketten, falsche
Prüfziffern und Leerzeichen am Ende. Führe die Tests aus, sie sollen zuerst
fehlschlagen. Dann implementiere die Funktion, bis alle Tests grün sind.
Ändere die Tests dabei nicht.
```

### Beispiel 3: Code-Reviewer als Subagent

Wenn jede Änderung vor dem Commit einen zweiten Blick bekommen soll. Datei `.claude/agents/code-reviewer.md` (gekürzt aus der [Vorlage](../../src/claude_team/vorlage/.claude/agents/code-reviewer.md)):

```markdown
---
name: code-reviewer
description: Prüft geänderten Code auf Fehler, Sicherheit und Lesbarkeit. Nutzen nach jeder größeren Änderung.
tools: Read, Grep, Glob, Bash
model: sonnet
---

Du prüfst Code, du änderst nichts.

1. Lies den Diff mit git diff.
2. Prüfe auf Logikfehler, fehlende Fehlerbehandlung, Geheimnisse im Code und fehlende Tests.
3. Berichte nach Stufen: muss (blockiert), sollte, kann. Je Fund Datei, Zeile, Begründung.
```

Aufruf: "Lass den code-reviewer die Änderungen prüfen."

### Beispiel 4: Übergabe mit dem Handoff-Skill

Wenn du vor `/clear` oder Feierabend den Stand sichern willst. Datei `.claude/skills/handoff/SKILL.md` (gekürzt aus der [Vorlage](../../src/claude_team/vorlage/.claude/skills/handoff/SKILL.md)):

```markdown
---
name: handoff
description: Schreibt den Arbeitsstand nach docs/handoff.md, damit eine neue Sitzung nahtlos weitermacht.
disable-model-invocation: true
---

Schreibe docs/handoff.md mit diesen Abschnitten:

- Ziel
- Erledigt
- Offen
- Entscheidungen
- Fallen
- Prüfen
```

Nutzung: `/handoff`, dann `/clear`, in der neuen Sitzung "Lies docs/handoff.md und mach weiter".

### Beispiel 5: Schreiber und Prüfer in zwei Sitzungen

Wenn die Prüfung unabhängig vom Autor sein soll. Sitzung A:

```text
Implementiere ein Rate Limiting für unsere API-Endpunkte.
```

Sitzung B, frischer Kontext:

```text
Prüfe die Rate-Limiter-Umsetzung in src/middleware/rateLimiter.ts.
Suche nach Randfällen, Race Conditions und Abweichungen von unseren Mustern.
```

Zurück in Sitzung A:

```text
Hier ist das Review-Feedback: [Ausgabe von B]. Behebe diese Punkte.
```

### Beispiel 6: Fehler aus einem Log beheben

Wenn ein Build-Fehler vorliegt.

```bash
cat build-error.txt | claude -p "Erkläre die Ursache dieses Build-Fehlers knapp" > ursache.txt
```

Interaktiv geht es mit `@datei`: "Lies @logs/build.log und behebe die Ursache. Prüfe danach mit npm run build."

### Beispiel 7: Ein gutes Prompt-Muster für den Alltag

Wenn du eine Funktion nach einem vorhandenen Muster bauen willst.

```text
Schau dir an, wie bestehende Widgets auf der Startseite umgesetzt sind,
HotDogWidget.php ist ein gutes Beispiel. Folge dem Muster und baue ein
Kalender-Widget, in dem man einen Monat wählen und vor- und zurückblättern kann.
Keine neuen Bibliotheken außer denen, die wir schon nutzen.
```

## Schritt für Schritt: eine Funktion von der Idee bis zum PR

1. Neue Sitzung im Projekt starten, mit `/rename` benennen.
2. Plan Mode (Shift+Tab), erkunden lassen und Fragen stellen.
3. Plan schreiben lassen, mit Ctrl+G im Editor nachschärfen.
4. Für größere Pläne: Subagent prüft PLAN.md auf relevante Lücken.
5. Normalen Modus wählen, Tests zuerst schreiben lassen, dann umsetzen.
6. Tests ausführen lassen; bei UI einen Screenshot vergleichen.
7. Code-Reviewer-Subagent oder zweite Sitzung prüfen lassen, Funde beheben.
8. Committen und PR öffnen lassen.
9. `/handoff`, falls etwas offen bleibt, dann `/clear` vor der nächsten Aufgabe.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Alles in einer Sitzung | Claude vergisst frühere Anweisungen | `/clear` zwischen unabhängigen Aufgaben |
| Immer wieder korrigieren | Kontext voller gescheiterter Ansätze | nach zwei Korrekturen `/clear` und besserer Prompt |
| Überladene CLAUDE.md | Claude ignoriert die Hälfte | kürzen, siehe [CLAUDE.md](./claude-md.md) |
| Vertrauen ohne Prüfung | plausibler Code mit Randfehlern | Tests, Screenshot oder Prüfbefehl verlangen |
| Endloses Erkunden | "Untersuche" ohne Grenzen füllt den Kontext | Umfang eingrenzen oder Subagent nutzen |
| Plan bei Mini-Änderungen | mehr Aufwand als Nutzen | direkt umsetzen lassen |
| Tests nachträglich angepasst | Tests prüfen nichts mehr | "Ändere die Tests nicht" in den Prompt |

## Häufige Fragen

### Muss ich den Plan Mode immer nutzen?

Nein. Er lohnt sich bei unklarem Ansatz, mehreren betroffenen Dateien oder fremdem Code. Wenn du den Diff in einem Satz beschreiben könntest, lass Claude direkt arbeiten.

### Wie oft sollte ich /clear nutzen?

Bei jedem Wechsel zu einer Aufgabe ohne Bezug zur vorherigen und immer dann, wenn du Claude zweimal im selben Punkt korrigieren musstest. Den Stand vorher bei Bedarf mit einem Handoff-Skill sichern.

### Funktioniert "think hard" noch?

Nein, das ist kein Schlüsselwort mehr. Für mehr Denkaufwand bei einer einzelnen Aufgabe schreibst du `ultrathink` in den Prompt, dauerhaft steuerst du über `/effort`.

### Kann Claude Code UI-Änderungen selbst prüfen?

Ja, wenn du ihm einen Weg gibst: ein eingefügtes Zieldesign plus die Anweisung, einen Screenshot des Ergebnisses zu machen und zu vergleichen. Dafür braucht Claude Zugriff auf einen Browser, etwa über die Chrome-Erweiterung.

### Wie arbeite ich mit mehreren Aufgaben gleichzeitig?

Mit parallelen Sitzungen in eigenen Git-Worktrees (`claude --worktree <name>`) oder mit Agent Teams. Details in [Claude Code Agent Teams](./claude-code-agent-teams.md).

## Weiterlesen

- [Claude Code Tutorial auf Deutsch](./claude-code-tutorial-deutsch.md)
- [Claude Code Plan Mode](./claude-code-plan-mode.md)
- [Claude Code Subagents](./claude-code-subagents.md)
- [Claude Code Skills](./claude-code-skills.md)
- [Claude Code Hooks](./claude-code-hooks.md)
- Offizielle Best Practices: https://code.claude.com/docs/en/best-practices
