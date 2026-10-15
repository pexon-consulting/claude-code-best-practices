# Claude Code Tutorial auf Deutsch: die erste Stunde mit Claude Code

Dieses Claude Code Tutorial führt dich in etwa einer Stunde von der Installation bis zum ersten eigenen Commit: installieren, im Projekt starten, mit `/init` eine CLAUDE.md anlegen, eine erste kleine Aufgabe lösen, eine größere im Plan Mode planen, Tests laufen lassen und committen. Du brauchst ein Git-Projekt, ein Terminal und ein Konto für Claude Code, also ein Abo, einen Zugang über die Claude Console oder einen Cloud-Anbieter. Claude Code versteht deutsche Prompts, alle Beispiele hier sind auf Deutsch.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Installation mit einem Befehl, danach `claude` im Projektordner starten und anmelden.
- `/init` erzeugt eine CLAUDE.md mit Befehlen und Konventionen des Projekts; kürze sie danach auf das Wesentliche.
- Ab v2.1.283 startet eine interaktive Sitzung im Auto Mode; mit Shift+Tab wechselst du den Modus, etwa in den Plan Mode.
- Für größere Änderungen erst planen lassen, dann umsetzen, dann prüfen.
- Gib Claude immer ein Prüfkriterium: "Führe danach die Tests aus."
- `/clear` zwischen Aufgaben hält den Kontext sauber und spart Tokens.

## Minute 0-10: Wie installiere ich Claude Code?

macOS, Linux und WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

Weitere Wege: `brew install --cask claude-code` und `winget install Anthropic.ClaudeCode`. Beide aktualisieren sich standardmäßig nicht selbst; dann regelmäßig `brew upgrade claude-code` bzw. `winget upgrade Anthropic.ClaudeCode` ausführen. Prüfen:

```bash
claude --version
```

Details und Fehlerbilder in [Claude Code installieren](./claude-code-installieren.md) und [Claude Code unter Windows](./claude-code-windows.md).

## Minute 10-15: Wie starte ich Claude Code im Projekt?

```bash
cd mein-projekt
claude
```

Beim ersten Start meldest du dich an: mit einem Claude-Abo, einem Konto der Claude Console oder über einen Cloud-Anbieter wie Bedrock oder Vertex AI, falls deine Organisation das vorgibt. Die Zugangsdaten werden gespeichert, das passiert nur einmal.

Erste Orientierung:

| Eingabe | Wirkung |
| --- | --- |
| `/help` | zeigt verfügbare Befehle |
| `/` | listet alle Befehle und Skills |
| Tab | Befehle vervollständigen |
| Pfeil hoch | frühere Eingaben |
| Esc | Claude mitten in der Arbeit stoppen |
| Shift+Tab | Rechtemodus wechseln |
| `/exit` oder zweimal Ctrl+D | beenden |

Später fortsetzen: `claude -c` setzt die letzte Sitzung im Ordner fort, `claude -r` öffnet eine Auswahl.

### Welcher Rechtemodus ist aktiv?

Ab v2.1.283 starten interaktive Sitzungen im Terminal und in VS Code im Auto Mode: Ein Klassifikator prüft Aktionen, statt bei jeder Datei zu fragen. Wer am Anfang jede Änderung selbst bestätigen will, startet im manuellen Modus:

```bash
claude --permission-mode default
```

Mehr in [Claude Code Permissions](./claude-code-permissions.md).

## Minute 15-25: Erste Fragen an die Codebasis

Lass dir das Projekt erklären, bevor du etwas änderst:

```text
Was macht dieses Projekt?
```

```text
Welche Technologien nutzt das Projekt, und wo ist der Einstiegspunkt?
```

```text
Erkläre die Ordnerstruktur. Wo liegen die Tests, und wie führe ich sie aus?
```

Claude liest die nötigen Dateien selbst, du musst sie nicht von Hand einfügen. Willst du auf eine Datei zeigen, nutzt du `@`: "Erkläre @src/api/auth.ts".

## Minute 25-30: Was macht /init?

```text
/init
```

`/init` untersucht das Projekt und schreibt eine CLAUDE.md mit Build- und Testbefehlen, Konventionen und Besonderheiten. Vorhandene `.cursor/rules`, `.cursorrules` oder `.github/copilot-instructions.md` bezieht es ein. Mit `CLAUDE_CODE_NEW_INIT=1` startet ein interaktiver Ablauf, der auch Skills, Hooks und persönliche Memory-Dateien abfragt.

