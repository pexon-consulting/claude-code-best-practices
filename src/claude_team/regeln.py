"""Prüfregeln für ein Repo mit Claude Code. Jede Regel hat eine feste ID und einen Anker in docs/regeln.md."""

from __future__ import annotations

import re
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterator

from .projekt import Projekt, frontmatter, lade_muster

FEHLER, WARNUNG, HINWEIS = "fehler", "warnung", "hinweis"
DOKU = "https://github.com/pexon-consulting/claude-code-best-practices/blob/main/docs/regeln.md"


@dataclass(frozen=True)
class Regel:
    id: str
    anker: str
    schwere: str
    titel: str

    @property
    def link(self) -> str:
        return f"{DOKU}#{self.id.lower()}"


@dataclass(frozen=True)
class Befund:
    regel: str
    schwere: str
    datei: str
    meldung: str
    zeile: int = 0
    link: str = ""

    def als_dict(self) -> dict:
        return asdict(self)


REGELN: dict[str, Regel] = {}
PRUEFUNGEN: list[Callable[[Projekt], Iterator[Befund]]] = []


def regel(id: str, anker: str, schwere: str, titel: str) -> Regel:
    REGELN[id] = Regel(id, anker, schwere, titel)
    return REGELN[id]


def pruefung(funktion):
    PRUEFUNGEN.append(funktion)
    return funktion


def befund(r: Regel, datei: str, meldung: str, zeile: int = 0, schwere: str = "") -> Befund:
    return Befund(r.id, schwere or r.schwere, datei, meldung, zeile, r.link)


# --- CLAUDE.md ----------------------------------------------------------------

R_MD_FEHLT = regel("CC001", "cc001-claude-md-fehlt", WARNUNG, "Keine CLAUDE.md und keine AGENTS.md")
R_MD_LANG = regel("CC002", "cc002-claude-md-zu-lang", WARNUNG, "CLAUDE.md über 200 Zeilen")
R_MD_BEFEHLE = regel("CC003", "cc003-claude-md-ohne-befehle", HINWEIS, "CLAUDE.md nennt keine Befehle")
R_MD_IMPORT = regel("CC004", "cc004-import-fehlt", FEHLER, "@-Import zeigt auf fehlende Datei")
R_MD_LOKAL = regel("CC005", "cc005-claude-local-nicht-ignoriert", FEHLER, "CLAUDE.local.md nicht in .gitignore")
R_MD_AGENTS = regel("CC006", "cc006-agents-md-wird-ignoriert", HINWEIS, "AGENTS.md wird neben CLAUDE.md nicht gelesen")
R_MD_PLATZHALTER = regel("CC007", "cc007-platzhalter-offen", HINWEIS, "Platzhalter {{...}} in CLAUDE.md nicht ausgefüllt")

MD_DATEIEN = ("CLAUDE.md", ".claude/CLAUDE.md")
_IMPORT = re.compile(r"(?<![\w`/])@((?:~/|\.{1,2}/|/)?[\w./\\ -]*?[\w-]+(?:\.[\w]+)?)(?=[.!?]?(?:[\s,;:)]|$))")
_CODEBLOCK = re.compile(r"```.*?```|~~~.*?~~~", re.S)
_CODESPAN = re.compile(r"`[^`\n]*`")
_PLATZHALTER = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
_BEFEHL_HINWEIS = re.compile(r"(?im)(?:^\s*(?:[-*]\s+)?(?:[$>]\s*)?|`)(?:npm|pnpm|yarn|bun|npx|uv|uvx|pip|python3?|pytest|make|cargo|go|mvn|gradle|\./gradlew|dotnet|docker|composer|php|bundle|rake|deno|just|task|tox|nox|ruff)\b")


def imports(text: str) -> list[tuple[int, str]]:
    """@-Importe außerhalb von Codeblöcken und Codespans, mit Zeilennummer."""
    ohne = _CODEBLOCK.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    funde = []
    for nr, zeile in enumerate(ohne.splitlines(), 1):
        zeile = _CODESPAN.sub("", zeile)
        for m in _IMPORT.finditer(zeile):
            ziel = m.group(1).replace("\\ ", " ").rstrip(".")
            if _ist_dateiimport(ziel):
                funde.append((nr, ziel))
    return funde


