"""Base IaC Provider protocol.

This module defines the abstract base class for Infrastructure as Code providers,
allowing the framework to support multiple IaC tools (Terraform, Pulumi, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any


class IaCProvider(ABC):
    """Abstract base class for Infrastructure as Code providers.

    This protocol defines the interface that all IaC providers must implement,
    enabling the framework to support multiple backends while maintaining
    a consistent API for lifecycle management operations.

    Methods:
        validate: Validate IaC configuration before planning/applying.
        plan: Generate execution plan without applying changes.
        apply: Execute the IaC configuration to provision resources.
        destroy: Tear down resources managed by the IaC configuration.
    """

    @abstractmethod
    def validate(self, config: dict[str, Any]) -> bool:
        """Validate the IaC configuration.

        Args:
            config: Configuration dictionary containing provider-specific
                   and IaC-specific settings.

        Returns:
            True if configuration is valid, False otherwise.
        """
        pass

    @abstractmethod
    def plan(self, config: dict[str, Any]) -> str:
        """Generate an execution plan without applying changes.

        Args:
            config: Configuration dictionary for the IaC provider.

        Returns:
            Human-readable plan string describing what would be changed.
        """
        pass

    @abstractmethod
    def apply(self, config: dict[str, Any]) -> dict[str, Any]:
        """Apply the IaC configuration to provision resources.

        Args:
            config: Configuration dictionary for the IaC provider.

        Returns:
            Dictionary containing the results of the apply operation,
            including any outputs or error information.
        """
        pass

    @abstractmethod
    def destroy(self, config: dict[str, Any]) -> bool:
        """Destroy resources managed by the IaC configuration.

        Args:
            config: Configuration dictionary for the IaC provider.

        Returns:
            True if destroy completed successfully, False otherwise.
        """
        pass
