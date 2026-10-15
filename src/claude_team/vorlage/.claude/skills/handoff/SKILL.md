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

Schreibe `docs/handoff.md` neu (alte Fassung ersetzen) mit genau diesen Abschnitten:

1. **Ziel**: was erreicht werden soll, ein Satz.
2. **Erledigt**: was fertig und getestet ist, mit Dateien.
3. **Offen**: nächste Schritte in Reihenfolge, je ein Satz.
4. **Entscheidungen**: was festgelegt wurde und warum.
5. **Fallen**: was nicht funktioniert hat und warum, damit es niemand wiederholt.
6. **Prüfen**: der Befehl, mit dem man den Stand testet.

Keine Secrets, keine Kundendaten. Höchstens 60 Zeilen.
