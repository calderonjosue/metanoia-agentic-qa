"""Anomaly detection for APM metrics using statistical methods.

Detects anomalies in test duration, pass/fail rates, and agent
performance using z-score and IQR-based methods.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

import numpy as np


class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(str, Enum):
    SPIKE = "spike"
    DROP = "drop"
    FLATLINE = "flatline"
    UNUSUAL_PATTERN = "unusual_pattern"


class Metric(BaseModel):
    timestamp: datetime
    metric_name: str
    value: float
    tags: dict[str, str] = Field(default_factory=dict)


class Anomaly(BaseModel):
    metric_name: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detected_value: float
    expected_range: tuple[float, float]
    z_score: Optional[float] = None
    iqr_multiplier: Optional[float] = None
    timestamp: datetime
    message: str
    tags: dict[str, str] = Field(default_factory=dict)


@dataclass
class DetectionConfig:
    z_score_threshold: float = 3.0
    iqr_multiplier: float = 1.5
    min_samples: int = 10
    window_size: int = 100


class AnomalyDetector:
    """Detects anomalies in metrics using statistical methods.

    Supports z-score and IQR (Interquartile Range) based detection.

    Attributes:
        config: Detection configuration
    """

    def __init__(self, config: Optional[DetectionConfig] = None):
        """Initialize the anomaly detector.

        Args:
            config: Detection configuration
        """
        self.config = config or DetectionConfig()

    def detect(self, metrics: list[Metric]) -> list[Anomaly]:
        """Detect anomalies in the given metrics.

        Args:
            metrics: List of metric data points

        Returns:
            List of detected anomalies
        """
        if len(metrics) < self.config.min_samples:
            return []

        metrics_by_name: dict[str, list[Metric]] = {}
        for metric in metrics:
            if metric.metric_name not in metrics_by_name:
                metrics_by_name[metric.metric_name] = []
            metrics_by_name[metric.metric_name].append(metric)

        anomalies = []
        for metric_name, name_metrics in metrics_by_name.items():
            name_metrics.sort(key=lambda m: m.timestamp)
            values = np.array([m.value for m in name_metrics])

            z_anomalies = self._detect_z_score_anomalies(
                name_metrics, values, metric_name
            )
            anomalies.extend(z_anomalies)

            iqr_anomalies = self._detect_iqr_anomalies(
                name_metrics, values, metric_name
            )
            anomalies.extend(iqr_anomalies)

        return anomalies

    def _detect_z_score_anomalies(
        self,
        metrics: list[Metric],
        values: np.ndarray,
        metric_name: str,
    ) -> list[Anomaly]:
        """Detect anomalies using z-score method.

        Args:
            metrics: List of metrics
            values: Array of metric values
            metric_name: Name of the metric

        Returns:
            List of z-score based anomalies
        """
        anomalies = []
        mean = np.mean(values)
        std = np.std(values)

        if std == 0:
            return []

        z_scores = np.abs((values - mean) / std)

        for i, (metric, z_score) in enumerate(zip(metrics, z_scores)):
            if z_score > self.config.z_score_threshold:
                severity = self._get_z_score_severity(z_score)

                is_spike = metric.value > mean
                anomaly_type = AnomalyType.SPIKE if is_spike else AnomalyType.DROP

                anomalies.append(Anomaly(
                    metric_name=metric_name,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    detected_value=metric.value,
                    expected_range=(float(mean - 2 * std), float(mean + 2 * std)),
                    z_score=float(z_score),
                    timestamp=metric.timestamp,
                    message=f"{anomaly_type.value} detected: value {metric.value:.2f} "
                            f"differs significantly from mean {mean:.2f}",
                    tags=metric.tags,
                ))

        return anomalies

    def _detect_iqr_anomalies(
        self,
        metrics: list[Metric],
        values: np.ndarray,
        metric_name: str,
    ) -> list[Anomaly]:
        """Detect anomalies using IQR method.

        Args:
            metrics: List of metrics
            values: Array of metric values
            metric_name: Name of the metric

        Returns:
            List of IQR-based anomalies
        """
        anomalies = []

        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1

        if iqr == 0:
            return []

        lower_bound = q1 - self.config.iqr_multiplier * iqr
        upper_bound = q3 + self.config.iqr_multiplier * iqr

        for metric in metrics:
            if metric.value < lower_bound or metric.value > upper_bound:
                severity = self._get_iqr_severity(metric.value, lower_bound, upper_bound, iqr)

                if metric.value < lower_bound:
                    anomaly_type = AnomalyType.DROP
                else:
                    anomaly_type = AnomalyType.SPIKE

                anomalies.append(Anomaly(
                    metric_name=metric_name,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    detected_value=metric.value,
                    expected_range=(float(lower_bound), float(upper_bound)),
                    iqr_multiplier=float(self.config.iqr_multiplier),
                    timestamp=metric.timestamp,
                    message=f"{anomaly_type.value} detected: value {metric.value:.2f} "
                            f"outside expected range [{lower_bound:.2f}, {upper_bound:.2f}]",
                    tags=metric.tags,
                ))

        return anomalies

    def _get_z_score_severity(self, z_score: float) -> AnomalySeverity:
        """Determine severity based on z-score.

        Args:
            z_score: Absolute z-score value

        Returns:
            Anomaly severity level
        """
        if z_score > 5:
            return AnomalySeverity.CRITICAL
        elif z_score > 4:
            return AnomalySeverity.HIGH
        elif z_score > 3.5:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def _get_iqr_severity(
        self,
        value: float,
        lower: float,
        upper: float,
        iqr: float,
    ) -> AnomalySeverity:
        """Determine severity based on IQR deviation.

        Args:
            value: Detected value
            lower: Lower bound
            upper: Upper bound
            iqr: Interquartile range

        Returns:
            Anomaly severity level
        """
        if iqr == 0:
            return AnomalySeverity.HIGH

        distance = max(lower - value, value - upper)
        deviation = distance / iqr

        if deviation > 3:
            return AnomalySeverity.CRITICAL
        elif deviation > 2:
            return AnomalySeverity.HIGH
        elif deviation > 1.5:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def detect_in_stream(
        self,
        new_metric: Metric,
        historical_metrics: list[Metric],
    ) -> list[Anomaly]:
        """Detect anomalies in a streaming context with limited history.

        Args:
            new_metric: New metric data point
            historical_metrics: Historical metrics for baseline

        Returns:
            List of detected anomalies (if any)
        """
        all_metrics = historical_metrics + [new_metric]
        return self.detect(all_metrics)
