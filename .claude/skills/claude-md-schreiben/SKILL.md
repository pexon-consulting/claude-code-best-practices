---
name: claude-md-schreiben
description: "Eine gute CLAUDE.md für ein bestehendes Repo schreiben oder eine zu lange kürzen: Befehle, Aufbau, Arbeitsweise, Grenzen und bekannte Fallen in unter 200 Zeilen, Bereichsregeln nach .claude/rules mit paths, AGENTS.md per @-Import. Nutzen, wenn eine CLAUDE.md fehlt, über 200 Zeilen hat, veraltet ist oder Claude im Projekt immer wieder dieselben Fehler macht. Englisch: write or improve CLAUDE.md, CLAUDE.md best practices."
license: MIT
---

# CLAUDE.md schreiben

Teil von Claude Code Best Practices für Teams.

## Ablauf

1. Lies, was schon da ist: `CLAUDE.md`, `.claude/CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, `README.md`, `CONTRIBUTING.md`. Lies keine `.env` und keine Schlüsseldateien.
2. Ermittle die Befehle aus `package.json`, `pyproject.toml`, `Makefile`, `justfile`, `Taskfile.yml` oder der CI unter `.github/workflows/`. Nimm nur Befehle auf, die es dort wirklich gibt. Starte den Testbefehl einmal, wenn der Nutzer zustimmt, und notiere, ob er grün ist.
3. Schreibe in dieser Reihenfolge, jeweils knapp:
   - ein Satz, was das Projekt tut,
   - `## Befehle`: installieren, testen (auch einen einzelnen Test), linten, starten,
   - `## Aufbau`: die 5 bis 10 wichtigsten Ordner mit je einem Halbsatz,
   - `## Arbeitsweise`: Branches, Commits, wann Tests laufen,
   - `## Grenzen`: was Claude nicht tun soll (z.B. keine Migrationen ausführen, nichts unter `vendor/` ändern),
   - `## Fallen`: konkrete Stellen, an denen Menschen und Agents sich schon vertan haben.
4. Alles, was nur für einen Teil des Codes gilt, kommt nach `.claude/rules/<thema>.md` mit `paths` im Frontmatter, z.B. `paths: ["src/api/**/*.ts"]`.
5. Gibt es eine `AGENTS.md` für andere Agents, schreibe in die CLAUDE.md die Zeile `@AGENTS.md`, statt den Inhalt zu kopieren. Claude Code liest AGENTS.md sonst nicht, solange eine CLAUDE.md existiert.
6. Prüfe am Ende: unter 200 Zeilen, jeder @-Import zeigt auf eine vorhandene Datei, keine Tokens, keine Kundendaten. Optional: `uvx --from git+https://github.com/pexon-consulting/claude-code-best-practices@v0.1.0 claude-team audit .`

## Stil

- Konkrete Anweisungen statt Wünsche: "Tests mit `pnpm test -- <pfad>` einzeln starten" statt "achte auf Tests".
- Keine allgemeinen Programmierregeln, die jedes Modell kennt.
- Eine Regel, die oft verletzt wird, darf mit "WICHTIG" beginnen. Sparsam einsetzen.
- Was zwingend gelten muss (keine `.env` lesen, kein Force-Push), gehört zusätzlich in deny-Regeln oder einen Hook. CLAUDE.md ist eine Bitte, keine Sperre.

## Grenze

Eine bestehende CLAUDE.md nicht überschreiben. Schreibe einen Vorschlag als `CLAUDE.vorschlag.md` oder zeige den Unterschied und frage. Persönliche Vorlieben gehören in `CLAUDE.local.md`, die in `.gitignore` steht.
