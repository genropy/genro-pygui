"""
Tutorial Textual #06 - Screens e Navigation

Navigazione tra schermate multiple.
Concetti: Screen, push_screen, pop_screen, ModalScreen, passaggio dati

Esegui con: python 06_screens.py
"""

from textual.app import App
from textual.screen import Screen, ModalScreen
from textual.containers import Vertical, Horizontal, Center
from textual.widgets import Static, Button, Input


class HomeScreen(Screen):
    """Schermata principale."""

    CSS = """
    Vertical { padding: 2; }
    Button { margin: 1; }
    #title { font-size: 200%; text-align: center; }
    """

    def compose(self):
        with Vertical():
            yield Static("HOME SCREEN", id="title")
            yield Static("Questa è la schermata principale")
            yield Button("Vai a Settings", id="go-settings", variant="primary")
            yield Button("Apri Dialog", id="open-dialog")
            yield Button("Esci", id="quit", variant="error")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "go-settings":
            # push_screen aggiunge una schermata sopra la corrente
            self.app.push_screen(SettingsScreen())
        elif event.button.id == "open-dialog":
            # ModalScreen per dialoghi modali
            self.app.push_screen(ConfirmDialog())
        elif event.button.id == "quit":
            self.app.exit()


class SettingsScreen(Screen):
    """Schermata impostazioni."""

    CSS = """
    Vertical { padding: 2; }
    Input { margin-bottom: 1; }
    #title { font-size: 150%; color: $secondary; }
    """

    def compose(self):
        with Vertical():
            yield Static("SETTINGS", id="title")
            yield Static("Modifica le impostazioni:")
            yield Input(placeholder="Nome utente", id="username")
            yield Input(placeholder="Email", id="email")
            with Horizontal():
                yield Button("Salva", id="save", variant="success")
                yield Button("Indietro", id="back")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "back":
            # pop_screen torna alla schermata precedente
            self.app.pop_screen()
        elif event.button.id == "save":
            # Salva e torna indietro
            username = self.query_one("#username", Input).value
            email = self.query_one("#email", Input).value
            self.notify(f"Salvato: {username}, {email}")
            self.app.pop_screen()


class ConfirmDialog(ModalScreen):
    """Dialog modale di conferma."""

    CSS = """
    ConfirmDialog {
        align: center middle;
    }
    #dialog {
        width: 50;
        height: 12;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }
    #question { text-align: center; margin-bottom: 1; }
    Horizontal { align: center middle; }
    Button { margin: 0 1; }
    """

    def compose(self):
        with Vertical(id="dialog"):
            yield Static("Sei sicuro?", id="question")
            yield Static("Questa azione non può essere annullata.")
            with Horizontal():
                yield Button("Sì", id="yes", variant="success")
                yield Button("No", id="no", variant="error")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            # dismiss() chiude il dialog e può passare un risultato
            self.dismiss(True)
        else:
            self.dismiss(False)


class ScreensApp(App):
    """App con navigazione tra schermate."""

    CSS = """
    Screen { background: $background; }
    """

    def on_mount(self):
        # Installa la schermata iniziale
        self.push_screen(HomeScreen())

    def on_screen_resume(self, event):
        """Chiamato quando si torna a una schermata."""
        pass  # Puoi aggiornare dati qui se necessario


class DataPassingApp(App):
    """Esempio di passaggio dati tra schermate."""

    CSS = """
    Vertical { padding: 2; }
    #result { font-size: 150%; background: $primary; padding: 1; }
    """

    def compose(self):
        with Vertical():
            yield Static("DATA PASSING DEMO")
            yield Static("Nessun dato", id="result")
            yield Button("Apri form", id="open-form")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "open-form":
            # Passa una callback che riceve il risultato dal dialog
            self.push_screen(DataInputScreen(), callback=self.on_data_received)

    def on_data_received(self, data: str | None):
        """Riceve i dati dalla schermata chiusa."""
        result = self.query_one("#result", Static)
        if data:
            result.update(f"Ricevuto: {data}")
        else:
            result.update("Annullato")


class DataInputScreen(ModalScreen):
    """Schermata che ritorna dati."""

    CSS = """
    DataInputScreen { align: center middle; }
    #form {
        width: 60;
        height: 10;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }
    """

    def compose(self):
        with Vertical(id="form"):
            yield Static("Inserisci un valore:")
            yield Input(placeholder="Il tuo dato", id="data-input")
            with Horizontal():
                yield Button("OK", id="ok", variant="success")
                yield Button("Annulla", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok":
            value = self.query_one("#data-input", Input).value
            self.dismiss(value)  # Passa il valore alla callback
        else:
            self.dismiss(None)  # Passa None per indicare annullamento


if __name__ == "__main__":
    # Prova ScreensApp per navigazione base
    # Oppure DataPassingApp per passaggio dati
    app = ScreensApp()
    app.run()
