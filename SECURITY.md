# Sicherheit

## Lücke melden

Bitte keine öffentlichen Issues für Sicherheitslücken. Nutze [GitHub Private Vulnerability Reporting](https://github.com/pexon-consulting/claude-code-best-practices/security/advisories/new) dieses Repos. Wir antworten innerhalb von fünf Werktagen.

Besonders interessiert uns:

- ein Weg, an `secrets_schutz.py`, `pii_schutz.py` oder `befehle_schutz.py` vorbei eine gesperrte Datei zu lesen oder einen gesperrten Befehl auszuführen,
- ein Eingabe-JSON, mit dem ein Hook hängt, abstürzt oder etwas anderes als die Aktion durchlässt,
- eine Vorlage, die mehr freigibt, als die Doku verspricht.

## Was die Hooks leisten und was nicht

Die Hooks sind eine zusätzliche Schicht neben den deny-Regeln in `settings.json`. Sie erkennen bekannte Muster. Wer bewusst umgehen will, findet Wege, etwa einen Befehl in einem Skript verstecken, das Claude erst schreibt und dann ausführt. Für eine harte Grenze gehören die Sandbox von Claude Code, ein Devcontainer ohne Zugangsdaten und Managed Settings dazu. Siehe [Claude Code Sicherheit](docs/anleitungen/claude-code-sicherheit.md).

## Unterstützte Versionen

Sicherheitskorrekturen gibt es für die jeweils neueste Version.
