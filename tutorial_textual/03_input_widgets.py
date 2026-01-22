"""
Tutorial Textual #03 - Input Widgets

Widget per l'inserimento di testo.
Concetti: Input, TextArea, placeholder, password, eventi Changed/Submitted

Esegui con: python 03_input_widgets.py
"""

from textual.app import App
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input, TextArea, Label


class InputWidgetsApp(App):
    """Dimostra i widget di input."""

    CSS = """
    Vertical { padding: 1; }
    Label { margin-bottom: 0; color: $text-muted; }
    Input { margin-bottom: 1; }
    TextArea { height: 8; margin-bottom: 1; }
    #output { background: $surface; padding: 1; border: solid $primary; }
    """

    def compose(self):
        with Vertical():
            yield Static("INPUT WIDGETS DEMO", id="title")

            # Input base
            yield Label("Input semplice:")
            yield Input(placeholder="Scrivi qualcosa...", id="simple")

            # Input con max_length
            yield Label("Input con limite (max 10 caratteri):")
            yield Input(placeholder="Max 10 chars", max_length=10, id="limited")

            # Input password
            yield Label("Input password (testo nascosto):")
            yield Input(placeholder="Password", password=True, id="password")

            # Input numerico
            yield Label("Input numerico (solo numeri):")
            yield Input(placeholder="123", type="integer", id="numeric")

            # TextArea multi-riga
            yield Label("TextArea (multi-riga):")
            yield TextArea(id="textarea")

            # Output per mostrare gli eventi
            yield Static("Eventi appariranno qui...", id="output")

    def on_input_changed(self, event: Input.Changed):
        """Chiamato quando il testo in un Input cambia."""
        output = self.query_one("#output", Static)
        output.update(f"Changed [{event.input.id}]: {event.value}")

    def on_input_submitted(self, event: Input.Submitted):
        """Chiamato quando si preme Enter in un Input."""
        output = self.query_one("#output", Static)
        output.update(f"Submitted [{event.input.id}]: {event.value}")


if __name__ == "__main__":
    app = InputWidgetsApp()
    app.run()
