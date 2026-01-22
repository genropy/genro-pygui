# Piano di Implementazione - Widget Build (Struttura)

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

## Stato Attuale

### TextualBuilder (`textual_builder.py`)
- `compile()` → itera su nodi, crea widget
- `_compile_node()` → crea widget, salva in `node.compiled["widget"]`
- Nessun supporto per update incrementali

### BagApp (`bag_app.py`)
- `_on_page_change()` gestisce eventi
- `upd_value` → update widget esistente (OK)
- `ins/del` → **full recompose** (da migliorare)
- Flag `_building` per evitare trigger durante build iniziale

### Problemi da Risolvere
1. **INS**: aggiunge nodo → full recompose (inefficiente)
2. **DEL**: rimuove nodo → full recompose (inefficiente)
3. **UPD (struttura)**: sostituisce nodo → full recompose
4. **Cleanup**: nessun cleanup quando widget viene distrutto
5. **Indici**: nessun indice `nodeId → node` per lookup veloci

---

## Blocco 0: Indice Nodi

**Obiettivo**: Mantenere mappa `nodeId → node` per lookup veloci.

### Modifiche a BagApp

```python
class BagApp(App):
    def __init__(self):
        super().__init__()
        self._page = Bag(builder=TextualBuilder)
        self._page.subscribe("_bagapp_reactive", any=self._on_page_change)
        self._node_index = {}  # ← NUOVO: nodeId → node

    def _refresh_node_index(self) -> None:
        """Ricostruisce indice nodi."""
        self._node_index = {}
        for node in self._page.walk():
            node_id = node.attr.get("id")
            if node_id:
                self._node_index[node_id] = node

    def get_node_by_id(self, node_id: str) -> BagNode | None:
        """Trova nodo per ID."""
        return self._node_index.get(node_id)
```

### Test

```python
def test_node_index_basic():
    app = BagApp()
    app.page.static("Hello", id="s1")
    app.page.button("Click", id="b1")
    app._refresh_node_index()

    assert app.get_node_by_id("s1") is not None
    assert app.get_node_by_id("b1") is not None
    assert app.get_node_by_id("nonexistent") is None

def test_node_index_after_change():
    app = BagApp()
    app.page.static("Hello", id="s1")
    app._refresh_node_index()

    # Aggiungi nodo
    app.page.button("Click", id="b1")
    app._refresh_node_index()

    assert app.get_node_by_id("b1") is not None

def test_node_index_nested():
    app = BagApp()
    v = app.page.vertical(id="v1")
    v.static("Hello", id="s1")
    app._refresh_node_index()

    assert app.get_node_by_id("v1") is not None
    assert app.get_node_by_id("s1") is not None
```

### Verifica Manuale

```python
class MyApp(BagApp):
    def build(self):
        self.page.static("Hello", id="greeting")
        self.page.button("Click", id="btn")

app = MyApp()
app._refresh_node_index()
print(app.get_node_by_id("greeting"))  # → BagNode
print(app.get_node_by_id("btn"))       # → BagNode
```

---

## Blocco 1: Cleanup Pattern Base

**Obiettivo**: Ogni nodo può fare cleanup prima di essere distrutto.

### Nuovo: `cleanup_node()` in TextualBuilder

```python
def cleanup_node(self, node: BagNode) -> None:
    """Cleanup prima di distruggere un nodo.

    - Rimuove widget dal DOM (se possibile)
    - Pulisce riferimenti in node.compiled
    - Chiama cleanup ricorsivo sui figli
    """
    # Cleanup figli prima
    if isinstance(node.value, Bag):
        for child in node.value:
            self.cleanup_node(child)

    # Cleanup widget
    widget = node.compiled.get("widget")
    if widget is not None:
        # In Textual, remove() rimuove il widget
        if hasattr(widget, "remove"):
            widget.remove()
        del node.compiled["widget"]
```

### Test

```python
def test_cleanup_removes_widget_ref():
    bag = Bag(builder=TextualBuilder)
    bag.static("Hello", id="s1")
    node = bag["s1"]

    # Simula compilazione
    from textual.widgets import Static
    node.compiled["widget"] = Static("Hello")

    # Cleanup
    bag.builder.cleanup_node(node)

    assert "widget" not in node.compiled

def test_cleanup_recursive():
    bag = Bag(builder=TextualBuilder)
    v = bag.vertical(id="v1")
    v.static("A", id="s1")
    v.static("B", id="s2")

    # Simula compilazione
    from textual.widgets import Static, Vertical
    bag["v1"].compiled["widget"] = Vertical()
    bag["v1.s1"].compiled["widget"] = Static("A")
    bag["v1.s2"].compiled["widget"] = Static("B")

    # Cleanup parent → cleanup anche figli
    bag.builder.cleanup_node(bag["v1"])

    assert "widget" not in bag["v1"].compiled
    assert "widget" not in bag["v1.s1"].compiled
    assert "widget" not in bag["v1.s2"].compiled
```

