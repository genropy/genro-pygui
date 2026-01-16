# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""CLI for running BagApp applications.

Usage:
    bagapp run mymodule:MyApp --name myapp
    bagapp list
    bagapp connect myapp
"""

from __future__ import annotations

import argparse
import importlib
import sys

from genro_pygui.registry import (
    find_free_port,
    get_port,
    list_apps,
    register_app,
    unregister_app,
)


def run_app(module_class: str, name: str | None = None) -> None:
    """Run a BagApp from module:class specification."""
    # Add current directory to path for local imports
    import os

    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    module_path, class_name = module_class.split(":")
    module = importlib.import_module(module_path)
    app_class = getattr(module, class_name)

    port = find_free_port()
    app_name = name or class_name.lower()

    register_app(app_name, port)
    print(f"Starting {app_name} on port {port}")

    try:
        app = app_class(remote_port=port)
        app.run()
    finally:
        unregister_app(app_name)


def list_running() -> None:
    """List all registered apps."""
    apps = list_apps()
    if not apps:
        print("No apps registered")
        return
    for app_name, port in apps.items():
        print(f"  {app_name}: port {port}")


def connect_repl(name: str) -> None:
    """Start a REPL connected to an app."""
    port = get_port(name)
    if port is None:
        print(f"App '{name}' not found")
        sys.exit(1)

    from genro_pygui.remote import connect

    app = connect(port=port)
    print(f"Connected to {name} on port {port}")
    print("Use 'app.page.static(\"text\")' to add widgets")
    print("Type 'exit()' to quit")

    import code

    code.interact(local={"app": app})


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(prog="bagapp", description="BagApp CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    run_parser = subparsers.add_parser("run", help="Run a BagApp")
    run_parser.add_argument("module_class", help="module:ClassName")
    run_parser.add_argument("--name", "-n", help="App name for registry")

    # list command
    subparsers.add_parser("list", help="List running apps")

    # connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to an app")
    connect_parser.add_argument("name", help="App name")

    args = parser.parse_args()

    if args.command == "run":
        run_app(args.module_class, args.name)
    elif args.command == "list":
        list_running()
    elif args.command == "connect":
        connect_repl(args.name)


if __name__ == "__main__":
    main()
