"""BackstopJS executor for visual regression testing.

This skill provides visual regression testing capabilities using
BackstopJS with Puppeteer rendering and configurable viewports.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, TypedDict

from metanoia.skills.base import SkillExecutor, SkillInput, SkillOutput

logger = logging.getLogger(__name__)


class BackstopInput(TypedDict):
    """Input schema for BackstopJS executor."""
    action: str
    config: dict | None
    scenarios: list[dict] | None
    viewports: list[dict] | None
    paths: dict | None


class BackstopOutput(TypedDict):
    """Output schema for BackstopJS executor."""
    status: str
    report_path: str | None
    passed: int | None
    failed: int | None
    error: str | None


class ViewportConfig:
    """Predefined viewport configurations."""
    
    PRESETS = {
        "phone": {"width": 375, "height": 667},
        "tablet": {"width": 768, "height": 1024},
        "desktop": {"width": 1280, "height": 800},
        "wide": {"width": 1920, "height": 1080},
    }
    
    @classmethod
    def get_viewport(cls, name_or_config: str | dict) -> dict:
        """Get viewport configuration by name or return as-is."""
        if isinstance(name_or_config, str):
            return cls.PRESETS.get(name_or_config, cls.PRESETS["desktop"])
        return name_or_config


class ConfigBuilder:
    """Builds BackstopJS configuration from executor input."""
    
    DEFAULT_PATHS = {
        "bitmaps_reference": "backstop_data/bitmaps_reference",
        "bitmaps_test": "backstop_data/bitmaps_test",
        "html_report": "backstop_data/html_report",
        "ci_report": "backstop_data/ci_report",
    }
    
    def __init__(self, config: dict | None = None):
        self.config = config or {}
    
    def build(self, scenarios: list[dict], viewports: list[dict] | None = None) -> dict:
        """Build complete BackstopJS config."""
        viewport_list = viewports or [
            ViewportConfig.get_viewport("desktop")
        ]
        
        formatted_viewports = self._format_viewports(viewport_list)
        
        return {
            "id": self.config.get("id", "metanoia-backstop-test"),
            "viewports": formatted_viewports,
            "scenarios": scenarios,
            "paths": self.config.get("paths", self.DEFAULT_PATHS),
            "report": self.config.get("report", ["browser", "CI"]),
            "engine": self.config.get("engine", "puppeteer"),
            "engineOptions": self.config.get("engineOptions", {
                "headless": True,
                "args": ["--no-sandbox", "--disable-setuid-sandbox"],
            }),
            "asyncCaptureLimit": self.config.get("asyncCaptureLimit", 1),
            "asyncCompareLimit": self.config.get("asyncCompareLimit", 5),
            "debug": self.config.get("debug", False),
        }
    
    def _format_viewports(self, viewports: list[dict]) -> list[dict]:
        """Format viewport configurations."""
        formatted = []
        for vp in viewports:
            if isinstance(vp, str):
                preset = ViewportConfig.get_viewport(vp)
                formatted.append({
                    "name": vp,
                    "width": preset["width"],
                    "height": preset["height"],
                })
            else:
                formatted.append({
                    "name": vp.get("name", f"{vp['width']}x{vp['height']}"),
                    "width": vp["width"],
                    "height": vp["height"],
                })
        return formatted


class DynamicContentHandler:
    """Handles dynamic content with waits and scripts."""
    
    @staticmethod
    def process_scenario(scenario: dict) -> dict:
        """Process scenario with dynamic content handling."""
        processed = scenario.copy()
        
        if "delay" in scenario:
            processed["delay"] = scenario["delay"]
        
        if "waitForSelector" in scenario:
            processed["readySelector"] = scenario["waitForSelector"]
        
        if "onReadyScript" in scenario:
            script_path = scenario["onReadyScript"]
            if not os.path.isabs(script_path):
                processed["onReadyScript"] = f"./scripts/{script_path}"
        
        return processed


class BackstopExecutor(SkillExecutor):
    """Visual regression testing executor using BackstopJS."""
    
    name = "backstopjs-executor"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self._temp_config: Path | None = None
        self._workspace = Path.cwd()
    
    async def execute(self, input_data: BackstopInput) -> BackstopOutput:
        """Execute BackstopJS visual regression test.
        
        Args:
            input_data: Action and configuration for BackstopJS.
            
        Returns:
            BackstopOutput with test results and report path.
        """
        action = input_data.get("action", "test")
        config = input_data.get("config", {})
        scenarios = input_data.get("scenarios", [])
        viewports = input_data.get("viewports")
        paths = input_data.get("paths")
        
        if not scenarios:
            return self._error_output("No scenarios provided")
        
        try:
            config_builder = ConfigBuilder(config)
            
            if paths:
                config_builder.config["paths"] = paths
            
            processed_scenarios = [
                DynamicContentHandler.process_scenario(s) 
                for s in scenarios
            ]
            
            backstop_config = config_builder.build(processed_scenarios, viewports)
            
            temp_config = self._create_temp_config(backstop_config)
            self._temp_config = temp_config
            
            if action == "reference":
                return await self._run_reference(backstop_config, temp_config)
            elif action == "test":
                return await self._run_test(backstop_config, temp_config)
            elif action == "approve":
                return await self._run_approve(temp_config)
            else:
                return self._error_output(f"Unknown action: {action}")
                
        except Exception as e:
            logger.exception("BackstopJS execution failed")
            return self._error_output(str(e))
        finally:
            await self.cleanup()
    
    async def _run_reference(self, config: dict, temp_config: Path) -> BackstopOutput:
        """Capture reference screenshots."""
        try:
            result = await self._run_backstop(["reference", "-c", str(temp_config)])
            
            if result.returncode == 0:
                report_path = str(self._workspace / config["paths"]["html_report"])
                return {
                    "status": "success",
                    "report_path": report_path,
                    "passed": len(config["scenarios"]),
                    "failed": 0,
                    "error": None,
                }
            else:
                return self._error_output(f"Reference capture failed: {result.stderr}")
                
        except FileNotFoundError:
            return self._error_output("BackstopJS not found. Install with: npm install -g backstopjs")
    
    async def _run_test(self, config: dict, temp_config: Path) -> BackstopOutput:
        """Run visual regression test."""
        try:
            result = await self._run_backstop(["test", "-c", str(temp_config)])
            
            report_path = str(self._workspace / config["paths"]["html_report"])
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "report_path": report_path,
                    "passed": len(config["scenarios"]),
                    "failed": 0,
                    "error": None,
                }
            else:
                parsed = self._parse_test_output(result.stdout)
                return {
                    "status": "failed",
                    "report_path": report_path,
                    "passed": parsed.get("passed", 0),
                    "failed": parsed.get("failed", len(config["scenarios"])),
                    "error": None,
                }
                
        except FileNotFoundError:
            return self._error_output("BackstopJS not found. Install with: npm install -g backstopjs")
    
    async def _run_approve(self, temp_config: Path) -> BackstopOutput:
        """Approve failed tests and update references."""
        try:
            result = await self._run_backstop(["approve", "-c", str(temp_config)])
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "report_path": None,
                    "passed": 0,
                    "failed": 0,
                    "error": None,
                }
            else:
                return self._error_output(f"Approve failed: {result.stderr}")
                
        except FileNotFoundError:
            return self._error_output("BackstopJS not found. Install with: npm install -g backstopjs")
    
    async def _run_backstop(self, args: list[str]) -> subprocess.CompletedProcess:
        """Run backstop command."""
        cmd = ["npx", "backstopjs"] + args
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self._workspace,
        )
        
        stdout, stderr = await proc.communicate()
        
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=proc.returncode,
            stdout=stdout.decode() if stdout else "",
            stderr=stderr.decode() if stderr else "",
        )
    
    def _create_temp_config(self, config: dict) -> Path:
        """Create temporary config file."""
        temp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            dir=self._workspace,
        )
        json.dump(config, temp, indent=2)
        temp.close()
        return Path(temp.name)
    
    def _parse_test_output(self, output: str) -> dict:
        """Parse BackstopJS test output for results."""
        parsed = {"passed": 0, "failed": 0}
        
        try:
            for line in output.split("\n"):
                if "passed" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "passed" in part.lower() and i > 0:
                            try:
                                parsed["passed"] = int(parts[i - 1])
                            except (ValueError, IndexError):
                                pass
                elif "failed" in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "failed" in part.lower() and i > 0:
                            try:
                                parsed["failed"] = int(parts[i - 1])
                            except (ValueError, IndexError):
                                pass
        except Exception as e:
            logger.warning(f"Failed to parse test output: {e}")
        
        return parsed
    
    async def cleanup(self) -> None:
        """Cleanup temporary files."""
        if self._temp_config and self._temp_config.exists():
            try:
                self._temp_config.unlink()
            except OSError:
                pass
        self._temp_config = None
    
    def _success_output(self) -> BackstopOutput:
        """Create success output."""
        return {
            "status": "success",
            "report_path": None,
            "passed": 0,
            "failed": 0,
            "error": None,
        }
    
    def _error_output(self, error: str) -> BackstopOutput:
        """Create error output."""
        return {
            "status": "error",
            "report_path": None,
            "passed": None,
            "failed": None,
            "error": error,
        }