---

## Blocco 2: Handler DEL con Cleanup

**Obiettivo**: Quando un nodo viene rimosso, fare cleanup invece di full recompose.

### Modifiche a `_on_page_change`

```python
def _on_page_change(self, **kw: Any) -> None:
    if not self.is_running or self._building:
        return

    evt = kw.get("evt", "")
    node = kw.get("node")

    if node is None:
        self._safe_call(self.refresh, recompose=True)
        return

    if evt == "upd_value":
        # ... existing code ...
        return

    if evt == "del":
        # NUOVO: cleanup e rimuovi widget
        self._page.builder.cleanup_node(node)
        self._refresh_node_index()
        return

    # Fallback: full recompose
    self._safe_call(self.refresh, recompose=True)
```

### Test

```python
def test_del_triggers_cleanup(mocker):
    """DEL chiama cleanup_node invece di full recompose."""
    app = BagApp()
    app._build_done = True

    # Crea nodo
    app.page.static("Hello", id="s1")

    # Mock cleanup
    cleanup_spy = mocker.spy(app._page.builder, "cleanup_node")

    # Simula running
    app._is_running = True

    # Elimina nodo
    del app.page["s1"]

    # Verifica cleanup chiamato
    cleanup_spy.assert_called_once()

def test_del_updates_index():
    app = BagApp()
    app.page.static("Hello", id="s1")
    app._refresh_node_index()

    assert app.get_node_by_id("s1") is not None

    # Elimina
    del app.page["s1"]
    app._refresh_node_index()

    assert app.get_node_by_id("s1") is None
```

---

## Blocco 3: Handler INS Mirato

**Obiettivo**: Quando un nodo viene aggiunto, compilare e montare solo quello.

### Modifiche

```python
def _on_page_change(self, **kw: Any) -> None:
    # ... existing code ...

    if evt == "ins":
        # NUOVO: compila e monta solo il nuovo nodo
        self._handle_insert(node, kw)
        return

    # ... rest ...

def _handle_insert(self, node: BagNode, kw: dict) -> None:
    """Gestisce inserimento nodo."""
    parent_node = node.parent_node
    if parent_node is None:
        # Nodo radice → full recompose
        self._safe_call(self.refresh, recompose=True)
        return

    parent_widget = parent_node.compiled.get("widget")
    if parent_widget is None:
        # Parent non ancora compilato → full recompose
        self._safe_call(self.refresh, recompose=True)
        return

    # Compila nuovo nodo
    new_widgets = list(self._page.builder._compile_node(node))

    # Monta nel parent
    for widget in new_widgets:
        self._safe_call(parent_widget.mount, widget)

    self._refresh_node_index()
```

### Test

```python
def test_ins_compiles_only_new_node(mocker):
    """INS compila solo il nuovo nodo, non tutta la pagina."""
    app = BagApp()
    app._build_done = True
    app._is_running = True

    # Crea container
    app.page.vertical(id="v1")
    # Simula compilazione iniziale
    from textual.widgets import Vertical
    app.page["v1"].compiled["widget"] = Vertical()

    compile_spy = mocker.spy(app._page.builder, "_compile_node")

    # Aggiungi nodo
    app.page["v1"].static("New", id="s1")

    # Verifica che _compile_node sia stato chiamato solo per s1
    # (non per v1 o l'intera pagina)
    calls = compile_spy.call_args_list
    # L'ultimo call dovrebbe essere per il nuovo nodo

def test_ins_mounts_in_parent():
    """Nuovo widget viene montato nel parent container."""
    # Test con app reale (integration test)
    pass
```

---

## Blocco 4: Handler UPD Strutturale

**Obiettivo**: Quando un nodo viene sostituito (non solo valore), ricostruirlo in-place.

### Modifiche

