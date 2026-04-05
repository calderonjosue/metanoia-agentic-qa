"""CLI for Skill Hub community skill management."""

import asyncio
import sys
from pathlib import Path

import click
import yaml

from metanoia.src.skill_hub.registry import get_hub_registry
from metanoia.src.skill_hub.manifest import validate_manifest, parse_manifest


@click.group()
def skill():
    """Manage community skills."""
    pass


@skill.command()
@click.argument("name")
def install(name: str):
    """Install a skill from the community registry."""
    registry = get_hub_registry()
    result = asyncio.run(registry.install(name))
    if result:
        click.echo(f"✓ Installed skill: {name}")
    else:
        click.echo(f"✗ Failed to install skill: {name}", err=True)
        sys.exit(1)


@skill.command()
def list():
    """List installed skills."""
    registry = get_hub_registry()
    installed = registry.list_installed()
    
    if not installed:
        click.echo("No skills installed. Run 'metanoia skill install <name>' to install.")
        return
    
    click.echo(f"Installed skills ({len(installed)}):")
    for manifest in installed:
        click.echo(f"  • {manifest.name} v{manifest.version} - {manifest.description}")


@skill.command()
@click.argument("query")
def search(query: str):
    """Search the community registry."""
    registry = get_hub_registry()
    results = asyncio.run(registry.search(query))
    
    if not results:
        click.echo(f"No skills found matching: {query}")
        return
    
    click.echo(f"Search results for '{query}':")
    for manifest in results:
        click.echo(f"  • {manifest.name} v{manifest.version}")
        click.echo(f"    {manifest.description}")
        click.echo(f"    Author: {manifest.author}")
        click.echo()


@skill.command()
@click.argument("path", type=click.Path(exists=True))
def publish(path: str):
    """Publish a skill to the community registry."""
    skill_path = Path(path)
    manifest_file = skill_path / "skill-manifest.yaml"
    
    if not manifest_file.exists():
        click.echo(f"✗ No skill-manifest.yaml found in {path}", err=True)
        sys.exit(1)
    
    try:
        with open(manifest_file) as f:
            manifest_data = yaml.safe_load(f)
        
        if not validate_manifest(manifest_data):
            click.echo("✗ Invalid manifest: runtime_version must be '>=2.0'", err=True)
            sys.exit(1)
        
        manifest = parse_manifest(manifest_data)
        click.echo(f"✓ Publishing {manifest.name} v{manifest.version} to registry...")
        click.echo("  Note: Publishing requires GitHub credentials and repo access.")
        click.echo("  Please submit a PR to https://github.com/metanoia-qa/skills")
    except Exception as e:
        click.echo(f"✗ Failed to publish: {e}", err=True)
        sys.exit(1)


@skill.command()
@click.argument("name")
def uninstall(name: str):
    """Remove an installed skill."""
    registry = get_hub_registry()
    result = registry.uninstall(name)
    
    if result:
        click.echo(f"✓ Uninstalled skill: {name}")
    else:
        click.echo(f"✗ Skill not found: {name}", err=True)
        sys.exit(1)


def main():
    skill()


if __name__ == "__main__":
    main()
