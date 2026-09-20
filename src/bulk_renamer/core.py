from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class RenameOp:
    source: str
    target: str
    sha256: str


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _natural_key(path: Path):
    return [int(x) if x.isdigit() else x.casefold() for x in re.split(r"(\d+)", path.name)]


def collect(directory: Path, recursive: bool = False, include_hidden: bool = False) -> list[Path]:
    directory = directory.expanduser().resolve()
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    iterator: Iterable[Path] = directory.rglob("*") if recursive else directory.iterdir()
    files = []
    for path in iterator:
        if not path.is_file() or path.is_symlink():
            continue
        try:
            rel = path.relative_to(directory)
        except ValueError:
            continue
        if not include_hidden and any(part.startswith(".") for part in rel.parts):
            continue
        files.append(path)
    return sorted(files, key=_natural_key)


def plan(directory: Path, *, prefix: str = "file", start: int = 1, width: int = 3,
         suffix: str = "", recursive: bool = False, include_hidden: bool = False,
         extension: str | None = None) -> list[RenameOp]:
    if start < 0 or width < 1:
        raise ValueError("start must be >= 0 and width >= 1")
    files = collect(directory, recursive, include_hidden)
    ops: list[RenameOp] = []
    targets: set[Path] = set()
    sources = {p.resolve() for p in files}
    for index, source in enumerate(files, start):
        ext = source.suffix if extension is None else ("." + extension.lstrip(".") if extension else "")
        target = source.with_name(f"{prefix}{index:0{width}d}{suffix}{ext}")
        resolved = target.resolve()
        if resolved in targets:
            raise ValueError(f"Duplicate target: {target}")
        if target.exists() and resolved not in sources and resolved != source.resolve():
            raise FileExistsError(f"Target already exists: {target}")
        targets.add(resolved)
        if source.resolve() != resolved:
            ops.append(RenameOp(str(source), str(target), sha256(source)))
    return ops


def apply(ops: list[RenameOp], manifest: Path) -> Path:
    if not ops:
        raise ValueError("Nothing to rename")
    # Revalidate content and targets immediately before mutating anything.
    source_paths = {Path(op.source).resolve() for op in ops}
    for op in ops:
        src, dst = Path(op.source), Path(op.target)
        if not src.is_file() or sha256(src) != op.sha256:
            raise RuntimeError(f"Source changed since preview: {src}")
        if dst.exists() and dst.resolve() not in source_paths:
            raise FileExistsError(f"Target became occupied: {dst}")

    # Two-phase rename prevents swaps/cycles and minimizes partial-state risk.
    staged: list[tuple[RenameOp, Path]] = []
    completed: list[RenameOp] = []
    try:
        for i, op in enumerate(ops):
            src = Path(op.source)
            temp = src.with_name(f".{src.name}.bulk-renamer-{os.getpid()}-{i}.tmp")
            if temp.exists():
                raise FileExistsError(f"Temporary path exists: {temp}")
            src.rename(temp)
            staged.append((op, temp))
        for op, temp in staged:
            Path(op.target).parent.mkdir(parents=True, exist_ok=True)
            temp.rename(Path(op.target))
            completed.append(op)
    except Exception:
        # Best-effort transactional rollback, in reverse order.
        for op in reversed(completed):
            dst, src = Path(op.target), Path(op.source)
            if dst.exists() and not src.exists():
                dst.rename(src)
        for op, temp in reversed(staged):
            src = Path(op.source)
            if temp.exists() and not src.exists():
                temp.rename(src)
        raise

    manifest = manifest.expanduser().resolve()
    manifest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "operations": [asdict(op) for op in ops],
    }
    manifest.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def undo(manifest: Path) -> int:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    ops = [RenameOp(**item) for item in data.get("operations", [])]
    if not ops:
        raise ValueError("Manifest contains no operations")
    # Validate all operations before changing any file.
    for op in ops:
        current, original = Path(op.target), Path(op.source)
        if not current.is_file() or sha256(current) != op.sha256:
            raise RuntimeError(f"Renamed file changed or is missing: {current}")
        if original.exists() and original.resolve() != current.resolve():
            raise FileExistsError(f"Original path is occupied: {original}")
    for op in reversed(ops):
        Path(op.target).rename(Path(op.source))
    return len(ops)
