"""Lab Lifecycle Manager for provisioning and managing test lab environments.

This module provides a unified interface for creating, destroying, and managing
temporary lab environments used for testing. It integrates with IaC providers
to provision infrastructure on-demand.
"""

import logging
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generator

from src.infrastructure.iac_providers.base import IaCProvider
from src.infrastructure.iac_providers.terraform import TerraformProvider

logger = logging.getLogger(__name__)


class LabStatus(str, Enum):
    """Lab environment status enumeration."""
    PENDING = "pending"
    PROVISIONING = "provisioning"
    READY = "ready"
    FAILED = "failed"
    TEARDOWN = "teardown"
    DESTROYED = "destroyed"


@dataclass
class LabEnvironment:
    """Represents a lab environment instance.

    Attributes:
        lab_id: Unique identifier for the lab.
        name: Human-readable name for the lab.
        status: Current lifecycle status.
        iac_config: IaC configuration used to provision.
        metadata: Additional lab metadata.
        created_at: When the lab was created.
        ready_at: When the lab became ready for use.
        destroyed_at: When the lab was destroyed.
    """
    lab_id: str
    name: str
    status: LabStatus = LabStatus.PENDING
    iac_config: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    ready_at: datetime | None = None
    destroyed_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        """Check if lab is currently active and usable."""
        return self.status == LabStatus.READY


class IaCProviderFactory:
    """Factory for creating IaC provider instances."""

    _providers: dict[str, type[IaCProvider]] = {
        "terraform": TerraformProvider,
    }

    @classmethod
    def register(cls, name: str, provider_class: type[IaCProvider]) -> None:
        """Register a new IaC provider.

        Args:
            name: Provider identifier (e.g., 'terraform', 'pulumi').
            provider_class: Provider class implementing IaCProvider.
        """
        cls._providers[name] = provider_class

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> IaCProvider:
        """Create an IaC provider instance.

        Args:
            name: Provider identifier.
            **kwargs: Provider-specific configuration.

        Returns:
            Configured IaC provider instance.

        Raises:
            ValueError: If provider name is not registered.
        """
        if name not in cls._providers:
            raise ValueError(f"Unknown IaC provider: {name}")
        return cls._providers[name](**kwargs)


