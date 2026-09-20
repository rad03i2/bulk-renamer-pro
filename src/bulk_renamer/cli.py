from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import apply, plan, undo


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="bulk-renamer", description="Preview-first safe bulk file renaming")
    p.add_argument("--version", action="version", version="Bulk Renamer Pro 1.0.0 — Radwan Abdulhadi Ahmed (@rad03i2)")
    sub = p.add_subparsers(dest="command", required=True)
    rename = sub.add_parser("rename", help="Preview or apply a rename plan")
    rename.add_argument("directory", type=Path)
    rename.add_argument("--prefix", default="file")
    rename.add_argument("--suffix", default="")
    rename.add_argument("--start", type=int, default=1)
    rename.add_argument("--width", type=int, default=3)
    rename.add_argument("--extension", help="Replace extension; empty string removes it")
    rename.add_argument("--recursive", action="store_true")
    rename.add_argument("--include-hidden", action="store_true")
    rename.add_argument("--apply", action="store_true", help="Actually rename files; default is preview")
    rename.add_argument("--manifest", type=Path, default=Path("bulk-renamer-manifest.json"))
    rename.add_argument("--json", action="store_true", help="Print plan as JSON")
    restore = sub.add_parser("undo", help="Restore files from a manifest")
    restore.add_argument("manifest", type=Path)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "undo":
            count = undo(args.manifest)
            print(f"Restored {count} file(s).")
            return 0
        ops = plan(args.directory, prefix=args.prefix, suffix=args.suffix, start=args.start,
                   width=args.width, recursive=args.recursive, include_hidden=args.include_hidden,
                   extension=args.extension)
        if args.json:
            print(json.dumps([op.__dict__ for op in ops], indent=2, ensure_ascii=False))
        else:
            if not ops:
                print("Nothing to rename.")
            for op in ops:
                print(f"{Path(op.source).name} -> {Path(op.target).name}")
        if args.apply and ops:
            manifest = apply(ops, args.manifest)
            print(f"Applied {len(ops)} rename(s). Manifest: {manifest}")
        elif ops and not args.apply:
            print("Preview only. Re-run with --apply to execute.")
        return 0
    except (ValueError, FileExistsError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
