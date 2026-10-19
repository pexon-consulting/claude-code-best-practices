"""CLI, Berichtsformate und scannen."""

from __future__ import annotations

import io
import json
import subprocess
import sys

import pytest

from claude_team.cli import main
from claude_team.regeln import REGELN
from conftest import aws_schluessel, git, iban, schreibe


def kaputtes_repo(ordner):
    schreibe(ordner, "CLAUDE.md", "# App\n")
    schreibe(ordner, ".claude/settings.json", {"permissions": {"defaultMode": "bypassPermissions", "allow": ["Bash"]}})
    schreibe(ordner, "CLAUDE.local.md", "privat")
    return ordner


def lauf(capsys, *argumente) -> tuple[int, str]:
    code = main([*map(str, argumente)])
    return code, capsys.readouterr().out


def test_audit_text_und_exit_code(projekt, capsys):
    code, aus = lauf(capsys, "audit", kaputtes_repo(projekt))
    assert code == 1
    assert "FEHLER  CC012" in aus and "Fehler," in aus


def test_audit_schwelle(projekt, capsys):
    schreibe(projekt, "CLAUDE.md", "npm test\n")
    assert lauf(capsys, "audit", projekt)[0] == 1  # CC013 ohne settings
    assert lauf(capsys, "audit", projekt, "--ignorieren", "cc013")[0] == 0
    assert lauf(capsys, "audit", projekt, "--ignorieren", "CC013", "--schwelle", "warnung")[0] == 0
    assert lauf(capsys, "audit", projekt, "--ignorieren", "CC013", "--schwelle", "hinweis")[0] == 0


def test_audit_json(projekt, capsys):
    code, aus = lauf(capsys, "audit", kaputtes_repo(projekt), "--format", "json")
    daten = json.loads(aus)
    assert daten["werkzeug"] == "claude-team" and daten["anzahl"]["fehler"] >= 2
    assert all(b["link"].endswith("#" + b["regel"].lower()) for b in daten["befunde"])


def test_audit_sarif(projekt, capsys, tmp_path):
    ziel = tmp_path / "bericht.sarif"
    lauf(capsys, "audit", kaputtes_repo(projekt), "--format", "sarif", "--out", ziel)
    sarif = json.loads(ziel.read_text(encoding="utf-8"))
    assert sarif["version"] == "2.1.0"
    lauf_ = sarif["runs"][0]
    regel_ids = {r["id"] for r in lauf_["tool"]["driver"]["rules"]}
    assert {e["ruleId"] for e in lauf_["results"]} <= regel_ids
    assert {e["level"] for e in lauf_["results"]} <= {"error", "warning", "note"}
    assert all(r["helpUri"].startswith("https://github.com/") for r in lauf_["tool"]["driver"]["rules"])


def test_audit_markdown(projekt, capsys):
    _, aus = lauf(capsys, "audit", kaputtes_repo(projekt), "--format", "markdown")
    assert aus.startswith("# Claude-Code-Prüfung") and "| fehler | [CC012](" in aus


def test_audit_sauber(projekt, capsys):
    schreibe(projekt, "package.json", '{"scripts": {"test": "vitest"}}')
    main(["einrichten", str(projekt)])
    capsys.readouterr()
    code, aus = lauf(capsys, "audit", projekt, "--schwelle", "warnung")
    assert code == 0, aus


def test_bericht_singular():
    from claude_team.bericht import summe
    assert summe({"fehler": 1, "warnung": 1, "hinweis": 1}) == "1 Fehler, 1 Warnung, 1 Hinweis"
    assert summe({"fehler": 2, "warnung": 0, "hinweis": 3}) == "2 Fehler, 0 Warnungen, 3 Hinweise"


def test_falscher_ordner(capsys):
    with pytest.raises(SystemExit) as fehler:
        main(["audit", "/gibt/es/nicht"])
    assert fehler.value.code == 2


def test_einrichten_unbekannter_baustein(projekt, capsys):
    assert main(["einrichten", str(projekt), "--ohne", "hooks,quatsch"]) == 2


def test_einrichten_dry_run(projekt, capsys):
    code, aus = lauf(capsys, "einrichten", projekt, "--dry-run")
    assert code == 0 and "Probelauf" in aus and not (projekt / "CLAUDE.md").exists()


def test_regeln_liste(capsys):
    _, aus = lauf(capsys, "regeln", "--json")
    daten = json.loads(aus)
    assert len(daten) == len(REGELN) and {"id", "schwere", "titel", "link"} <= set(daten[0])


def test_scannen_findet_und_maskiert(projekt, capsys):
    schreibe(projekt, "app.py", f'KEY = "{aws_schluessel()}"\n')
    schreibe(projekt, "kunden.csv", f"Max;{iban()}\n")
    schreibe(projekt, "nicht_getrackt.txt", f"{iban()}\n")
    git(projekt, "add", "app.py", "kunden.csv")
    code, aus = lauf(capsys, "scannen", projekt, "--json")
    treffer = json.loads(aus)
    assert code == 1
    assert {(t["datei"].rsplit("/", 1)[-1], t["art"]) for t in treffer} == {("app.py", "aws-zugangsschluessel"), ("kunden.csv", "iban")}
    assert aws_schluessel() not in aus and iban() not in aus


def test_scannen_alle(projekt, capsys):
    schreibe(projekt, "nicht_getrackt.txt", f"{iban()}\n")
    assert lauf(capsys, "scannen", projekt)[0] == 0
    assert lauf(capsys, "scannen", projekt, "--alle")[0] == 1


def test_scannen_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(f"Konto {iban()}"))
    code, aus = lauf(capsys, "scannen", "-")
    assert code == 1 and "<stdin>:1" in aus


def test_scannen_kontakte(projekt, capsys):
    schreibe(projekt, "liste.txt", "\n".join(f"p{i}@firma.example" for i in range(3)))
    assert lauf(capsys, "scannen", projekt / "liste.txt")[0] == 0
    assert lauf(capsys, "scannen", projekt / "liste.txt", "--kontakte-ab", "3")[0] == 1


def test_modul_aufruf():
    lauf_ = subprocess.run([sys.executable, "-m", "claude_team.cli", "--version"], capture_output=True, text=True, check=False)
    assert lauf_.returncode == 0 and lauf_.stdout.startswith("claude-team ")
