# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Remote control for BagApp.

Server side (in BagApp):
    app.enable_remote(port=9999)

Client side:
    from genro_pygui.remote import connect
    app = connect()
    app.page.static("Hello!")
"""

from __future__ import annotations

import pickle
import socket
import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from genro_pygui.textual_app import TextualApp


class RemoteProxy:
    """Proxy that sends method calls to remote BagApp."""

    def __init__(self, host: str = "localhost", port: int = 9999) -> None:
        self._host = host
        self._port = port

    def _send(self, cmd: str) -> Any:
        """Send command and receive result."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._host, self._port))
        sock.send(cmd.encode())
        data = sock.recv(65536)
        sock.close()
        if data:
            return pickle.loads(data)  # noqa: S301
        return None

    @property
    def page(self) -> PageProxy:
        """Return proxy for page Bag."""
        return PageProxy(self)


class PageProxy:
    """Proxy for page Bag - forwards all method calls."""

    def __init__(self, remote: RemoteProxy) -> None:
        self._remote = remote

    def __getattr__(self, name: str) -> Any:
        """Forward method calls to remote page."""

        def method(*args: Any, **kwargs: Any) -> Any:
            cmd = f"__call__:{name}:{pickle.dumps((args, kwargs)).hex()}"
            return self._remote._send(cmd)

        return method

    def keys(self) -> list[str]:
        """Get keys from remote Bag."""
        return self._remote._send("__keys__")

    def __getitem__(self, key: str) -> Any:
        """Get item from remote Bag."""
        cmd = f"__getitem__:{key}"
        return self._remote._send(cmd)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item on remote Bag."""
        cmd = f"__setitem__:{key}:{pickle.dumps(value).hex()}"
        self._remote._send(cmd)


def connect(
    name: str | None = None, host: str = "localhost", port: int | None = None
) -> RemoteProxy:
    """Connect to a remote BagApp by name or port."""
    if name is not None:
        from genro_pygui.registry import get_port

        found_port = get_port(name)
        if found_port is None:
            raise ValueError(f"App '{name}' not found in registry")
        port = found_port
    elif port is None:
        port = 9999
    return RemoteProxy(host, port)


class RemoteServer:
    """Server that receives commands for TextualApp."""

    def __init__(self, app: TextualApp, port: int = 9999) -> None:
        self._app = app
        self._port = port
        self._thread: threading.Thread | None = None
        self._running = False

    def start(self) -> None:
        """Start the server in a background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the server."""
        self._running = False

    def _run(self) -> None:
        """Run the socket server."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", self._port))
        server.listen(1)
        server.settimeout(1.0)

        while self._running:
            try:
                conn, _ = server.accept()
                data = conn.recv(65536).decode()
                if data:
                    result = self._handle_command(data)
                    conn.send(pickle.dumps(result))
                conn.close()
            except socket.timeout:
                continue
            except Exception:
                break

        server.close()

    def _handle_command(self, cmd: str) -> Any:
        """Handle incoming command."""
        if cmd == "__keys__":
            return list(self._app.page.keys())

        if cmd.startswith("__getitem__:"):
            key = cmd.split(":", 1)[1]
            return self._app.page[key]

        if cmd.startswith("__setitem__:"):
            _, key, value_hex = cmd.split(":", 2)
            value = pickle.loads(bytes.fromhex(value_hex))  # noqa: S301

            def do_set() -> None:
                self._app.page[key] = value

            self._app._safe_call(do_set)
            return "ok"

        if cmd.startswith("__call__:"):
            _, method_name, args_hex = cmd.split(":", 2)
            args, kwargs = pickle.loads(bytes.fromhex(args_hex))  # noqa: S301

            def do_call() -> Any:
                method = getattr(self._app.page, method_name)
                return method(*args, **kwargs)

            self._app._safe_call(do_call)
            return "ok"

        return None
