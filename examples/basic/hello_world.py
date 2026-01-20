# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Minimal BagApp example.

Run with:
    PYTHONPATH=src python examples/basic/hello_world.py
"""

from __future__ import annotations

from genro_pygui import BagApp


class HelloApp(BagApp):
    """Minimal BagApp showing basic usage."""

    def build(self) -> None:
        self.page.static("Hello, Textual!")
        self.page.static("Press 'q' to quit")


if __name__ == "__main__":
    HelloApp().run()