def _ist_dateiimport(ziel: str) -> bool:
    """Datei mit Endung, expliziter Pfad oder README/AGENTS. Nicht: @types/node, @agent-reviewer, @team."""
    if ziel.startswith(("./", "../", "~/", "/")):
        return True
    if Path(ziel).name in ("README", "AGENTS", "CLAUDE", "CONTRIBUTING", "LICENSE"):
        return True
    return bool(re.search(r"\.[A-Za-z0-9]{1,6}$", ziel))


@pruefung
def claude_md(p: Projekt) -> Iterator[Befund]:
    vorhanden = [d for d in MD_DATEIEN if p.datei(d).is_file()]
    agents = p.datei("AGENTS.md").is_file()
    if not vorhanden and not agents:
        yield befund(R_MD_FEHLT, "CLAUDE.md", "Ohne CLAUDE.md startet jede Sitzung ohne Projektwissen. claude-team einrichten legt eine Vorlage an.")
    if vorhanden and agents:
        haupt = p.text(vorhanden[0])
        if "@AGENTS.md" not in haupt.replace("@./AGENTS.md", "@AGENTS.md"):
            yield befund(R_MD_AGENTS, vorhanden[0], "AGENTS.md liegt daneben, wird aber nicht geladen, solange eine CLAUDE.md existiert. In CLAUDE.md @AGENTS.md eintragen.")
    for relativ in vorhanden + (["CLAUDE.local.md"] if p.datei("CLAUDE.local.md").is_file() else []):
        text = p.text(relativ)
        zeilen = text.count("\n") + 1
        if relativ != "CLAUDE.local.md" and zeilen > 200:
            yield befund(R_MD_LANG, relativ, f"{zeilen} Zeilen. Anthropic empfiehlt unter 200. Bereichsregeln nach .claude/rules/ mit paths verschieben.")
        if relativ != "CLAUDE.local.md" and not _BEFEHL_HINWEIS.search(text):
            yield befund(R_MD_BEFEHLE, relativ, "Keine Build- oder Testbefehle gefunden. Claude rät sonst, wie getestet wird.")
        offen = sorted(set(_PLATZHALTER.findall(_CODEBLOCK.sub("", text))))
        if offen:
            nr = next(i for i, z in enumerate(text.splitlines(), 1) if offen[0] in z)
            yield befund(R_MD_PLATZHALTER, relativ, f"Noch nicht ausgefüllt: {', '.join(offen)}. Claude liest die Platzhalter wörtlich.", nr)
        basis = p.datei(relativ).parent
        for nr, ziel in imports(text):
            pfad = Path(ziel).expanduser() if ziel.startswith("~/") else (Path(ziel) if ziel.startswith("/") else basis / ziel)
            if not pfad.exists():
                yield befund(R_MD_IMPORT, relativ, f"@{ziel} existiert nicht. Claude lädt den Import still nicht.", nr)
    if p.datei("CLAUDE.local.md").is_file() and not p.ist_ignoriert("CLAUDE.local.md"):
        yield befund(R_MD_LOKAL, "CLAUDE.local.md", "Persönliche Notizen landen sonst im Repo. CLAUDE.local.md in .gitignore eintragen.")


# --- settings.json ------------------------------------------------------------

R_SET_JSON = regel("CC010", "cc010-settings-ungueltig", FEHLER, "settings.json ist kein gültiges JSON")
R_SET_LOKAL = regel("CC011", "cc011-settings-local-nicht-ignoriert", FEHLER, "settings.local.json im Repo")
R_SET_BYPASS = regel("CC012", "cc012-bypass-erlaubt", FEHLER, "bypassPermissions als Standard oder nicht gesperrt")
R_SET_ENV = regel("CC013", "cc013-env-nicht-gesperrt", FEHLER, "Keine deny-Regel für .env")
R_SET_KEYS = regel("CC014", "cc014-schluessel-nicht-gesperrt", WARNUNG, "Keine deny-Regel für Schlüsseldateien")
R_SET_BREIT = regel("CC015", "cc015-allow-zu-breit", WARNUNG, "allow-Regel gibt zu viel frei")
R_SET_STERN = regel("CC016", "cc016-stern-vor-unterbefehl", WARNUNG, "Stern vor dem Unterbefehl")
R_SET_WIRKUNGSLOS = regel("CC017", "cc017-regel-wirkungslos", WARNUNG, "Regel wird von Claude Code ignoriert")
R_SET_MCPAUTO = regel("CC018", "cc018-mcp-automatisch-freigegeben", WARNUNG, "Alle MCP-Server aus .mcp.json automatisch freigegeben")
R_SET_TELEMETRIE = regel("CC019", "cc019-telemetrie-an", HINWEIS, "Telemetrie nicht abgeschaltet")

