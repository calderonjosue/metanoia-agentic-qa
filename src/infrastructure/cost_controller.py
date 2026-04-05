"""Cost controller for monitoring and limiting spend.

This module provides spend tracking and budget enforcement capabilities
to prevent runaway costs during lab provisioning and CI/CD operations.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class BudgetExceeded(Exception):
    """Raised when a spend threshold is exceeded."""

    def __init__(self, threshold: float, actual: float, period: str):
        self.threshold = threshold
        self.actual = actual
        self.period = period
        super().__init__(
            f"Budget exceeded: {actual:.2f} spent (limit: {threshold:.2f}) for {period}"
        )


@dataclass
class SpendRecord:
    """Record of a single spend event."""

    amount: float
    timestamp: datetime
    description: str
    category: str = "default"


class CostController:
    """Spend watchdog with configurable thresholds.

    Monitors spending per run and per day, raising BudgetExceeded
    when thresholds are breached.

    Attributes:
        max_spend_per_run: Maximum spend allowed per individual run
        max_spend_per_day: Maximum spend allowed per 24-hour period
        current_run_spend: Accumulated spend for current run
        daily_spend: Accumulated spend for current day
        run_start_time: When the current run started
        daily_start_time: When the current day started
    """

    def __init__(
        self,
        max_spend_per_run: Optional[float] = None,
        max_spend_per_day: Optional[float] = None,
    ):
        self.max_spend_per_run = max_spend_per_run or float(
            os.getenv("MAX_SPEND_PER_RUN", "100.0")
        )
        self.max_spend_per_day = max_spend_per_day or float(
            os.getenv("MAX_SPEND_PER_DAY", "1000.0")
        )
        self.current_run_spend: float = 0.0
        self.daily_spend: float = 0.0
        self.run_start_time: datetime = datetime.now()
        self.daily_start_time: datetime = self._start_of_day()
        self._spend_history: list[SpendRecord] = []

    def _start_of_day(self) -> datetime:
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    def track_spend(
        self,
        amount: float,
        description: str = "",
        category: str = "default",
    ) -> None:
        """Record a spend event and check thresholds.

        Args:
            amount: Amount spent in USD
            description: Human-readable description of the spend
            category: Spend category (e.g., 'compute', 'storage', 'network')

        Raises:
            BudgetExceeded: If adding this spend would breach a threshold
        """
        self._reset_daily_if_needed()

        record = SpendRecord(
            amount=amount,
            timestamp=datetime.now(),
            description=description,
            category=category,
        )
        self._spend_history.append(record)

        self.current_run_spend += amount
        self.daily_spend += amount

        self.check_threshold()

    def check_threshold(self) -> None:
        """Check if current spend exceeds any threshold.

        Raises:
            BudgetExceeded: If a threshold is breached
        """
        self._reset_daily_if_needed()

        if self.current_run_spend > self.max_spend_per_run:
            raise BudgetExceeded(
                threshold=self.max_spend_per_run,
                actual=self.current_run_spend,
                period="run",
            )

        if self.daily_spend > self.max_spend_per_day:
            raise BudgetExceeded(
                threshold=self.max_spend_per_day,
                actual=self.daily_spend,
                period="day",
            )

    def _reset_daily_if_needed(self) -> None:
        current_day = self._start_of_day()
        if current_day > self.daily_start_time:
            self.daily_spend = 0.0
            self.daily_start_time = current_day
            self._spend_history = [
                r for r in self._spend_history if r.timestamp >= current_day
            ]

    def reset_run(self) -> None:
        """Reset the current run spend counter."""
        self.current_run_spend = 0.0
        self.run_start_time = datetime.now()

    def get_spend_summary(self) -> dict:
        """Get current spend summary.

        Returns:
            Dictionary with spend breakdown by category and totals
        """
        self._reset_daily_if_needed()

        by_category: dict[str, float] = {}
        for record in self._spend_history:
            by_category[record.category] = by_category.get(record.category, 0.0) + record.amount

        return {
            "current_run_spend": self.current_run_spend,
            "daily_spend": self.daily_spend,
            "max_spend_per_run": self.max_spend_per_run,
            "max_spend_per_day": self.max_spend_per_day,
            "run_duration_seconds": (datetime.now() - self.run_start_time).total_seconds(),
            "by_category": by_category,
        }
