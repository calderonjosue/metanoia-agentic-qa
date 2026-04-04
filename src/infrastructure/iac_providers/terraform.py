"""Terraform IaC Provider implementation.

This module implements the IaCProvider protocol using Terraform CLI,
providing infrastructure provisioning and lifecycle management.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from src.infrastructure.iac_providers.base import IaCProvider

logger = logging.getLogger(__name__)


class TerraformProvider(IaCProvider):
    """Terraform IaC provider using subprocess for CLI invocation.

    This provider wraps Terraform CLI commands to enable infrastructure
    provisioning through the standard Terraform workflow (validate,
    plan, apply, destroy).

    Attributes:
        working_dir: Default working directory for Terraform commands.
        terraform_binary: Path to the terraform CLI binary.
    """

    def __init__(
        self,
        working_dir: str | Path | None = None,
        terraform_binary: str = "terraform",
    ):
        """Initialize the Terraform provider.

        Args:
            working_dir: Default directory containing Terraform configurations.
                        If None, each operation must specify the config directory.
            terraform_binary: Path to terraform CLI binary.
        """
        self.working_dir = Path(working_dir) if working_dir else None
        self.terraform_binary = terraform_binary

    def _get_working_dir(self, config: dict[str, Any]) -> Path | None:
        """Resolve working directory from config or default.

        Args:
            config: Configuration dictionary.

        Returns:
            Path to working directory or None.
        """
        if "working_dir" in config:
            return Path(config["working_dir"])
        return self.working_dir

    def _run_terraform(
        self,
        args: list[str],
        config: dict[str, Any],
        capture_output: bool = True,
    ) -> subprocess.CompletedProcess:
        """Execute a Terraform CLI command.

        Args:
            args: Command-line arguments for terraform.
            config: Configuration containing working_dir override.
            capture_output: Whether to capture stdout/stderr.

        Returns:
            CompletedProcess instance with command results.

        Raises:
            subprocess.CalledProcessError: If command returns non-zero exit.
            FileNotFoundError: If terraform binary not found.
        """
        working_dir = self._get_working_dir(config)
        logger.debug(f"Running: terraform {' '.join(args)} in {working_dir}")

        return subprocess.run(
            [self.terraform_binary] + args,
            cwd=str(working_dir) if working_dir else None,
            capture_output=capture_output,
            text=True,
            check=False,
        )

    def validate(self, config: dict[str, Any]) -> bool:
        """Validate Terraform configuration files.

        Args:
            config: Configuration dictionary. Supports:
                - working_dir: Directory containing .tf files
                - validate_options: Additional terraform validate flags

        Returns:
            True if validation succeeds, False otherwise.
        """
        try:
            args = ["validate"]
            if config.get("validate_options"):
                args.extend(config["validate_options"])

            result = self._run_terraform(args, config)

            if result.returncode == 0:
                logger.info("Terraform configuration is valid")
                return True
            else:
                logger.error(f"Terraform validation failed: {result.stderr}")
                return False

        except FileNotFoundError:
            logger.error(f"Terraform binary not found: {self.terraform_binary}")
            return False
        except Exception as e:
            logger.error(f"Terraform validation error: {e}")
            return False

    def plan(self, config: dict[str, Any]) -> str:
        """Generate Terraform execution plan.

        Args:
            config: Configuration dictionary. Supports:
                - working_dir: Directory containing .tf files
                - plan_file: Path to save the plan file
                - var_file: Path to variable file
                - vars: Dictionary of variables

        Returns:
            Human-readable plan string describing intended changes.
            Returns error message if planning fails.
        """
        try:
            args = ["plan", "-json"]

            if "plan_file" in config:
                args.extend(["-out", config["plan_file"]])

            if "var_file" in config:
                args.extend(["-var-file", config["var_file"]])

            if "vars" in config:
                for key, value in config["vars"].items():
                    args.extend(["-var", f"{key}={value}"])

            result = self._run_terraform(args, config)

            if result.returncode == 0 and result.stdout:
                plan_data = json.loads(result.stdout)
                return self._format_plan_output(plan_data)
            elif result.returncode == 0:
                return "Plan generated successfully (no output)"
            else:
                error_msg = result.stderr or "Unknown error during plan"
                logger.error(f"Terraform plan failed: {error_msg}")
                return f"Plan failed: {error_msg}"

        except FileNotFoundError:
            return f"Terraform binary not found: {self.terraform_binary}"
        except json.JSONDecodeError:
            return result.stdout if result.stdout else "Failed to parse plan output"
        except Exception as e:
            return f"Terraform plan error: {e}"

    def _format_plan_output(self, plan_data: dict[str, Any]) -> str:
        """Format Terraform plan JSON output into human-readable string.

        Args:
            plan_data: Parsed JSON output from terraform plan -json.

        Returns:
            Formatted plan summary string.
        """
        lines = ["Terraform Plan:"]

        if "changes" in plan_data:
            changes = plan_data["changes"]
            for change in changes.get("root_module", {}).get("changes", []):
                address = change.get("address", "unknown")
                action = change.get("actions", ["no-op"])[0]
                lines.append(f"  {action.upper()}: {address}")

        if "diagnostics" in plan_data:
            for diag in plan_data["diagnostics"]:
                severity = diag.get("severity", "info")
                summary = diag.get("summary", "No summary")
                lines.append(f"  [{severity}] {summary}")

        return "\n".join(lines) if lines else "No changes planned"

    def apply(self, config: dict[str, Any]) -> dict[str, Any]:
        """Apply Terraform configuration to provision resources.

        Args:
            config: Configuration dictionary. Supports:
                - working_dir: Directory containing .tf files
                - plan_file: Previously generated plan file to apply
                - auto_approve: Skip approval prompt (default: True)
                - var_file: Path to variable file
                - vars: Dictionary of variables

        Returns:
            Dictionary containing:
                - success: bool
                - outputs: dict of terraform outputs
                - error: str or None
        """
        result = {
            "success": False,
            "outputs": {},
            "error": None,
        }

        try:
            args = ["apply", "-json"]

            if "plan_file" in config:
                args.append(config["plan_file"])
            else:
                args.append("-auto-approve")

            if "var_file" in config:
                args.extend(["-var-file", config["var_file"]])

            if "vars" in config:
                for key, value in config["vars"].items():
                    args.extend(["-var", f"{key}={value}"])

            process = self._run_terraform(args, config)

            if process.returncode == 0 and process.stdout:
                apply_data = json.loads(process.stdout)
                result["success"] = True
                result["outputs"] = self._parse_outputs(apply_data)
                logger.info("Terraform apply completed successfully")
            else:
                result["error"] = process.stderr or "Apply failed"
                logger.error(f"Terraform apply failed: {result['error']}")

        except FileNotFoundError:
            result["error"] = f"Terraform binary not found: {self.terraform_binary}"
        except json.JSONDecodeError:
            result["error"] = "Failed to parse apply output"
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Terraform apply error: {e}")

        return result

    def _parse_outputs(self, apply_data: dict[str, Any]) -> dict[str, Any]:
        """Parse Terraform outputs from apply JSON output.

        Args:
            apply_data: Parsed JSON from terraform apply.

        Returns:
            Dictionary of output key-value pairs.
        """
        outputs = {}

        if "outputs" in apply_data:
            for key, value in apply_data["outputs"].items():
                outputs[key] = value.get("value")

        return outputs

    def destroy(self, config: dict[str, Any]) -> bool:
        """Destroy Terraform-managed resources.

        Args:
            config: Configuration dictionary. Supports:
                - working_dir: Directory containing .tf files
                - auto_approve: Skip approval prompt (default: True)
                - var_file: Path to variable file
                - vars: Dictionary of variables

        Returns:
            True if destroy completed successfully, False otherwise.
        """
        try:
            args = ["destroy", "-json", "-auto-approve"]

            if "var_file" in config:
                args.extend(["-var-file", config["var_file"]])

            if "vars" in config:
                for key, value in config["vars"].items():
                    args.extend(["-var", f"{key}={value}"])

            result = self._run_terraform(args, config)

            if result.returncode == 0:
                logger.info("Terraform destroy completed successfully")
                return True
            else:
                logger.error(f"Terraform destroy failed: {result.stderr}")
                return False

        except FileNotFoundError:
            logger.error(f"Terraform binary not found: {self.terraform_binary}")
            return False
        except Exception as e:
            logger.error(f"Terraform destroy error: {e}")
            return False

    def output(self, config: dict[str, Any]) -> dict[str, Any]:
        """Get Terraform output values.

        Args:
            config: Configuration dictionary. Supports:
                - working_dir: Directory containing .tf files
                - output_names: List of specific outputs to retrieve

        Returns:
            Dictionary of output key-value pairs.
        """
        try:
            args = ["output", "-json"]

            result = self._run_terraform(args, config)

            if result.returncode == 0 and result.stdout:
                outputs = json.loads(result.stdout)
                if "output_names" in config:
                    return {
                        k: v.get("value")
                        for k, v in outputs.items()
                        if k in config["output_names"]
                    }
                return {k: v.get("value") for k, v in outputs.items()}

            return {}

        except Exception as e:
            logger.error(f"Terraform output error: {e}")
            return {}
