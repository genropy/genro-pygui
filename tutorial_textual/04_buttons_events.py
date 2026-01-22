"""
Tutorial Textual #04 - Buttons e Eventi

Gestione dei button e del sistema di eventi.
Concetti: Button, varianti, on_button_pressed, decoratore @on, Message custom

Esegui con: python 04_buttons_events.py
"""

from textual.app import App
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button
from textual.on import on


class ButtonsEventsApp(App):
    """Dimostra button e gestione eventi."""

    CSS = """
    Vertical { padding: 1; }
    Horizontal { height: auto; margin-bottom: 1; }
    Button { margin-right: 1; }
    #counter { font-size: 200%; text-align: center; padding: 2; }
    #log { background: $surface; padding: 1; height: 10; border: solid $primary; }
    """

    def __init__(self):
        super().__init__()
        self.counter = 0

    def compose(self):
        with Vertical():
            yield Static("BUTTONS & EVENTS DEMO", id="title")

            # Contatore
            yield Static("0", id="counter")

            # Button base - gestiti da on_button_pressed generico
            with Horizontal():
                yield Button("+1", id="increment")
                yield Button("-1", id="decrement")
                yield Button("Reset", id="reset", variant="warning")

            # Button con varianti di stile
            yield Static("Varianti di stile:")
            with Horizontal():
                yield Button("Default", id="default")
                yield Button("Primary", id="primary", variant="primary")
                yield Button("Success", id="success", variant="success")
                yield Button("Warning", id="warning", variant="warning")
                yield Button("Error", id="error", variant="error")

            # Log eventi
            yield Static("Log eventi:", id="log-label")
            yield Static("", id="log")

    def on_button_pressed(self, event: Button.Pressed):
        """Handler generico per tutti i button."""
        button_id = event.button.id
        log = self.query_one("#log", Static)

        if button_id == "increment":
            self.counter += 1
            self.update_counter()
            log.update(f"Incrementato a {self.counter}")

        elif button_id == "decrement":
            self.counter -= 1
            self.update_counter()
            log.update(f"Decrementato a {self.counter}")

        elif button_id == "reset":
            self.counter = 0
            self.update_counter()
            log.update("Counter resettato")

        else:
            # Per i button delle varianti, mostra solo il log
            log.update(f"Premuto button: {button_id} (variant: {event.button.variant})")

    def update_counter(self):
        """Aggiorna il display del contatore."""
        counter_display = self.query_one("#counter", Static)
        counter_display.update(str(self.counter))


class TargetedEventsApp(App):
    """Esempio con decoratore @on per eventi mirati."""

    CSS = """
    Vertical { padding: 1; }
    Horizontal { height: auto; }
    Button { margin: 1; }
    #status { padding: 1; background: $surface; }
    """

    def compose(self):
        with Vertical():
            yield Static("TARGETED EVENTS con @on")
            with Horizontal():
                yield Button("Salva", id="save", variant="success")
                yield Button("Annulla", id="cancel", variant="error")
                yield Button("Altro", id="other")
            yield Static("Premi un button...", id="status")

    @on(Button.Pressed, "#save")
    def handle_save(self):
        """Gestisce SOLO il button #save."""
        self.query_one("#status", Static).update("Salvato!")

    @on(Button.Pressed, "#cancel")
    def handle_cancel(self):
        """Gestisce SOLO il button #cancel."""
        self.query_one("#status", Static).update("Annullato!")

    # Il button "other" non ha handler specifico, quindi non fa nulla


if __name__ == "__main__":
    # Prova ButtonsEventsApp per l'esempio completo
    # Oppure TargetedEventsApp per vedere @on in azione
    app = ButtonsEventsApp()
    app.run()