class LabLifecycleManager:
    """Manages the lifecycle of test lab environments.

    This class provides methods to provision, tear down, and query
    lab environments used for testing. It supports multiple IaC
    providers and can manage multiple concurrent labs.

    Example:
        manager = LabLifecycleManager()

        lab = manager.provision(
            name="e2e-test-env",
            iac_provider="terraform",
            iac_config={"working_dir": "/path/to/tf"}
        )

        # Use the lab environment...

        manager.teardown(lab.lab_id)
    """

    def __init__(self, default_provider: str = "terraform"):
        """Initialize the lab lifecycle manager.

        Args:
            default_provider: Default IaC provider to use.
        """
        self._labs: dict[str, LabEnvironment] = {}
        self._default_provider = default_provider
        self._provider_factory = IaCProviderFactory()

    def provision(
        self,
        name: str,
        iac_provider: str | None = None,
        iac_config: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> LabEnvironment:
        """Provision a new lab environment.

        Args:
            name: Human-readable name for the lab.
            iac_provider: IaC provider to use (defaults to configured default).
            iac_config: Provider-specific configuration dictionary.
            metadata: Additional metadata to attach to the lab.

        Returns:
            LabEnvironment instance representing the provisioned lab.

        Raises:
            ValueError: If provisioning fails.
        """
        lab_id = str(uuid.uuid4())[:8]
        lab = LabEnvironment(
            lab_id=lab_id,
            name=name,
            status=LabStatus.PROVISIONING,
            iac_config=iac_config or {},
            metadata=metadata or {},
        )

        self._labs[lab_id] = lab
        logger.info(f"Provisioning lab {lab_id} ({name})...")

        provider_name = iac_provider or self._default_provider
        provider = self._provider_factory.create(provider_name)

        try:
            if not provider.validate(lab.iac_config):
                raise ValueError(f"IaC configuration validation failed for {provider_name}")

            plan_output = provider.plan(lab.iac_config)
            logger.debug(f"Plan output: {plan_output}")

            apply_result = provider.apply(lab.iac_config)

            if apply_result.get("success"):
                lab.status = LabStatus.READY
                lab.ready_at = datetime.utcnow()
                if apply_result.get("outputs"):
                    lab.metadata["outputs"] = apply_result["outputs"]
                logger.info(f"Lab {lab_id} provisioned successfully")
            else:
                lab.status = LabStatus.FAILED
                lab.metadata["error"] = apply_result.get("error", "Unknown error")
                logger.error(f"Lab {lab_id} provisioning failed: {lab.metadata['error']}")
                raise ValueError(f"Provisioning failed: {lab.metadata['error']}")

        except Exception as e:
            lab.status = LabStatus.FAILED
            lab.metadata["error"] = str(e)
            logger.error(f"Lab {lab_id} provisioning error: {e}")
            raise

        return lab

    def teardown(self, lab_id: str, force: bool = False) -> bool:
        """Tear down a lab environment.

        Args:
            lab_id: ID of the lab to destroy.
            force: Force destroy even if lab is not in READY state.

        Returns:
            True if teardown succeeded, False otherwise.
        """
        lab = self._labs.get(lab_id)
        if not lab:
            logger.warning(f"Lab {lab_id} not found")
            return False

        if not force and lab.status != LabStatus.READY:
            logger.error(f"Lab {lab_id} is not in READY state (current: {lab.status})")
            return False

        logger.info(f"Tearing down lab {lab_id} ({lab.name})...")
        lab.status = LabStatus.TEARDOWN

        provider_name = lab.iac_config.get("provider", self._default_provider)
        provider = self._provider_factory.create(provider_name)

        try:
            success = provider.destroy(lab.iac_config)

            if success:
                lab.status = LabStatus.DESTROYED
                lab.destroyed_at = datetime.utcnow()
                logger.info(f"Lab {lab_id} destroyed successfully")
            else:
                lab.status = LabStatus.FAILED
                logger.error(f"Lab {lab_id} destroy failed")

            return success

        except Exception as e:
            lab.status = LabStatus.FAILED
            lab.metadata["teardown_error"] = str(e)
            logger.error(f"Lab {lab_id} teardown error: {e}")
            return False

    def status(self, lab_id: str) -> LabStatus | None:
        """Get the current status of a lab.

        Args:
            lab_id: ID of the lab to query.

        Returns:
            LabStatus if lab exists, None otherwise.
        """
        lab = self._labs.get(lab_id)
        return lab.status if lab else None

    def list(self, status_filter: LabStatus | None = None) -> list[LabEnvironment]:
        """List all labs, optionally filtered by status.

        Args:
            status_filter: Only return labs with this status.

        Returns:
            List of LabEnvironment instances.
        """
        labs = list(self._labs.values())

        if status_filter is not None:
            labs = [lab for lab in labs if lab.status == status_filter]

        return labs

    def get(self, lab_id: str) -> LabEnvironment | None:
        """Get a lab by ID.

        Args:
            lab_id: ID of the lab to retrieve.

        Returns:
            LabEnvironment if found, None otherwise.
        """
        return self._labs.get(lab_id)

    @contextmanager
    def managed_lab(
        self,
        name: str,
        iac_provider: str | None = None,
        iac_config: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Generator[LabEnvironment, None, None]:
        """Context manager for automatic lab cleanup.

        Provisions a lab and automatically tears it down when
        the context exits, even if an exception occurs.

        Args:
            name: Human-readable name for the lab.
            iac_provider: IaC provider to use.
            iac_config: Provider-specific configuration.
            metadata: Additional metadata.

        Yields:
            LabEnvironment instance.

        Example:
            with manager.managed_lab("temp-test-env") as lab:
                # Run tests against lab environment
                pass
            # Lab is automatically destroyed
        """
        lab = None
        try:
            lab = self.provision(name, iac_provider, iac_config, metadata)
            yield lab
        finally:
            if lab and lab.lab_id in self._labs:
                self.teardown(lab.lab_id, force=True)

    def cleanup_all(self) -> int:
        """Tear down all active labs.

        Returns:
            Number of labs successfully destroyed.
        """
        active_labs = self.list(status_filter=LabStatus.READY)
        destroyed = 0

        for lab in active_labs:
            if self.teardown(lab.lab_id, force=True):
                destroyed += 1

        logger.info(f"Cleaned up {destroyed}/{len(active_labs)} labs")
        return destroyed
