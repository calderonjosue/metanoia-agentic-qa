"""Supabase client for Metanoia-QA Knowledge Base.

This module provides the Supabase client connection with proper
environment variable handling and connection management.
"""

import os
from typing import Optional
from urllib.parse import urlparse

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions


_supabase_client: Optional[Client] = None


def get_supabase_url() -> str:
    """Get Supabase URL from environment variables.

    Returns:
        Supabase project URL

    Raises:
        ValueError: If SUPABASE_URL is not set
    """
    url = os.getenv("SUPABASE_URL")
    if not url:
        raise ValueError(
            "SUPABASE_URL environment variable is not set. "
            "Please set it to your Supabase project URL."
        )
    return url


def get_supabase_key() -> str:
    """Get Supabase API key from environment variables.

    Returns:
        Supabase API key (anon or service role)

    Raises:
        ValueError: If SUPABASE_KEY is not set
    """
    key = os.getenv("SUPABASE_KEY")
    if not key:
        raise ValueError(
            "SUPABASE_KEY environment variable is not set. "
            "Please set it to your Supabase API key."
        )
    return key


def get_supabase_client() -> Client:
    """Get or create Supabase client instance.

    This function implements a singleton pattern to reuse
    the Supabase client across the application.

    Returns:
        Configured Supabase client instance

    Note:
        Sets up client with custom options for production use.
    """
    global _supabase_client

    if _supabase_client is None:
        url = get_supabase_url()
        key = get_supabase_key()

        options = ClientOptions(
            auto_refresh_token=True,
            persist_session=True,
        )

        _supabase_client = create_client(url, key, options=options)

    return _supabase_client


def reset_supabase_client() -> None:
    """Reset the Supabase client singleton.

    Useful for testing or when you need to reconnect with
    different credentials.
    """
    global _supabase_client
    _supabase_client = None


class SupabaseClient:
    """Wrapper class for Supabase client with additional utilities.

    This class provides a more Pythonic interface to the Supabase
    client with type hints and convenience methods.

    Attributes:
        client: The underlying Supabase client
        url: Supabase project URL
    """

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        options: Optional[ClientOptions] = None,
    ):
        """Initialize Supabase client with credentials.

        Args:
            url: Supabase URL (defaults to SUPABASE_URL env var)
            key: Supabase API key (defaults to SUPABASE_KEY env var)
            options: Custom client options
        """
        self.url = url or get_supabase_url()
        self.key = key or get_supabase_key()
        self._options = options or ClientOptions()
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Get the Supabase client, creating if necessary.

        Returns:
            Supabase client instance
        """
        if self._client is None:
            self._client = create_client(self.url, self.key, options=self._options)
        return self._client

    @property
    def table(self):
        """Access a table via attribute access.

        Returns:
            Table reference for chaining

        Example:
            supabase.table.users.select("*").execute()
        """
        return self.client.table

    @property
    def auth(self):
        """Access auth functionality.

        Returns:
            Auth client
        """
        return self.client.auth

    def health_check(self) -> bool:
        """Check if Supabase connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            self.client.table("pg_stat_activity").select("pid").limit(1).execute()
            return True
        except Exception:
            return False

    def get_project_info(self) -> dict:
        """Get Supabase project information.

        Returns:
            Dictionary with project details
        """
        parsed = urlparse(self.url)
        return {
            "host": parsed.netloc,
            "ref": parsed.path.strip("/") if parsed.path else None,
        }
