"""Kopiert jede kanonische skills/<name>/SKILL.md in die Spiegel für Claude und Codex
und die Subagents der Vorlage nach agents/, wo das Plugin team-basis sie findet."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"
MIRRORS = (ROOT / ".claude" / "skills", ROOT / ".agents" / "skills")
AGENTS_SOURCE = ROOT / "src" / "claude_team" / "vorlage" / ".claude" / "agents"
AGENTS_MIRROR = ROOT / "agents"


def skills() -> list[Path]:
    return sorted(p for p in SOURCE.glob("*/SKILL.md"))


def agents() -> list[Path]:
    return sorted(AGENTS_SOURCE.glob("*.md"))


def paare() -> list[tuple[Path, Path]]:
    """(Quelle, Ziel) für alle gespiegelten Dateien."""
    ergebnis = [(p, mirror / p.parent.name / "SKILL.md") for mirror in MIRRORS for p in skills()]
    return ergebnis + [(p, AGENTS_MIRROR / p.name) for p in agents()]


def verwaist() -> list[Path]:
    namen = {p.parent.name for p in skills()}
    extra = [e for mirror in MIRRORS for e in mirror.glob("*/SKILL.md") if e.parent.name not in namen]
    agent_namen = {p.name for p in agents()}
    return extra + [e for e in AGENTS_MIRROR.glob("*.md") if e.name not in agent_namen]


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--check" in args:
        ok = True
        for quelle, dest in paare():
            if not dest.is_file() or dest.read_text(encoding="utf-8") != quelle.read_text(encoding="utf-8"):
                print(f"weicht ab: {dest}", file=sys.stderr)
                ok = False
        for extra in verwaist():
            print(f"verwaist: {extra}", file=sys.stderr)
            ok = False
        return 0 if ok else 1
    for extra in verwaist():
        extra.unlink()
        if extra.parent != AGENTS_MIRROR:
            extra.parent.rmdir()
    for quelle, dest in paare():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(quelle.read_text(encoding="utf-8"), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
