"""
Tutorial Textual #01 - Hello World

L'app Textual più semplice possibile.
Concetti: App, compose(), Static, run()

Esegui con: python 01_hello_world.py
Esci con: Ctrl+C o Q
"""

from textual.app import App
from textual.widgets import Static


class HelloWorldApp(App):
    """App minima che mostra un messaggio."""

    BINDINGS = [("q", "quit", "Esci")]

    def compose(self):
        """Genera i widget dell'interfaccia."""
        yield Static("Hello, Textual!")
        yield Static("Premi Q per uscire")


if __name__ == "__main__":
    app = HelloWorldApp()
    app.run()
