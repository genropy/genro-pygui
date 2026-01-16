# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Interactive BagApp with CLI control.

Run in one terminal:
    bagapp run examples.interactive_app:InteractiveApp --name demo

In another terminal:
    bagapp connect demo

Then in the REPL:
    >>> app.page.static("Hello from CLI!")
"""

from __future__ import annotations

from genro_pygui import BagApp


class InteractiveApp(BagApp):
    """BagApp controllabile via bagapp CLI."""

    def build(self) -> None:
        self.page.static("Interactive BagApp")
        self.page.static("Usa 'bagapp connect <name>' per aggiungere widget")
        self.page.static("Premi 'q' per uscire")


if __name__ == "__main__":
    InteractiveApp(remote_port=9999).run()
