# Freigabe-Paket: Claude Code bei [Firma]

Unterlage für IT-Sicherheit, Legal und Einkauf. Sie beschreibt das Werkzeug, die Datenflüsse, die geplante Konfiguration und die Schutzmaßnahmen und endet mit einer Checkliste für die Freigabe.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md). Inoffizielles Projekt: Claude und Claude Code sind Marken von Anthropic PBC; dieses Projekt ist nicht mit Anthropic verbunden.

Diese Unterlage erklärt Technik und Einstellungen. Sie ist keine Rechtsberatung. Datenschutz, Verträge und Mitbestimmung klärst du mit Datenschutzbeauftragtem, Rechtsabteilung und Betriebsrat. Angaben zu Regionen und Datenverarbeitung der Anbieter können sich ändern; maßgeblich sind deren aktuelle Dokumentation und Verträge.

| Feld | Eintrag |
| --- | --- |
| Version | [1.0] |
| Datum | [Datum] |
| Erstellt von | [Name, Rolle] |
| Geprüft von | [Name, IT-Sicherheit] |
| Gültig für | [Pilot / Regelbetrieb], [Teams] |

## 1. Steckbrief des Werkzeugs

| Feld | Eintrag |
| --- | --- |
| Name | Claude Code |
| Hersteller | Anthropic PBC |
| Art | KI-Coding-Agent im Terminal, als IDE-Erweiterung (VS Code, JetBrains) und in der Desktop-App |
| Funktion | liest Code, schlägt Änderungen vor, führt nach Freigabe Befehle aus, erstellt Commits |
| Laufzeit | lokal auf dem Entwicklerrechner; Modellanfragen gehen an den Modellanbieter |
| Version im Einsatz | [z.B. 2.1.294], Mindestversion per `requiredMinimumVersion` |
| Lizenz und Bedingungen | Commercial Terms of Service für Team, Enterprise und API ([Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance)) |
| Vertragsweg | [Claude for Teams / Claude for Enterprise / Claude Console (API) / Amazon Bedrock / Google Vertex AI / Microsoft Foundry] |
| Vertragspartner | [Anthropic / AWS / Google / Microsoft] |
| Region | [z.B. AWS eu-central-1 mit Präfix eu] |
| Zero Data Retention | [ja, freigeschaltet am [Datum] / nein / nicht zutreffend] |
| Nutzerkreis | [Anzahl] Entwickler in [Teams] |
| Sicherheitsmeldungen an den Hersteller | über HackerOne laut Doku |

## 2. Datenflüsse

| Fluss | Inhalt | Ziel | Status bei [Firma] |
| --- | --- | --- | --- |
| Modellanfragen | Prompts, Modellausgaben, gelesene Dateiinhalte, TLS 1.2+ | [Modellanbieter, Endpunkt] | erforderlich |
| Metriken | Latenz, Zuverlässigkeit, Nutzung; laut Doku ohne Code, Prompts, Dateipfade | Anthropic und Dienstleister | [aus per `DISABLE_TELEMETRY`] |
| Fehlerberichte | Fehlermeldungen und Stacktraces, redigiert | Fehler-Tracking-Dienstleister | [aus per `DISABLE_ERROR_REPORTING`] |
| `/feedback`, `/bug`, `/share` | Verlauf inklusive Code, 5 Jahre Aufbewahrung | Anthropic | [aus per `DISABLE_FEEDBACK_COMMAND`] |
| Sitzungsumfrage | Bewertung; Transkript nur nach "Yes" | Anthropic | [aus per `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY`] |
| WebFetch-Domain-Check | Hostname | `api.anthropic.com` | [an / aus per `skipWebFetchPreflight`] |
| Auto-Update | Programmdateien | Verteilserver von Anthropic | [an / über Softwareverteilung] |
| MCP-Server | je nach Server | [Liste freigegebener Server] | [Allowlist] |
| Optional: OpenTelemetry | Metriken, Ereignisse; Prompts standardmäßig redigiert | [eigener Collector] | [an / aus] |
| Lokal | Transkripte im Klartext unter `~/.claude/projects/` | Entwicklerrechner | Frist [x] Tage per `cleanupPeriodDays` |

