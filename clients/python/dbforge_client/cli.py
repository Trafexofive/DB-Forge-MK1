"""Command-line interface for DB-Forge client."""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

from . import DBForgeClient
from .exceptions import DBForgeError


def format_output(data: Any, format_type: str = "json") -> str:
    """Format output data."""
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "table" and isinstance(data, list):
        # Simple table format for list of dicts
        if not data:
            return "No data"
        
        if isinstance(data[0], dict):
            headers = list(data[0].keys())
            lines = []
            lines.append(" | ".join(headers))
            lines.append("-" * len(lines[0]))
            for row in data:
                lines.append(" | ".join(str(row.get(h, "")) for h in headers))
            return "\n".join(lines)
    
    return str(data)


def create_client(args: argparse.Namespace) -> DBForgeClient:
    """Create DB-Forge client from CLI arguments."""
    return DBForgeClient(
        base_url=args.base_url,
        api_key=args.api_key,
        timeout=args.timeout,
    )


def cmd_spawn(args: argparse.Namespace) -> None:
    """Spawn database command."""
    client = create_client(args)
    try:
        result = client.spawn_database(args.name)
        print(format_output(result, args.format))
    except DBForgeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_prune(args: argparse.Namespace) -> None:
    """Prune database command."""
    client = create_client(args)
    try:
        result = client.prune_database(args.name)
        print(format_output(result, args.format))
    except DBForgeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    """List databases command."""
    client = create_client(args)
    try:
        result = client.list_databases()
        print(format_output(result, args.format))
    except DBForgeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_query(args: argparse.Namespace) -> None:
    """Execute query command."""
    client = create_client(args)
    try:
        db = client.get_database(args.database)
        result = db.execute_query(args.sql, args.params)
        print(format_output(result, args.format))
    except DBForgeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_create_table(args: argparse.Namespace) -> None:
    """Create table command."""
    client = create_client(args)
    try:
        # Parse columns from JSON string or file
        if args.columns.startswith("@"):
            with open(args.columns[1:], "r") as f:
                columns = json.load(f)
        else:
            columns = json.loads(args.columns)
        
        db = client.get_database(args.database)
        result = db.create_table(args.table, columns)
        print(format_output(result, args.format))
    except (DBForgeError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_insert(args: argparse.Namespace) -> None:
    """Insert rows command."""
    client = create_client(args)
    try:
        # Parse rows from JSON string or file
        if args.rows.startswith("@"):
            with open(args.rows[1:], "r") as f:
                rows = json.load(f)
        else:
            rows = json.loads(args.rows)
        
        db = client.get_database(args.database)
        result = db.insert_rows(args.table, rows)
        print(format_output(result, args.format))
    except (DBForgeError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_select(args: argparse.Namespace) -> None:
    """Select rows command."""
    client = create_client(args)
    try:
        filters = {}
        if args.filters:
            if args.filters.startswith("@"):
                with open(args.filters[1:], "r") as f:
                    filters = json.load(f)
            else:
                filters = json.loads(args.filters)
        
        db = client.get_database(args.database)
        result = db.select_rows(args.table, filters)
        print(format_output(result, args.format))
    except (DBForgeError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DB-Forge Command Line Interface",
        prog="dbforge"
    )
    
    # Global options
    parser.add_argument(
        "--base-url",
        default=os.getenv("DBFORGE_BASE_URL", "http://db.localhost"),
        help="DB-Forge server base URL"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("DBFORGE_API_KEY"),
        help="API key for authentication"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds"
    )
    parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Admin commands
    spawn_parser = subparsers.add_parser("spawn", help="Spawn a database")
    spawn_parser.add_argument("name", help="Database name")
    spawn_parser.set_defaults(func=cmd_spawn)
    
    prune_parser = subparsers.add_parser("prune", help="Prune a database")
    prune_parser.add_argument("name", help="Database name")
    prune_parser.set_defaults(func=cmd_prune)
    
    list_parser = subparsers.add_parser("list", help="List databases")
    list_parser.set_defaults(func=cmd_list)
    
    # Query commands
    query_parser = subparsers.add_parser("query", help="Execute SQL query")
    query_parser.add_argument("database", help="Database name")
    query_parser.add_argument("sql", help="SQL query")
    query_parser.add_argument("params", nargs="*", help="Query parameters")
    query_parser.set_defaults(func=cmd_query)
    
    # Table commands
    create_table_parser = subparsers.add_parser("create-table", help="Create table")
    create_table_parser.add_argument("database", help="Database name")
    create_table_parser.add_argument("table", help="Table name")
    create_table_parser.add_argument("columns", help="Columns definition (JSON string or @file)")
    create_table_parser.set_defaults(func=cmd_create_table)
    
    insert_parser = subparsers.add_parser("insert", help="Insert rows")
    insert_parser.add_argument("database", help="Database name")
    insert_parser.add_argument("table", help="Table name")
    insert_parser.add_argument("rows", help="Rows data (JSON string or @file)")
    insert_parser.set_defaults(func=cmd_insert)
    
    select_parser = subparsers.add_parser("select", help="Select rows")
    select_parser.add_argument("database", help="Database name")
    select_parser.add_argument("table", help="Table name")
    select_parser.add_argument("--filters", help="Filter conditions (JSON string or @file)")
    select_parser.set_defaults(func=cmd_select)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()