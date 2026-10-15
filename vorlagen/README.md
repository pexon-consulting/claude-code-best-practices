# Vorlagen für die zentrale Verteilung

`managed-settings.json` ist eine Ausgangsfassung der Managed Settings für Claude Code. Sie sperrt den Bypass-Modus, blockiert das Lesen von `.env`, Schlüsseldateien und Cloud-Credentials, schaltet Telemetrie, Fehlerberichte und Feedback ab, löscht lokale Verläufe nach 14 Tagen, setzt eine Mindestversion und erlaubt Plugins nur aus dem offiziellen Marketplace und diesem Repo.

> Stand: 15.10.2026, geprüft mit Claude Code 2.1.294. Teil von [Claude Code Best Practices](../README.md).

## Wohin die Datei gehört

| Betriebssystem | Pfad |
| --- | --- |
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` |
| Linux und WSL | `/etc/claude-code/managed-settings.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` |

Der alte Windows-Pfad unter `C:\ProgramData` wird nicht mehr gelesen. Per MDM geht es auch über die plist-Domain `com.anthropic.claudecode` (macOS) oder den Registry-Wert `Settings` unter `HKLM\SOFTWARE\Policies\ClaudeCode` (Windows).

## Vor dem Verteilen anpassen

- `cleanupPeriodDays` und `requiredMinimumVersion` auf die eigenen Vorgaben setzen.
- In `strictKnownMarketplaces` nur die Marketplaces eintragen, die freigegeben sind. Ein leeres Array sperrt alle.
- Optional ergänzen: `forceLoginMethod` und `forceLoginOrgUUID`, `allowedProviders`, `allowedMcpServers`, `sandbox`. Beispiele stehen in der Enterprise-Anleitung.

## Prüfen

```bash
python3 -m json.tool managed-settings.json > /dev/null && echo "JSON gültig"
```

Ungültiges JSON in den Managed Settings verhindert den Start von Claude Code. Nach dem Verteilen auf einem Testrechner `claude` starten und `/status` aufrufen: Die Zeile mit den Setting-Quellen muss die Managed Settings nennen. `claude doctor` zeigt Fehler in der Konfiguration. Gegenprobe: `claude --dangerously-skip-permissions` muss abgelehnt werden.

## Weiterlesen

- [Claude Code Enterprise: Managed Settings zentral verteilen](../docs/anleitungen/claude-code-enterprise.md)
- [Freigabe-Paket für IT-Sicherheit](../docs/rollout/freigabe-paket.md)
