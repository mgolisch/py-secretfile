# py-secretfile
Python library for the Secretfile specification.

## Usage

Create a `Secretfile`:

```
# Secretfile
AWS_ACCESS_KEY_ID     secrets/services/aws:id
AWS_ACCESS_KEY_SECRET secrets/services/aws:secret
PG_USERNAME           postgresql/$VAULT_ENV/creds/readonly:username
PG_PASSWORD           postgresql/$VAULT_ENV/creds/readonly:password
```

Load secrets from Vault:

```python
from secretfile import load_secretfile

bundle = load_secretfile()
db_user = bundle.get("PG_USERNAME")
```

CLI usage:

```shell
$ secretfile env
$ secretfile run -- myprogram arg1 arg2
```

CLI options:

- `--kv-version 1|2` to force Vault KV version (default: auto-detect)
- `--mount <name>` to override Vault mount (default: `VAULT_MOUNT` or `secret`)

Vault configuration uses the standard environment variables:

- `VAULT_ADDR`
- `VAULT_TOKEN`
- `VAULT_MOUNT` (optional, defaults to `secret`)
