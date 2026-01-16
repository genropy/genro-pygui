# genro-pygui

Terminal UI for Genro Bag visualization and interaction, built with [Textual](https://textual.textualize.io/).

## Status

**Development Status: Pre-Alpha** - Early exploration and POC phase.

## Purpose

Provide a terminal-based interface to:
- Visualize Bag structures as interactive trees
- Edit values and attributes in real-time
- Observe reactive updates (subscriptions, FormulaResolver)
- Debug and explore Bag hierarchies

## Installation

```bash
pip install genro-pygui
```

## Quick Start

```python
from genro_bag import Bag
from genro_pygui import BagViewer

bag = Bag()
bag['cliente.nome'] = 'Mario'
bag['cliente.cognome'] = 'Rossi'
bag['ordini.0.prodotto'] = 'Widget'
bag['ordini.0.qta'] = 10

# Launch terminal viewer
BagViewer(bag).run()
```

## Features (Planned)

- [ ] Tree view of Bag structure
- [ ] Value/attribute display
- [ ] Live updates via subscription
- [ ] Inline editing
- [ ] FormulaResolver visualization
- [ ] Search/filter

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.
