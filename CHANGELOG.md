# Änderungen

## 0.1.0 (15.10.2026)

Erste Version.

- `claude-team audit` mit 35 Regeln (CC001 bis CC051) für CLAUDE.md, settings.json, Hooks, Secrets, MCP, Subagents, Skills und Git. Ausgabe als Text, Markdown, JSON und SARIF.
- `claude-team einrichten` mit Profil `standard` und `streng`. Überschreibt nie, bestehende Dateien bekommen einen Vorschlag daneben.
- `claude-team scannen` für Secrets und deutsche personenbezogene Daten mit Prüfziffer (IBAN, Steuer-ID, USt-IdNr., Sozialversicherungsnummer, Kreditkarte).
- Sieben Hooks: Secrets, personenbezogene Daten, gefährliche Befehle, Protokoll, Formatieren, Sitzungsstart, Tests vor dem Stopp. Die Schutz-Hooks prüfen Bash und das PowerShell-Tool unter Windows.
- Plugin `team-basis` für Claude Code und Codex, GitHub Action mit SARIF-Upload.
- 35 Anleitungen, Freigabe-Unterlagen für Datenschutz, IT-Sicherheit und Betriebsrat, Vorlage für Managed Settings.
