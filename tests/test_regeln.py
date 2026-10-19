"""Prüfregeln: jede Regel feuert in einem passenden Repo und schweigt im eingerichteten."""

from __future__ import annotations

import pytest

from claude_team.einrichten import Einrichtung
from claude_team.regeln import REGELN, imports, pruefe, version_offen, zu_breit
from conftest import git, github_token, schreibe

GUTE_SETTINGS = {
    "permissions": {
        "disableBypassPermissionsMode": "disable",
        "deny": ["Read(.env)", "Read(.env.*)", "Read(**/*.pem)"],
    },
    "env": {"DISABLE_TELEMETRY": "1"},
    "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "true"}]}]},
}


def regeln(ordner) -> set[str]:
    return {b.regel for b in pruefe(ordner)}


def befunde(ordner, regel: str):
    return [b for b in pruefe(ordner) if b.regel == regel]


def basis(ordner, settings: dict | None = None, claude_md: str = "# App\n\n`npm test` startet die Tests.\n"):
    schreibe(ordner, "CLAUDE.md", claude_md)
    schreibe(ordner, ".claude/settings.json", settings or GUTE_SETTINGS)
    return ordner


def test_eingerichtetes_repo_hat_keine_fehler_und_warnungen(projekt):
    schreibe(projekt, "package.json", '{"scripts": {"test": "vitest", "lint": "eslint ."}}')
    Einrichtung(projekt, set()).ausfuehren()
    rest = [b for b in pruefe(projekt) if b.schwere != "hinweis"]
    assert rest == [], rest


def test_gute_basis_ist_ruhig(projekt):
    basis(projekt)
    assert regeln(projekt) == set()


# --- CLAUDE.md ----------------------------------------------------------------

def test_cc001_ohne_claude_md(projekt):
    assert "CC001" in regeln(projekt)


def test_cc001_agents_md_reicht(projekt):
    schreibe(projekt, "AGENTS.md", "# Agents\n")
    assert "CC001" not in regeln(projekt)


def test_cc002_zu_lang(projekt):
    basis(projekt, claude_md="npm test\n" + "Regel\n" * 220)
    assert "CC002" in regeln(projekt)


def test_cc003_ohne_befehle(projekt):
    basis(projekt, claude_md="# App\n\nSei gründlich.\n")
    assert "CC003" in regeln(projekt)


def test_cc004_import_fehlt(projekt):
    basis(projekt, claude_md="npm test\n\nSiehe @docs/architektur.md und @README.\n")
    funde = befunde(projekt, "CC004")
    assert {f.zeile for f in funde} == {3}
    assert len(funde) == 2


def test_cc004_ignoriert_codebloecke_und_pakete(projekt):
    text = "npm test\n\n`@docs/fehlt.md`\n\n```\n@auch/fehlt.md\n```\n\nPakete: @types/node, @angular/core. Team: @backend\n"
    basis(projekt, claude_md=text)
    assert "CC004" not in regeln(projekt)


def test_cc004_vorhandener_import_ok(projekt):
    schreibe(projekt, "docs/architektur.md", "x")
    basis(projekt, claude_md="npm test\n@docs/architektur.md\n")
    assert "CC004" not in regeln(projekt)


def test_cc005_claude_local_nicht_ignoriert(projekt):
    basis(projekt)
    schreibe(projekt, "CLAUDE.local.md", "privat")
    assert "CC005" in regeln(projekt)
    schreibe(projekt, ".gitignore", "CLAUDE.local.md\n")
    assert "CC005" not in regeln(projekt)


def test_cc006_agents_md_neben_claude_md(projekt):
    basis(projekt)
    schreibe(projekt, "AGENTS.md", "# Agents\n")
    assert "CC006" in regeln(projekt)
    basis(projekt, claude_md="@AGENTS.md\n\nnpm test\n")
    assert "CC006" not in regeln(projekt)


def test_cc007_offene_platzhalter(projekt):
    basis(projekt, claude_md="# App\n\n{{EIN_SATZ_WAS_DAS_PROJEKT_TUT}}\n\n- Test: `npm test`\n- Lint: {{LINT}}\n")
    (b,) = befunde(projekt, "CC007")
    assert b.zeile == 3 and "{{EIN_SATZ_WAS_DAS_PROJEKT_TUT}}" in b.meldung and "{{LINT}}" in b.meldung
    basis(projekt, claude_md="# App\n\n`npm test`\n\n```\n{{BEISPIEL}}\n```\n")
    assert "CC007" not in regeln(projekt)


