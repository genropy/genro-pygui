"""
Tutorial Textual #08 - App Completa

Mini-applicazione che combina tutti i concetti.
Form con validazione, reactive, screens, styling.

Esegui con: python 08_complete_app.py
"""

from textual.app import App
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, Center
from textual.widgets import Static, Button, Input, Label
from textual.reactive import reactive


class ContactFormApp(App):
    """Form contatti con validazione e preview in tempo reale."""

    CSS = """
    /* Layout principale */
    #main {
        padding: 2;
    }

    #title {
        font-size: 200%;
        text-align: center;
        background: $primary;
        padding: 1;
        margin-bottom: 2;
    }

    /* Form styling */
    .form-row {
        height: auto;
        margin-bottom: 1;
    }

    .form-label {
        width: 15;
        padding: 1 0;
    }

    .form-input {
        width: 1fr;
    }

    /* Preview card */
    #preview-card {
        border: double $accent;
        padding: 1;
        margin: 2 0;
        background: $surface;
    }

    #preview-title {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    #preview-content {
        font-size: 120%;
        text-align: center;
    }

    /* Validation feedback */
    .error {
        color: $error;
    }

    .valid {
        color: $success;
    }

    #validation-status {
        padding: 1;
        text-align: center;
    }

    /* Buttons */
    #buttons {
        height: auto;
        margin-top: 2;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    # Attributi reattivi per i campi del form
    nome = reactive("")
    cognome = reactive("")
    email = reactive("")

    def compose(self):
        with Vertical(id="main"):
            yield Static("CONTACT FORM", id="title")

            # Campo Nome
            with Horizontal(classes="form-row"):
                yield Label("Nome:", classes="form-label")
                yield Input(placeholder="Il tuo nome", id="input-nome", classes="form-input")

            # Campo Cognome
            with Horizontal(classes="form-row"):
                yield Label("Cognome:", classes="form-label")
                yield Input(placeholder="Il tuo cognome", id="input-cognome", classes="form-input")

            # Campo Email
            with Horizontal(classes="form-row"):
                yield Label("Email:", classes="form-label")
                yield Input(placeholder="email@example.com", id="input-email", classes="form-input")

            # Preview card - si aggiorna in tempo reale
            with Vertical(id="preview-card"):
                yield Static("PREVIEW", id="preview-title")
                yield Static("(inserisci i dati)", id="preview-content")

            # Status validazione
            yield Static("", id="validation-status")

            # Buttons
            with Horizontal(id="buttons"):
                yield Button("Salva", id="save", variant="success", disabled=True)
                yield Button("Reset", id="reset", variant="warning")
                yield Button("Esci", id="quit", variant="error")

    def on_input_changed(self, event: Input.Changed):
        """Aggiorna i reactive quando gli input cambiano."""
        input_id = event.input.id
        if input_id == "input-nome":
            self.nome = event.value
        elif input_id == "input-cognome":
            self.cognome = event.value
        elif input_id == "input-email":
            self.email = event.value

    def watch_nome(self, value: str):
        self.update_preview()
        self.validate_form()

    def watch_cognome(self, value: str):
        self.update_preview()
        self.validate_form()

    def watch_email(self, value: str):
        self.update_preview()
        self.validate_form()

    def update_preview(self):
        """Aggiorna la preview card."""
        preview = self.query_one("#preview-content", Static)
        if self.nome or self.cognome:
            fullname = f"{self.nome} {self.cognome}".strip()
            email_line = f"\n{self.email}" if self.email else ""
            preview.update(f"{fullname}{email_line}")
        else:
            preview.update("(inserisci i dati)")

    def validate_form(self):
        """Valida il form e aggiorna lo stato."""
        errors = []

        if not self.nome:
            errors.append("Nome richiesto")
        if not self.cognome:
            errors.append("Cognome richiesto")
        if not self.email:
            errors.append("Email richiesta")
        elif "@" not in self.email:
            errors.append("Email non valida")

        status = self.query_one("#validation-status", Static)
        save_btn = self.query_one("#save", Button)

        if errors:
            status.update(" | ".join(errors))
            status.remove_class("valid")
            status.add_class("error")
            save_btn.disabled = True
        else:
            status.update("Form valido!")
            status.remove_class("error")
            status.add_class("valid")
            save_btn.disabled = False

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id

        if button_id == "save":
            self.push_screen(ConfirmSaveDialog(
                nome=self.nome,
                cognome=self.cognome,
                email=self.email
            ), callback=self.on_save_confirmed)

        elif button_id == "reset":
            self.reset_form()

        elif button_id == "quit":
            self.exit()

    def reset_form(self):
        """Resetta tutti i campi."""
        self.query_one("#input-nome", Input).value = ""
        self.query_one("#input-cognome", Input).value = ""
        self.query_one("#input-email", Input).value = ""
        self.nome = ""
        self.cognome = ""
        self.email = ""

    def on_save_confirmed(self, confirmed: bool):
        """Callback quando il dialog di conferma si chiude."""
        if confirmed:
            self.notify(f"Salvato: {self.nome} {self.cognome} <{self.email}>", severity="information")
            self.reset_form()


class ConfirmSaveDialog(ModalScreen):
    """Dialog di conferma salvataggio."""

    CSS = """
    ConfirmSaveDialog {
        align: center middle;
    }

    #dialog {
        width: 60;
        height: 14;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
    }

    #dialog-title {
        text-align: center;
        font-size: 150%;
        margin-bottom: 1;
    }

    #dialog-content {
        text-align: center;
        margin-bottom: 1;
    }

    #dialog-buttons {
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self, nome: str, cognome: str, email: str):
        super().__init__()
        self.nome = nome
        self.cognome = cognome
        self.email = email

    def compose(self):
        with Vertical(id="dialog"):
            yield Static("Conferma Salvataggio", id="dialog-title")
            yield Static(f"Nome: {self.nome} {self.cognome}", id="dialog-content")
            yield Static(f"Email: {self.email}")
            with Horizontal(id="dialog-buttons"):
                yield Button("Conferma", id="confirm", variant="success")
                yield Button("Annulla", id="cancel", variant="error")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)


if __name__ == "__main__":
    app = ContactFormApp()
    app.run()
