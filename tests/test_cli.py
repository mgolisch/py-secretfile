import os

import secretfile.cli as cli


class _Bundle:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return dict(self._data)


class _Result:
    def __init__(self, returncode=0):
        self.returncode = returncode


def test_cli_env_prints_sorted_output(monkeypatch, capsys):
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


def test_cli_run_executes_command(monkeypatch):
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
