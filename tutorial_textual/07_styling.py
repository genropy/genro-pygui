"""
Tutorial Textual #07 - Styling con CSS

Styling dell'interfaccia con Textual CSS.
Concetti: CSS inline, selettori, colori, dimensioni, pseudo-classi

Esegui con: python 07_styling.py
"""

from textual.app import App
from textual.containers import Vertical, Horizontal, Grid
from textual.widgets import Static, Button, Input


class StylingApp(App):
    """Dimostra le varie opzioni di styling CSS."""

    # CSS definito come stringa nella classe
    CSS = """
    /* ===== SELETTORI ===== */

    /* Type selector - tutti i widget di questo tipo */
    Static {
        padding: 1;
    }

    /* ID selector - widget specifico */
    #title {
        font-size: 200%;
        text-align: center;
        background: $primary;
        color: $text;
    }

    /* Class selector - widget con questa classe */
    .important {
        background: $warning;
        color: black;
    }

    .muted {
        color: $text-muted;
    }

    /* ===== COLORI ===== */

    #colors-section {
        border: solid $primary;
        margin: 1;
        padding: 1;
    }

    .color-named { background: crimson; }
    .color-hex { background: #3498db; }
    .color-rgb { background: rgb(46, 204, 113); }
    .color-var { background: $success; }

    /* ===== DIMENSIONI ===== */

    #sizes-section {
        border: solid $secondary;
        margin: 1;
        padding: 1;
        height: 12;
    }

    .size-fixed { width: 20; }      /* 20 caratteri */
    .size-percent { width: 50%; }   /* 50% del parent */
    .size-fr { width: 1fr; }        /* frazione disponibile */

    /* ===== BOX MODEL ===== */

    #box-section {
        border: solid $accent;
        margin: 1;
        padding: 1;
    }

    .box-demo {
        margin: 1;           /* spazio esterno */
        padding: 2;          /* spazio interno */
        border: heavy white; /* bordo */
        background: $surface;
    }

    /* ===== PSEUDO-CLASSI ===== */

    #pseudo-section {
        margin: 1;
        padding: 1;
    }

    /* Stile quando il widget ha il focus */
    Input:focus {
        border: heavy $primary;
    }

    /* Stile quando il mouse è sopra */
    .hoverable:hover {
        background: $primary;
    }

    /* Button disabilitato */
    Button:disabled {
        opacity: 50%;
    }

    /* ===== LAYOUT ===== */

    Horizontal {
        height: auto;
    }

    /* Grid layout */
    #grid-demo {
        grid-size: 3;        /* 3 colonne */
        grid-gutter: 1;      /* spazio tra celle */
        height: 8;
        margin: 1;
    }

    .grid-cell {
        background: $surface;
        text-align: center;
        padding: 1;
    }
    """

    def compose(self):
        yield Static("TEXTUAL CSS STYLING", id="title")

        # Sezione colori
        with Vertical(id="colors-section"):
            yield Static("COLORI")
            with Horizontal():
                yield Static("named", classes="color-named")
                yield Static("#hex", classes="color-hex")
                yield Static("rgb()", classes="color-rgb")
                yield Static("$var", classes="color-var")

        # Sezione dimensioni
        with Vertical(id="sizes-section"):
            yield Static("DIMENSIONI")
            with Horizontal():
                yield Static("20 chars", classes="size-fixed")
                yield Static("50%", classes="size-percent")
                yield Static("1fr", classes="size-fr")

        # Sezione box model
        with Vertical(id="box-section"):
            yield Static("BOX MODEL")
            yield Static("margin + padding + border", classes="box-demo")

        # Sezione pseudo-classi
        with Vertical(id="pseudo-section"):
            yield Static("PSEUDO-CLASSI (prova hover e focus)")
            yield Static("Passa il mouse qui", classes="hoverable")
            yield Input(placeholder="Clicca per focus")
            with Horizontal():
                yield Button("Attivo")
                yield Button("Disabilitato", disabled=True)

        # Grid demo
        yield Static("GRID LAYOUT")
        with Grid(id="grid-demo"):
            yield Static("1", classes="grid-cell")
            yield Static("2", classes="grid-cell")
            yield Static("3", classes="grid-cell")
            yield Static("4", classes="grid-cell")
            yield Static("5", classes="grid-cell")
            yield Static("6", classes="grid-cell")


class ExternalCSSApp(App):
    """Esempio con CSS in file esterno."""

    # Carica CSS da file .tcss (Textual CSS)
    CSS_PATH = "07_styling.tcss"

    def compose(self):
        with Vertical():
            yield Static("APP CON CSS ESTERNO", id="title")
            yield Static("Il CSS è in 07_styling.tcss")
            yield Button("Un button", variant="primary")


# CSS che può essere salvato come 07_styling.tcss
EXTERNAL_CSS = """
#title {
    font-size: 200%;
    text-align: center;
    background: $primary;
    padding: 2;
}

Static {
    margin: 1;
}
"""


if __name__ == "__main__":
    # Per testare ExternalCSSApp, prima salva EXTERNAL_CSS in 07_styling.tcss
    app = StylingApp()
    app.run()
