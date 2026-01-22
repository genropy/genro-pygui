# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Test se compose può restituire una lista invece di yield."""

from textual.app import App
from textual.widgets import Static


class TestApp(App):
    """App di test che restituisce lista da compose."""

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self):
        """Genera i widget dell'interfaccia."""
        return [Static("Hello, Textual!"), Static("Premi Q per uscire")]


if __name__ == "__main__":
    TestApp().run()