```python
def _on_page_change(self, **kw: Any) -> None:
    # ... existing code ...

    if evt == "upd":
        # UPD strutturale: destroy + rebuild in-place
        self._handle_update(node, kw)
        return

    # ... rest ...

def _handle_update(self, node: BagNode, kw: dict) -> None:
    """Gestisce update strutturale di un nodo."""
    parent_node = node.parent_node
    if parent_node is None:
        self._safe_call(self.refresh, recompose=True)
        return

    parent_widget = parent_node.compiled.get("widget")
    old_widget = node.compiled.get("widget")

    if parent_widget is None or old_widget is None:
        self._safe_call(self.refresh, recompose=True)
        return

    # 1. Trova posizione del vecchio widget
    children = list(parent_widget.children)
    try:
        index = children.index(old_widget)
    except ValueError:
        index = -1

    # 2. Cleanup vecchio
    self._page.builder.cleanup_node(node)

    # 3. Compila nuovo
    new_widgets = list(self._page.builder._compile_node(node))

    # 4. Monta nella stessa posizione
    for widget in new_widgets:
        if index >= 0:
            self._safe_call(parent_widget.mount, widget, before=children[index] if index < len(children) else None)
        else:
            self._safe_call(parent_widget.mount, widget)

    self._refresh_node_index()
```

### Test

```python
def test_upd_rebuilds_in_place():
    """UPD distrugge e ricostruisce nella stessa posizione."""
    app = BagApp()
    app._build_done = True

    # Setup iniziale
    v = app.page.vertical(id="v1")
    v.static("A", id="s1")
    v.static("B", id="s2")
    v.static("C", id="s3")

    # L'ordine dovrebbe essere: s1, s2, s3
    # Se update s2, dovrebbe restare tra s1 e s3
```

---

## Blocco 5: Differenziare upd_value vs upd

**Obiettivo**: Distinguere update di solo valore vs update strutturale.

### Analisi

Attualmente:
- `upd_value` → solo il contenuto testuale cambia
- `upd` → l'intero nodo (attributi, figli) cambia

### Modifiche

```python
def _on_page_change(self, **kw: Any) -> None:
    # ... existing code ...

    if evt == "upd_value":
        # Solo valore testuale → update in-place
        widget = node.compiled.get("widget")
        if widget is not None:
            content = str(node.value) if node.value else ""
            self._safe_call(widget.update, content)
            return

    if evt == "upd_attr":
        # NUOVO: solo attributi cambiano
        self._handle_attr_update(node, kw)
        return

    if evt == "upd":
        # Struttura cambia → destroy + rebuild
        self._handle_update(node, kw)
        return

    # ... rest ...

def _handle_attr_update(self, node: BagNode, kw: dict) -> None:
    """Gestisce update di attributi senza ricostruire."""
    widget = node.compiled.get("widget")
    if widget is None:
        return

    # Aggiorna attributi del widget
    changed_attr = kw.get("attr_name")
    new_value = kw.get("new_value")

    if changed_attr and hasattr(widget, changed_attr):
        setattr(widget, changed_attr, new_value)
```

### Test

```python
def test_upd_value_updates_content():
    """upd_value aggiorna solo il contenuto."""
    app = BagApp()
    app.page.static("Hello", id="s1")
    # ... compile ...

    # Cambia solo valore
    app.page["s1"].value = "World"

    # Widget dovrebbe aggiornarsi senza ricostruirsi

def test_upd_attr_updates_attribute():
    """upd_attr aggiorna attributo senza ricostruire."""
    app = BagApp()
    app.page.button("Click", id="b1", disabled=False)
    # ... compile ...

    # Cambia attributo
    app.page["b1"].attr["disabled"] = True

    # Widget.disabled dovrebbe aggiornarsi
```

---

## Blocco 6: Pending Build Queue

**Obiettivo**: Gestire trigger nidificati con coda.

### Modifiche

```python
class BagApp(App):
    def __init__(self):
        # ... existing ...
        self._pending_builds: list[dict] = []
        self._processing_builds = False

    def _on_page_change(self, **kw: Any) -> None:
        if not self.is_running or self._building:
            return

        # Aggiungi alla coda
        self._pending_builds.append(kw)

        # Processa se non già in corso
        if not self._processing_builds:
            self._process_pending_builds()

    def _process_pending_builds(self) -> None:
        """Processa coda di build."""
        self._processing_builds = True
        try:
            while self._pending_builds:
                kw = self._pending_builds.pop(0)
                self._handle_build_event(kw)
        finally:
            self._processing_builds = False

    def _handle_build_event(self, kw: dict) -> None:
        """Gestisce singolo evento di build."""
        evt = kw.get("evt", "")
        node = kw.get("node")

        if node is None:
            self._safe_call(self.refresh, recompose=True)
            return

        if evt == "upd_value":
            # ... handle upd_value ...
        elif evt == "del":
            # ... handle del ...
        elif evt == "ins":
            # ... handle ins ...
        elif evt == "upd":
            # ... handle upd ...
        else:
            self._safe_call(self.refresh, recompose=True)
```

