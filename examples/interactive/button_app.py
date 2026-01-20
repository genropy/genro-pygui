# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Button that adds widgets dynamically.

Run with:
    PYTHONPATH=src python examples/interactive/button_app.py

Press the button to add a new Static widget.
"""

from __future__ import annotations

from textual.widgets import Button

from genro_pygui import BagApp


class ButtonApp(BagApp):
    """App with button that adds widgets dynamically."""

    BINDINGS = [("q", "quit", "Quit")]

    def build(self) -> None:
        self.page.static("Press the button to add widgets")
        self.page.static("Press 'q' to quit")

    def compose(self):
        yield Button("Add Static", id="add_btn")
        yield from super().compose()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_btn":
            count = len(list(self.page.keys()))
            self.page.static(f"Widget #{count + 1}")


if __name__ == "__main__":
    ButtonApp().run()
