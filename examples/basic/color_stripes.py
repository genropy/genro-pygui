# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Colored stripes example (inspired by Textual Pride app).

Run with:
    PYTHONPATH=src python examples/basic/color_stripes.py

Shows how to create multiple Static widgets with different colors.
"""

from __future__ import annotations

from genro_pygui import BagApp


class ColorStripesApp(BagApp):
    """Display colored stripes using Static widgets."""

    COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]

    def build(self) -> None:
        for i, color in enumerate(self.COLORS):
            self.page.static(f"  {color.upper()}  ", classes=f"stripe-{i}")

    CSS = """
    Static {
        text-align: center;
        text-style: bold;
        height: 1fr;
    }
    .stripe-0 { background: red; }
    .stripe-1 { background: orange; }
    .stripe-2 { background: yellow; color: black; }
    .stripe-3 { background: green; }
    .stripe-4 { background: blue; }
    .stripe-5 { background: purple; }
    """


if __name__ == "__main__":
    ColorStripesApp().run()
