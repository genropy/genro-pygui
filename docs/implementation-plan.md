# Piano di Implementazione - Data Binding

**Status**: 🔴 DA REVISIONARE
**Data**: 2026-01-21

---

## Filosofia

Ogni blocco è:
- **Auto-contenuto**: può essere testato indipendentemente
- **Incrementale**: costruisce su quello precedente
- **Piccolo**: max 1-2 ore di lavoro
- **Verificabile**: test chiari per confermare correttezza

---

## Blocco 0: Setup Base (Prerequisito)

**Obiettivo**: Avere un'app BagApp funzionante con due Bag separate.

### Stato Attuale
- `BagApp` ha solo `self._page` (Bag struttura)
- Manca `self._data` (Bag dati)

### Modifiche
```python
# bag_app.py
class BagApp(App):
    def __init__(self):
        super().__init__()
        self._page = Bag(builder=TextualBuilder)
        self._data = Bag()  # ← NUOVO: Bag dati
```

### Test
```python
def test_bagapp_has_data_bag():
    app = BagApp()
    assert hasattr(app, '_data')
    assert isinstance(app._data, Bag)

def test_page_and_data_are_separate():
    app = BagApp()
    app._page.static("hello")
    app._data["test"] = 123
    assert app._page.len() == 1
    assert app._data["test"] == 123
```

### Verifica Manuale
```python
class MyApp(BagApp):
    def build(self):
        self.page.static("Hello")
        self.data["nome"] = "Mario"
        print(f"Data: {self.data['nome']}")  # → "Mario"
```

---

## Blocco 1: Path Resolution Base

**Obiettivo**: Risolvere path relativi con `datapath` statico.

### Nuovo File: `path_resolver.py`

```python
def resolve_path(path: str, datapath: str | None) -> str:
    """Risolve un path relativo dato un datapath.

    Args:
        path: Il path da risolvere (es. ".nome" o "cliente.nome")
        datapath: Il contesto datapath (es. "cliente")

    Returns:
        Path assoluto (es. "cliente.nome")
    """
    if not path:
        return datapath or ""

    # Path assoluto (non inizia con '.')
    if not path.startswith('.'):
        return path

    # Path relativo
    if not datapath:
        return path[1:]  # Rimuovi il punto iniziale

    return f"{datapath}{path}"
```

### Test
```python
def test_resolve_absolute_path():
    assert resolve_path("cliente.nome", "form") == "cliente.nome"

def test_resolve_relative_path():
    assert resolve_path(".nome", "cliente") == "cliente.nome"

def test_resolve_relative_nested():
    assert resolve_path(".via", "cliente.indirizzo") == "cliente.indirizzo.via"

def test_resolve_relative_no_datapath():
    assert resolve_path(".nome", None) == "nome"

def test_resolve_dot_only():
    assert resolve_path(".", "cliente") == "cliente"

def test_resolve_empty_path():
    assert resolve_path("", "cliente") == "cliente"
```

### Verifica
Funzione pura, nessuna dipendenza. Test unitari sufficienti.

---

## Blocco 2: Attributo `datapath` sui Nodi

**Obiettivo**: I nodi possono avere `datapath` e risolverlo risalendo la gerarchia.

### Modifiche a BagNode (o nuovo mixin)

```python
# In bagnode o in un mixin per pygui
def abs_datapath(self, path: str) -> str:
    """Risolve path risalendo la gerarchia dei datapath."""
    current = self
    resolved = path

    while current is not None:
        node_datapath = current.attr.get('datapath')
        if node_datapath:
            resolved = resolve_path(resolved, node_datapath)
        current = current.parent

    return resolved
```