Danach die Datei lesen und kürzen. Die Doku empfiehlt unter 200 Zeilen; für jede Zeile gilt die Frage: Würde Claude ohne sie einen Fehler machen? Liegt im Projekt schon eine AGENTS.md, liest Claude Code sie ab v2.1.277, wenn keine CLAUDE.md existiert. Mehr in [CLAUDE.md](./claude-md.md).

## Minute 30-40: Die erste kleine Aufgabe

Wähle etwas Kleines mit klarem Ergebnis:

```text
Ergänze in src/utils/datum.ts eine Funktion, die ein Datum im Format
TT.MM.JJJJ ausgibt. Schreib einen Test dafür und führe die Tests aus.
```

Claude zeigt dir Änderungen an Dateien; je nach Modus bestätigst du sie oder Claude arbeitet direkt weiter. Danach:

```text
Welche Dateien hast du geändert? Fasse die Änderungen in drei Sätzen zusammen.
```

## Minute 40-50: Eine größere Aufgabe im Plan Mode

Drücke Shift+Tab, bis unten `plan mode on` steht. Im Plan Mode liest und plant Claude, ändert aber nichts.

```text
Ich will eine CSV-Exportfunktion für die Kundenliste. Lies den relevanten Code
und schreib einen Plan: welche Dateien, welche Tests, welche Randfälle.
```

Mit Ctrl+G öffnest du den Plan im Editor und kannst ihn anpassen. Wenn er passt, wechselst du mit Shift+Tab zurück und sagst:

```text
Setze den Plan um. Schreib zuerst die Tests, dann den Code, bis alle Tests grün sind.
```

Mehr in [Claude Code Plan Mode](./claude-code-plan-mode.md).

## Minute 50-55: Tests laufen lassen und Fehler beheben

```text
Führe die komplette Testsuite aus und behebe fehlschlagende Tests.
Behebe die Ursache, nicht das Symptom, und ändere keine Tests, ohne mich zu fragen.
```

Wenn Claude falsch abbiegt: Esc drücken und korrigieren. Mit zweimal Esc oder `/rewind` springst du zu einem früheren Stand zurück.

## Minute 55-60: Committen

```text
Zeig mir die Änderungen als git diff.
```

```text
Committe die Änderungen mit einer aussagekräftigen Nachricht auf Deutsch.
```

Danach `/clear`, bevor du mit der nächsten Aufgabe beginnst.

## Beispiele

### Beispiel 1: Fehler über ein Log beheben

Wenn ein Build oder Test fehlschlägt.

```text
Der Build schlägt fehl. Hier ist die Fehlermeldung: [Meldung einfügen].
Finde die Ursache, behebe sie und prüfe mit npm run build.
```

### Beispiel 2: Code verstehen, bevor du ihn änderst

Wenn du in einen unbekannten Teil einsteigst.

```text
Wie funktioniert die Anmeldung in diesem Projekt? Zeig mir die beteiligten
Dateien in der Reihenfolge, in der eine Anfrage sie durchläuft.
```

### Beispiel 3: Einfache Regeln für den Anfang in der CLAUDE.md

Wenn du die von `/init` erzeugte Datei um eigene Vorgaben ergänzt.

```markdown
# Projektregeln

- Tests mit `npm test` ausführen, einzelne Datei mit `npm test -- <pfad>`.
- Vor jedem Commit `npm run lint` ausführen.
- Commit-Nachrichten auf Deutsch, im Imperativ, höchstens 72 Zeichen in der ersten Zeile.
- Keine neuen Abhängigkeiten ohne Rückfrage.
- Die Datei .env nie lesen oder ändern.
```

### Beispiel 4: Geheimnisse von Anfang an sperren