def test_cc007_nach_einrichten(projekt):
    schreibe(projekt, "package.json", '{"scripts": {"test": "vitest"}}')
    Einrichtung(projekt, set()).ausfuehren()
    assert "CC007" in regeln(projekt)


def test_imports_funktion():
    assert imports("Lies @./a.md, dann @~/x.md.\n`@b.md`") == [(1, "./a.md"), (1, "~/x.md")]


# --- settings.json ------------------------------------------------------------

def test_cc010_kaputtes_json(projekt):
    schreibe(projekt, "CLAUDE.md", "npm test")
    schreibe(projekt, ".claude/settings.json", '{"permissions": {,}}')
    assert "CC010" in regeln(projekt)


def test_cc011_settings_local_im_repo(projekt):
    basis(projekt)
    schreibe(projekt, ".claude/settings.local.json", "{}")
    assert "CC011" in regeln(projekt)
    schreibe(projekt, ".gitignore", ".claude/settings.local.json\n")
    assert "CC011" not in regeln(projekt)
    git(projekt, "add", "-f", ".claude/settings.local.json")
    assert "CC011" in regeln(projekt), "getrackt zählt, auch wenn ignoriert"


def test_cc012_bypass(projekt):
    basis(projekt, {**GUTE_SETTINGS, "permissions": {**GUTE_SETTINGS["permissions"], "defaultMode": "bypassPermissions"}})
    assert befunde(projekt, "CC012")[0].schwere == "fehler"


def test_cc012_nicht_gesperrt_ist_hinweis(projekt):
    rechte = {k: v for k, v in GUTE_SETTINGS["permissions"].items() if k != "disableBypassPermissionsMode"}
    basis(projekt, {**GUTE_SETTINGS, "permissions": rechte})
    assert befunde(projekt, "CC012")[0].schwere == "hinweis"


def test_cc013_ohne_env_sperre(projekt):
    basis(projekt, {**GUTE_SETTINGS, "permissions": {"disableBypassPermissionsMode": "disable", "deny": ["Read(**/*.pem)"]}})
    assert "CC013" in regeln(projekt)


def test_cc013_ohne_settings(projekt):
    schreibe(projekt, "CLAUDE.md", "npm test")
    assert "CC013" in regeln(projekt)


def test_cc014_ohne_schluessel_sperre(projekt):
    basis(projekt, {**GUTE_SETTINGS, "permissions": {"disableBypassPermissionsMode": "disable", "deny": ["Read(.env)"]}})
    assert "CC014" in regeln(projekt)


@pytest.mark.parametrize("r, erwartet", [
    ("Bash", True), ("Bash(*)", True), ("Edit", True), ("Bash(python3 *)", True), ("Bash(curl:*)", True),
    ("Bash(git *)", True), ("Bash(git status *)", False), ("Bash(npm run test *)", False), ("Read", False),
])
def test_zu_breit(r, erwartet):
    assert zu_breit(r) is erwartet


def test_cc015_allow_zu_breit(projekt):
    basis(projekt, {**GUTE_SETTINGS, "permissions": {**GUTE_SETTINGS["permissions"], "allow": ["Bash(git *)", "Bash(git status *)"]}})
    assert len(befunde(projekt, "CC015")) == 1


def test_cc016_stern_vor_unterbefehl(projekt):
    basis(projekt, {**GUTE_SETTINGS, "permissions": {**GUTE_SETTINGS["permissions"], "allow": ["Bash(git * main)"]}})
    assert "CC016" in regeln(projekt)


@pytest.mark.parametrize("r", ["Write(docs/**)", "Glob(src/**)", "Bash(git:* push)", "Bash(command:rm)", "MultiEdit(a.py)"])
def test_cc017_wirkungslos(projekt, r):
    basis(projekt, {**GUTE_SETTINGS, "permissions": {**GUTE_SETTINGS["permissions"], "ask": [r]}})
    assert "CC017" in regeln(projekt), r


