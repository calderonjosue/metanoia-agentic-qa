"""Metanoia-QA Agents Package.

This package contains the specialized agents that execute
the Software Testing Life Cycle (STLC) pipeline.

Planning Agents:
- ContextAnalyst: Historical context analysis
- StrategyManager: Test planning and strategy
- TestDesignLead: Test case design

Execution Agents:
- UIAutomationEngineer: Playwright-based UI test execution
- PerformanceEngineer: k6-based performance test execution
- SecurityEngineer: ZAP-based security scanning
- IntegrationEngineer: Integration testing
"""

from src.agents.context_analyst import (
    ContextAnalysisResult,
    ContextAnalyst,
    FlakyTest,
    HistoricalSimilarity,
    ModuleRisk,
    SprintScope,
)
from src.agents.design_lead import (
    SyntheticDataTemplate,
    TestCase,
    TestDesignLead,
    TestDesignResult,
    TestEnvironment,
    TestScenario,
)
from src.agents.performance import PerformanceEngineer, PerformanceMetrics
from src.agents.performance import TestResult as PerfTestResult
from src.agents.release_analyst import AgentResult, ReleaseAnalyst, ReleaseScore
from src.agents.release_analyst import TestResult as ReleaseTestResult
from src.agents.security import SecurityEngineer, SecurityFinding
from src.agents.security import TestResult as SecTestResult
from src.agents.strategy_manager import (
    EffortDistribution,
    StrategyManager,
    TestPlan,
    TestPriority,
)
from src.agents.ui_automation import TestResult as UITestResult
from src.agents.ui_automation import UIAutomationEngineer

__all__ = [
    "ContextAnalyst",
    "ContextAnalysisResult",
    "SprintScope",
    "HistoricalSimilarity",
    "FlakyTest",
    "ModuleRisk",
    "StrategyManager",
    "TestPlan",
    "EffortDistribution",
    "TestPriority",
    "TestDesignLead",
    "TestDesignResult",
    "TestScenario",
    "TestCase",
    "TestEnvironment",
    "SyntheticDataTemplate",
    "UIAutomationEngineer",
    "UITestResult",
    "PerformanceEngineer",
    "PerfTestResult",
    "PerformanceMetrics",
    "SecurityEngineer",
    "SecTestResult",
    "SecurityFinding",
    "ReleaseAnalyst",
    "ReleaseTestResult",
    "ReleaseScore",
    "AgentResult",
]
