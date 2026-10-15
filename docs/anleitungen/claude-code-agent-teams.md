# Claude Code Agent Teams: mehrere Agenten parallel koordinieren

Claude Code Agent Teams sind eine experimentelle Funktion, bei der eine Hauptsitzung als Lead mehrere eigenständige Claude-Code-Instanzen als Teammitglieder startet, die über eine gemeinsame Aufgabenliste und direkte Nachrichten zusammenarbeiten. Sie lohnen sich für Recherche, Reviews mit mehreren Blickwinkeln, Debugging mit konkurrierenden Hypothesen und Funktionen mit klar getrennten Teilen; für fokussierte Aufgaben, bei denen nur das Ergebnis zählt, reichen Subagents und sind günstiger. Damit sich parallele Änderungen nicht überschreiben, gibt es Git-Worktrees: `claude --worktree <name>` für eigene Sitzungen und `isolation: worktree` für Subagents.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

## Das Wichtigste in Kürze

- Agent Teams sind standardmäßig aus; du schaltest sie mit `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` ein.
- Jedes Teammitglied hat ein eigenes Kontextfenster, lädt CLAUDE.md, MCP-Server und Skills, erbt aber nicht den Verlauf des Lead.
- Teams verbrauchen deutlich mehr Tokens als eine einzelne Sitzung, der Verbrauch wächst mit der Zahl aktiver Mitglieder.
- Die Doku empfiehlt den Start mit 3-5 Teammitgliedern und 5-6 Aufgaben pro Mitglied.
- Teammitglieder laufen nur interaktiv, nicht in `claude -p` und nicht im Agent SDK.
- Für parallele Sitzungen ohne Koordination reichen Git-Worktrees; für Subagents mit Schreibzugriff gibt es `isolation: worktree`.

## Wie funktionieren Agent Teams in Claude Code?

Ein Team besteht aus vier Teilen:

| Teil | Aufgabe |
| --- | --- |
| Lead | die Hauptsitzung; startet Teammitglieder und koordiniert |
| Teammitglieder | eigene Claude-Code-Instanzen, die Aufgaben bearbeiten |
| Aufgabenliste | gemeinsame Liste mit den Zuständen pending, in progress, completed und Abhängigkeiten |
| Mailbox | Nachrichten zwischen den Agenten |

Der Lead verteilt Aufgaben oder die Mitglieder nehmen sich nach Abschluss selbst die nächste freie Aufgabe. Das Beanspruchen läuft über Dateisperren, damit nicht zwei Mitglieder dieselbe Aufgabe nehmen. Wird eine Aufgabe fertig, gibt Claude Code abhängige Aufgaben automatisch frei.

Team-Konfiguration und Aufgaben liegen lokal unter `~/.claude/teams/{team}/config.json` und `~/.claude/tasks/{team}/`. Die Konfiguration verwaltet Claude Code selbst; nicht von Hand bearbeiten. Eine Datei wie `.claude/teams/teams.json` im Projekt wird nicht als Konfiguration erkannt.

### Aktivieren

