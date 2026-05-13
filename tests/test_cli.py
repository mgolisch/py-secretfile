import os
from pathlib import Path

import secretfile.cli as cli


class _Bundle:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return dict(self._data)


class _Result:
    def __init__(self, returncode=0):
        self.returncode = returncode


def test_cli_env_prints_sorted_output(monkeypatch, capsys, tmp_path):
    (tmp_path / "Secretfile").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        cli,
        "load_secretfile",
        lambda **_: _Bundle({"B": "2", "A": "1"}),
    )
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["secretfile", "env"],
    )

    assert cli.main() == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out == ["A=1", "B=2"]


def test_cli_run_executes_command(monkeypatch, tmp_path):
    (tmp_path / "Secretfile").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        cli,
        "load_secretfile",
        lambda **_: _Bundle({"TOKEN": "abc"}),
    )

    captured = {}

    def _run(cmd, env):
        captured["cmd"] = cmd
        captured["env"] = env
        return _Result(returncode=7)

    monkeypatch.setattr(cli.subprocess, "run", _run)
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["secretfile", "run", "--", "echo", "hello"],
    )

    code = cli.main()
    assert code == 7
    assert captured["cmd"] == ["echo", "hello"]
    assert captured["env"]["TOKEN"] == "abc"
    assert captured["env"]["PATH"] == os.environ["PATH"]


def test_cli_finds_secretfile_in_parent_dirs(monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (repo / "Secretfile").write_text("", encoding="utf-8")

    captured = {}

    def _load_secretfile(*, path, **kwargs):
        captured["path"] = path
        return _Bundle({})

    monkeypatch.setattr(cli, "load_secretfile", _load_secretfile)
    monkeypatch.chdir(nested)
    monkeypatch.setattr(cli.sys, "argv", ["secretfile", "env"])

    assert cli.main() == 0
    assert Path(captured["path"]) == repo / "Secretfile"


def test_cli_prefers_nearest_secretfile(monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    service = repo / "service"
    nested = service / "a"
    nested.mkdir(parents=True)
    (repo / "Secretfile").write_text("", encoding="utf-8")
    (service / "Secretfile").write_text("", encoding="utf-8")

    captured = {}

    def _load_secretfile(*, path, **kwargs):
        captured["path"] = path
        return _Bundle({})

    monkeypatch.setattr(cli, "load_secretfile", _load_secretfile)
    monkeypatch.chdir(nested)
    monkeypatch.setattr(cli.sys, "argv", ["secretfile", "env"])

    assert cli.main() == 0
    assert Path(captured["path"]) == service / "Secretfile"


def test_cli_does_not_search_when_file_has_dir_component(monkeypatch, tmp_path):
    repo = tmp_path / "repo"
    nested = repo / "a" / "b"
    nested.mkdir(parents=True)
    (repo / "Secretfile").write_text("", encoding="utf-8")

    captured = {}

    def _load_secretfile(*, path, **kwargs):
        captured["path"] = path
        return _Bundle({})

    monkeypatch.setattr(cli, "load_secretfile", _load_secretfile)
    monkeypatch.chdir(nested)
    monkeypatch.setattr(
        cli.sys,
        "argv",
        ["secretfile", "--file", "../Secretfile", "env"],
    )

    assert cli.main() == 0
    assert captured["path"] == "../Secretfile"


def test_cli_search_stops_at_git_root(monkeypatch, tmp_path, capsys):
    root = tmp_path / "root"
    git_root = root / "repo"
    nested = git_root / "a" / "b"
    nested.mkdir(parents=True)
    (git_root / ".git").mkdir()
    (root / "Secretfile").write_text("", encoding="utf-8")

    def _load_secretfile(**_):
        raise AssertionError("load_secretfile should not be called")

    monkeypatch.setattr(cli, "load_secretfile", _load_secretfile)
    monkeypatch.chdir(nested)
    monkeypatch.setattr(cli.sys, "argv", ["secretfile", "env"])

    try:
        cli.main()
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert exc.code == 2

    err = capsys.readouterr().err
    assert "Secretfile not found" in err
