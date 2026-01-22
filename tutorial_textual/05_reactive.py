"""
Tutorial Textual #05 - Reactive Attributes

Attributi reattivi che aggiornano automaticamente l'UI.
Concetti: reactive(), watch_*(), validate_*(), auto-refresh

Esegui con: python 05_reactive.py
"""

from textual.app import App
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Button, Input
from textual.reactive import reactive


class ReactiveApp(App):
    """Dimostra gli attributi reattivi."""

    CSS = """
    Vertical { padding: 1; }
    Horizontal { height: auto; margin-bottom: 1; }
    Button { margin-right: 1; }
    #counter-display {
        font-size: 300%;
        text-align: center;
        padding: 2;
        background: $primary;
    }
    #log { background: $surface; padding: 1; height: 6; }
    """

    # Attributo reattivo - quando cambia, l'UI si aggiorna automaticamente
    counter = reactive(0)

    def compose(self):
        with Vertical():
            yield Static("REACTIVE ATTRIBUTES DEMO")

            # Display del counter - si aggiorna automaticamente
            yield Static("0", id="counter-display")

            with Horizontal():
                yield Button("+1", id="inc")
                yield Button("-1", id="dec")
                yield Button("+10", id="inc10")
                yield Button("Reset", id="reset", variant="warning")

            yield Static("", id="log")

    def on_button_pressed(self, event: Button.Pressed):
        """Modifica l'attributo reattivo."""
        if event.button.id == "inc":
            self.counter += 1
        elif event.button.id == "dec":
            self.counter -= 1
        elif event.button.id == "inc10":
            self.counter += 10
        elif event.button.id == "reset":
            self.counter = 0

    def watch_counter(self, old_value: int, new_value: int):
        """Chiamato automaticamente quando counter cambia."""
        # Aggiorna il display
        display = self.query_one("#counter-display", Static)
        display.update(str(new_value))

        # Aggiorna il log
        log = self.query_one("#log", Static)
        log.update(f"Counter cambiato: {old_value} → {new_value}")


class ValidatedReactiveApp(App):
    """Esempio con validazione degli attributi reattivi."""

    CSS = """
    Vertical { padding: 1; }
    Horizontal { height: auto; }
    #value { font-size: 200%; text-align: center; padding: 1; }
    #info { color: $text-muted; }
    """

    # Attributo con validazione: valore tra 0 e 100
    percentage = reactive(50)

    def compose(self):
        with Vertical():
            yield Static("VALIDATED REACTIVE (0-100)")
            yield Static("50", id="value")
            with Horizontal():
                yield Button("-10", id="dec10")
                yield Button("-1", id="dec1")
                yield Button("+1", id="inc1")
                yield Button("+10", id="inc10")
            yield Static("Il valore viene validato tra 0 e 100", id="info")

    def validate_percentage(self, value: int) -> int:
        """Validazione: forza il valore nel range 0-100."""
        return max(0, min(100, value))

    def watch_percentage(self, new_value: int):
        """Aggiorna il display."""
        self.query_one("#value", Static).update(f"{new_value}%")

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        if button_id == "dec10":
            self.percentage -= 10  # validate_percentage lo terrà >= 0
        elif button_id == "dec1":
            self.percentage -= 1
        elif button_id == "inc1":
            self.percentage += 1
        elif button_id == "inc10":
            self.percentage += 10  # validate_percentage lo terrà <= 100


class ComputedReactiveApp(App):
    """Esempio con valori calcolati che dipendono da altri reactive."""

    CSS = """
    Vertical { padding: 1; }
    Input { margin-bottom: 1; }
    #fullname {
        font-size: 150%;
        padding: 1;
        background: $primary;
        text-align: center;
    }
    """

    nome = reactive("")
    cognome = reactive("")

    def compose(self):
        with Vertical():
            yield Static("COMPUTED VALUES")
            yield Input(placeholder="Nome", id="nome")
            yield Input(placeholder="Cognome", id="cognome")
            yield Static("(inserisci nome e cognome)", id="fullname")

    def on_input_changed(self, event: Input.Changed):
        """Aggiorna i reactive quando gli input cambiano."""
        if event.input.id == "nome":
            self.nome = event.value
        elif event.input.id == "cognome":
            self.cognome = event.value

    def watch_nome(self, value: str):
        """Ricalcola fullname quando nome cambia."""
        self.update_fullname()

    def watch_cognome(self, value: str):
        """Ricalcola fullname quando cognome cambia."""
        self.update_fullname()

    def update_fullname(self):
        """Aggiorna il display del nome completo."""
        fullname = f"{self.nome} {self.cognome}".strip()
        display = self.query_one("#fullname", Static)
        display.update(fullname or "(inserisci nome e cognome)")


if __name__ == "__main__":
    # Prova una delle tre app:
    # - ReactiveApp: base reactive con watcher
    # - ValidatedReactiveApp: reactive con validazione
    # - ComputedReactiveApp: valori che dipendono da altri
    app = ComputedReactiveApp()
    app.run()
