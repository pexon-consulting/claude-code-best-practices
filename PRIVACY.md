# Datenschutz

`claude-team` und die Hooks laufen vollständig auf deinem Rechner. Es gibt keinen Upload, keine Telemetrie und keinen Netzabruf. Einzige Ausnahme ist `uvx` oder `pip`, das beim ersten Aufruf dieses Paket herunterlädt.

- `claude-team audit` liest Konfigurationsdateien und schreibt nur dorthin, wo `--out` hinzeigt.
- `claude-team einrichten` legt Dateien im angegebenen Projekt an und überschreibt keine bestehende.
- `claude-team scannen` liest die angegebenen Dateien. Treffer erscheinen nur maskiert, nie mit vollem Wert.
- Die Hooks lesen, was Claude Code ihnen auf stdin übergibt, und antworten auf stdout. Der Protokoll-Hook ist standardmäßig aus. Eingeschaltet schreibt er nach `.claude/protokoll/` im Projekt: Zeit, Werkzeug, Dateipfad und Befehl mit maskierten Tokens, Kennungen und E-Mail-Adressen, keine Dateiinhalte. Dateien älter als `aufbewahrung_tage` (Standard 30) löscht er selbst.

Was Claude Code selbst an Anthropic oder einen Cloud-Anbieter sendet, regeln dessen Bedingungen. Dazu: [Claude Code DSGVO](docs/anleitungen/claude-code-dsgvo.md).
