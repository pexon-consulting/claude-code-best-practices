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
   Typen: feat, fix, docs, refactor, test, chore, ci. Danach eine Leerzeile und das Warum in ein bis drei Sätzen.
5. Committen. Nicht pushen.

Hinweis des Nutzers: $ARGUMENTS