def test_cc017_mcp_stern_in_allow(projekt):
    basis(projekt, {**GUTE_SETTINGS, "permissions": {**GUTE_SETTINGS["permissions"], "allow": ["mcp__*"]}})
    assert "CC017" in regeln(projekt)


def test_cc018_alle_mcp_automatisch(projekt):
    basis(projekt, {**GUTE_SETTINGS, "enableAllProjectMcpServers": True})
    assert "CC018" in regeln(projekt)


def test_cc019_telemetrie(projekt):
    basis(projekt, {k: v for k, v in GUTE_SETTINGS.items() if k != "env"})
    assert "CC019" in regeln(projekt)


# --- Hooks --------------------------------------------------------------------

def _hook_settings(befehl: str, ereignis: str = "PreToolUse", **extra) -> dict:
    return {**GUTE_SETTINGS, "hooks": {ereignis: [{"matcher": "Bash", "hooks": [{"type": "command", "command": befehl, **extra}]}]}}


def test_cc020_keine_hooks(projekt):
    basis(projekt, {k: v for k, v in GUTE_SETTINGS.items() if k != "hooks"})
    assert "CC020" in regeln(projekt)


def test_cc021_hook_datei_fehlt(projekt):
    basis(projekt, _hook_settings('python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/fehlt.py"'))
    assert [b.regel for b in befunde(projekt, "CC021")] == ["CC021"]


def test_cc021_mit_args(projekt):
    basis(projekt, _hook_settings("python3", args=["${CLAUDE_PROJECT_DIR}/.claude/hooks/fehlt.py"]))
    assert "CC021" in regeln(projekt)


def test_cc022_nicht_ausfuehrbar(projekt):
    schreibe(projekt, ".claude/hooks/pruef.sh", "#!/bin/sh\nexit 0\n").chmod(0o644)
    basis(projekt, _hook_settings('"$CLAUDE_PROJECT_DIR"/.claude/hooks/pruef.sh'))
    assert "CC022" in regeln(projekt)
    (projekt / ".claude/hooks/pruef.sh").chmod(0o755)
    assert "CC022" not in regeln(projekt)


def test_cc022_mit_interpreter_egal(projekt):
    schreibe(projekt, ".claude/hooks/check.py", "print()").chmod(0o644)
    basis(projekt, _hook_settings('python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/check.py"'))
    assert regeln(projekt) & {"CC021", "CC022", "CC023"} == set()


def test_cc023_relativer_pfad(projekt):
    schreibe(projekt, ".claude/hooks/check.py", "print()")
    basis(projekt, _hook_settings("python3 .claude/hooks/check.py"))
    assert "CC023" in regeln(projekt)


def test_cc024_unbekanntes_ereignis(projekt):
    basis(projekt, _hook_settings("true", ereignis="PreToolUsage"))
    assert "CC024" in regeln(projekt)


# --- Secrets und MCP ----------------------------------------------------------

def test_cc030_token_in_claude_md(projekt):
    basis(projekt, claude_md=f"npm test\n\nGitHub: {github_token()}\n")
    funde = befunde(projekt, "CC030")
    assert funde and funde[0].zeile == 3
    assert github_token() not in funde[0].meldung


def _mcp(projekt, server: dict):
    basis(projekt)
    schreibe(projekt, ".mcp.json", {"mcpServers": {"dienst": server}})


def test_cc031_mcp_kaputt(projekt):
    basis(projekt)
    schreibe(projekt, ".mcp.json", "{")
    assert "CC031" in regeln(projekt)


def test_cc032_klartext_header(projekt):
    _mcp(projekt, {"type": "http", "url": "https://mcp.example.org", "headers": {"Authorization": "Bearer abc123def456"}})
    meldung = befunde(projekt, "CC032")[0].meldung
    assert "Bearer ${DIENST_TOKEN}" in meldung


def test_cc032_klartext_env(projekt):
    _mcp(projekt, {"command": "node", "args": ["server.js"], "env": {"API_KEY": "abc123def456"}})
    assert "${API_KEY}" in befunde(projekt, "CC032")[0].meldung


def test_cc032_variable_ok(projekt):
    _mcp(projekt, {"type": "http", "url": "https://mcp.example.org", "headers": {"Authorization": "Bearer ${DIENST_TOKEN}"}})
    assert "CC032" not in regeln(projekt)


