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
    ContextAnalyst,
    ContextAnalysisResult,
    SprintScope,
    HistoricalSimilarity,
    FlakyTest,
    ModuleRisk,
)
from src.agents.strategy_manager import (
    StrategyManager,
    TestPlan,
    EffortDistribution,
    TestPriority,
)
from src.agents.design_lead import (
    TestDesignLead,
    TestDesignResult,
    TestScenario,
    TestCase,
    TestEnvironment,
    SyntheticDataTemplate,
)
from src.agents.ui_automation import UIAutomationEngineer, TestResult as UITestResult
from src.agents.performance import PerformanceEngineer, TestResult as PerfTestResult, PerformanceMetrics
from src.agents.security import SecurityEngineer, TestResult as SecTestResult, SecurityFinding
from src.agents.release_analyst import ReleaseAnalyst, TestResult as ReleaseTestResult, ReleaseScore, AgentResult

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
