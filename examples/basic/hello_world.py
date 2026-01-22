# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Minimal TextualApp example.

Run with:
    python -m genro_pygui.cli run examples/basic/hello_world.py
"""

from genro_pygui import TextualApp


class Main(TextualApp):
    """Minimal TextualApp showing basic usage."""

    def main(self, root):
        root.static("Hello, Textual!")
        root.static("Press 'q' to quit")