### Test
```python
def test_abs_datapath_single_level():
    """datapath su nodo diretto."""
    page = Bag()
    page.vertical(datapath="cliente")
    node = page["vertical"]
    # Simula abs_datapath
    assert node.abs_datapath(".nome") == "cliente.nome"

def test_abs_datapath_nested():
    """datapath annidati."""
    page = Bag()
    v1 = page.vertical(datapath="cliente")
    v2 = v1.vertical(datapath=".indirizzo")
    # Il nodo interno dovrebbe risolvere:
    # ".via" → ".indirizzo.via" → "cliente.indirizzo.via"
```

### Verifica Manuale
```python
page.vertical(datapath="cliente")
    page.input(value="^.nome")  # Dovrebbe risolvere a "cliente.nome"
```

---

## Blocco 3: Parsing Prefissi Binding

**Obiettivo**: Identificare e parsare `^path`, `=path`, `==expr`.

### Nuovo: `binding_parser.py`

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class ParsedBinding:
    type: Literal['trigger', 'value', 'formula', 'literal']
    path: str | None
    expression: str | None = None

def parse_binding(value: str) -> ParsedBinding:
    """Parsa un valore di attributo per identificare il tipo di binding."""
    if not isinstance(value, str):
        return ParsedBinding(type='literal', path=None)

    if value.startswith('=='):
        return ParsedBinding(type='formula', path=None, expression=value[2:])
    elif value.startswith('^'):
        return ParsedBinding(type='trigger', path=value[1:])
    elif value.startswith('='):
        return ParsedBinding(type='value', path=value[1:])
    else:
        return ParsedBinding(type='literal', path=None)
```

### Test
```python
def test_parse_trigger():
    b = parse_binding("^.nome")
    assert b.type == 'trigger'
    assert b.path == '.nome'

def test_parse_value():
    b = parse_binding("=.titolo")
    assert b.type == 'value'
    assert b.path == '.titolo'

def test_parse_formula():
    b = parse_binding("==nome + ' ' + cognome")
    assert b.type == 'formula'
    assert b.expression == "nome + ' ' + cognome"

def test_parse_literal():
    b = parse_binding("Hello World")
    assert b.type == 'literal'
    assert b.path is None
```

---

## Blocco 4: Lettura Iniziale da Data

**Obiettivo**: Durante compile, widget con `^path` legge valore iniziale da `data`.

### Modifiche al Compiler

```python
def _compile_node(self, node):
    # ... existing code ...

    # Per ogni attributo, controlla se è un binding
    for attr_name, attr_value in node.attr.items():
        binding = parse_binding(attr_value)

        if binding.type in ('trigger', 'value'):
            # Risolvi il path
            abs_path = node.abs_datapath(binding.path)
            # Leggi valore da data
            data_value = self.app.data.get(abs_path)
            # Sostituisci nell'attributo per il widget
            node.attr[attr_name] = data_value
```

### Test
```python
def test_initial_value_from_data():
    app = BagApp()
    app.data["cliente.nome"] = "Mario"

    app.page.vertical(datapath="cliente")
    app.page.input(value="^.nome")

    # Dopo compile, il widget dovrebbe avere value="Mario"
    compiled = list(app.page.builder.compile(app.page))
    # Verifica che l'input abbia il valore corretto
```

### Verifica Manuale
```python
class MyApp(BagApp):
    def build(self):
        self.data["cliente.nome"] = "Mario"
        self.page.vertical(datapath="cliente")
        self.page.input(value="^.nome")  # Dovrebbe mostrare "Mario"
```

---

## Blocco 5: Scrittura Widget → Data (senza validazione)

**Obiettivo**: Quando widget cambia, scrive su `data`.

### Modifiche

```python
# Nel widget o nel compiler
def on_widget_change(self, widget, new_value):
    """Chiamato quando il widget cambia valore."""
    source_node = widget.source_node
    binding = parse_binding(source_node.attr.get('value', ''))

    if binding.type == 'trigger':  # Solo ^ scrive
        abs_path = source_node.abs_datapath(binding.path)
        self.app.data[abs_path] = new_value