### Test

```python
def test_nested_triggers_queued():
    """Trigger nidificati vengono processati in ordine."""
    app = BagApp()
    app._build_done = True
    app._is_running = True

    events_processed = []

    def track_event(kw):
        events_processed.append(kw.get("evt"))

    # Simula trigger nidificati
    app._pending_builds.append({"evt": "ins", "node": None})
    app._pending_builds.append({"evt": "ins", "node": None})
    app._pending_builds.append({"evt": "del", "node": None})

    # Processa
    app._process_pending_builds()

    assert len(events_processed) == 3
```

---

## Blocco 7: Freeze Pattern

**Obiettivo**: Sospendere trigger durante modifiche batch.

### Modifiche a BagApp

```python
class BagApp(App):
    def __init__(self):
        # ... existing ...
        self._frozen = False

    def freeze(self) -> None:
        """Sospende i trigger di build."""
        self._frozen = True

    def unfreeze(self) -> None:
        """Riattiva i trigger e processa pending."""
        self._frozen = False
        if self._pending_builds:
            self._process_pending_builds()

    def _on_page_change(self, **kw: Any) -> None:
        if not self.is_running or self._building:
            return

        if self._frozen:
            # In freeze mode, accumula solo se necessario
            # oppure ignora (dipende dalla semantica voluta)
            return

        # ... rest ...
```

### Context Manager

```python
from contextlib import contextmanager

@contextmanager
def batch_updates(app: BagApp):
    """Context manager per modifiche batch."""
    app.freeze()
    try:
        yield
    finally:
        app.unfreeze()
```

### Test

```python
def test_freeze_prevents_triggers():
    app = BagApp()
    app._build_done = True
    app._is_running = True

    trigger_count = 0
    original = app._handle_build_event
    def counting_handler(kw):
        nonlocal trigger_count
        trigger_count += 1
        original(kw)
    app._handle_build_event = counting_handler

    app.freeze()
    app.page.static("A")
    app.page.static("B")
    app.page.static("C")

    # Nessun trigger durante freeze
    assert trigger_count == 0

    app.unfreeze()
    # Ora dovrebbe processare (o fare un singolo recompose)

def test_batch_updates_context():
    app = BagApp()

    with batch_updates(app):
        app.page.static("A")
        app.page.static("B")

    # Verificare comportamento dopo unfreeze
```

---

## Blocco 8: AfterBuild Callbacks

**Obiettivo**: Eseguire callback dopo che un nodo è stato compilato.

### Modifiche

```python
class BagApp(App):
    def __init__(self):
        # ... existing ...
        self._after_build_callbacks: list[callable] = []

    def register_after_build(self, callback: callable) -> None:
        """Registra callback da eseguire dopo build."""
        self._after_build_callbacks.append(callback)

    def _process_pending_builds(self) -> None:
        self._processing_builds = True
        try:
            while self._pending_builds:
                kw = self._pending_builds.pop(0)
                self._handle_build_event(kw)

            # NUOVO: esegui callback post-build
            while self._after_build_callbacks:
                cb = self._after_build_callbacks.pop(0)
                cb()
        finally:
            self._processing_builds = False
```

### Test

```python
def test_after_build_callbacks_executed():
    app = BagApp()
    app._build_done = True
    app._is_running = True

    callback_executed = False
    def my_callback():
        nonlocal callback_executed
        callback_executed = True

    app.register_after_build(my_callback)
    app.page.static("Hello")

    # Dopo processing, callback dovrebbe essere eseguito
    assert callback_executed
```

---

## Riepilogo Blocchi

| # | Blocco | Dipende da | Output |
|---|--------|------------|--------|
| 0 | Indice Nodi | - | `_node_index`, `get_node_by_id()` |
| 1 | Cleanup Pattern | 0 | `cleanup_node()` |
| 2 | Handler DEL | 1 | DEL con cleanup |
| 3 | Handler INS | 0, 1 | INS mirato |
| 4 | Handler UPD | 1, 3 | UPD strutturale |
| 5 | upd_value vs upd | 4 | Differenziazione eventi |
| 6 | Pending Queue | 0-5 | Coda eventi |
| 7 | Freeze Pattern | 6 | Batch mode |
| 8 | AfterBuild | 6 | Callback post-build |

---

## Ordine Suggerito

