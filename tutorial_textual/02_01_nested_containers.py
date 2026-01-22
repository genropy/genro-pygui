"""
Tutorial Textual #02_01 - Nested Containers

Esempio di container annidati su più livelli.
Mostra come compose() gestisce la struttura ad albero.

Esegui con: python 02_01_nested_containers.py
"""

from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static


class NestedApp(App):
    """Container annidati su 3 livelli."""

    BINDINGS = [("q", "quit", "Esci")]

    CSS = """
    Vertical { border: solid green; padding: 1; margin: 1; }
    Horizontal { border: solid blue; padding: 1; margin: 1; }
    Static { background: $surface; padding: 1; }
    .level1 { border: solid yellow; }
    .level2 { border: solid cyan; }
    .level3 { border: solid magenta; }
    """

    def compose(self):
        # Livello 1: Vertical principale
        with Vertical(classes="level1"):
            yield Static("Livello 1 - Vertical principale")

            # Livello 2: due Horizontal affiancati concettualmente
            with Horizontal(classes="level2"):
                yield Static("L2 - Sinistra")

                # Livello 3: Vertical dentro Horizontal
                with Vertical(classes="level3"):
                    yield Static("L3 - Alto")
                    yield Static("L3 - Centro")
                    yield Static("L3 - Basso")

                yield Static("L2 - Destra")

            # Altro blocco livello 2
            with Horizontal(classes="level2"):
                with Vertical(classes="level3"):
                    yield Static("L3 - A")
                    yield Static("L3 - B")
                with Vertical(classes="level3"):
                    yield Static("L3 - C")
                    yield Static("L3 - D")

        yield Button("Esci", id="quit", variant="error")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "quit":
            self.exit()


if __name__ == "__main__":
    NestedApp().run()
