# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Showcase: all examples in a TabbedContent.

Run with:
    PYTHONPATH=src python examples/showcase.py
"""

from __future__ import annotations

from genro_pygui import BagApp


class ShowcaseApp(BagApp):
    """All examples in tabs."""

    def build(self) -> None:
        with self.page.tabbedcontent(id="examples"):
            with self.page.tabpane("Hello World", id="tab-hello"):
                self.page.static("Hello, Textual!")
                self.page.static("Press 'q' to quit")

            with self.page.tabpane("Colors", id="tab-colors"):
                for color in ["red", "orange", "yellow", "green", "blue", "purple"]:
                    self.page.static(f"  {color.upper()}  ", classes=f"stripe-{color}")

            with self.page.tabpane("Buttons", id="tab-buttons"):
                self.page.static("Button Variants")
                self.page.button("Default", id="btn_default")
                self.page.button("Primary", id="btn_primary", variant="primary")
                self.page.button("Success", id="btn_success", variant="success")
                self.page.button("Warning", id="btn_warning", variant="warning")
                self.page.button("Error", id="btn_error", variant="error")

            with self.page.tabpane("Form", id="tab-form"):
                self.page.static("User Registration")
                self.page.input(placeholder="First Name", id="first_name")
                self.page.input(placeholder="Last Name", id="last_name")
                self.page.input(placeholder="Email", id="email")

    CSS = """
    .stripe-red { background: red; }
    .stripe-orange { background: orange; }
    .stripe-yellow { background: yellow; color: black; }
    .stripe-green { background: green; }
    .stripe-blue { background: blue; }
    .stripe-purple { background: purple; }
    """


if __name__ == "__main__":
    ShowcaseApp().run()
