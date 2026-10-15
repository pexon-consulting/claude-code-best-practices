"""claude-team: prüft, richtet ein und scannt Projekte, die mit Claude Code arbeiten.

Exit-Codes: 0 ohne Befund über der Schwelle, 1 mit Befund, 2 bei falscher Bedienung.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .bericht import FORMATE
from .einrichten import BAUSTEINE, PROFILE, Einrichtung
from .regeln import FEHLER, HINWEIS, REGELN, WARNUNG, pruefe
from .scannen import scanne, scanne_text

SCHWELLEN = {"fehler": {FEHLER}, "warnung": {FEHLER, WARNUNG}, "hinweis": {FEHLER, WARNUNG, HINWEIS}}
TEXT = {"angelegt": "angelegt  ", "vorschlag": "vorschlag ", "ergaenzt": "ergänzt   ", "unveraendert": "unverändert", "uebersprungen": "bleibt    "}


def _ordner(pfad: str) -> Path:
    ziel = Path(pfad)
    if not ziel.is_dir():
        print(f"Ordner nicht gefunden: {pfad}", file=sys.stderr)
        sys.exit(2)
    return ziel


def befehl_audit(args: argparse.Namespace) -> int:
    ziel = _ordner(args.pfad)
    befunde = pruefe(ziel)
    if args.ignorieren:
        weg = {r.strip().upper() for r in args.ignorieren.split(",")}
        befunde = [b for b in befunde if b.regel not in weg]
    ausgabe = FORMATE[args.format](befunde, args.pfad)
    if args.out:
        Path(args.out).write_text(ausgabe, encoding="utf-8")
        print(f"Bericht: {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(ausgabe)
    return 1 if any(b.schwere in SCHWELLEN[args.schwelle] for b in befunde) else 0


def befehl_einrichten(args: argparse.Namespace) -> int:
    ziel = _ordner(args.pfad)
    ohne = {b.strip() for b in (args.ohne or "").split(",") if b.strip()}
    unbekannt = ohne - set(BAUSTEINE)
    if unbekannt:
        print(f"Unbekannte Bausteine: {', '.join(sorted(unbekannt))}. Möglich: {', '.join(BAUSTEINE)}", file=sys.stderr)
        return 2
    aktionen = Einrichtung(ziel, ohne, args.profil, args.dry_run).ausfuehren()
    if args.dry_run:
        print("Probelauf, nichts geschrieben:")
    for a in aktionen:
        print(f"  {TEXT[a.art]} {a.datei}" + (f"  ({a.grund})" if a.grund else ""))
    if any(a.art == "vorschlag" for a in aktionen):
        print("\nVorschläge mit dem Original vergleichen, z.B. diff .claude/settings.json .claude/settings.vorschlag.json")
    if not args.dry_run:
        print("\nNächster Schritt: claude-team audit", args.pfad)
    return 0


def befehl_scannen(args: argparse.Namespace) -> int:
    if args.pfade == ["-"]:
        treffer = scanne_text(sys.stdin.read(), "<stdin>", args.kontakte_ab)
    else:
        treffer = scanne([Path(p) for p in args.pfade], nur_git=not args.alle, kontakte_ab=args.kontakte_ab)
    if args.json:
        print(json.dumps([t.__dict__ for t in treffer], ensure_ascii=False, indent=2))
    else:
        for t in treffer:
            ort = f"{t.datei}:{t.zeile}" if t.zeile else t.datei
            print(f"{t.klasse:6} {t.art:28} {ort}  {t.vorschau}")
        print(f"{len(treffer)} Treffer.", file=sys.stderr)
    return 1 if treffer else 0


def befehl_regeln(args: argparse.Namespace) -> int:
    if args.json:
        print(json.dumps([{**r.__dict__, "link": r.link} for r in REGELN.values()], ensure_ascii=False, indent=2))
    else:
        for r in REGELN.values():
            print(f"{r.id}  {r.schwere:8} {r.titel}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="claude-team", description="Claude Code Best Practices für Teams: audit, einrichten, scannen.")
    p.add_argument("--version", action="version", version=f"claude-team {__version__}")
    unter = p.add_subparsers(dest="befehl", required=True)

    pr = unter.add_parser("audit", help="Repo gegen die Team-Basis prüfen (CLAUDE.md, Settings, Hooks, MCP, Git)")
    pr.add_argument("pfad", nargs="?", default=".")
    pr.add_argument("--format", choices=sorted(FORMATE), default="text")
    pr.add_argument("--out", help="Bericht in Datei schreiben statt auf stdout")
    pr.add_argument("--schwelle", choices=sorted(SCHWELLEN), default="fehler", help="ab welcher Stufe der Exit-Code 1 ist")
    pr.add_argument("--ignorieren", help="Regel-IDs, kommagetrennt, z.B. CC019,CC020")
    pr.set_defaults(funktion=befehl_audit)

    ei = unter.add_parser("einrichten", help="CLAUDE.md, Settings, Hooks und Vorlagen anlegen, ohne zu überschreiben")
    ei.add_argument("pfad", nargs="?", default=".")
    ei.add_argument("--dry-run", action="store_true", help="nur anzeigen, was passieren würde")
    ei.add_argument("--ohne", help=f"Bausteine auslassen, kommagetrennt: {', '.join(BAUSTEINE)}")
    ei.add_argument("--profil", choices=PROFILE, default="standard", help="streng sperrt zusätzlich Web und Netzwerkbefehle")
    ei.set_defaults(funktion=befehl_einrichten)

    sc = unter.add_parser("scannen", help="Dateien nach Secrets und personenbezogenen Daten durchsuchen")
    sc.add_argument("pfade", nargs="*", default=["."], help="Dateien oder Ordner, - für stdin")
    sc.add_argument("--alle", action="store_true", help="auch Dateien, die Git nicht kennt")
    sc.add_argument("--kontakte-ab", type=int, default=5, help="ab so vielen E-Mails oder Telefonnummern melden")
    sc.add_argument("--json", action="store_true")
    sc.set_defaults(funktion=befehl_scannen)

    rg = unter.add_parser("regeln", help="alle Prüfregeln auflisten")
    rg.add_argument("--json", action="store_true")
    rg.set_defaults(funktion=befehl_regeln)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.funktion(args)


if __name__ == "__main__":
    sys.exit(main())