Wenn das Projekt eine `.env` mit Zugangsdaten hat. Datei `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

Eine Anweisung in der CLAUDE.md ist eine Bitte, eine deny-Regel ist eine Sperre. Siehe Prüfregel [CC013](../regeln.md#cc013) und die [Vorlage](../../src/claude_team/vorlage/.claude/settings.json).

### Beispiel 5: Einmalige Aufgabe ohne Sitzung

Wenn du nur eine schnelle Antwort im Terminal brauchst.

```bash
claude -p "Erkläre in drei Sätzen, was die Datei src/index.ts macht"
```

### Beispiel 6: Eine Aufgabe direkt beim Start übergeben

Wenn du schon weißt, was zu tun ist.

```bash
claude "Ergänze im README einen Abschnitt, wie man die Tests ausführt"
```

### Beispiel 7: Einen Vorschlag kritisch prüfen lassen

Wenn du unsicher bist, ob eine Lösung gut ist.

```text
Prüfe deine letzte Änderung kritisch: Welche Randfälle fehlen? Was würde ein
erfahrener Reviewer bemängeln? Ändere noch nichts, gib mir nur eine Liste.
```

## Schritt für Schritt: die erste Stunde als Checkliste

1. Claude Code installieren und `claude --version` prüfen.
2. Im Projektordner `claude` starten und anmelden.
3. Drei Fragen zur Codebasis stellen.
4. `/init` ausführen, CLAUDE.md lesen und kürzen.
5. `.env` per deny-Regel sperren (Beispiel 4).
6. Eine kleine Aufgabe mit Test umsetzen lassen.
7. Eine größere Aufgabe im Plan Mode planen, dann umsetzen.
8. Tests laufen lassen, Fehler beheben lassen.
9. Diff ansehen, committen, `/clear`.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Vage Aufgabe wie "Verbessere den Code" | lange Läufe, unklare Änderungen | konkrete Datei, konkretes Ziel, Prüfkriterium |
| Kein Prüfkriterium | Code sieht richtig aus, ist es aber nicht | "Führe danach die Tests aus" |
| CLAUDE.md von `/init` ungeprüft übernommen | zu lang, Regeln werden übersehen | lesen und kürzen |
| Alles in einer Sitzung | Claude vergisst frühere Vorgaben | `/clear` zwischen Aufgaben |
| Zu spät eingreifen | Claude arbeitet lange in die falsche Richtung | früh Esc drücken und korrigieren |
| Ohne Git arbeiten | Änderungen schwer rückgängig zu machen | immer in einem Git-Repo, häufig committen |
| Mit `--dangerously-skip-permissions` anfangen | keine Kontrolle über Befehle | Standardmodus oder Plan Mode, siehe [Prüfregel CC012](../regeln.md#cc012) |

## Häufige Fragen

### Wie fange ich mit Claude Code an?

Installieren, im Projektordner `claude` starten, anmelden und mit Fragen zur Codebasis beginnen. Danach `/init` für eine CLAUDE.md und eine erste kleine Aufgabe mit Test. Die Checkliste oben führt in einer Stunde durch alles.

### Versteht Claude Code Deutsch?

Ja, Prompts auf Deutsch funktionieren. Für Commit-Nachrichten oder Codekommentare legst du die Sprache am besten in der CLAUDE.md fest, damit sie einheitlich bleibt.

### Brauche ich ein Abo für Claude Code?

Du brauchst einen Zugang: ein Claude-Abo, ein Konto in der Claude Console mit Abrechnung nach Verbrauch oder einen Cloud-Anbieter wie Bedrock, Vertex AI oder Foundry. Unterschiede und Budgets in [Claude Code Kosten](./claude-code-kosten.md).

### Kann ich Claude Code in VS Code oder JetBrains nutzen?

Ja, es gibt eine Erweiterung für VS Code (auch in Cursor nutzbar) und ein Plugin für JetBrains. Siehe [Claude Code in VS Code und JetBrains](./claude-code-vscode-jetbrains.md).

### Wie mache ich eine Änderung rückgängig?

Mit zweimal Esc oder `/rewind` springst du zu einem früheren Stand der Sitzung. Änderungen, die über Bash-Befehle entstanden sind, erfassen diese Checkpoints nicht; dafür ist Git da.

### Was ist der Unterschied zwischen Plan Mode und normalem Modus?

Im Plan Mode liest und plant Claude, ändert aber keine Dateien. Im normalen Modus setzt Claude um. Für größere oder unklare Änderungen erst planen, für kleine direkt umsetzen.

## Weiterlesen

- [Claude Code Workflow: Erkunden, Planen, Umsetzen, Committen](./claude-code-workflow.md)
- [Claude Code installieren](./claude-code-installieren.md)
- [CLAUDE.md](./claude-md.md)
- [Claude Code Befehle](./claude-code-befehle.md)
- [Claude Code Permissions](./claude-code-permissions.md)
- Offizieller Quickstart: https://code.claude.com/docs/en/quickstart
