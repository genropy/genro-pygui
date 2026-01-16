# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""BagApp - Base class for Textual apps built with Bag.

Example:
    from genro_pygui import BagApp

    class MyApp(BagApp):
        def build(self):
            self.page.static("Hello, Textual!")
            self.page.static("Built with Bag")

    if __name__ == "__main__":
        MyApp().run()
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from genro_bag import Bag
from textual.app import App, ComposeResult

from genro_pygui.textual_builder import TextualBuilder

if TYPE_CHECKING:
    from genro_pygui.remote import RemoteServer


class BagApp(App):
    """Base class for Textual apps built with Bag.

    Subclass and override build() to define your UI using self.page.
    Automatically recomposes when page Bag changes.
    """

    BINDINGS = [("q", "quit", "Esci")]

    def __init__(self, remote_port: int | None = None) -> None:
        super().__init__()
        self._page = Bag(builder=TextualBuilder)
        self._page.subscribe("_bagapp_reactive", any=self._on_page_change)
        self._build_done = False
        self._building = False
        self._remote_server: RemoteServer | None = None
        self._remote_port = remote_port

    def on_mount(self) -> None:
        """Start remote server if port specified."""
        if self._remote_port is not None:
            self.enable_remote(self._remote_port)

    def enable_remote(self, port: int = 9999) -> None:
        """Enable remote control via socket."""
        from genro_pygui.remote import RemoteServer

        self._remote_server = RemoteServer(self, port)
        self._remote_server.start()

    @property
    def page(self) -> Bag:
        """The page Bag with TextualBuilder for building UI."""
        return self._page

    def build(self) -> None:
        """Override this method to build your UI using self.page."""

    def compose(self) -> ComposeResult:
        """Generate widgets from page Bag."""
        if not self._build_done:
            self._building = True
            self.build()
            self._building = False
            self._build_done = True
        yield from self._page.builder.compile(self._page)

    def _on_page_change(self, **kw: Any) -> None:
        """Handle Bag changes with targeted updates when possible.

        - upd_value: update just the affected widget
        - ins/del: full app refresh
        - fallback: full app refresh
        """
        if not self.is_running or self._building:
            return

        evt = kw.get("evt", "")
        node = kw.get("node")

        if node is None:
            self._safe_call(self.recompose)
            return

        if evt == "upd_value":
            widget = node.compiled.get("widget")
            if widget is not None:
                content = str(node.value) if node.value else ""
                self._safe_call(widget.update, content)
                return

        self._safe_call(self.refresh, recompose=True)

    def _safe_call(self, callback: Any, *args: Any, **kwargs: Any) -> None:
        """Call callback safely, using call_from_thread if needed."""
        import threading

        if self._thread_id == threading.get_ident():
            callback(*args, **kwargs)
        else:
            self.call_from_thread(callback, *args, **kwargs)
