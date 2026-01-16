# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualBuilder - Schema definition for Textual widgets.

Defines the schema for building Textual TUI apps using Bag's builder pattern.
Use with BagApp for the complete solution.

Example:
    from genro_pygui import BagApp

    class MyApp(BagApp):
        def build(self):
            self.page.static("Hello, Textual!")

    MyApp().run()
"""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING, Any

from genro_bag import Bag
from genro_bag.builder import BagBuilderBase, abstract, element
from textual.widget import Widget
from textual.widgets import Button, Input, Static

if TYPE_CHECKING:
    from genro_bag.bagnode import BagNode


class TextualBuilder(BagBuilderBase):
    """Builder schema for Textual TUI elements.

    Uses @abstract for common widget attributes and @element with ellipsis
    for elements that use the default handler. Each element stores its
    Textual class in _textual_class attribute.
    """

    # -------------------------------------------------------------------------
    # Abstract: common attributes for all widgets
    # -------------------------------------------------------------------------

    @abstract()
    def widget(
        self,
        node_value: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        name: str | None = None,
        disabled: bool = False,
    ): ...

    # -------------------------------------------------------------------------
    # Elements
    # -------------------------------------------------------------------------

    @element(inherits_from="@widget", compile_class=Static)
    def static(
        self,
        node_value: str | None = None,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
    ): ...

    @element(inherits_from="@widget", compile_class=Input)
    def input(
        self,
        node_value: str | None = None,
        placeholder: str = "",
        password: bool = False,
        max_length: int = 0,
    ): ...

    @element(inherits_from="@widget", compile_class=Button)
    def button(
        self,
        node_value: str | None = None,
        variant: str = "default",
    ): ...

    # -------------------------------------------------------------------------
    # Compile: transform Bag to Textual widgets
    # -------------------------------------------------------------------------

    def compile(self, bag: Bag) -> Generator[Widget, None, None]:
        """Compile a Bag to Textual widgets. Yields widgets recursively."""
        for node in bag:
            yield from self._compile_node(node)

    def _compile_node(self, node: BagNode) -> Generator[Widget, None, None]:
        """Compile a single node and its children."""
        tag = node.tag or "static"
        attr = dict(node.attr)

        schema_info = self.get_schema_info(tag)
        compile_kwargs = schema_info.get("compile_kwargs", {})
        textual_class = compile_kwargs.get("class")
        if textual_class is None:
            raise ValueError(f"Element '{tag}' missing compile_class in schema")

        kwargs = self._build_widget_kwargs(attr)

        if isinstance(node.value, Bag):
            # Node has children - it's a container
            widget = textual_class(**kwargs)
            node.compiled["widget"] = widget
            with widget:
                for child_node in node.value:
                    yield from self._compile_node(child_node)
            yield widget
        else:
            # Leaf node
            content = str(node.value) if node.value else ""
            widget = textual_class(content, **kwargs)
            node.compiled["widget"] = widget
            yield widget

    def _build_widget_kwargs(self, attr: dict[str, Any]) -> dict[str, Any]:
        """Build kwargs for widget constructor, filtering internal attrs."""
        kwargs = {}
        for key, value in attr.items():
            if key.startswith("_"):
                continue
            kwargs[key] = value
        return kwargs