In `.claude/settings.json` oder `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Danach bittest du Claude in normaler Sprache um Teammitglieder. Claude startet sie ohne Rückfrage.

### Anzeige wählen

| `teammateMode` | Verhalten |
| --- | --- |
| `in-process` (Standard) | alle Mitglieder im Hauptterminal; mit Pfeiltasten auswählen, Enter zeigt die Sitzung |
| `auto` | eigene Bereiche, wenn du schon in tmux oder iTerm2 mit `it2` arbeitest, sonst in-process |
| `tmux` | eigene Bereiche, erkennt tmux oder iTerm2 |
| `iterm2` | native iTerm2-Bereiche, braucht die `it2`-CLI |

Für eine einzelne Sitzung geht `claude --teammate-mode auto`; das Flag ist experimentell und erscheint nicht in `claude --help`. Eigene Bereiche funktionieren nicht im integrierten Terminal von VS Code, in Windows Terminal und in Ghostty.

Bedienung im In-process-Modus: Pfeiltasten wählen ein Mitglied, Enter öffnet es, Tippen schickt ihm eine Nachricht, `x` stoppt es, Ctrl+T blendet die Aufgabenliste ein.

### Modelle und Rechte

Das Modell eines Teammitglieds bestimmt Claude Code in dieser Reihenfolge: das im Startprompt genannte Modell, das `model` einer Subagent-Definition, `CLAUDE_CODE_SUBAGENT_MODEL`, das Modell des Lead. Vor v2.1.251 stand `CLAUDE_CODE_SUBAGENT_MODEL` an erster Stelle. Die Einstellung `teammateDefaultModel` wurde in v2.1.234 entfernt.

Teammitglieder starten mit dem Rechtemodus des Lead, außer `dontAsk`, den sie nicht erben. Läuft der Lead mit `--dangerously-skip-permissions`, gilt das für alle Mitglieder. Rechteabfragen erscheinen in der Sitzung des Lead, dort bestätigst du sie selbst. Ausnahme: Pläne von Teammitgliedern genehmigt der Lead automatisch, ohne dich zu fragen. Wer Teammitglieder erst planen lassen will, schaltet den Lead vorher in den Plan Mode.

## Wann lohnen sich Agent Teams gegenüber Subagents?

| | Subagents | Agent Teams |
| --- | --- | --- |
| Kontext | eigenes Fenster, Ergebnis geht an den Aufrufer | eigenes Fenster, vollständig unabhängig |
| Kommunikation | liefern ein Ergebnis zurück | Mitglieder schreiben sich direkt |
| Koordination | Hauptagent steuert alles | Selbstkoordination über Nachrichten und Aufgabenliste |
| Gut für | fokussierte Aufgaben, bei denen nur das Ergebnis zählt | Arbeit, die Austausch und gegenseitiges Prüfen braucht |
| Tokenkosten | niedriger, Ergebnis wird zusammengefasst | höher, jedes Mitglied ist eine eigene Instanz |
| Headless (`-p`, SDK) | ja | nein |

Faustregel aus der Doku: Für aufeinanderfolgende Aufgaben, Änderungen an derselben Datei oder viele Abhängigkeiten sind eine einzelne Sitzung oder Subagents wirksamer. Teams spielen ihre Stärke aus, wenn Mitglieder unabhängig arbeiten können.

Laut Kosten-Doku verbrauchen Agent Teams etwa 7-mal mehr Tokens als normale Sitzungen, wenn die Mitglieder im Plan Mode laufen. Mehr in [Claude Code Kosten](./claude-code-kosten.md).

Wichtig: Ist die Funktion aktiv, wird jeder Subagent, dem Claude einen Namen gibt, zum Teammitglied. Willst du wieder normale Subagents, setze `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` auf `0`.

## Grenzen der Agent Teams

- **Kein Fortsetzen:** `/resume` und `/rewind` stellen In-process-Mitglieder nicht wieder her. Nach dem Fortsetzen neue Mitglieder starten lassen.
- **Ein Team pro Sitzung:** keine zusätzlichen benannten Teams, kein Teilen über Sitzungen.
- **Keine verschachtelten Teams:** Mitglieder können keine eigenen Mitglieder starten.
- **Fester Lead:** die Sitzung, die das Team startet, bleibt Lead.

## Wie arbeite ich mit Git-Worktrees parallel?

Ein Worktree ist ein eigener Checkout desselben Repositorys mit eigenem Branch. Parallele Sitzungen kommen sich so nicht in die Quere.

```bash
claude --worktree feature-auth
```

Das legt `.claude/worktrees/feature-auth/` mit dem Branch `worktree-feature-auth` an. Eine zweite Sitzung in einem anderen Terminal bekommt einen anderen Namen. `-w` ist die Kurzform; ohne Namen erzeugt Claude einen.

Wissenswert:

- `.claude/worktrees/` gehört in die `.gitignore`.
- Ein Worktree ist ein frischer Checkout: Abhängigkeiten neu installieren. Ignorierte Dateien wie `.env` kopiert eine `.worktreeinclude`-Datei im gitignore-Format.
- Neue Worktrees starten vom Standard-Branch des Repositorys. `worktree.baseRef: "head"` startet vom aktuellen Stand.
- `claude --worktree "#1234"` startet von einem Pull Request.
- `claude -w feature-auth --tmux` öffnet den Worktree in einer eigenen tmux-Sitzung.
- Beim Beenden fragt Claude, ob ein Worktree mit Änderungen bleiben soll. Läufe mit `-p` räumen nicht auf; dann `git worktree remove` und bei Sperre vorher `git worktree unlock`.

Mitten in einer Sitzung reicht "Arbeite in einem Worktree", Claude nutzt dann das Tool `EnterWorktree`.

### Subagents mit isolation: worktree

Subagents, die Dateien ändern, bekommen mit `isolation: worktree` im Frontmatter einen eigenen temporären Worktree. Ohne Änderungen wird er beim Ende automatisch entfernt, mit Änderungen bleibt er, bis eine regelmäßige Bereinigung ihn gefahrlos entfernen kann.

### /batch für große Umbauten

`/batch <anweisung>` untersucht die Codebasis, zerlegt die Arbeit in 5 bis 30 unabhängige Einheiten und legt einen Plan vor. Nach deiner Freigabe arbeitet je Einheit ein Subagent im Hintergrund in eigenem Worktree.

## Beispiele

### Beispiel 1: Paralleles Review mit drei Blickwinkeln

Wenn ein großer PR gründlich geprüft werden soll.

```text
Starte drei Teammitglieder, die PR #142 prüfen:
- eins achtet auf Sicherheit
- eins auf Performance
- eins auf Testabdeckung
Jedes prüft und berichtet seine Funde. Fasse danach alles zusammen.
```

### Beispiel 2: Konkurrierende Hypothesen beim Debugging

Wenn die Ursache unklar ist und ein einzelner Agent sich zu früh festlegen würde.

```text
Nutzer berichten, dass die App nach einer Nachricht die Verbindung beendet.
Starte 5 Teammitglieder, die verschiedene Hypothesen untersuchen. Sie sollen
miteinander sprechen und versuchen, die Theorien der anderen zu widerlegen,
wie in einer wissenschaftlichen Debatte. Halte den Konsens in findings.md fest.
```

### Beispiel 3: Teammitglied aus einer Subagent-Definition

Wenn eine Rolle schon als Subagent existiert, etwa `.claude/agents/code-reviewer.md` aus der [Vorlage](../../src/claude_team/vorlage/.claude/agents/code-reviewer.md).

```text
Starte ein Teammitglied vom Agententyp code-reviewer, das src/auth/ prüft.
Kontext: Die App speichert JWT in httpOnly-Cookies. Achte auf Token-Handling,
Session-Verwaltung und Eingabevalidierung. Berichte mit Schweregrad.
```

Das Mitglied übernimmt `tools` und `model` der Definition. Kontext aus deiner Sitzung musst du im Startprompt mitgeben.

### Beispiel 4: Qualitätstor mit dem Hook TaskCompleted

Wenn eine Aufgabe erst als erledigt gelten soll, wenn die Tests grün sind. In `.claude/settings.json`:

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          { "type": "command", "command": "npm test --silent || { echo 'Tests rot, Aufgabe nicht abschließen' >&2; exit 2; }" }
        ]
      }
    ]
  }
}
```

