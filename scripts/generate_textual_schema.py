# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Generate Textual widgets schema in Bag MessagePack format.

Usage:
    python scripts/generate_textual_schema.py

Output:
    src/genro_pygui/schemas/textual_widgets.bag.mp
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, get_args, get_origin

from genro_bag import Bag
from genro_bag.builders import SchemaBuilder
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

# Parameters to skip (internal or complex types not serializable)
SKIP_PARAMS = {
    "self",
    "highlighter",
    "suggester",
    "validators",
    "validate_on",
}

# Common widget params (inherited from @widget abstract)
COMMON_PARAMS = {"id", "classes", "name", "disabled"}


def get_type_string(annotation: Any) -> str:
    """Convert a type annotation to a simple type string."""
    if annotation is inspect.Parameter.empty:
        return "any"

    # Handle string annotations
    if isinstance(annotation, str):
        # Clean common Textual types
        if "None" in annotation:
            return "str?"
        return "str"

    # Handle Union types (X | None)
    origin = get_origin(annotation)
    if origin is not None:
        args = get_args(annotation)
        if type(None) in args:
            return "str?"

    # Handle basic types
    if hasattr(annotation, "__name__"):
        name = annotation.__name__
        if name in ("str", "int", "bool", "float"):
            return name

    return "str"


def extract_widget_validations(widget_class: type) -> dict[str, tuple[Any, list, Any]]:
    """Extract call_args_validations from widget __init__ signature."""
    validations: dict[str, tuple[Any, list, Any]] = {}

    try:
        sig = inspect.signature(widget_class.__init__)
        for name, param in sig.parameters.items():
            if name in SKIP_PARAMS or name in COMMON_PARAMS:
                continue

            type_str = get_type_string(param.annotation)
            default = param.default if param.default is not inspect.Parameter.empty else None

            # Only include serializable defaults
            if default is not None and not isinstance(default, (str, int, float, bool)):
                default = None

            # Format: (type, validators, default)
            validations[name] = (type_str, [], default)

    except Exception as e:
        print(f"  Warning: {widget_class.__name__}: {e}")

    return validations


def generate_schema() -> Bag:
    """Generate schema Bag for all Textual widgets using SchemaBuilder."""
    schema = Bag(builder=SchemaBuilder)

    # Define @widget abstract with common attributes
    schema.item(
        "@widget",
        call_args_validations={
            "id": ("str?", [], None),
            "classes": ("str?", [], None),
            "name": ("str?", [], None),
            "disabled": ("bool", [], False),
        },
    )

    # Define each widget element
    for widget_class in WIDGETS:
        widget_name = widget_class.__name__.lower()
        print(f"Processing: {widget_class.__name__} -> {widget_name}")

        validations = extract_widget_validations(widget_class)
        doc = widget_class.__doc__ or f"Textual {widget_class.__name__} widget"

        schema.item(
            widget_name,
            inherits_from="@widget",
            call_args_validations=validations,
            compile_module="textual.widgets",
            compile_class=widget_class.__name__,
            documentation=doc.split("\n")[0],  # First line only
        )

    return schema


def main() -> None:
    """Generate and save schema file."""
    print("Generating Textual widgets schema...")
    print("=" * 50)

    schema = generate_schema()

    # Create output directory
    output_dir = Path(__file__).parent.parent / "src" / "genro_pygui" / "schemas"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save as MessagePack
    output_file = output_dir / "textual_widgets.bag.mp"
    schema.builder.compile(str(output_file))

    print("=" * 50)
    print(f"Schema saved to: {output_file}")

    # Print schema for verification
    print("\nSchema content:")
    print("-" * 50)
    for node in schema:
        print(f"\n{node.label}:")
        if node.attr.get("documentation"):
            print(f"  doc: {node.attr['documentation']}")
        if node.attr.get("inherits_from"):
            print(f"  inherits_from: {node.attr['inherits_from']}")
        ck = node.attr.get("compile_kwargs", {})
        if ck:
            print(f"  compile: {ck}")
        cav = node.attr.get("call_args_validations", {})
        for param_name, (type_str, _, default) in cav.items():
            print(f"  {param_name}: {type_str} = {default!r}")


if __name__ == "__main__":
    main()