```
Blocco 0 (Indice Nodi)
    │
    ├─► Blocco 1 (Cleanup Pattern)
    │       │
    │       ├─► Blocco 2 (Handler DEL)
    │       │
    │       └─► Blocco 3 (Handler INS)
    │               │
    │               └─► Blocco 4 (Handler UPD)
    │                       │
    │                       └─► Blocco 5 (upd_value vs upd)
    │
    └─► Blocco 6 (Pending Queue)
            │
            ├─► Blocco 7 (Freeze Pattern)
            │
            └─► Blocco 8 (AfterBuild)
```

---

## Blocco 9: Schema Abstract `@enterable`

**Obiettivo**: Definire abstract per widget di input con supporto dtype e validazioni.

### Gerarchia Abstract

```
@enterable
    │
    ├── dtype: str           # Tipo tytx: T, I, N, F, D, H, B
    ├── validate_notnull     # Campo obbligatorio
    ├── validate_len         # Lunghezza max
    ├── validate_regex       # Pattern
    │
    └── @numeric_enterable (inherits @enterable)
    │       ├── validate_min
    │       └── validate_max
    │
    └── @date_enterable (inherits @enterable)
            ├── validate_min_date
            └── validate_max_date
```

### Modifiche a TextualBuilder

```python
# In textual_builder.py - aggiungere nello schema generato

def _generate_textual_schema() -> Bag:
    schema = Bag(builder=SchemaBuilder)

    # @widget abstract (esistente)
    schema.item("@widget", ...)

    # NUOVO: @enterable abstract per widget di input
    schema.item(
        "@enterable",
        inherits_from="@widget",
        call_args_validations={
            "dtype": ("str?", [], "T"),  # Default: Text
            "validate_notnull": ("bool", [], False),
            "validate_notnull_error": ("str?", [], None),
            "validate_len": ("int?", [], None),
            "validate_len_error": ("str?", [], None),
            "validate_regex": ("str?", [], None),
            "validate_regex_error": ("str?", [], None),
        },
    )

    # NUOVO: @numeric_enterable per numeri
    schema.item(
        "@numeric_enterable",
        inherits_from="@enterable",
        call_args_validations={
            "validate_min": ("float?", [], None),
            "validate_max": ("float?", [], None),
            "validate_range_error": ("str?", [], None),
        },
    )

    # NUOVO: @date_enterable per date
    schema.item(
        "@date_enterable",
        inherits_from="@enterable",
        call_args_validations={
            "validate_min_date": ("str?", [], None),
            "validate_max_date": ("str?", [], None),
        },
    )

    # Input eredita da @enterable
    schema.item(
        "input",
        inherits_from="@enterable",
        compile_module="textual.widgets",
        compile_class="Input",
    )

    # ... altri widget
```

### Convenzione dtype (tytx)

| dtype | Suffisso | Tipo Python | Widget hint |
|-------|----------|-------------|-------------|
| `T` | (nessuno) | `str` | Input text |
| `I` | `::I` | `int` | Input numeric |
| `N` | `::N` | `Decimal` | Input numeric |
| `F` | `::F` | `float` | Input numeric |
| `D` | `::D` | `date` | Input date |
| `H` | `::H` | `datetime` | Input datetime |
| `B` | `::B` | `bool` | Switch/Checkbox |

### Test

```python
def test_input_inherits_enterable():
    """Input deve ereditare attributi da @enterable."""
    bag = Bag(builder=TextualBuilder)
    info = bag.builder.get_schema_info("input")

    # Deve avere dtype
    validations = info.get("call_args_validations", {})
    assert "dtype" in validations

def test_enterable_default_dtype():
    """dtype default è 'T' (text)."""
    bag = Bag(builder=TextualBuilder)
    info = bag.builder.get_schema_info("input")
    validations = info.get("call_args_validations", {})
    _, _, default = validations.get("dtype", (None, None, None))
    assert default == "T"
```

---

## Blocco 10: Type Converter (tytx integration)

**Obiettivo**: Convertire valori tra widget (stringa) e Bag (tipo Python) usando tytx.

### Nuovo: `type_converter.py`