```

### Test
```python
def test_widget_writes_to_data():
    app = BagApp()
    app.page.vertical(datapath="cliente")
    app.page.input(value="^.nome", id="nome_input")

    # Simula modifica widget
    app._on_widget_change("nome_input", "Luigi")

    assert app.data["cliente.nome"] == "Luigi"
```

---

## Blocco 6: Trigger Data → Widget (get_trigger_reason)

**Obiettivo**: Quando `data` cambia, widget sottoscritti si aggiornano.

### Nuovo: `trigger_utils.py`

```python
def get_trigger_reason(node_path: str, event_path: str) -> str | None:
    """Determina relazione tra path nodo e path evento."""
    if node_path == event_path:
        return 'node'
    elif node_path.startswith(event_path + '.'):
        return 'container'
    elif event_path.startswith(node_path + '.'):
        return 'child'
    return None
```

### Test
```python
def test_trigger_reason_node():
    assert get_trigger_reason("a.b.c", "a.b.c") == 'node'

def test_trigger_reason_container():
    assert get_trigger_reason("a.b.c", "a.b") == 'container'

def test_trigger_reason_child():
    assert get_trigger_reason("a.b", "a.b.c") == 'child'

def test_trigger_reason_none():
    assert get_trigger_reason("a.b.c", "x.y.z") is None
```

---

## Blocco 7: Subscription e Update Widget

**Obiettivo**: Setup subscription durante compile, update widget su trigger.

### Modifiche

```python
# Durante compile
def _setup_data_binding(self, node, widget):
    binding = parse_binding(node.attr.get('value', ''))

    if binding.type == 'trigger':
        abs_path = node.abs_datapath(binding.path)

        # Registra subscription
        def on_data_change(event):
            reason = get_trigger_reason(abs_path, event.path)
            if reason and event.reason != node:
                new_value = self.app.data.get(abs_path)
                widget.update(str(new_value))

        self.app.data.subscribe(f"widget_{id(widget)}", path=abs_path, callback=on_data_change)

        # Salva per cleanup
        node.compiled['subscription_id'] = f"widget_{id(widget)}"
```

### Test
```python
def test_data_change_updates_widget():
    app = BagApp()
    app.data["nome"] = "Mario"
    app.page.input(value="^nome", id="inp")

    # Compile e run
    # ...

    # Modifica data
    app.data["nome"] = "Luigi"

    # Widget dovrebbe aggiornarsi
    # assert widget.value == "Luigi"
```

---

## Blocco 8: Evitare Loop Infiniti

**Obiettivo**: Widget che scrive non si auto-aggiorna.

### Modifiche

```python
def on_widget_change(self, widget, new_value):
    source_node = widget.source_node
    binding = parse_binding(source_node.attr.get('value', ''))

    if binding.type == 'trigger':
        abs_path = source_node.abs_datapath(binding.path)
        # Passa reason=source_node
        self.app.data.set_item(abs_path, new_value, reason=source_node)

# In on_data_change:
def on_data_change(event):
    if event.reason == node:  # Sono io che ho causato la modifica
        return  # Ignora
    # ... update widget
```

### Test
```python
def test_no_infinite_loop():
    """Widget che scrive non si auto-aggiorna."""
    app = BagApp()
    app.page.input(value="^nome", id="inp")

    update_count = 0
    original_update = widget.update
    def counting_update(*args):
        nonlocal update_count
        update_count += 1
        original_update(*args)
    widget.update = counting_update

    # Simula modifica da widget
    app._on_widget_change("inp", "Test")

    # Widget non dovrebbe essersi auto-aggiornato
    assert update_count == 0
