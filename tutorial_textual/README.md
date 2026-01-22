# Tutorial Textual

Esempi progressivi per imparare Textual, il framework TUI per Python.

## Requisiti

```bash
pip install textual
```

## Come eseguire

Ogni file è standalone:

```bash
python 01_hello_world.py
```

Per uscire: premi `Q` o `Ctrl+C`

## Indice

| # | File | Concetti |
|---|------|----------|
| 01 | [hello_world.py](01_hello_world.py) | App, compose(), Static |
| 02 | [containers.py](02_containers.py) | Vertical, Horizontal, Grid, nesting |
| 03 | [input_widgets.py](03_input_widgets.py) | Input, TextArea, eventi Changed/Submitted |
| 04 | [buttons_events.py](04_buttons_events.py) | Button, varianti, handler, @on decorator |
| 05 | [reactive.py](05_reactive.py) | reactive(), watch_*(), validate_*() |
| 06 | [screens.py](06_screens.py) | Screen, push/pop, ModalScreen, passaggio dati |
| 07 | [styling.py](07_styling.py) | CSS selettori, colori, dimensioni, pseudo-classi |
| 08 | [complete_app.py](08_complete_app.py) | App completa con form, validazione, reactive |

## Concetti chiave

### Struttura base

```python
from textual.app import App
from textual.widgets import Static

class MyApp(App):
    def compose(self):
        yield Static("Hello!")

if __name__ == "__main__":
    MyApp().run()
```

### Container

- `Vertical` - widget impilati verticalmente
- `Horizontal` - widget affiancati
- `Grid` - griglia con `grid-size: cols rows`

### Eventi

Handler con naming convention:
```python
def on_button_pressed(self, event: Button.Pressed):
    ...

def on_input_changed(self, event: Input.Changed):
    ...
```

O con decoratore `@on` per target specifici:
```python
@on(Button.Pressed, "#save")
def handle_save(self):
    ...
```

### Reactive

```python
from textual.reactive import reactive

class MyApp(App):
    counter = reactive(0)  # Auto-refresh UI quando cambia

    def watch_counter(self, new_value):
        # Chiamato quando counter cambia
        ...

    def validate_counter(self, value):
        # Valida/trasforma prima dell'assegnazione
        return max(0, value)
```

### CSS

```python
class MyApp(App):
    CSS = """
    #title { font-size: 200%; background: $primary; }
    .important { color: $warning; }
    Button:hover { background: $accent; }
    """
```

### Query widgets

```python
# Per ID
widget = self.query_one("#my-id", Static)

# Per tipo
buttons = self.query(Button)

# Modifica
widget.update("Nuovo testo")
```

## Risorse

- [Documentazione ufficiale](https://textual.textualize.io/)
- [Repository GitHub](https://github.com/Textualize/textual)
- [Widget Gallery](https://textual.textualize.io/widget_gallery/)
