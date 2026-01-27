from __future__ import annotations

from typing import Mapping, Protocol

import hvac
from hvac import exceptions as hvac_exceptions

from .exceptions import SecretFieldNotFound, SecretNotFound, VaultError


class _KvV2Reader(Protocol):
    def read_secret_version(self, path: str, mount_point: str) -> dict | None: ...


class _KvV1Reader(Protocol):
    def read_secret(self, path: str, mount_point: str) -> dict | None: ...


class _KvReader(Protocol):
    v2: _KvV2Reader
    v1: _KvV1Reader


class _Secrets(Protocol):
    kv: _KvReader


class VaultClient(Protocol):
    secrets: _Secrets


def read_secret(
    path: str,
    field: str,
    *,
    client: VaultClient,
    kv_version: int | None,
    mount: str,
) -> str:
    if kv_version == 2:
        return _read_kv2(client, path, field, mount)
    if kv_version == 1:
        return _read_kv1(client, path, field, mount)
    return _read_kv_auto(client, path, field, mount)


def resolve_mount(mount: str | None, env: Mapping[str, str]) -> str:
    return mount or env.get("VAULT_MOUNT") or "secret"


def ensure_client(vault_client: hvac.Client | None) -> hvac.Client:
    return vault_client or hvac.Client()


def _read_kv_auto(
    client: VaultClient,
    path: str,
    field: str,
    mount: str,
) -> str:
    try:
        return _read_kv2(client, path, field, mount)
    except hvac_exceptions.InvalidPath:
        try:
            return _read_kv1(client, path, field, mount)
        except hvac_exceptions.InvalidPath as err:
            raise SecretNotFound(
                f"secret not found at '{path}'"
            ) from err
    except hvac_exceptions.Forbidden as err:
        raise VaultError(
            f"access denied for secret at '{path}'"
        ) from err
    except Exception as err:  # pragma: no cover - defensive
        raise VaultError(
            f"vault error while reading '{path}'"
        ) from err


def _read_kv2(
    client: VaultClient,
    path: str,
    field: str,
    mount: str,
) -> str:
    try:
        response = client.secrets.kv.v2.read_secret_version(
            path=path,
            mount_point=mount,
        )
    except hvac_exceptions.InvalidPath as err:
        raise err
    except hvac_exceptions.Forbidden as err:
        raise err
    except Exception as err:  # pragma: no cover - defensive
        raise VaultError(
            f"vault error while reading '{path}'"
        ) from err
    data = _extract_kv2_data(response)
    return _extract_field(data, path, field)


def _read_kv1(
    client: VaultClient,
    path: str,
    field: str,
    mount: str,
) -> str:
    try:
        response = client.secrets.kv.v1.read_secret(
            path=path,
            mount_point=mount,
        )
    except hvac_exceptions.InvalidPath as err:
        raise err
    except hvac_exceptions.Forbidden as err:
        raise err
    except Exception as err:  # pragma: no cover - defensive
        raise VaultError(
            f"vault error while reading '{path}'"
        ) from err
    data = _extract_kv1_data(response)
    return _extract_field(data, path, field)


def _extract_kv2_data(response: dict | None) -> dict:
    if not response:
        return {}
    data = response.get("data") or {}
    return data.get("data") or {}


def _extract_kv1_data(response: dict | None) -> dict:
    if not response:
        return {}
    return response.get("data") or {}


def _extract_field(data: dict, path: str, field: str) -> str:
    if not data:
        raise SecretNotFound(f"secret not found at '{path}'")
    if field not in data:
        raise SecretFieldNotFound(
            f"field '{field}' not found at '{path}'"
        )
    value = data[field]
    return str(value)
