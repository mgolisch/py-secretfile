from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from . import load_secretfile


def _find_git_root(start_dir: Path) -> Path | None:
    current = start_dir
    while True:
        marker = current / ".git"
        if marker.exists():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def _find_file_upward(
    *,
    filename: str,
    start_dir: Path,
    stop_dir: Path | None,
    max_depth: int,
) -> Path | None:
    current = start_dir
    depth = 0
    while True:
        candidate = current / filename
        if candidate.is_file():
            return candidate
        if stop_dir is not None and current == stop_dir:
            return None
        parent = current.parent
        if parent == current:
            return None
        depth += 1
        if depth > max_depth:
            return None
        current = parent


def _resolve_secretfile_path(file_arg: str) -> str:
    path = Path(file_arg)
    if path.is_absolute() or path.parent != Path("."):
        return file_arg

    start_dir = Path.cwd()
    git_root = _find_git_root(start_dir)
    resolved = _find_file_upward(
        filename=file_arg,
        start_dir=start_dir,
        stop_dir=git_root,
        max_depth=25,
    )
    if resolved is None:
        return file_arg
    return str(resolved)


def main() -> int:
    parser = argparse.ArgumentParser(prog="secretfile")
    parser.add_argument(
        "-f",
        "--file",
        default="Secretfile",
        help="Path to Secretfile",
    )
    parser.add_argument(
        "--kv-version",
        type=int,
        choices=[1, 2],
        help="Vault KV version",
    )
    parser.add_argument(
        "--mount",
        help="Vault mount (default: VAULT_MOUNT or 'secret')",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("env", help="Print resolved secrets as KEY=value")

    run_parser = subparsers.add_parser(
        "run",
        help="Run a command with secrets in the environment",
    )
    run_parser.add_argument(
        "cmd",
        nargs=argparse.REMAINDER,
        help="Command to run (prefix with -- to avoid flag parsing)",
    )

    args = parser.parse_args()

    secretfile_path = _resolve_secretfile_path(args.file)
    if (
        Path(args.file).parent == Path(".")
        and not Path(args.file).is_absolute()
        and Path(secretfile_path) == Path(args.file)
        and not Path(secretfile_path).is_file()
    ):
        parser.error(
            f"{args.file} not found in current or parent directories"
        )

    bundle = load_secretfile(
        path=secretfile_path,
        kv_version=args.kv_version,
        mount=args.mount,
    )

    if args.command == "env":
        for key, value in sorted(bundle.as_dict().items()):
            print(f"{key}={value}")
        return 0

    if args.command == "run":
        cmd = list(args.cmd or [])
        if cmd and cmd[0] == "--":
            cmd = cmd[1:]
        if not cmd:
            parser.error("run requires a command to execute")
        env = os.environ.copy()
        env.update(bundle.as_dict())
        result = subprocess.run(cmd, env=env)
        return int(result.returncode)

    return 1


if __name__ == "__main__":
    sys.exit(main())