SETTINGS = ".claude/settings.json"
SETTINGS_LOKAL = ".claude/settings.local.json"
ZU_BREIT = {
    "Bash", "Bash(*)", "Bash(* *)", "Edit", "Edit(*)", "Edit(**)", "Write", "WebFetch",
}
ZU_BREIT_PRAEFIX = (
    "bash", "sh", "zsh", "python", "python3", "node", "npx", "uvx", "bunx", "deno", "ruby", "perl", "php",
    "curl", "wget", "ssh", "scp", "docker", "kubectl", "aws", "gcloud", "az", "git", "rm", "sudo", "eval", "env", "xargs",
)
WIRKUNGSLOSE_TOOLS = ("Write", "NotebookEdit", "Glob", "MultiEdit")
ENV_SPERREN = ("Read(.env)", "Read(./.env)", "Read(**/.env)", "Read(.env*)", "Read(./.env*)", "Read(**/.env*)", "Read(*.env)", "Read(**/*.env)")
KEY_SPERREN = re.compile(r"Read\([^)]*(?:\.pem|\.key|id_rsa|id_ed25519|secrets)")


def _regeln(daten: dict, art: str) -> list[str]:
    liste = (daten.get("permissions") or {}).get(art) or []
    return [r for r in liste if isinstance(r, str)]


def zu_breit(r: str) -> bool:
    r = r.strip()
    if r in ZU_BREIT:
        return True
    m = re.fullmatch(r"Bash\(([\w./-]+)(?::\*| \*)\)", r)
    return bool(m) and Path(m.group(1)).name in ZU_BREIT_PRAEFIX