Exit-Code 2 verhindert den Abschluss und gibt die Meldung als Rückmeldung zurück. Analog gibt es `TeammateIdle` und `TaskCreated`. Mehr in [Claude Code Hooks](./claude-code-hooks.md).

### Beispiel 5: Refactoring-Subagent im eigenen Worktree

Wenn ein Subagent viele Dateien mechanisch ändern soll, ohne deine Arbeit zu stören. Datei `.claude/agents/refactorer.md`:

```markdown
---
name: refactorer
description: Führt mechanische Refactorings über viele Dateien aus
isolation: worktree
---

Führe das gewünschte Refactoring in allen betroffenen Dateien aus,
lass dann die Tests laufen und berichte das Ergebnis.
```

### Beispiel 6: Zwei Sitzungen in Worktrees mit Umgebungsdateien

Wenn du selbst zwei Aufgaben parallel steuern willst. Einmalig im Projekt:

```bash
echo ".claude/worktrees/" >> .gitignore
printf ".env\n.env.local\n" > .worktreeinclude
```

Dann in zwei Terminals:

```bash
claude --worktree feature-export
claude --worktree bugfix-login
```

Aufräumen, falls ein Worktree hängen bleibt:

```bash
git worktree list
git worktree remove .claude/worktrees/bugfix-login
```

### Beispiel 7: Worktree von Hand

Wenn du den Ort und den Branch selbst bestimmen willst.