```python
"""Type conversion using tytx conventions."""

from decimal import Decimal
from datetime import date, datetime

# Mapping dtype → suffisso tytx
DTYPE_TO_TYTX = {
    "T": None,      # str, no suffix
    "I": "I",       # int
    "N": "N",       # Decimal
    "F": "F",       # float
    "D": "D",       # date
    "H": "H",       # datetime
    "B": "B",       # bool
}

def value_to_widget(value: Any, dtype: str = "T") -> str:
    """Converte valore Python in stringa per widget.

    Args:
        value: Valore dalla Bag (già deserializzato da tytx)
        dtype: Tipo atteso

    Returns:
        Stringa da mostrare nel widget
    """
    if value is None:
        return ""

    if dtype == "D" and isinstance(value, date):
        return value.isoformat()

    if dtype == "H" and isinstance(value, datetime):
        return value.isoformat()

    if dtype == "N" and isinstance(value, Decimal):
        return str(value)

    return str(value)


def value_from_widget(text: str, dtype: str = "T") -> str | None:
    """Converte stringa widget in valore per Bag con suffisso tytx.

    Args:
        text: Stringa dal widget
        dtype: Tipo di destinazione

    Returns:
        Stringa con suffisso tytx (es. "123.45::N") o None se vuoto
    """
    if not text or text.strip() == "":
        return None

    suffix = DTYPE_TO_TYTX.get(dtype)
    if suffix:
        return f"{text}::{suffix}"
    return text


def parse_typed_value(text: str, dtype: str = "T") -> Any:
    """Parse stringa in tipo Python (per validazione locale).

    Args:
        text: Stringa dal widget
        dtype: Tipo atteso

    Returns:
        Valore Python (int, float, Decimal, date, etc.)

    Raises:
        ValueError: Se parsing fallisce
    """
    if not text:
        return None

    if dtype == "I":
        return int(text)
    elif dtype == "F":
        return float(text)
    elif dtype == "N":
        return Decimal(text)
    elif dtype == "D":
        return date.fromisoformat(text)
    elif dtype == "H":
        return datetime.fromisoformat(text)
    elif dtype == "B":
        return text.lower() in ("true", "1", "yes", "si", "sì")
    else:
        return text
```

### Test

```python
def test_value_to_widget_decimal():
    from decimal import Decimal
    result = value_to_widget(Decimal("123.45"), "N")
    assert result == "123.45"

def test_value_to_widget_date():
    from datetime import date
    result = value_to_widget(date(2026, 1, 21), "D")
    assert result == "2026-01-21"

def test_value_from_widget_decimal():
    result = value_from_widget("123.45", "N")
    assert result == "123.45::N"

def test_value_from_widget_int():
    result = value_from_widget("42", "I")
    assert result == "42::I"

def test_value_from_widget_empty():
    result = value_from_widget("", "N")
    assert result is None

def test_parse_typed_value_decimal():
    from decimal import Decimal
    result = parse_typed_value("123.45", "N")
    assert result == Decimal("123.45")

def test_parse_typed_value_date():
    from datetime import date
    result = parse_typed_value("2026-01-21", "D")
    assert result == date(2026, 1, 21)
```

---

## Blocco 11: Validatore Enterable

**Obiettivo**: Validare valori in base a dtype e attributi validate_*.

### Architettura Validazione a Due Livelli

La validazione avviene su **due livelli** complementari:

**Livello 1 - Widget (feedback immediato)**:
- Usa validators Textual nativi (`Number`, `Integer`, `Function`)
- Validazione del formato/dtype mentre l'utente digita
- Feedback visivo istantaneo nel widget
- Previene input malformati PRIMA che lascino il widget

**Livello 2 - Pre-write (business logic)**:
- `EnterableValidator` valida PRIMA del `set_item` sulla Bag
- Validazioni genropy-style: `notnull`, `len`, `regex`, `min/max`, `date_range`
- Può bloccare il set e mostrare errore
- Eseguito quando l'utente conferma l'input (blur, enter, etc.)

**Flusso completo**:
```
Utente digita → Textual Validator (L1) → Feedback immediato
       │
       └─► Input non valido? Widget mostra errore, non procede
       │
       └─► Input valido? → Utente conferma (blur/enter)
                                │
                                ▼
                    EnterableValidator (L2)
                                │
                    ├─► Errore? → Mostra errore, blocca set
                    │
                    └─► OK? → value_from_widget() → set_item(path, "123::N")
```

**Vantaggi**:
- L1 previene errori di formato istantaneamente (UX migliore)
- L2 centralizza business logic (notnull, range, etc.)
- L2 è il "gatekeeper" finale prima della Bag
- Timing istantaneo, nessun problema di performance

### Nuovo: `enterable_validator.py`

