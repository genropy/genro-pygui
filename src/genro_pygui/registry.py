# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""App registry for name-based connection.

Stores mapping of app names to ports in a JSON file.
"""

from __future__ import annotations

import json
import socket
from pathlib import Path

REGISTRY_FILE = Path("/tmp/bagapp_registry.json")


def find_free_port() -> int:
    """Find a free port on localhost."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def register_app(name: str, port: int) -> None:
    """Register an app name with its port."""
    registry = load_registry()
    registry[name] = port
    save_registry(registry)


def unregister_app(name: str) -> None:
    """Remove an app from the registry."""
    registry = load_registry()
    registry.pop(name, None)
    save_registry(registry)


def get_port(name: str) -> int | None:
    """Get port for an app name."""
    registry = load_registry()
    return registry.get(name)


def load_registry() -> dict[str, int]:
    """Load registry from file."""
    if not REGISTRY_FILE.exists():
        return {}
    try:
        return json.loads(REGISTRY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_registry(registry: dict[str, int]) -> None:
    """Save registry to file."""
    REGISTRY_FILE.write_text(json.dumps(registry))


def list_apps() -> dict[str, int]:
    """List all registered apps."""
    return load_registry()