```bash
git worktree add ../projekt-feature-a -b feature-a
cd ../projekt-feature-a
claude
```

## Schritt für Schritt: das erste Agent Team

1. Eine Aufgabe wählen, die sich klar teilen lässt, etwa ein Review mit drei Blickwinkeln. Keine Änderungen an denselben Dateien.
2. `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `settings.json` setzen und Claude Code neu starten.
3. Optional `teammateMode` wählen; zum Start reicht in-process.
4. Den Startprompt mit allen nötigen Details schreiben, denn Mitglieder kennen deinen Verlauf nicht. Modell nennen, etwa "Nutze Sonnet für jedes Mitglied".
5. Mit 3 Mitgliedern beginnen. Mit Ctrl+T die Aufgabenliste beobachten.
6. Rechteabfragen in der Lead-Sitzung beantworten.
7. Mitglieder beenden, wenn sie fertig sind: "Bitte das Teammitglied researcher, sich zu beenden."
8. Danach `/usage` ansehen und entscheiden, ob sich das Team gegenüber Subagents gelohnt hat.

## Häufige Fehler

| Fehler | Symptom | Lösung |
| --- | --- | --- |
| Zwei Mitglieder an derselben Datei | gegenseitiges Überschreiben | Arbeit nach Dateien trennen |
| Zu wenig Kontext im Startprompt | Mitglieder fragen nach oder raten | Ziel, Pfade und Randbedingungen mitgeben |
| Zu viele Mitglieder | hohe Kosten, viel Abstimmung | mit 3-5 beginnen |
| Team für sequentielle Aufgaben | kein Zeitgewinn | einzelne Sitzung oder Subagents |
| Mitglieder laufen weiter | Tokenverbrauch ohne Nutzen | Mitglieder beenden, wenn fertig |
| Teams in `claude -p` erwartet | keine Mitglieder | Teams nur interaktiv, sonst Subagents |
| `.claude/worktrees/` nicht ignoriert | viele unversionierte Dateien | Eintrag in `.gitignore` |
| Worktrees nach `-p` nicht entfernt | Plattenplatz, Sperren | `git worktree remove`, ggf. `unlock` |

## Häufige Fragen

### Was ist der Unterschied zwischen Agent Teams und Subagents?

Subagents arbeiten innerhalb einer Sitzung und liefern ihr Ergebnis an den Aufrufer zurück. Teammitglieder sind eigene Claude-Code-Instanzen, die sich gegenseitig Nachrichten schicken und eine gemeinsame Aufgabenliste nutzen. Teams kosten mehr und laufen nur interaktiv.

### Sind Agent Teams stabil genug für den Alltag?

Sie sind laut Doku experimentell und haben bekannte Grenzen, etwa kein Wiederherstellen der Mitglieder beim Fortsetzen und nur ein Team pro Sitzung. Für Recherche, Reviews und gut trennbare Funktionen sind sie nutzbar; für Routine reicht eine Sitzung.

### Wie viele Teammitglieder sollte ich starten?

Die Doku empfiehlt 3-5 für die meisten Abläufe und 5-6 Aufgaben pro Mitglied. Bei 15 unabhängigen Aufgaben sind 3 Mitglieder ein guter Start. Drei fokussierte Mitglieder sind oft besser als fünf verstreute.

### Brauche ich Worktrees für Agent Teams?

Nicht zwingend. Teams teilen Arbeit über Aufgaben auf; Konflikte vermeidest du, indem jedes Mitglied eigene Dateien bearbeitet. Worktrees brauchst du für parallele eigene Sitzungen oder für Subagents mit `isolation: worktree`.

### Kann ich Agent Teams in CI nutzen?

Nein, Teammitglieder gibt es nur in interaktiven Sitzungen, nicht in `claude -p` oder im Agent SDK. In CI nutzt du Subagents oder mehrere getrennte Läufe.

## Weiterlesen

- [Claude Code Subagents](./claude-code-subagents.md)
- [Claude Code Workflow](./claude-code-workflow.md)
- [Claude Code Kosten](./claude-code-kosten.md)
- [Claude Code Hooks](./claude-code-hooks.md)
- Offizielle Doku: https://code.claude.com/docs/en/agent-teams und https://code.claude.com/docs/en/worktrees
