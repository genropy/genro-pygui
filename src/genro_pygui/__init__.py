# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Terminal UI for Genro Bag visualization and interaction."""

from genro_pygui.remote import connect
from genro_pygui.textual_app import TextualApp
from genro_pygui.textual_builder import TextualBuilder

__all__ = ["TextualApp", "TextualBuilder", "connect"]
