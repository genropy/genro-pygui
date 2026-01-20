# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Button variants example.

Run with:
    PYTHONPATH=src python examples/basic/button_variants.py

Shows all Button variants: default, primary, success, warning, error.
"""

from __future__ import annotations

from textual.widgets import Button

from genro_pygui import BagApp


class ButtonVariantsApp(BagApp):
    """Display all button variants."""

    def build(self) -> None:
        self.page.static("Button Variants")
        self.page.button("Default", id="btn_default")
        self.page.button("Primary", id="btn_primary", variant="primary")
        self.page.button("Success", id="btn_success", variant="success")
        self.page.button("Warning", id="btn_warning", variant="warning")
        self.page.button("Error", id="btn_error", variant="error")
        self.page.static("")
        self.page.static("Click a button or press 'q' to quit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.page.static(f"Pressed: {event.button.label}")


if __name__ == "__main__":
    ButtonVariantsApp().run()
