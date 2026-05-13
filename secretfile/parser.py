from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Iterable, Mapping

from .exceptions import MissingInterpolation, SecretfileParseError

_ENV_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_INTERPOLATION_RE = re.compile(r"\$(\w+)|\$\{([^}]+)\}")


@dataclass(frozen=True)
class SecretEntry:
    env_key: str
    path: str
    field: str
    line_no: int


def parse_secretfile(
    path: str | Path,
    env: Mapping[str, str],
) -> list[SecretEntry]:
    file_path = Path(path)
    content = file_path.read_text(encoding="utf-8")
    return _parse_lines(content.splitlines(), env, source=str(file_path))


def _parse_lines(
    lines: Iterable[str],
    env: Mapping[str, str],
    source: str,
) -> list[SecretEntry]:
    entries: list[SecretEntry] = []
    for line_no, line in enumerate(lines, start=1):
        if _is_comment_or_blank(line):
            continue
        env_key, reference = _split_line(line, source, line_no)
        path, field = _split_reference(reference, source, line_no)
        path = _interpolate(path, env, source, line_no)
        field = _interpolate(field, env, source, line_no)
        entries.append(
            SecretEntry(
                env_key=env_key,
                path=path,
                field=field,
                line_no=line_no,
            )
        )
    return entries


def _is_comment_or_blank(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    return line.lstrip().startswith("#")


def _split_line(line: str, source: str, line_no: int) -> tuple[str, str]:
    stripped = line.strip()
    parts = stripped.split(maxsplit=1)
    if len(parts) != 2:
        raise SecretfileParseError(
            f"{source}:{line_no}: expected 'ENV_KEY path:field'"
        )
    env_key, reference = parts
    if not _ENV_KEY_RE.match(env_key):
        raise SecretfileParseError(
            f"{source}:{line_no}: invalid env var name '{env_key}'"
        )
    return env_key, reference


def _split_reference(reference: str, source: str, line_no: int) -> tuple[str, str]:
    if ":" not in reference:
        raise SecretfileParseError(
            f"{source}:{line_no}: expected 'path:field'"
        )
    path, field = reference.rsplit(":", 1)
    if not path or not field:
        raise SecretfileParseError(
            f"{source}:{line_no}: expected 'path:field'"
        )
    return path, field


def _interpolate(
    value: str,
    env: Mapping[str, str],
    source: str,
    line_no: int,
) -> str:
    def replacer(match: re.Match[str]) -> str:
        name = match.group(1) or match.group(2)
        if name is None:
            return match.group(0)
        if name not in env:
            raise MissingInterpolation(
                f"{source}:{line_no}: missing interpolation '{name}'"
            )
        return env[name]

    return _INTERPOLATION_RE.sub(replacer, value)
