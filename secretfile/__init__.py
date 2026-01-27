from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping

from .exceptions import (
    MissingInterpolation,
    SecretFieldNotFound,
    SecretNotFound,
    SecretfileError,
    SecretfileParseError,
    VaultError,
)
from .parser import SecretEntry, parse_secretfile
from .vault import ensure_client, read_secret, resolve_mount

__all__ = [
    "MissingInterpolation",
    "SecretBundle",
    "SecretFieldNotFound",
    "SecretNotFound",
    "SecretfileError",
    "SecretfileParseError",
    "VaultError",
    "load_secretfile",
]


@dataclass(frozen=True)
class SecretBundle:
    _secrets: Mapping[str, str]

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._secrets.get(key, default)

    def as_dict(self) -> dict[str, str]:
        return dict(self._secrets)


def load_secretfile(
    path: str | Path = "Secretfile",
    vault_client=None,
    env: Mapping[str, str] | None = None,
    *,
    kv_version: int | None = None,
    mount: str | None = None,
) -> SecretBundle:
    env = env or os.environ
    entries = parse_secretfile(path, env)
    mount_point = resolve_mount(mount, env)
    client = ensure_client(vault_client)
    secrets: dict[str, str] = {}
    for entry in entries:
        secrets[entry.env_key] = read_secret(
            entry.path,
            entry.field,
            client=client,
            kv_version=kv_version,
            mount=mount_point,
        )
    return SecretBundle(secrets)
