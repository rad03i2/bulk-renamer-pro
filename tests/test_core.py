from pathlib import Path

import pytest

from bulk_renamer.core import apply, collect, plan, sha256, undo


def write(path: Path, content: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def test_plan_preserves_extensions_and_natural_order(tmp_path):
    write(tmp_path / "photo10.jpg", b"10")
    write(tmp_path / "photo2.jpg", b"2")
    ops = plan(tmp_path, prefix="Trip-", start=7, width=2)
    assert [Path(x.source).name for x in ops] == ["photo2.jpg", "photo10.jpg"]
    assert [Path(x.target).name for x in ops] == ["Trip-07.jpg", "Trip-08.jpg"]


def test_preview_does_not_mutate(tmp_path):
    source = write(tmp_path / "a.txt", b"hello")
    plan(tmp_path, prefix="doc-")
    assert source.exists()


def test_apply_and_undo_round_trip(tmp_path):
    source = write(tmp_path / "old.txt", b"hello")
    digest = sha256(source)
    ops = plan(tmp_path, prefix="new-", width=2)
    manifest = tmp_path / "manifest.json"
    apply(ops, manifest)
    target = tmp_path / "new-01.txt"
    assert target.read_bytes() == b"hello"
    assert sha256(target) == digest
    assert not source.exists()
    assert undo(manifest) == 1
    assert source.read_bytes() == b"hello"


def test_apply_refuses_changed_source(tmp_path):
    source = write(tmp_path / "a.txt", b"before")
    ops = plan(tmp_path, prefix="x-")
    source.write_bytes(b"after")
    with pytest.raises(RuntimeError):
        apply(ops, tmp_path / "m.json")
    assert source.read_bytes() == b"after"


def test_unrelated_occupied_target_is_rejected(tmp_path):
    write(tmp_path / "a.txt")
    (tmp_path / "file001.txt").mkdir()
    with pytest.raises(FileExistsError):
        plan(tmp_path)


def test_existing_source_name_can_be_reused_safely(tmp_path):
    write(tmp_path / "a.txt", b"a")
    write(tmp_path / "file001.txt", b"b")
    ops = plan(tmp_path)
    apply(ops, tmp_path / "m.json")
    assert (tmp_path / "file001.txt").read_bytes() == b"a"
    assert (tmp_path / "file002.txt").read_bytes() == b"b"


def test_hidden_and_symlink_safety(tmp_path):
    write(tmp_path / ".secret", b"s")
    write(tmp_path / "visible.txt", b"v")
    assert [p.name for p in collect(tmp_path)] == ["visible.txt"]


def test_recursive_is_opt_in(tmp_path):
    write(tmp_path / "top.txt")
    write(tmp_path / "nested" / "deep.txt")
    assert [p.name for p in collect(tmp_path)] == ["top.txt"]
    assert {p.name for p in collect(tmp_path, recursive=True)} == {"top.txt", "deep.txt"}


def test_undo_refuses_modified_target(tmp_path):
    source = write(tmp_path / "a.txt", b"original")
    manifest = tmp_path / "m.json"
    apply(plan(tmp_path, prefix="renamed-"), manifest)
    target = tmp_path / "renamed-001.txt"
    target.write_bytes(b"modified")
    with pytest.raises(RuntimeError):
        undo(manifest)
    assert target.read_bytes() == b"modified"
    assert not source.exists()
