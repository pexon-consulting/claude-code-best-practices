# TOM-Vorlage: Claude Code bei [Firma]

Vorlage für die technischen und organisatorischen Maßnahmen (TOM) beim Einsatz von Claude Code. Die Gliederung folgt den Punkten aus Art. 32 Abs. 1 DSGVO. Die Maßnahmen, die Claude Code und die Team-Basis dieses Repos technisch liefern, sind bereits eingetragen; unternehmensspezifische Maßnahmen stehen als Platzhalter.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../../README.md).

Diese Vorlage ist keine Rechtsberatung. Ob die Maßnahmen ein angemessenes Schutzniveau ergeben, bewertet der Datenschutzbeauftragte. Die TOM des Modellanbieters selbst ([Anthropic / AWS / Google / Microsoft]) sind nicht Teil dieser Vorlage; sie stammen aus dessen Vertragsunterlagen, bei Anthropic aus dem [Trust Center](https://trust.anthropic.com).

| Feld | Eintrag |
| --- | --- |
| Verantwortlicher | [Firma, Anschrift] |
| Verarbeitung | Einsatz des KI-Coding-Agenten Claude Code in der Softwareentwicklung |
| Betriebsvariante | [Anthropic Team / Enterprise / API / Amazon Bedrock EU / Google Vertex AI EU / Microsoft Foundry / Gateway] |
| Auftragsverarbeiter | [Anbieter], AVV vom [Datum] |
| Version, Datum | [1.0], [Datum] |
| Erstellt von | [Name, Rolle] |

## 1. Pseudonymisierung und Verschlüsselung (Art. 32 Abs. 1 lit. a)

| Maßnahme | Umsetzung | Status |
| --- | --- | --- |
| Transportverschlüsselung | Modellanfragen laufen laut Doku über TLS 1.2+ | umgesetzt (Herstellerangabe) |
| Verschlüsselung beim Anbieter | Anthropic API: Festplattenverschlüsselung AES-256; Bedrock: AES-256, eigene Schlüssel per AWS KMS; Vertex AI: Google-Schlüssel, CMEK möglich; Foundry: je nach Hosting-Option | [Variante eintragen] |
| Verschlüsselung der Endgeräte | [Festplattenverschlüsselung, z.B. FileVault, BitLocker, LUKS] | [Status] |
| Keine Echtdaten in Prompts | Regel in Organisations-CLAUDE.md (`claudeMd`) und Schulung | [Status] |
| Synthetische oder pseudonymisierte Testdaten | [Vorgabe für Testdaten, Ablage unter `tests/fixtures/`] | [Status] |
| Blockieren personenbezogener Daten | Hook `pii_schutz.py`: IBAN, Steuer-ID, SV-Nummer, Kreditkarte mit Prüfziffer werden vor dem Senden an das Modell geblockt; viele E-Mails oder Telefonnummern führen zu einer Rückfrage | umgesetzt in [Repos] |

## 2. Vertraulichkeit

### 2.1 Zugang zum Werkzeug

| Maßnahme | Umsetzung | Status |
| --- | --- | --- |
| Nur Firmenkonten | `forceLoginMethod` und `forceLoginOrgUUID` in den Managed Settings | [Status] |
| Nur freigegebene Anbieter | `allowedProviders` in den Managed Settings (ab v2.1.285) | [Status] |
| Anmeldung | [SSO über Claude for Teams oder Enterprise / IAM des Cloud-Anbieters] | [Status] |
| Vergabe und Entzug von Zugängen | [Prozess, z.B. über Identity-Provider-Gruppe] | [Status] |

### 2.2 Zugriff des Agenten auf Daten

| Maßnahme | Umsetzung | Status |
| --- | --- | --- |
| Sperre für Secrets | deny-Regeln für `.env`, Schlüsseldateien, `~/.aws`, `~/.ssh`, `~/.kube` und weitere in Managed Settings und `.claude/settings.json` | umgesetzt |
| Zusätzlicher Secrets-Schutz | Hook `secrets_schutz.py` sperrt `env`, `printenv`, `gh auth token` und blockt neuen Code mit Tokens | umgesetzt in [Repos] |
| Kein Bypass-Modus | `permissions.disableBypassPermissionsMode: "disable"` | umgesetzt |
| Rückfrage vor Änderungen und Befehlen | Standard-Permission-Modus; Hook `befehle_schutz.py` fragt nach bei `git reset --hard`, `sudo`, `DROP TABLE`, `terraform destroy` und der Liste `befehle.fragen_bei` | umgesetzt |
| Sperre für Datenordner | [deny-Regeln für Ordner mit Exporten oder Personaldaten] | [Status] |
| Begrenzter Netzzugriff | [Sandbox mit `allowedDomains`; deny für `curl`, `wget`, WebFetch] | [Status] |
| Begrenzte MCP-Server | `allowedMcpServers`, `allowManagedMcpServersOnly` | [Status] |
| Credentials aus Unterprozessen entfernen | [`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`] | [Status] |

### 2.3 Trennung

| Maßnahme | Umsetzung | Status |
| --- | --- | --- |
| Getrennte Umgebungen | [kein Zugriff aus Entwicklerrechnern auf Produktionsdaten] | [Status] |
| Getrennte Organisationen oder Workspaces | [eigene Organisation oder Workspace für Claude Code] | [Status] |

## 3. Integrität

| Maßnahme | Umsetzung | Status |
| --- | --- | --- |
| Schutz vor zerstörerischen Befehlen | Hook `befehle_schutz.py` sperrt u.a. `rm -rf` auf `/`, `~`, `.`, `git push --force`, `--no-verify`, `curl ... \| sh` | umgesetzt in [Repos] |
| Review aller Änderungen | Pull-Request-Pflicht, `/security-review` vor dem Merge | [Status] |
| Prüfung der Konfiguration | `claude-team audit` in CI mit Exit-Code | [Status] |
| Nachvollziehbarkeit | Hook `protokoll.py`: Zeit, Sitzung (8 Zeichen), Tool, Datei, Befehl mit maskierten Tokens, Dauer; keine Dateiinhalte | [Status] |
| Plugins nur aus freigegebenen Quellen | `strictKnownMarketplaces` | umgesetzt |
| Organisationsweite Hooks erzwingen | [`allowManagedHooksOnly` mit erzwungenem Plugin] | [Status] |

## 4. Verfügbarkeit und Belastbarkeit (Art. 32 Abs. 1 lit. b und c)

| Maßnahme | Umsetzung | Status |
| --- | --- | --- |
| Code in Versionsverwaltung | alle Änderungen über Git, Checkpoints von Claude Code zusätzlich lokal | [Status] |
| Mindestversion | `requiredMinimumVersion` in den Managed Settings | [Status] |
| Update-Weg | [Auto-Update / Softwareverteilung] | [Status] |
| Ausfall des Modellanbieters | [Arbeit ohne Claude Code möglich, kein kritischer Prozess hängt davon ab] | [Status] |

## 5. Speicherung und Löschung

| Maßnahme | Umsetzung | Status |
| --- | --- | --- |
| Aufbewahrung beim Anbieter | [30 Tage Standard bei kommerziellen Konten / Zero Data Retention / Richtlinie des Cloud-Anbieters] | [Status] |
| Kein Training mit Firmendaten | kommerzielle Bedingungen; Development Partner Program nicht aktiviert | [geprüft am Datum] |
| Lokale Transkripte | `cleanupPeriodDays: [x]` in den Managed Settings | umgesetzt |
| Kein Feedback-Upload (5 Jahre Aufbewahrung) | `DISABLE_FEEDBACK_COMMAND=1` | umgesetzt |
| Keine Telemetrie an Anthropic | `DISABLE_TELEMETRY=1`, `DISABLE_ERROR_REPORTING=1`, `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1` | umgesetzt |
| Hook-Protokolle | Ordner `.claude/protokoll/`, nicht im Git; Löschfrist [x] Tage | [Status] |

## 6. Organisatorische Maßnahmen

| Maßnahme | Umsetzung | Status |
| --- | --- | --- |
| Nutzungsrichtlinie | [Dokument, Ablage] | [Status] |
| Schulung vor Nutzung | [Inhalt, Dauer, Nachweis] | [Status] |
| Ansprechpartner | [Name, Kanal] | [Status] |
| Vorfallmeldung | [Prozess bei abgeflossenen Secrets oder Daten] | [Status] |
| Information des Betriebsrats | [Datum, Infoblatt] | [Status] |
| Verarbeitungsverzeichnis | [Eintrag ergänzt am] | [Status] |

## 7. Regelmäßige Überprüfung (Art. 32 Abs. 1 lit. d)

| Maßnahme | Rhythmus | Verantwortlich |
| --- | --- | --- |
| `claude-team audit` in CI | bei jedem Pull Request | Teams |
| Prüfung der Managed Settings gegen neue Claude-Code-Versionen | [quartalsweise] | [Plattform-Team] |
| Prüfung der Datenflüsse in der Herstellerdoku | [halbjährlich] | [Datenschutz] |
| Stichprobe der Hook-Protokolle | [monatlich] | [IT-Sicherheit] |
| Überprüfung dieser TOM | [jährlich] | [Datenschutz] |

## Freigabe

| Name | Rolle | Datum | Unterschrift |
| --- | --- | --- | --- |
| [Name] | Datenschutzbeauftragter | [Datum] | |
| [Name] | IT-Sicherheit | [Datum] | |
