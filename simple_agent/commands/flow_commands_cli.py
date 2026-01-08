"""Click CLI wrapper for flow orchestration commands."""

import click

from simple_agent.commands.flow_commands import FlowCommands


@click.group()
@click.pass_context
def flow(context: click.Context) -> None:
    """Manage and execute multi-agent orchestration flows. (list,show, run, debug, debug)"""
    # Ensure FlowCommands is initialized
    if "flow_manager" not in context.obj:
        raise click.ClickException("FlowManager not initialized")

    # Create FlowCommands instance with flow manager from context
    context.ensure_object(dict)
    context.obj["flow_commands"] = FlowCommands(
        flow_manager=context.obj["flow_manager"]
    )


@flow.command("list")
@click.pass_context
def list_flows(context: click.Context) -> None:
    """List all available flows."""
    flow_commands = context.obj["flow_commands"]
    output = flow_commands.list_flows()
    click.echo(output)


@flow.command("show")
@click.argument("flow_name")
@click.pass_context
def show_flow(context: click.Context, flow_name: str) -> None:
    """Display flow definition.

    Args:
        flow_name: Name of the flow to display
    """
    flow_commands = context.obj["flow_commands"]
    try:
        output = flow_commands.show_flow(flow_name)
        click.echo(output)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))


@flow.command("run")
@click.argument("flow_name")
@click.argument("user_input")
@click.pass_context
def run_flow(context: click.Context, flow_name: str, user_input: str) -> None:
    """Execute a flow with input.

    Args:
        flow_name: Name of the flow to execute
        user_input: Input for the orchestrator
    """
    flow_commands = context.obj["flow_commands"]
    try:
        output = flow_commands.run_flow(flow_name, user_input)
        click.echo(output)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Error running flow: {str(e)}")


@flow.command("debug")
@click.argument("flow_name")
@click.argument("user_input")
@click.pass_context
def debug_flow(context: click.Context, flow_name: str, user_input: str) -> None:
    """Run flow in debug mode with detailed output.

    Args:
        flow_name: Name of the flow to debug
        user_input: Input for the orchestrator
    """
    flow_commands = context.obj["flow_commands"]
    try:
        output = flow_commands.debug_flow(flow_name, user_input)
        click.echo(output)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Error debugging flow: {str(e)}")


@flow.command("delete")
@click.argument("flow_name")
@click.confirmation_option(prompt="Are you sure you want to delete this flow?")
@click.pass_context
def delete_flow(context: click.Context, flow_name: str) -> None:
    """Delete a flow file.

    Args:
        flow_name: Name of the flow to delete
    """
    flow_commands = context.obj["flow_commands"]
    try:
        output = flow_commands.delete_flow(flow_name)
        click.echo(output)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
