import pytest

from secretfile.exceptions import MissingInterpolation, SecretfileParseError
from secretfile.parser import _parse_lines


def test_parse_ignores_comments_and_blank_lines():
    lines = [
        "",
        "   ",
        "# comment",
        "  # indented comment",
        "API_KEY secrets/service:key",
    ]
    entries = _parse_lines(lines, env={}, source="Secretfile")
    assert len(entries) == 1
    assert entries[0].env_key == "API_KEY"
    assert entries[0].path == "secrets/service"
    assert entries[0].field == "key"


def test_parse_requires_env_key_and_reference():
    with pytest.raises(SecretfileParseError):
        _parse_lines(["ONLY_KEY"], env={}, source="Secretfile")


def test_parse_validates_env_key():
    with pytest.raises(SecretfileParseError):
        _parse_lines(["bad-key secrets/app:key"], env={}, source="Secretfile")


def test_parse_allows_mixed_case_env_key():
    entries = _parse_lines(
        ["TF_TOKEN_app_terraform_io secrets/app:token"],
        env={},
        source="Secretfile",
    )
    assert entries[0].env_key == "TF_TOKEN_app_terraform_io"


def test_parse_rejects_leading_digit_env_key():
    with pytest.raises(SecretfileParseError):
        _parse_lines(["1BAD secrets/app:key"], env={}, source="Secretfile")


def test_parse_splits_on_last_colon():
    entries = _parse_lines(
        ["TOKEN secret/path:with:colons:value"],
        env={},
        source="Secretfile",
    )
    assert entries[0].path == "secret/path:with:colons"
    assert entries[0].field == "value"


def test_interpolation_requires_env_value():
    with pytest.raises(MissingInterpolation):
        _parse_lines(
            ["TOKEN secret/$MISSING:key"],
            env={},
            source="Secretfile",
        )


def test_interpolation_replaces_vars():
    entries = _parse_lines(
        ["TOKEN secret/${ENV}/path:key"],
        env={"ENV": "prod"},
        source="Secretfile",
    )
    assert entries[0].path == "secret/prod/path"
