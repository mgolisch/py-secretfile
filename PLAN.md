# py-secretfile plan

Vault-only Secretfile library (v0)

Spec + API
- Secretfile grammar: `ENV_VAR_NAME <whitespace> vault/path:field`
- Full-line comments only (`#` after optional leading whitespace)
- Blank lines ignored
- Split on the last `:` for `path`/`field`
- Interpolation in path/field: `$VAR` and `${VAR}`
- Missing interpolation -> `MissingInterpolation`
- Fail fast on first error

API sketch
- `load_secretfile(path="Secretfile", vault_client=None, env=os.environ, *, kv_version=None, mount=None) -> SecretBundle`
- `SecretBundle.get(key)` / `SecretBundle.as_dict()`
- Exceptions: `SecretfileParseError`, `MissingInterpolation`, `SecretNotFound`,
  `SecretFieldNotFound`, `VaultError`

Modules
- `secretfile/parser.py` parses, validates, interpolates
- `secretfile/vault.py` reads from Vault via `hvac`
- `secretfile/__init__.py` exports API + exceptions

Vault behavior
- `kv_version=None` -> try v2, fallback to v1
- `mount` default: `VAULT_MOUNT` env var or `"secret"`
- Extract field; raise `SecretFieldNotFound` if missing

Security
- Never log secret values
- Exceptions include only env key/path/field, not values

Tests (if pytest is added)
- Parser: valid/invalid lines, comments/blank lines, last-colon split
- Interpolation: missing env var
- Vault: mocked v1/v2 responses
- Fail-fast + redaction

README update (after API stabilizes)
- Usage example
- Vault setup: `VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_MOUNT`

CLI (later)
- `secretfile env` prints `KEY=value`
- `secretfile run -- cmd` executes with injected env