@pruefung
def settings(p: Projekt) -> Iterator[Befund]:
    for relativ in (SETTINGS, SETTINGS_LOKAL):
        datei = p.json(relativ)
        if datei.fehler:
            yield befund(R_SET_JSON, relativ, f"JSON-Fehler: {datei.fehler}. Claude Code überspringt dann die ganze Datei.")
    if p.datei(SETTINGS_LOKAL).is_file() and (SETTINGS_LOKAL in p.getrackt or not p.ist_ignoriert(SETTINGS_LOKAL)):
        yield befund(R_SET_LOKAL, SETTINGS_LOKAL, "Persönliche Freigaben gehören nicht ins Repo. Datei aus Git nehmen und in .gitignore eintragen.")

    datei = p.json(SETTINGS)
    if not isinstance(datei.daten, dict):
        if not datei.vorhanden:
            yield befund(R_SET_ENV, SETTINGS, "Keine Team-Settings. Ohne deny-Regeln darf Claude .env lesen. claude-team einrichten legt eine Basis an.")
        return
    daten = datei.daten
    rechte = daten.get("permissions") or {}
    allow, ask, deny = (_regeln(daten, a) for a in ("allow", "ask", "deny"))

    if rechte.get("defaultMode") == "bypassPermissions":
        yield befund(R_SET_BYPASS, SETTINGS, "defaultMode bypassPermissions schaltet alle Rückfragen ab, für jedes Teammitglied.")
    elif rechte.get("disableBypassPermissionsMode") != "disable":
        yield befund(R_SET_BYPASS, SETTINGS, "disableBypassPermissionsMode ist nicht \"disable\". Jeder kann --dangerously-skip-permissions nutzen.", schwere=HINWEIS)

    if not any(r.replace(" ", "") in ENV_SPERREN for r in deny):
        yield befund(R_SET_ENV, SETTINGS, "Keine deny-Regel wie \"Read(.env)\" und \"Read(.env.*)\". Claude kann Zugangsdaten in den Kontext laden.")
    if not any(KEY_SPERREN.search(r) for r in deny):
        yield befund(R_SET_KEYS, SETTINGS, "Keine deny-Regel für *.pem, *.key, id_rsa oder secrets/.")

    for r in allow:
        if zu_breit(r):
            yield befund(R_SET_BREIT, SETTINGS, f"allow \"{r}\" erlaubt fast alles ohne Rückfrage. Konkrete Unterbefehle freigeben, z.B. \"Bash(git status *)\".")
    for r in allow + ask + deny:
        m = re.fullmatch(r"Bash\((\S+) \* (\S.*)\)", r)
        if m and r in allow:
            yield befund(R_SET_STERN, SETTINGS, f"\"{r}\": Der Stern steht vor dem Unterbefehl und erlaubt damit jeden Unterbefehl samt Optionen wie -c.")
        if ":*" in r and not r.endswith(":*)"):
            yield befund(R_SET_WIRKUNGSLOS, SETTINGS, f"\"{r}\": :* wirkt nur am Ende. In der Mitte ist der Doppelpunkt ein normales Zeichen.")
        werkzeug = r.split("(", 1)[0]
        if werkzeug in WIRKUNGSLOSE_TOOLS and "(" in r:
            ersatz = "Read" if werkzeug == "Glob" else "Edit"
            yield befund(R_SET_WIRKUNGSLOS, SETTINGS, f"\"{r}\" wird nie geprüft. Pfadregeln wirken nur für Read und Edit, also \"{ersatz}({r.split('(', 1)[1]}\".")
        if re.match(r"Bash\(command:", r):
            yield befund(R_SET_WIRKUNGSLOS, SETTINGS, f"\"{r}\" wird ignoriert. Für Bash die Form \"Bash(befehl *)\" nutzen.")
    if "mcp__*" in allow:
        yield befund(R_SET_WIRKUNGSLOS, SETTINGS, "\"mcp__*\" wirkt nur in deny und ask. Für allow je Server freigeben, z.B. \"mcp__github__*\".")

    if daten.get("enableAllProjectMcpServers") is True:
        yield befund(R_SET_MCPAUTO, SETTINGS, "Jeder neue Server in .mcp.json läuft ohne Freigabe. Besser enabledMcpjsonServers mit Namen.")
    env = daten.get("env") or {}
    if not any(k in env for k in ("DISABLE_TELEMETRY", "DO_NOT_TRACK", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC")):
        yield befund(R_SET_TELEMETRIE, SETTINGS, "DISABLE_TELEMETRY und DISABLE_ERROR_REPORTING im env-Block setzen, wenn der Datenschutz das verlangt.")


# --- Hooks --------------------------------------------------------------------

R_HOOK_KEINE = regel("CC020", "cc020-keine-hooks", HINWEIS, "Keine Hooks konfiguriert")
R_HOOK_DATEI = regel("CC021", "cc021-hook-datei-fehlt", FEHLER, "Hook-Skript fehlt")
R_HOOK_AUSF = regel("CC022", "cc022-hook-nicht-ausfuehrbar", FEHLER, "Hook-Skript nicht ausführbar")
R_HOOK_PFAD = regel("CC023", "cc023-hook-relativer-pfad", WARNUNG, "Hook mit relativem Pfad")
R_HOOK_EVENT = regel("CC024", "cc024-hook-unbekanntes-ereignis", WARNUNG, "Unbekanntes Hook-Ereignis")

EREIGNISSE = {
    "PreToolUse", "PostToolUse", "PostToolUseFailure", "PostToolBatch", "PermissionRequest", "PermissionDenied",
    "UserPromptSubmit", "UserPromptExpansion", "Notification", "Stop", "StopFailure", "SubagentStart", "SubagentStop",
    "PreCompact", "PostCompact", "SessionStart", "SessionEnd", "Setup", "TaskCreated", "TaskCompleted", "TeammateIdle",
    "ConfigChange", "CwdChanged", "DirectoryAdded", "FileChanged", "InstructionsLoaded", "MessageDisplay", "WorktreeCreate", "WorktreeRemove",
    "Elicitation", "ElicitationResult", "PreModelSwitch", "PostModelSwitch",
}
INTERPRETER = {"python", "python3", "node", "bash", "sh", "zsh", "uv", "uvx", "bun", "deno", "ruby", "perl", "pwsh", "powershell", "powershell.exe", "npx"}


def _hook_skript(befehl: str, args: list | None) -> tuple[str, bool]:
    """(pfad, direkt) des Skripts in einem Hook-Befehl. direkt heißt: ohne Interpreter gestartet."""
    try:
        teile = shlex.split(befehl)
    except ValueError:
        teile = befehl.split()
    teile += [str(a) for a in (args or [])]
    if not teile:
        return "", False
    direkt = Path(teile[0]).name not in INTERPRETER
    kandidaten = teile[:1] if direkt else [t for t in teile[1:] if not t.startswith("-")][:1]
    for t in kandidaten:
        if "CLAUDE_PROJECT_DIR" in t or t.startswith((".claude/", "./")):
            return t, direkt
    return "", direkt


@pruefung
def hooks(p: Projekt) -> Iterator[Befund]:
    daten = p.json(SETTINGS).daten
    konfig = daten.get("hooks") if isinstance(daten, dict) else None
    if not konfig:
        if isinstance(daten, dict):
            yield befund(R_HOOK_KEINE, SETTINGS, "Ohne Hooks gilt nur, was in CLAUDE.md steht. Hooks setzen Regeln technisch durch.")
        return
    for ereignis, gruppen in konfig.items():
        if ereignis not in EREIGNISSE:
            yield befund(R_HOOK_EVENT, SETTINGS, f"Ereignis \"{ereignis}\" ist unbekannt (Tippfehler?). Der Hook läuft nie.")
            continue
        for gruppe in gruppen or []:
            for hook in (gruppe or {}).get("hooks") or []:
                if hook.get("type", "command") != "command":
                    continue
                befehl = str(hook.get("command", ""))
                skript, direkt = _hook_skript(befehl, hook.get("args"))
                if not skript:
                    if re.match(r"^\.?\.?/?\.claude/", befehl):
                        yield befund(R_HOOK_PFAD, SETTINGS, f"\"{befehl}\" ist relativ zum Arbeitsordner. Mit \"${{CLAUDE_PROJECT_DIR}}\" beginnen.")
                    continue
                if "CLAUDE_PROJECT_DIR" not in skript:
                    yield befund(R_HOOK_PFAD, SETTINGS, f"\"{skript}\" ist relativ zum Arbeitsordner und bricht, wenn Claude in einen Unterordner wechselt. \"${{CLAUDE_PROJECT_DIR}}\" voranstellen.")
                relativ = re.sub(r"^\$\{?CLAUDE_PROJECT_DIR(?::-[^}]*)?\}?/", "", skript).removeprefix("./")
                pfad = p.datei(relativ)
                if not pfad.is_file():
                    yield befund(R_HOOK_DATEI, SETTINGS, f"{ereignis}: {relativ} existiert nicht. Claude Code meldet bei jedem Aufruf einen Hook-Fehler.")
                elif direkt and not (pfad.stat().st_mode & 0o111):
                    yield befund(R_HOOK_AUSF, relativ, f"Wird direkt gestartet, ist aber nicht ausführbar. chmod +x {relativ} oder mit Interpreter aufrufen.")


# --- Secrets in Konfigurationsdateien -----------------------------------------

R_SECRET = regel("CC030", "cc030-secret-in-konfiguration", FEHLER, "Zugangsschlüssel in einer Claude-Datei")
KONFIG_MUSTER = ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", ".mcp.json", ".claude/**/*.md", ".claude/**/*.json")


@pruefung
def secrets(p: Projekt) -> Iterator[Befund]:
    muster = lade_muster()
    gesehen: set[Path] = set()
    for glob in KONFIG_MUSTER:
        for pfad in p.suche(glob):
            if pfad in gesehen or "protokoll" in pfad.parts:
                continue
            gesehen.add(pfad)
            text = p.text(p.rel(pfad))
            for fund in muster.finde_secrets(text):
                zeile = text.count("\n", 0, fund.stelle) + 1
                yield befund(R_SECRET, p.rel(pfad), f"{fund.art} ({fund.vorschau}). Schlüssel rotieren und als ${{VARIABLE}} referenzieren.", zeile)


# --- MCP ----------------------------------------------------------------------

R_MCP_JSON = regel("CC031", "cc031-mcp-ungueltig", FEHLER, ".mcp.json ist kein gültiges JSON")
R_MCP_KLARTEXT = regel("CC032", "cc032-mcp-wert-im-klartext", FEHLER, "Token im Klartext in .mcp.json")
R_MCP_VERSION = regel("CC033", "cc033-mcp-version-offen", WARNUNG, "MCP-Server ohne feste Version")
R_MCP_TYP = regel("CC034", "cc034-mcp-url-ohne-typ", FEHLER, "MCP-Server mit url, aber ohne type")
R_MCP_SSE = regel("CC035", "cc035-mcp-sse-veraltet", HINWEIS, "MCP-Transport sse ist veraltet")
R_MCP_LEER = regel("CC036", "cc036-mcp-variable-wird-leer", FEHLER, "Geschützte Variable in Remote-MCP")

GEHEIM_NAME = re.compile(r"(?i)(token|secret|passw|api[_-]?key|auth|credential|private)")
STARTER = {"npx": "-y", "bunx": "", "pnpx": "", "uvx": "", "pipx": "run"}
GESCHUETZT = {"ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "AWS_BEARER_TOKEN_BEDROCK", "NPM_TOKEN"}


def _paket(args: list[str]) -> str:
    for a in args:
        if not a.startswith("-") and a != "run":
            return a
    return ""


def version_offen(paket: str, starter: str) -> bool:
    if not paket or paket.startswith(("/", ".", "$")):
        return False
    if starter == "uvx" or starter == "pipx":
        return "==" not in paket and "@" not in paket
    name, _, version = paket[1:].partition("@") if paket.startswith("@") else paket.partition("@")
    return not version or version in ("latest", "next")


@pruefung
def mcp(p: Projekt) -> Iterator[Befund]:
    datei = p.json(".mcp.json")
    if datei.fehler:
        yield befund(R_MCP_JSON, ".mcp.json", f"JSON-Fehler: {datei.fehler}")
        return
    if not isinstance(datei.daten, dict):
        return
    for name, server in (datei.daten.get("mcpServers") or {}).items():
        if not isinstance(server, dict):
            continue
        werte = {**(server.get("env") or {}), **(server.get("headers") or {})}
        for schluessel, wert in werte.items():
            if isinstance(wert, str) and wert and "${" not in wert and (GEHEIM_NAME.search(schluessel) or wert.lower().startswith("bearer ")):
                variable = re.sub(r"\W", "_", f"{name}_TOKEN" if wert.lower().startswith("bearer ") else schluessel).upper()
                vorschlag = f"Bearer ${{{variable}}}" if wert.lower().startswith("bearer ") else f"${{{variable}}}"
                yield befund(R_MCP_KLARTEXT, ".mcp.json", f"{name}.{schluessel} steht im Klartext. \"{vorschlag}\" verwenden, Wert in der Shell setzen.")
            for var in re.findall(r"\$\{([A-Z0-9_]+)", str(wert)):
                if var in GESCHUETZT and server.get("url"):
                    yield befund(R_MCP_LEER, ".mcp.json", f"{name}: ${{{var}}} wird in url und headers von Remote-Servern als leer gelesen. Eigenen Variablennamen nutzen.")
        if server.get("url") and not server.get("type"):
            yield befund(R_MCP_TYP, ".mcp.json", f"{name}: url ohne type gilt als stdio und wird übersprungen. \"type\": \"http\" ergänzen.")
        if server.get("type") == "sse":
            yield befund(R_MCP_SSE, ".mcp.json", f"{name}: sse ist veraltet. Auf \"type\": \"http\" wechseln, wenn der Server es kann.")
        starter = Path(str(server.get("command", ""))).name
        if starter in STARTER:
            paket = _paket([str(a) for a in server.get("args") or []])
            if version_offen(paket, starter):
                yield befund(R_MCP_VERSION, ".mcp.json", f"{name}: {paket} ohne feste Version. Jeder Start lädt die neueste, auch eine kompromittierte. Version pinnen, z.B. {paket.split('@latest')[0]}@1.2.3.")


# --- Subagents und Skills -----------------------------------------------------

R_AGENT = regel("CC040", "cc040-agent-frontmatter", FEHLER, "Subagent ohne name oder description")
R_AGENT_RECHTE = regel("CC041", "cc041-agent-bypass", FEHLER, "Subagent mit bypassPermissions")
R_SKILL = regel("CC042", "cc042-skill-frontmatter", WARNUNG, "Skill ohne description")
R_SKILL_LANG = regel("CC043", "cc043-skill-zu-lang", HINWEIS, "SKILL.md über 500 Zeilen")
R_AGENT_TOOLS = regel("CC044", "cc044-agent-ohne-tools", HINWEIS, "Subagent ohne tools-Liste")


@pruefung
def agents_und_skills(p: Projekt) -> Iterator[Befund]:
    for pfad in p.suche(".claude/agents/**/*.md"):
        rel = p.rel(pfad)
        fm = frontmatter(p.text(rel))
        if fm is None or not fm.get("name") or not fm.get("description"):
            yield befund(R_AGENT, rel, "name und description sind Pflicht. Ohne sie lädt Claude Code den Subagent nicht.")
            continue
        if fm.get("permissionMode") == "bypassPermissions":
            yield befund(R_AGENT_RECHTE, rel, "permissionMode bypassPermissions: Der Subagent läuft ohne jede Rückfrage.")
        if "tools" not in fm:
            yield befund(R_AGENT_TOOLS, rel, "Ohne tools erbt der Subagent alle Werkzeuge. Für Review-Agents reicht \"tools: Read, Grep, Glob\".")
    for pfad in p.suche(".claude/skills/*/SKILL.md"):
        rel = p.rel(pfad)
        text = p.text(rel)
        fm = frontmatter(text) or {}
        if not fm.get("description"):
            yield befund(R_SKILL, rel, "Ohne description wählt Claude den Skill nur zufällig über die erste Zeile. Was und wann in einem Satz.")
        if text.count("\n") > 500:
            yield befund(R_SKILL_LANG, rel, "Anthropic empfiehlt unter 500 Zeilen. Details in Zusatzdateien im Skill-Ordner auslagern.")


# --- Git ----------------------------------------------------------------------

R_ENV_GIT = regel("CC050", "cc050-env-im-repo", FEHLER, ".env im Repo oder nicht ignoriert")
R_PROTOKOLL = regel("CC051", "cc051-protokoll-nicht-ignoriert", WARNUNG, "Hook-Protokoll nicht ignoriert")


@pruefung
def git(p: Projekt) -> Iterator[Befund]:
    for relativ in sorted(p.getrackt):
        name = Path(relativ).name
        if (name == ".env" or name.startswith(".env.")) and name not in (".env.example", ".env.sample", ".env.template", ".env.dist"):
            yield befund(R_ENV_GIT, relativ, "Liegt in Git. Inhalt als kompromittiert betrachten, Schlüssel rotieren, Datei mit git rm --cached entfernen.")
    if p.datei(".env").is_file() and ".env" not in p.getrackt and not p.ist_ignoriert(".env"):
        yield befund(R_ENV_GIT, ".env", "Nicht in .gitignore. Der nächste git add -A nimmt sie mit.")
    if p.datei(".claude/protokoll").is_dir() and not p.ist_ignoriert(".claude/protokoll/x.jsonl"):
        yield befund(R_PROTOKOLL, ".claude/protokoll", "Protokoll der Tool-Nutzung gehört nicht ins Repo. .claude/protokoll/ in .gitignore eintragen.")


def pruefe(wurzel: Path) -> list[Befund]:
    p = Projekt(wurzel.resolve())
    befunde = [b for f in PRUEFUNGEN for b in f(p)]
    rang = {FEHLER: 0, WARNUNG: 1, HINWEIS: 2}
    return sorted(befunde, key=lambda b: (rang[b.schwere], b.regel, b.datei, b.zeile))