```python
"""Validator for enterable widgets."""

from dataclasses import dataclass
from typing import Any
from .type_converter import parse_typed_value

@dataclass
class ValidationResult:
    value: Any              # Valore (possibilmente modificato)
    error: str | None = None
    warnings: list[str] | None = None
    modified: bool = False


class EnterableValidator:
    """Validatore per widget enterable."""

    def validate(self, text: str, node_attr: dict) -> ValidationResult:
        """Valida input in base a dtype e attributi validate_*.

        Args:
            text: Stringa dal widget
            node_attr: Attributi del nodo (dtype, validate_*, etc.)

        Returns:
            ValidationResult con valore ed eventuali errori
        """
        dtype = node_attr.get("dtype", "T")
        result = ValidationResult(value=text)

        # 1. notnull check
        if node_attr.get("validate_notnull") and not text.strip():
            result.error = node_attr.get("validate_notnull_error", "Campo obbligatorio")
            return result

        if not text.strip():
            result.value = None
            return result

        # 2. Parse to typed value (verifica formato)
        try:
            typed_value = parse_typed_value(text, dtype)
        except ValueError as e:
            result.error = f"Formato non valido: {e}"
            return result

        # 3. len check (solo per stringhe)
        max_len = node_attr.get("validate_len")
        if max_len and len(text) > max_len:
            result.error = node_attr.get("validate_len_error", f"Max {max_len} caratteri")
            return result

        # 4. regex check
        pattern = node_attr.get("validate_regex")
        if pattern:
            import re
            if not re.fullmatch(pattern, text):
                result.error = node_attr.get("validate_regex_error", "Formato non valido")
                return result

        # 5. min/max check (per numerici)
        if dtype in ("I", "F", "N"):
            min_val = node_attr.get("validate_min")
            max_val = node_attr.get("validate_max")

            if min_val is not None and typed_value < min_val:
                result.error = node_attr.get("validate_range_error", f"Minimo: {min_val}")
                return result

            if max_val is not None and typed_value > max_val:
                result.error = node_attr.get("validate_range_error", f"Massimo: {max_val}")
                return result

        # 6. date range check
        if dtype in ("D", "H"):
            min_date = node_attr.get("validate_min_date")
            max_date = node_attr.get("validate_max_date")

            if min_date:
                from datetime import date
                min_d = date.fromisoformat(min_date) if isinstance(min_date, str) else min_date
                if typed_value < min_d:
                    result.error = f"Data minima: {min_date}"
                    return result

            if max_date:
                from datetime import date
                max_d = date.fromisoformat(max_date) if isinstance(max_date, str) else max_date
                if typed_value > max_d:
                    result.error = f"Data massima: {max_date}"
                    return result

        result.value = text
        return result
```

### Test

```python
def test_validate_notnull_error():
    v = EnterableValidator()
    result = v.validate("", {"validate_notnull": True})
    assert result.error == "Campo obbligatorio"

def test_validate_notnull_ok():
    v = EnterableValidator()
    result = v.validate("hello", {"validate_notnull": True})
    assert result.error is None

def test_validate_len_error():
    v = EnterableValidator()
    result = v.validate("toolong", {"validate_len": 5})
    assert result.error is not None

def test_validate_min_error():
    v = EnterableValidator()
    result = v.validate("5", {"dtype": "I", "validate_min": 10})
    assert result.error is not None

def test_validate_max_ok():
    v = EnterableValidator()
    result = v.validate("50", {"dtype": "I", "validate_max": 100})
    assert result.error is None

def test_validate_decimal_format_error():
    v = EnterableValidator()
    result = v.validate("not_a_number", {"dtype": "N"})
    assert result.error is not None

def test_validate_date_format_error():
    v = EnterableValidator()
    result = v.validate("not_a_date", {"dtype": "D"})
    assert result.error is not None

def test_validate_date_ok():
    v = EnterableValidator()
    result = v.validate("2026-01-21", {"dtype": "D"})
    assert result.error is None
```

---

## Blocco 12: Integrazione Type Conversion nel Compile

**Obiettivo**: Durante compile, configurare widget Input con validators Textual basati su dtype.

### Modifiche a `_compile_node` in TextualBuilder

