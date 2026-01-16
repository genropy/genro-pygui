# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Test: Button che aggiunge widget dinamicamente.

Esegui con:
    PYTHONPATH=src:. python examples/button_test.py

Premi il bottone "Aggiungi" per aggiungere uno Static.
Se funziona qui ma non via remote, il problema è nel remote.
"""

from __future__ import annotations

from textual.widgets import Button

from genro_pygui import BagApp


class ButtonTestApp(BagApp):
    """Test app con bottone che aggiunge widget."""

    BINDINGS = [("q", "quit", "Esci")]

    def build(self) -> None:
        self.page.static("Premi il bottone per aggiungere widget")
        self.page.static("Premi 'q' per uscire")

    def compose(self):
        yield Button("Aggiungi Static", id="add_btn")
        yield from super().compose()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_btn":
            count = len(list(self.page.keys()))
            self.page.static(f"Widget aggiunto #{count + 1}")


if __name__ == "__main__":
    ButtonTestApp().run()
