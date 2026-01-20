# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Simple input form example.

Run with:
    PYTHONPATH=src python examples/basic/input_form.py

Shows Input widgets with placeholders.
"""

from __future__ import annotations

from textual.widgets import Input

from genro_pygui import BagApp


class InputFormApp(BagApp):
    """Simple form with input fields."""

    def build(self) -> None:
        self.page.static("User Registration")
        self.page.input(placeholder="First Name", id="first_name")
        self.page.input(placeholder="Last Name", id="last_name")
        self.page.input(placeholder="Email", id="email")
        self.page.static("Press Tab to move between fields, q to quit")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.page.static(f"Submitted: {event.input.id} = {event.value}")


if __name__ == "__main__":
    InputFormApp().run()