```python
def _compile_node(self, node: BagNode) -> Generator[Widget, None, None]:
    tag = node.tag or "static"
    attr = dict(node.attr)

    schema_info = self.get_schema_info(tag)

    # NUOVO: Check se è un enterable
    if self._is_enterable(tag):
        yield from self._compile_enterable(node, attr, schema_info)
        return

    # ... resto del codice esistente ...


def _is_enterable(self, tag: str) -> bool:
    """Check se il tag eredita da @enterable."""
    try:
        info = self.get_schema_info(tag)
        inherits = info.get("inherits_from", "")
        return "@enterable" in inherits or "@numeric_enterable" in inherits or "@date_enterable" in inherits
    except KeyError:
        return False


def _compile_enterable(
    self,
    node: BagNode,
    attr: dict,
    schema_info: dict,
) -> Generator[Widget, None, None]:
    """Compila widget enterable con type conversion e validators."""
    from textual.widgets import Input
    from textual.validation import Number, Integer, Function

    dtype = attr.get("dtype", "T")
    validators = []

    # Aggiungi validators Textual basati su dtype
    if dtype == "I":
        validators.append(Integer())
    elif dtype in ("F", "N"):
        validators.append(Number())
    elif dtype == "D":
        validators.append(Function(
            lambda v: self._validate_date_format(v),
            "Formato data non valido (YYYY-MM-DD)"
        ))

    # Aggiungi validators da attributi validate_*
    if attr.get("validate_regex"):
        import re
        pattern = attr["validate_regex"]
        validators.append(Function(
            lambda v, p=pattern: bool(re.fullmatch(p, v)),
            attr.get("validate_regex_error", "Formato non valido")
        ))

    # Costruisci kwargs per Input
    kwargs = self._build_widget_kwargs(attr)
    kwargs["validators"] = validators if validators else None

    # Crea widget
    widget = Input(**kwargs)
    node.compiled["widget"] = widget
    node.compiled["dtype"] = dtype  # Salva per conversione successiva

    yield widget


def _validate_date_format(self, value: str) -> bool:
    """Valida formato data ISO."""
    try:
        from datetime import date
        date.fromisoformat(value)
        return True
    except ValueError:
        return False
```

### Test

```python
def test_compile_input_with_dtype_decimal():
    """Input con dtype=N deve avere Number validator."""
    bag = Bag(builder=TextualBuilder)
    bag.input(value="", dtype="N", id="price")

    widgets = list(bag.builder.compile(bag))

    assert len(widgets) == 1
    # Verifica che abbia validators
    assert bag["price"].compiled.get("dtype") == "N"

def test_compile_input_with_dtype_date():
    """Input con dtype=D deve avere date validator."""
    bag = Bag(builder=TextualBuilder)
    bag.input(value="", dtype="D", id="birthdate")

    widgets = list(bag.builder.compile(bag))
    assert bag["birthdate"].compiled.get("dtype") == "D"
```

---

## Riepilogo Blocchi (Aggiornato)

| # | Blocco | Dipende da | Output |
|---|--------|------------|--------|
| 0 | Indice Nodi | - | `_node_index`, `get_node_by_id()` |
| 1 | Cleanup Pattern | 0 | `cleanup_node()` |
| 2 | Handler DEL | 1 | DEL con cleanup |
| 3 | Handler INS | 0, 1 | INS mirato |
| 4 | Handler UPD | 1, 3 | UPD strutturale |
| 5 | upd_value vs upd | 4 | Differenziazione eventi |
| 6 | Pending Queue | 0-5 | Coda eventi |
| 7 | Freeze Pattern | 6 | Batch mode |
| 8 | AfterBuild | 6 | Callback post-build |
| **9** | **@enterable Schema** | - | Abstract per input widgets |
| **10** | **Type Converter** | 9 | Conversione tytx ↔ widget |
| **11** | **Enterable Validator** | 10 | Validazione con dtype |
| **12** | **Compile Integration** | 9, 10, 11 | Widget con validators |

---

## Ordine Suggerito (Aggiornato)

```
Blocco 0 (Indice Nodi)
    │
    ├─► Blocco 1 (Cleanup Pattern)
    │       │
    │       ├─► Blocco 2 (Handler DEL)
    │       │
    │       └─► Blocco 3 (Handler INS)
    │               │
    │               └─► Blocco 4 (Handler UPD)
    │                       │
    │                       └─► Blocco 5 (upd_value vs upd)
    │
    ├─► Blocco 6 (Pending Queue)
    │       │
    │       ├─► Blocco 7 (Freeze Pattern)
    │       │
    │       └─► Blocco 8 (AfterBuild)
    │
    └─► Blocco 9 (@enterable Schema)
            │
            └─► Blocco 10 (Type Converter)
                    │
                    └─► Blocco 11 (Enterable Validator)
                            │
                            └─► Blocco 12 (Compile Integration)
```

---

## Dopo il Piano Struttura

Una volta completato questo piano, si procede con il **Piano Data Binding** (`implementation-plan.md`) che costruisce sopra questo:
- Data Bag (`self._data`)
- Path resolution
- Binding `^path`, `=path`, `==formula`
- Trigger data → widget
- **Integrazione type conversion nel flusso widget ↔ data**

---

## Note

- Ogni blocco ha test isolati
- Si può fare commit dopo ogni blocco
- Se un blocco fallisce, non compromette i precedenti
- Test con app Textual reale per integration test
- **Blocchi 9-12 sono indipendenti da 0-8** e possono essere sviluppati in parallelo
