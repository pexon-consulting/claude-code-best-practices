@AGENTS.md

## Nur für Claude Code

- Die Hooks dieses Repos laufen direkt aus `src/claude_team/vorlage/.claude/hooks/`. Wer dort etwas ändert, ändert den eigenen Schutz mit. Nach jeder Änderung `pytest -q tests/test_hooks.py`.
- Bevor du "fertig" meldest: `pytest -q` und `claude-team audit .` müssen grün sein.
- Skills nur unter `skills/<name>/SKILL.md` ändern, danach `python3 scripts/sync_skills.py`.
