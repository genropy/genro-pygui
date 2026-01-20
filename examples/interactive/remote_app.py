# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""BagApp controllable via CLI.

Run in one terminal:
    PYTHONPATH=src python -m genro_pygui.cli run examples.interactive.remote_app:RemoteApp --name demo

In another terminal:
    PYTHONPATH=src python -m genro_pygui.cli connect demo

Then in the REPL:
    >>> app.page.static("Hello from CLI!")
    >>> app.page.button("Click me", id="btn1")
"""

from __future__ import annotations

from genro_pygui import BagApp


class RemoteApp(BagApp):
    """BagApp controllable via bagapp CLI."""

    def build(self) -> None:
        self.page.static("Remote BagApp")
        self.page.static("Use 'bagapp connect <name>' to add widgets")
        self.page.static("Press 'q' to quit")


if __name__ == "__main__":
    RemoteApp(remote_port=9999).run()
