"""CLI for Metanoia-QA."""
import click


@click.group()
@click.version_option(version="2.1.0")
def main():
    """Metanoia-QA: Autonomous Agentic STLC Framework."""
    pass

@main.command()
@click.option("--sprint", required=True, help="Sprint ID")
@click.option("--goal", required=True, help="Sprint goal")
def run(sprint: str, goal: str):
    """Run a quality mission."""
    click.echo(f"Starting mission for {sprint}: {goal}")
    # Implementation here

@main.command()
def agents():
    """List all available agents."""
    from metanoia_qa.agents import AgentType
    for agent in AgentType:
        click.echo(f"  - {agent.name}")

if __name__ == "__main__":
    main()
