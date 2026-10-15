"""Kopiert jede kanonische skills/<name>/SKILL.md in die Spiegel für Claude und Codex."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"
MIRRORS = (ROOT / ".claude" / "skills", ROOT / ".agents" / "skills")


def skills() -> list[Path]:
    return sorted(p for p in SOURCE.glob("*/SKILL.md"))


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    quellen = skills()
    namen = {p.parent.name for p in quellen}
    if "--check" in args:
        ok = True
        for mirror in MIRRORS:
            for p in quellen:
                dest = mirror / p.parent.name / "SKILL.md"
                if not dest.is_file() or dest.read_text(encoding="utf-8") != p.read_text(encoding="utf-8"):
                    print(f"weicht ab: {dest}", file=sys.stderr)
                    ok = False
            for extra in mirror.glob("*/SKILL.md"):
                if extra.parent.name not in namen:
                    print(f"verwaist: {extra}", file=sys.stderr)
                    ok = False
        return 0 if ok else 1
    for mirror in MIRRORS:
        for extra in mirror.glob("*/SKILL.md"):
            if extra.parent.name not in namen:
                extra.unlink()
                extra.parent.rmdir()
        for p in quellen:
            dest = mirror / p.parent.name / "SKILL.md"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