Quelle: [Data usage](https://code.claude.com/docs/en/data-usage). Bei Amazon Bedrock, Google Vertex AI und Microsoft Foundry sind Metriken, Fehlerberichte und `/feedback`-Upload standardmäßig aus.

## 3. Geplante Konfiguration

| Ebene | Inhalt | Ablage |
| --- | --- | --- |
| Managed Settings | Bypass-Modus gesperrt, deny-Regeln für Secrets, Telemetrie aus, Login-Organisation, Marketplaces, [MCP-Allowlist], [Sandbox] | [MDM-Profil / `managed-settings.json`] |
| Plugin | `team-basis` mit Schutz-Hooks und Skills | Marketplace [Quelle] |
| Repo | `.claude/settings.json`, Hooks, `.claude/schutz.json`, CLAUDE.md | Git, angelegt mit `claude-team einrichten` |
| CI | `claude-team audit` als GitHub Action, SARIF an Code Scanning | jedes Repo |

Die Ausgangsfassung der Managed Settings liegt unter [vorlagen/managed-settings.json](../../vorlagen/managed-settings.json). Abweichungen: [Liste].

## 4. Schutzmaßnahmen

| Bedrohung | Maßnahme | Technisch erzwungen durch |
| --- | --- | --- |
| Secrets im Kontext | deny-Regeln für `.env`, Schlüssel, Cloud-Credentials; Hook `secrets_schutz.py` | Managed Settings, Repo-Hooks |
| Personenbezogene Daten im Prompt | Hook `pii_schutz.py` mit Prüfziffern für IBAN, Steuer-ID, SV-Nummer, Kreditkarte in Prompts, Befehlen und geschriebenem Code (nicht in gelesenen Dateien); deny-Regeln für Datenordner | Repo-Hooks, Plugin |
| Zerstörerische Befehle | Hook `befehle_schutz.py` sperrt z.B. `rm -rf /` und `git push --force`, fragt nach bei `git reset --hard`, `sudo`, `terraform destroy` | Repo-Hooks |
| Umgehen der Rückfragen | `disableBypassPermissionsMode: "disable"` | Managed Settings |
| Aufweichen der Regeln | [`allowManagedPermissionRulesOnly`], [`allowManagedHooksOnly`] | Managed Settings |
| Datenabfluss über Netz | [Sandbox mit `allowedDomains`], deny für `curl`, `wget`, [WebFetch] | Managed Settings |
| Lieferkette MCP und Plugins | `strictKnownMarketplaces`, `allowedMcpServers`, gepinnte Versionen | Managed Settings, Audit |
| Konto am Firmenvertrag vorbei | `forceLoginMethod`, `forceLoginOrgUUID`, [`allowedProviders`] | Managed Settings |
| Veraltete Clients | `requiredMinimumVersion` | Managed Settings |
| Fehlkonfiguration im Repo | `claude-team audit` mit Exit-Code | CI |

Grenzen, die IT-Sicherheit kennen sollte:

- Bash-deny-Regeln greifen auf den Befehl, wie Claude ihn schreibt; `sh -c` oder absolute Pfade umgehen sie. Die Sandbox schließt diese Lücke für Shell-Befehle.
- Die Sandbox läuft nicht nativ unter Windows und isoliert nur Shell-Befehle, nicht Read, Edit, WebFetch, Hooks und MCP.
- Hooks der Team-Basis lassen bei einem eigenen Absturz die Aktion durch (fail open).
- Lokale Admins können Managed-Dateien ändern; MDM verteilt sie deshalb regelmäßig neu.
- Managed Settings binden nur Claude Code, keine anderen Werkzeuge mit API-Zugriff.

## 5. Verantwortliche

| Bereich | Name | Vertretung |
| --- | --- | --- |
| Fachlich verantwortlich | [Name] | [Name] |
| Betrieb und Konfiguration | [Name] | [Name] |
| IT-Sicherheit | [Name] | [Name] |
| Datenschutz | [Name] | [Name] |
| Vertrag und Einkauf | [Name] | [Name] |
| Ansprechpartner für Nutzer | [Name, Kanal] | [Name] |

## 6. Offene Punkte

| Nr. | Punkt | Zuständig | Frist | Status |
| --- | --- | --- | --- | --- |
| 1 | Auftragsverarbeitungsvertrag mit [Anbieter] geprüft (Art. 28 DSGVO) | Datenschutz, Legal | [Datum] | [offen] |
| 2 | Region und Drittlandtransfer dokumentiert | Datenschutz | [Datum] | [offen] |
| 3 | Notwendigkeit einer DSFA (Art. 35 DSGVO) geprüft | Datenschutz | [Datum] | [offen] |
| 4 | Betriebsrat informiert, Regelungsbedarf geklärt | Personal | [Datum] | [offen] |
| 5 | [Bei Berufsgeheimnisträgern: Punkte zu § 203 StGB geklärt] | Legal | [Datum] | [offen] |
| 6 | Update-Weg festgelegt (Auto-Update oder Softwareverteilung) | Betrieb | [Datum] | [offen] |
| 7 | [Weiterer Punkt] | [Name] | [Datum] | [offen] |

## 7. Checkliste für die IT-Sicherheit

- [ ] Vertragsweg ist kommerziell (kein privates Free-, Pro- oder Max-Konto).
- [ ] Login ist per `forceLoginMethod` und `forceLoginOrgUUID` auf die Firmenorganisation festgelegt, oder der Zugang läuft ausschließlich über den Cloud-Anbieter.
- [ ] `managed-settings.json` ist gültiges JSON und liegt am Systempfad oder kommt per MDM.
- [ ] `/status` zeigt auf einem Testrechner `Enterprise managed settings` als Quelle.
- [ ] `claude --dangerously-skip-permissions` wird abgelehnt.
- [ ] Lesen von `.env` und `~/.ssh` wird blockiert (Gegenprobe durchgeführt).
- [ ] Telemetrie, Fehlerberichte und `/feedback` sind abgeschaltet.
- [ ] Plugin-Marketplaces sind per `strictKnownMarketplaces` begrenzt.
- [ ] MCP-Server sind per Allowlist begrenzt und gepinnt.
- [ ] [Sandbox ist aktiv, `failIfUnavailable` und `allowUnsandboxedCommands: false` gesetzt.]
- [ ] `claude-team audit` läuft in allen Repos ohne Fehler.
- [ ] Update-Weg und Mindestversion sind festgelegt.
- [ ] Vorfallprozess ist bekannt: Meldung an [Kanal], Sperre über [Weg].

**Freigabe:** [ ] erteilt [ ] mit Auflagen: [Auflagen] [ ] abgelehnt

| Name | Rolle | Datum | Unterschrift |
| --- | --- | --- | --- |
| [Name] | IT-Sicherheit | [Datum] | |
| [Name] | Datenschutz | [Datum] | |