@pytest.mark.parametrize("paket, starter, offen", [
    ("@modelcontextprotocol/server-postgres", "npx", True),
    ("@modelcontextprotocol/server-postgres@latest", "npx", True),
    ("@modelcontextprotocol/server-postgres@0.6.2", "npx", False),
    ("mcp-server-git", "uvx", True),
    ("mcp-server-git==0.6.2", "uvx", False),
    ("./lokal.js", "npx", False),
])
def test_version_offen(paket, starter, offen):
    assert version_offen(paket, starter) is offen


def test_cc033_ohne_version(projekt):
    _mcp(projekt, {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]})
    assert "CC033" in regeln(projekt)


def test_cc034_url_ohne_typ(projekt):
    _mcp(projekt, {"url": "https://mcp.example.org/mcp"})
    assert "CC034" in regeln(projekt)


def test_cc035_sse(projekt):
    _mcp(projekt, {"type": "sse", "url": "https://mcp.example.org/sse"})
    assert "CC035" in regeln(projekt)


def test_cc036_geschuetzte_variable(projekt):
    _mcp(projekt, {"type": "http", "url": "https://mcp.example.org", "headers": {"X-Key": "${ANTHROPIC_API_KEY}"}})
    assert "CC036" in regeln(projekt)


# --- Subagents und Skills -----------------------------------------------------

def test_cc040_agent_ohne_description(projekt):
    basis(projekt)
    schreibe(projekt, ".claude/agents/review.md", "---\nname: review\n---\nPrüfe.")
    assert "CC040" in regeln(projekt)


def test_cc041_agent_bypass(projekt):
    basis(projekt)
    schreibe(projekt, ".claude/agents/r.md", "---\nname: r\ndescription: d\ntools: Read\npermissionMode: bypassPermissions\n---\n")
    assert "CC041" in regeln(projekt)


def test_cc042_skill_ohne_description(projekt):
    basis(projekt)
    schreibe(projekt, ".claude/skills/release/SKILL.md", "# Release\n")
    assert "CC042" in regeln(projekt)


def test_cc043_skill_zu_lang(projekt):
    basis(projekt)
    schreibe(projekt, ".claude/skills/gross/SKILL.md", "---\ndescription: d\n---\n" + "x\n" * 510)
    assert "CC043" in regeln(projekt)


def test_cc044_agent_ohne_tools(projekt):
    basis(projekt)
    schreibe(projekt, ".claude/agents/r.md", "---\nname: r\ndescription: >\n  Mehrzeilige\n  Beschreibung\n---\n")
    assert regeln(projekt) & {"CC040", "CC044"} == {"CC044"}


# --- Git ----------------------------------------------------------------------

def test_cc050_env_getrackt(projekt):
    basis(projekt)
    schreibe(projekt, ".env.production", "X=1")
    schreibe(projekt, ".env.example", "X=")
    git(projekt, "add", ".env.production", ".env.example")
    assert [b.datei for b in befunde(projekt, "CC050")] == [".env.production"]


def test_cc050_env_nicht_ignoriert(projekt):
    basis(projekt)
    schreibe(projekt, ".env", "X=1")
    assert "CC050" in regeln(projekt)
    schreibe(projekt, ".gitignore", ".env\n")
    assert "CC050" not in regeln(projekt)


def test_cc051_protokoll(projekt):
    basis(projekt)
    schreibe(projekt, ".claude/protokoll/2026-10-15.jsonl", "{}")
    assert "CC051" in regeln(projekt)


def test_ohne_git_funktioniert(tmp_path):
    basis(tmp_path)
    schreibe(tmp_path, ".env", "X=1")
    schreibe(tmp_path, ".gitignore", ".env\n")
    assert "CC050" not in regeln(tmp_path)


def test_alle_regeln_sind_dokumentiert():
    from pathlib import Path
    doku = (Path(__file__).parent.parent / "docs" / "regeln.md").read_text(encoding="utf-8")
    for r in REGELN.values():
        assert f'<a id="{r.id.lower()}"></a>' in doku, r.id
        assert f"| [{r.id}](#{r.id.lower()}) | {r.schwere} | {r.titel} |" in doku, r.id


def test_alle_regeln_haben_tests():
    getestet = {name.split("_")[1].upper() for name in globals() if name.startswith("test_cc")}
    assert set(REGELN) <= getestet, set(REGELN) - getestet
