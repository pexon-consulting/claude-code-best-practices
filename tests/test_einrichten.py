"""einrichten: legt an, überschreibt nie, führt settings.json zusammen."""

from __future__ import annotations

import json
import os

from claude_team.einrichten import Einrichtung, erkenne_befehle, settings_daten, zusammenfuehren
from claude_team.projekt import VORLAGE
from conftest import schreibe


def arten(aktionen) -> dict[str, str]:
    return {a.datei: a.art for a in aktionen}


def test_leeres_projekt_bekommt_alles(projekt):
    ergebnis = arten(Einrichtung(projekt, set()).ausfuehren())
    for datei in ("CLAUDE.md", ".claude/settings.json", ".claude/schutz.json", ".claude/hooks/secrets_schutz.py",
                  ".claude/agents/code-reviewer.md", ".claude/skills/commit/SKILL.md", ".claude/rules/tests.md", ".mcp.json.example", ".gitignore"):
        assert ergebnis[datei] == "angelegt", datei
        assert (projekt / datei).is_file()
    assert not any("__pycache__" in d for d in ergebnis)


def test_hooks_ausfuehrbar_hilfsmodule_nicht(projekt):
    Einrichtung(projekt, set()).ausfuehren()
    hooks = projekt / ".claude" / "hooks"
    assert os.access(hooks / "secrets_schutz.py", os.X_OK)
    assert not os.access(hooks / "_hook.py", os.X_OK)
    assert not os.access(hooks / "muster.py", os.X_OK)


def test_zweiter_lauf_aendert_nichts(projekt):
    Einrichtung(projekt, set()).ausfuehren()
    vorher = {p: p.read_bytes() for p in projekt.rglob("*") if p.is_file() and ".git" not in p.parts}
    zweiter = Einrichtung(projekt, set()).ausfuehren()
    assert {a.art for a in zweiter} == {"unveraendert"}
    assert vorher == {p: p.read_bytes() for p in projekt.rglob("*") if p.is_file() and ".git" not in p.parts}


def test_probelauf_schreibt_nichts(projekt):
    aktionen = Einrichtung(projekt, set(), probelauf=True).ausfuehren()
    assert aktionen and all(a.art == "angelegt" for a in aktionen)
    assert [p.name for p in projekt.iterdir()] == [".git"]


def test_eigene_claude_md_bleibt(projekt):
    schreibe(projekt, "CLAUDE.md", "# Meins\n")
    ergebnis = arten(Einrichtung(projekt, set()).ausfuehren())
    assert (projekt / "CLAUDE.md").read_text(encoding="utf-8") == "# Meins\n"
    assert ergebnis["CLAUDE.vorschlag.md"] == "vorschlag"


def test_eigener_hook_bleibt(projekt):
    schreibe(projekt, ".claude/hooks/secrets_schutz.py", "# eigene Version\n")
    ergebnis = arten(Einrichtung(projekt, set()).ausfuehren())
    assert ergebnis[".claude/hooks/secrets_schutz.py"] == "uebersprungen"
    assert (projekt / ".claude/hooks/secrets_schutz.py").read_text(encoding="utf-8") == "# eigene Version\n"


def test_settings_werden_zusammengefuehrt(projekt):
    alt = {
        "model": "opus",
        "permissions": {"defaultMode": "bypassPermissions", "allow": ["Bash(make *)"], "deny": ["Read(.env)"]},
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "./eigener.sh"}]}]},
    }
    schreibe(projekt, ".claude/settings.json", alt)
    ergebnis = arten(Einrichtung(projekt, set()).ausfuehren())
    assert ergebnis[".claude/settings.vorschlag.json"] == "vorschlag"
    assert json.loads((projekt / ".claude/settings.json").read_text(encoding="utf-8")) == alt

    vorschlag = json.loads((projekt / ".claude/settings.vorschlag.json").read_text(encoding="utf-8"))
    rechte = vorschlag["permissions"]
    assert vorschlag["model"] == "opus"
    assert rechte["defaultMode"] == "default", "bypassPermissions darf der Vorschlag nicht übernehmen"
    assert rechte["allow"][0] == "Bash(make *)" and "Bash(git status *)" in rechte["allow"]
    assert rechte["deny"].count("Read(.env)") == 1
    befehle = [h["command"] for g in vorschlag["hooks"]["PreToolUse"] for h in g["hooks"]]
    assert befehle[0] == "./eigener.sh" and any("secrets_schutz.py" in b for b in befehle)


