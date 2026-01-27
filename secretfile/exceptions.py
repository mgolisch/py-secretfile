class SecretfileError(Exception):
    """Base error for Secretfile operations."""


class SecretfileParseError(SecretfileError):
    """Raised when a Secretfile line cannot be parsed."""


class MissingInterpolation(SecretfileError):
    """Raised when a required interpolation variable is missing."""


class SecretNotFound(SecretfileError):
    """Raised when a secret path cannot be found."""


class SecretFieldNotFound(SecretfileError):
    """Raised when a field is missing in a secret."""


class VaultError(SecretfileError):
    """Raised when Vault access fails unexpectedly."""
