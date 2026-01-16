# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualBuilder - Dynamic builder for Textual widgets.

Generates schema automatically from Textual widget classes using inspect.
Use with BagApp for the complete solution.

Example:
    from genro_pygui import BagApp

    class MyApp(BagApp):
        def build(self):
            self.page.static("Hello, Textual!")
            self.page.button("Click me", id="btn1")

    MyApp().run()
"""

from __future__ import annotations

import inspect
from collections.abc import Generator
from importlib import import_module
from typing import TYPE_CHECKING, Any, get_args, get_origin

from genro_bag import Bag
from genro_bag.builder import BagBuilderBase
from genro_bag.builders import SchemaBuilder
from textual.widget import Widget
from textual.widgets import (
    Button,
    Checkbox,
    Input,
    Label,
    RadioButton,
    Static,
    Switch,
    TextArea,
)

if TYPE_CHECKING:
    from genro_bag.bagnode import BagNode

# Widgets to include in schema
WIDGETS = [
    Static,
    Button,
    Input,
    Label,
    Switch,
    Checkbox,
    RadioButton,
    TextArea,
]

# Parameters to skip (internal or complex types)
SKIP_PARAMS = {"self", "highlighter", "suggester", "validators", "validate_on"}

# Common widget params (inherited from @widget)
COMMON_PARAMS = {"id", "classes", "name", "disabled"}


def _get_type_string(annotation: Any) -> str:
    """Convert a type annotation to a simple type string."""
    if annotation is inspect.Parameter.empty:
        return "any"

    if isinstance(annotation, str):
        if "None" in annotation:
            return "str?"
        return "str"

    origin = get_origin(annotation)
    if origin is not None:
        args = get_args(annotation)
        if type(None) in args:
            return "str?"

    if hasattr(annotation, "__name__"):
        name = annotation.__name__
        if name in ("str", "int", "bool", "float"):
            return name

    return "str"


def _extract_widget_validations(widget_class: type) -> dict[str, tuple[Any, list, Any]]:
    """Extract call_args_validations from widget __init__ signature."""
    validations: dict[str, tuple[Any, list, Any]] = {}

    try:
        sig = inspect.signature(widget_class.__init__)
        for name, param in sig.parameters.items():
            if name in SKIP_PARAMS or name in COMMON_PARAMS:
                continue

            type_str = _get_type_string(param.annotation)
            default = param.default if param.default is not inspect.Parameter.empty else None

            if default is not None and not isinstance(default, (str, int, float, bool)):
                default = None

            validations[name] = (type_str, [], default)
    except Exception:
        pass

    return validations


def _generate_textual_schema() -> Bag:
    """Generate schema Bag for Textual widgets."""
    schema = Bag(builder=SchemaBuilder)

    # @widget abstract with common attributes
    schema.item(
        "@widget",
        call_args_validations={
            "id": ("str?", [], None),
            "classes": ("str?", [], None),
            "name": ("str?", [], None),
            "disabled": ("bool", [], False),
        },
    )

    # Generate element for each widget
    for widget_class in WIDGETS:
        widget_name = widget_class.__name__.lower()
        validations = _extract_widget_validations(widget_class)
        doc = widget_class.__doc__ or f"Textual {widget_class.__name__} widget"

        schema.item(
            widget_name,
            inherits_from="@widget",
            call_args_validations=validations,
            compile_module="textual.widgets",
            compile_class=widget_class.__name__,
            documentation=doc.split("\n")[0],
        )

    return schema


class TextualBuilder(BagBuilderBase):
    """Builder for Textual TUI elements.

    Schema is generated dynamically from Textual widget classes.
    Supports all standard Textual widgets plus custom components
    defined with @element decorator.
    """

    def __init__(self, bag: Bag) -> None:
        super().__init__(bag)
        self._schema = _generate_textual_schema()

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

        # Get class from compile_kwargs
        module_name = compile_kwargs.get("module", "textual.widgets")
        class_name = compile_kwargs.get("class")

        if class_name is None:
            raise ValueError(f"Element '{tag}' missing compile_class in schema")

        # Import and get class
        module = import_module(module_name)
        textual_class = getattr(module, class_name)

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