def test_kaputte_settings_bekommen_vorschlag(projekt):
    schreibe(projekt, ".claude/settings.json", "{ kaputt")
    ergebnis = arten(Einrichtung(projekt, {"claude-md"}).ausfuehren())
    assert ergebnis[".claude/settings.vorschlag.json"] == "vorschlag"
    assert (projekt / ".claude/settings.json").read_text(encoding="utf-8") == "{ kaputt"


def test_gitignore_wird_nur_ergaenzt(projekt):
    schreibe(projekt, ".gitignore", "node_modules/\n.env")
    Einrichtung(projekt, {"claude-md", "settings", "hooks", "regeln", "agents", "skills", "mcp"}).ausfuehren()
    zeilen = (projekt / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert zeilen[:2] == ["node_modules/", ".env"]
    assert zeilen.count(".env") == 1 and "CLAUDE.local.md" in zeilen and ".claude/protokoll/" in zeilen


def test_ohne_hooks_keine_hooks_in_settings(projekt):
    Einrichtung(projekt, {"hooks"}).ausfuehren()
    assert "hooks" not in json.loads((projekt / ".claude/settings.json").read_text(encoding="utf-8"))
    assert not (projekt / ".claude/hooks").exists()


def test_profil_streng():
    daten = settings_daten("streng")
    assert "WebFetch" in daten["permissions"]["deny"] and "WebFetch" not in daten["permissions"]["ask"]
    assert "Bash(curl *)" in daten["permissions"]["deny"]
    assert daten["env"]["DISABLE_FEEDBACK_COMMAND"] == "1"


def test_vorlage_ist_gueltiges_json():
    for datei in (".claude/settings.json", ".claude/schutz.json", ".mcp.json.example"):
        json.loads((VORLAGE / datei).read_text(encoding="utf-8"))


def test_zusammenfuehren_behaelt_werte():
    assert zusammenfuehren({"a": 1, "l": [1]}, {"a": 2, "b": 3, "l": [1, 2]}) == {"a": 1, "b": 3, "l": [1, 2]}


def test_befehle_aus_package_json(projekt):
    schreibe(projekt, "package.json", '{"scripts": {"test": "vitest", "lint": "eslint .", "dev": "vite"}}')
    schreibe(projekt, "pnpm-lock.yaml", "")
    assert erkenne_befehle(projekt) == {"INSTALL": "pnpm install", "TEST": "pnpm run test", "LINT": "pnpm run lint", "START": "pnpm run dev"}


def test_befehle_npm(projekt):
    schreibe(projekt, "package.json", '{"scripts": {"test": "jest", "start": "node ."}}')
    assert erkenne_befehle(projekt) == {"INSTALL": "npm install", "TEST": "npm test", "LINT": "", "START": "npm start"}


def test_befehle_python_uv(projekt):
    schreibe(projekt, "pyproject.toml", "[tool.ruff]\n")
    schreibe(projekt, "uv.lock", "")
    befehle = erkenne_befehle(projekt)
    assert befehle["INSTALL"] == "uv sync" and befehle["TEST"] == "uv run pytest" and befehle["LINT"].startswith("ruff")


def test_befehle_makefile(projekt):
    schreibe(projekt, "Makefile", "install:\n\tpip install .\ntest:\n\tpytest\nrun:\n\tpython app.py\n")
    assert erkenne_befehle(projekt) == {"INSTALL": "make install", "TEST": "make test", "LINT": "", "START": "make run"}


def test_claude_md_mit_befehlen(projekt):
    schreibe(projekt, "package.json", '{"scripts": {"test": "vitest"}}')
    Einrichtung(projekt, set()).ausfuehren()
    text = (projekt / "CLAUDE.md").read_text(encoding="utf-8")
    assert "npm test" in text and "{{TEST}}" not in text and projekt.name in text
