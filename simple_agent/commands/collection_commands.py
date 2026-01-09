"""REPL commands for RAG collection management."""

import click
import logging
from rich.console import Console
from rich.table import Table

from simple_agent.rag.collection_manager import CollectionManager

logger = logging.getLogger(__name__)


def get_collection_manager(ctx) -> CollectionManager:
    """
    Get collection manager, initializing lazily if needed.
    
    Args:
        ctx: Click context
        
    Returns:
        CollectionManager instance
    """
    collection_manager = ctx.obj.get("collection_manager")
    
    # Lazy initialization on first access
    if collection_manager is None:
        logger.info("Lazy loading RAG collection manager")
        collections_dir = ctx.obj.get("collections_dir", "./chroma_db")
        collection_manager = CollectionManager(collections_dir)
        ctx.obj["collection_manager"] = collection_manager
    
    return collection_manager


@click.group()
@click.pass_context
def collection(ctx):
    """Manage RAG collections."""
    pass


@collection.command()
@click.argument("name")
@click.option("--path", default=None, help="Path to documents directory")
@click.option("--embedding-model", default="text-embedding-ada-002", help="Embedding model")
@click.option("--chunk-size", default=1000, type=int, help="Chunk size in characters")
@click.option("--chunk-overlap", default=200, type=int, help="Chunk overlap in characters")
@click.pass_context
def create(ctx, name: str, path: str, embedding_model: str, chunk_size: int, chunk_overlap: int):
    """Create a new collection."""
    console: Console = ctx.obj["console"]
    collection_manager = get_collection_manager(ctx)

    try:
        collection_manager.create_collection(
            name=name,
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            path=path,
        )
        console.print(f"[green]✓[/green] Created collection: {name}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@collection.command(name="list")
@click.pass_context
def list_collections(ctx):
    """List all collections."""
    console: Console = ctx.obj["console"]
    collection_manager = get_collection_manager(ctx)

    collections = collection_manager.list_collections()

    if not collections:
        console.print("[dim]No collections found.[/dim]")
        return

    table = Table(title="RAG Collections")
    table.add_column("Name", style="cyan")
    table.add_column("Embedding Model", style="green")
    table.add_column("Chunk Size", style="yellow")
    table.add_column("Document Count", style="magenta")

    for col in collections:
        table.add_row(
            col["name"],
            col.get("embedding_model", "N/A"),
            str(col.get("chunk_size", "N/A")),
            str(col.get("document_count", 0)),
        )

    console.print(table)


@collection.command()
@click.argument("name")
@click.pass_context
def info(ctx, name: str):
    """Show collection information."""
    console: Console = ctx.obj["console"]
    collection_manager = get_collection_manager(ctx)

    try:
        col = collection_manager.get_collection(name)
        stats = col.get_stats()

        console.print(f"\n[bold cyan]Collection: {name}[/bold cyan]")
        console.print(f"  Embedding Model: {stats.get('embedding_model')}")
        console.print(f"  Chunk Size: {stats.get('chunk_size')} characters")
        console.print(f"  Chunk Overlap: {stats.get('chunk_overlap')} characters")
        console.print(f"  Documents: {stats.get('document_count')}")
        console.print(f"  Created: {stats.get('created_timestamp')}")
        console.print(f"  Last Indexed: {stats.get('last_indexed') or 'Never'}")
        console.print()

    except KeyError:
        console.print(f"[red]Error:[/red] Collection '{name}' not found")


@collection.command()
@click.argument("name")
@click.pass_context
def delete(ctx, name: str):
    """Delete a collection."""
    console: Console = ctx.obj["console"]
    collection_manager = get_collection_manager(ctx)

    try:
        collection_manager.delete_collection(name)
        console.print(f"[green]✓[/green] Deleted collection: {name}")
    except KeyError:
        console.print(f"[red]Error:[/red] Collection '{name}' not found")


@collection.command()
@click.argument("agent_name")
@click.argument("collection_name")
@click.pass_context
def connect(ctx, agent_name: str, collection_name: str):
    """Connect agent to a collection."""
    console: Console = ctx.obj["console"]
    collection_manager = get_collection_manager(ctx)

    try:
        collection_manager.connect_agent(agent_name, collection_name)
        console.print(f"[green]✓[/green] Connected {agent_name} to {collection_name}")
    except KeyError as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@collection.command()
@click.argument("agent_name")
@click.pass_context
def disconnect(ctx, agent_name: str):
    """Disconnect agent from collection."""
    console: Console = ctx.obj["console"]
    collection_manager = get_collection_manager(ctx)

    collection_manager.disconnect_agent(agent_name)
    console.print(f"[green]✓[/green] Disconnected {agent_name} from collection")
