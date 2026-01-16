# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""BagViewer - Terminal UI for Bag visualization."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Tree
from textual.widgets.tree import TreeNode

if TYPE_CHECKING:
    from genro_bag import Bag, BagNode


class BagViewer(App):
    """Terminal application to view and interact with a Bag structure."""

    TITLE = "Genro Bag Viewer"
    CSS = """
    Tree {
        width: 100%;
        height: 100%;
    }

    .tree--label {
        color: $text;
    }

    .tree--guides {
        color: $primary-darken-2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("e", "expand_all", "Expand All"),
        ("c", "collapse_all", "Collapse All"),
    ]

    def __init__(self, bag: Bag) -> None:
        """Initialize viewer with a Bag.

        Args:
            bag: The Bag to visualize.
        """
        super().__init__()
        self._bag = bag
        self._tree: Tree[BagNode] | None = None
        self._subscriber_id = f"pygui_viewer_{id(self)}"

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()
        yield Tree("Bag", id="bag-tree")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the tree when app mounts."""
        self._tree = self.query_one("#bag-tree", Tree)
        self._populate_tree()
        self._subscribe_to_bag()

    def _populate_tree(self) -> None:
        """Populate tree from Bag structure."""
        if self._tree is None:
            return

        self._tree.clear()
        root = self._tree.root
        root.expand()

        self._add_bag_nodes(root, self._bag)

    def _add_bag_nodes(self, parent: TreeNode, bag: Bag) -> None:  # type: ignore[type-arg]
        """Recursively add Bag nodes to tree.

        Args:
            parent: Parent tree node.
            bag: Bag to add nodes from.
        """
        for node in bag:
            label = self._format_node_label(node)
            tree_node = parent.add(label, data=node)

            # If node value is a Bag, recurse
            value = node.get_value(static=True)
            if hasattr(value, "_nodes") and hasattr(value, "walk"):
                self._add_bag_nodes(tree_node, value)

    def _format_node_label(self, node: BagNode) -> str:
        """Format a BagNode for display.

        Args:
            node: The BagNode to format.

        Returns:
            Formatted string for tree display.
        """
        value = node.get_value(static=True)

        # Check if value is a Bag
        if hasattr(value, "_nodes"):
            value_str = f"[Bag: {len(value)} nodes]"
        elif value is None:
            value_str = "[None]"
        elif isinstance(value, str) and len(value) > 30:
            value_str = f'"{value[:30]}..."'
        else:
            value_str = repr(value)

        # Show attributes if present
        attr_str = ""
        if node.attr:
            attr_keys = list(node.attr.keys())[:3]
            if len(node.attr) > 3:
                attr_str = f" {{{', '.join(attr_keys)}...}}"
            else:
                attr_str = f" {{{', '.join(attr_keys)}}}"

        return f"{node.label}: {value_str}{attr_str}"

    def _subscribe_to_bag(self) -> None:
        """Subscribe to Bag changes for live updates."""
        self._bag.subscribe(
            self._subscriber_id,
            update=self._on_bag_change,
            insert=self._on_bag_change,
            delete=self._on_bag_change,
        )

    def _on_bag_change(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Handle Bag change events.

        Args:
            **kwargs: Event data from subscription.
        """
        # For now, just refresh the whole tree
        # TODO: Optimize to update only changed nodes
        self.call_from_thread(self._populate_tree)

    def action_refresh(self) -> None:
        """Refresh the tree view."""
        self._populate_tree()

    def action_expand_all(self) -> None:
        """Expand all tree nodes."""
        if self._tree:
            self._tree.root.expand_all()

    def action_collapse_all(self) -> None:
        """Collapse all tree nodes."""
        if self._tree:
            self._tree.root.collapse_all()

    def on_unmount(self) -> None:
        """Cleanup when app closes."""
        self._bag.unsubscribe(self._subscriber_id, any=True)


if __name__ == "__main__":
    # Demo with sample Bag
    from genro_bag import Bag

    demo_bag = Bag()
    demo_bag["cliente.nome"] = "Mario"
    demo_bag["cliente.cognome"] = "Rossi"
    demo_bag["cliente.email"] = "mario.rossi@example.com"
    demo_bag["ordini.0.prodotto"] = "Widget A"
    demo_bag["ordini.0.qta"] = 10
    demo_bag["ordini.0.prezzo"] = 25.50
    demo_bag["ordini.1.prodotto"] = "Widget B"
    demo_bag["ordini.1.qta"] = 5
    demo_bag["ordini.1.prezzo"] = 15.00
    demo_bag["config.debug"] = True

    app = BagViewer(demo_bag)
    app.run()
