# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Example with nested containers.

Run with CLI:
    textual run examples/basic/nested_containers.py
"""

from genro_pygui import TextualApp


class Application(TextualApp):
    """App with nested containers."""

    def main(self, root):
        root.static("Main Title")

        box = root.container()
        box.static("Inside container")
        box.button("Click me", variant="primary")
