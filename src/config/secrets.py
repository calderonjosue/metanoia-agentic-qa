"""Secrets management for API keys and sensitive configuration."""

import os
from typing import Optional


class SecretsManager:
    """Manages API keys and secrets from environment variables or vault."""

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variable or vault.

        Args:
            key: The secret key name
            default: Default value if key not found

        Returns:
            The secret value or default
        """
        return os.environ.get(key, default)

    def require(self, key: str) -> str:
        """Get secret or raise ValueError if not found.

        Args:
            key: The secret key name

        Returns:
            The secret value

        Raises:
            ValueError: If the secret is not found
        """
        value = os.environ.get(key)
        if value is None:
            raise ValueError(f"Required secret '{key}' not found in environment")
        return value