```

---

## Blocco 9: Validazione Base (notnull, len)

**Obiettivo**: Validazioni bloccano scrittura se errore.

### Nuovo: `validator.py`

```python
class Validator:
    def validate(self, node, value) -> dict:
        result = {'value': value, 'warnings': []}
        validations = self._extract_validations(node.attr)

        if validations.get('notnull') and not value:
            result['error'] = validations.get('notnull_error', 'Campo obbligatorio')
            return result

        max_len = validations.get('len')
        if max_len and len(str(value)) > max_len:
            result['error'] = validations.get('len_error', f'Max {max_len} caratteri')
            return result

        return result

    def _extract_validations(self, attr: dict) -> dict:
        return {k[9:]: v for k, v in attr.items() if k.startswith('validate_')}
```

### Test
```python
def test_validate_notnull_error():
    v = Validator()
    node = MockNode(attr={'validate_notnull': True})
    result = v.validate(node, '')
    assert result.get('error') is not None

def test_validate_notnull_ok():
    v = Validator()
    node = MockNode(attr={'validate_notnull': True})
    result = v.validate(node, 'hello')
    assert result.get('error') is None

def test_validate_len_error():
    v = Validator()
    node = MockNode(attr={'validate_len': 5})
    result = v.validate(node, 'toolong')
    assert result.get('error') is not None
```

---

## Blocco 10: Integrazione Validazione

**Obiettivo**: Validazione integrata nel flusso di scrittura.

### Modifiche

```python
def on_widget_change(self, widget, new_value):
    source_node = widget.source_node

    # Validazione
    if self._has_validations(source_node):
        result = self.validator.validate(source_node, new_value)

        if result.get('error'):
            self._show_error(result['error'])
            return  # NON scrive

        new_value = result['value']  # Potrebbe essere modificato

    # Scrittura
    binding = parse_binding(source_node.attr.get('value', ''))
    if binding.type == 'trigger':
        abs_path = source_node.abs_datapath(binding.path)
        self.app.data.set_item(abs_path, new_value, reason=source_node)
```

### Test
```python
def test_validation_blocks_write():
    app = BagApp()
    app.page.input(value="^nome", validate_notnull=True)

    # Simula scrittura di valore vuoto
    app._on_widget_change("inp", "")

    # Data non dovrebbe essere modificata
    assert app.data.get("nome") is None
```

---

## Riepilogo Blocchi

| # | Blocco | Dipende da | Output |
|---|--------|------------|--------|
| 0 | Setup Base | - | `self._data` in BagApp |
| 1 | Path Resolution | 0 | `resolve_path()` |
| 2 | `abs_datapath` | 1 | Metodo sui nodi |
| 3 | Parsing Binding | - | `parse_binding()` |
| 4 | Lettura Iniziale | 2, 3 | Widget legge da data |
| 5 | Scrittura Widget→Data | 2, 3 | Widget scrive su data |
| 6 | Trigger Reason | - | `get_trigger_reason()` |
| 7 | Subscription/Update | 5, 6 | Data→Widget reattivo |
| 8 | Anti-Loop | 7 | `reason` pattern |
| 9 | Validazione Base | - | `Validator` class |
| 10 | Integrazione Valid. | 5, 9 | Validazione nel flusso |

---

## Ordine Suggerito

```
Blocco 0 (Setup)
    │
    ├─► Blocco 1 (Path Resolution)
    │       │
    │       └─► Blocco 2 (abs_datapath)
    │
    └─► Blocco 3 (Parsing Binding)
            │
            └─► Blocco 4 (Lettura Iniziale)
                    │
                    └─► Blocco 5 (Scrittura)
                            │
                            ├─► Blocco 6 (Trigger Reason)
                            │       │
                            │       └─► Blocco 7 (Subscription)
                            │               │
                            │               └─► Blocco 8 (Anti-Loop)
                            │
                            └─► Blocco 9 (Validazione)
                                    │
                                    └─► Blocco 10 (Integrazione)
```

---

## Note

- Ogni blocco ha test isolati
- Si può fare commit dopo ogni blocco
- Se un blocco fallisce, non compromette i precedenti
- Path simbolici (#DATA, #WORKSPACE) sono fase successiva
