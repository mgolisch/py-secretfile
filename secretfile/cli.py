from __future__ import annotations

import argparse
import os
import subprocess
import sys

from . import load_secretfile


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

    bundle = load_secretfile(
        path=args.file,
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
