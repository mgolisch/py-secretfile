import pytest

hvac = pytest.importorskip("hvac")
from hvac import exceptions as hvac_exceptions

from secretfile.exceptions import SecretFieldNotFound, SecretNotFound
from secretfile.vault import read_secret


class _KvV2:
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error

    def read_secret_version(self, path, mount_point):
        if self._error:
            raise self._error
        return self._response


class _KvV1:
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error

    def read_secret(self, path, mount_point):
        if self._error:
            raise self._error
        return self._response


class _Secrets:
    def __init__(self, v2, v1):
        self.kv = type("_Kv", (), {"v2": v2, "v1": v1})


class _Client:
    def __init__(self, v2=None, v1=None):
        self.secrets = _Secrets(v2 or _KvV2(), v1 or _KvV1())


def test_read_secret_kv2_success():
    client = _Client(
        v2=_KvV2(response={"data": {"data": {"token": "abc"}}}),
    )
    value = read_secret(
        "secret/app",
        "token",
        client=client,
        kv_version=2,
        mount="secret",
    )
    assert value == "abc"


def test_read_secret_kv1_success():
    client = _Client(
        v1=_KvV1(response={"data": {"token": "abc"}}),
    )
    value = read_secret(
        "secret/app",
        "token",
        client=client,
        kv_version=1,
        mount="secret",
    )
    assert value == "abc"


def test_read_secret_auto_fallback_to_kv1():
    client = _Client(
        v2=_KvV2(error=hvac_exceptions.InvalidPath()),
        v1=_KvV1(response={"data": {"token": "abc"}}),
    )
    value = read_secret(
        "secret/app",
        "token",
        client=client,
        kv_version=None,
        mount="secret",
    )
    assert value == "abc"


def test_read_secret_missing_secret_raises():
    client = _Client(
        v2=_KvV2(error=hvac_exceptions.InvalidPath()),
        v1=_KvV1(error=hvac_exceptions.InvalidPath()),
    )
    with pytest.raises(SecretNotFound):
        read_secret(
            "secret/app",
            "token",
            client=client,
            kv_version=None,
            mount="secret",
        )


def test_read_secret_missing_field_raises():
    client = _Client(
        v2=_KvV2(response={"data": {"data": {"other": "abc"}}}),
    )
    with pytest.raises(SecretFieldNotFound):
        read_secret(
            "secret/app",
            "token",
            client=client,
            kv_version=2,
            mount="secret",
        )
