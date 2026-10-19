# Änderungen

## 0.2.0 (19.10.2026)

- Hooks: `befehle_schutz.py` erkennt Force-Push auch nach globalen Git-Optionen (`git -C . push --force`), mit `-f` in Kurzoptionen und als `+refspec`, dazu `bash -c`, `eval`, `$(...)`, `bash <(curl ...)` und `rm -rf ~/*`. Commit-Nachrichten zählen nicht mehr als Befehl.
- Hooks: `secrets_schutz.py` blockt Pfade in Interpreter-Code und Anführungszeichen, `export`, `declare -x`, `/usr/bin/env`, Platzhalter wie `cat .e*v` und `grep -r` über Ordner mit `.env`. `.credentials.json` gilt als sensibel.
- Hooks: IBAN in Kleinbuchstaben und mit Bindestrichen wird erkannt. Weitere verbreitete Testkarten sind erlaubt.
- Protokoll-Hook standardmäßig aus, mit Löschfrist `aufbewahrung_tage` (Standard 30) und Maskierung von Kennungen, E-Mail-Adressen und Heredocs.
- `stopp.befehl` läuft in der Shell, Ketten mit `&&` gehen.
- Vorlage: keine Testbefehle mehr in `allow`, `git diff/log/show --output` in `deny`, `Read(~/.claude/.credentials.json)` in `deny`.
- Neue Regel CC007 (offene Platzhalter in CLAUDE.md), jetzt 36 Regeln. Bericht mit Singular bei 1 Warnung oder 1 Hinweis.
- Plugin: Subagents liegen unter `agents/` und werden ohne `agents`-Liste im Manifest gefunden. CI prüft das Plugin mit `claude plugin validate`.
- Managed-Settings-Vorlage gibt nur noch den offiziellen Marketplace frei. Anleitungen empfehlen für eigene Plugins einen Fork mit festem `ref`.
- Doku: Abschnitt "Was die Hooks nicht abdecken", Markenhinweis und Hinweis "keine Rechtsberatung", Bedrock-Region als Präferenz statt Garantie.

## 0.1.0 (15.10.2026)

Erste Version.

- `claude-team audit` mit 35 Regeln (CC001 bis CC051) für CLAUDE.md, settings.json, Hooks, Secrets, MCP, Subagents, Skills und Git. Ausgabe als Text, Markdown, JSON und SARIF.
- `claude-team einrichten` mit Profil `standard` und `streng`. Überschreibt nie, bestehende Dateien bekommen einen Vorschlag daneben.
- `claude-team scannen` für Secrets und deutsche personenbezogene Daten mit Prüfziffer (IBAN, Steuer-ID, USt-IdNr., Sozialversicherungsnummer, Kreditkarte).
- Sieben Hooks: Secrets, personenbezogene Daten, gefährliche Befehle, Protokoll, Formatieren, Sitzungsstart, Tests vor dem Stopp. Die Schutz-Hooks prüfen Bash und das PowerShell-Tool unter Windows.
- Plugin `team-basis` für Claude Code und Codex, GitHub Action mit SARIF-Upload.
- 35 Anleitungen, Freigabe-Unterlagen für Datenschutz, IT-Sicherheit und Betriebsrat, Vorlage für Managed Settings.
