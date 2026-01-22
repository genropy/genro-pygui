si"""
Tutorial Textual #02 - Containers

I container organizzano i widget nel layout.
Concetti: Vertical, Horizontal, Grid, nesting

Esegui con: python 02_containers.py
"""

from textual.app import App
from textual.containers import Vertical, Horizontal, Grid
from textual.widgets import Static, Button


class ContainersApp(App):
    """Dimostra i principali container di layout."""

    BINDINGS = [("q", "quit", "Esci")]

    CSS = """
    /* Stile per vedere i confini dei container */
    Vertical { border: solid green; padding: 1; }
    Horizontal { border: solid blue; padding: 1; }
    Grid { border: solid red; padding: 1; }
    Static { background: $surface; padding: 1; }
    """

    def compose(self):
        # Vertical: widget impilati dall'alto al basso
        with Vertical():
            yield Static("VERTICAL - I widget sono impilati verticalmente")
            yield Static("Primo elemento")
            yield Static("Secondo elemento")
            yield Static("Terzo elemento")

        # Horizontal: widget affiancati da sinistra a destra
        with Horizontal():
            yield Static("HORIZONTAL")
            yield Static("Uno")
            yield Static("Due")
            yield Static("Tre")

        # Nesting: container dentro container
        with Vertical():
            yield Static("NESTING - Container annidati")
            with Horizontal():
                yield Static("Sinistra")
                with Vertical():
                    yield Static("Centro Alto")
                    yield Static("Centro Basso")
                yield Static("Destra")

        yield Button("Esci", id="quit", variant="error")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "quit":
            self.exit()


class GridApp(App):
    """Esempio specifico di Grid layout."""

    CSS = """
    Grid {
        grid-size: 3 2;  /* 3 colonne, 2 righe */
        grid-gutter: 1;  /* spazio tra celle */
    }
    .cell { background: $primary; padding: 1; text-align: center; }
    """

    def compose(self):
        yield Static("Grid Layout 3x2:", classes="header")
        with Grid():
            yield Static("1,1", classes="cell")
            yield Static("1,2", classes="cell")
            yield Static("1,3", classes="cell")
            yield Static("2,1", classes="cell")
            yield Static("2,2", classes="cell")
            yield Static("2,3", classes="cell")


if __name__ == "__main__":
    # Prova ContainersApp per vedere Vertical/Horizontal/Nesting
    # Oppure GridApp per vedere il Grid layout
    app = ContainersApp()
    app.run()
