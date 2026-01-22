# Data Binding Architecture

**Status**: 🔴 DA REVISIONARE
**Data**: 2026-01-21

---

## Overview

Questo documento descrive l'architettura del data binding tra Bag struttura (UI) e Bag dati, un pattern fondamentale di Genropy che permette:

1. **Separazione UI/Dati**: La struttura dell'interfaccia è indipendente dai dati
2. **Rilocabilità**: Componenti riusabili che funzionano con qualsiasi path dati
3. **Reattività**: Cambiamenti nei dati aggiornano automaticamente l'UI
4. **Bidirezionalità**: Input dell'utente aggiorna automaticamente i dati

---

## Le Due Bag

| Bag | Contenuto | Esempio |
|-----|-----------|---------|
| **Struttura** (`page`) | Definizione UI: widget, layout, attributi | `page.input(value="^.nome")` |
| **Dati** (`data`) | Valori applicativi | `data["cliente.nome"] = "Mario"` |

```python
class MyApp(BagApp):
    def build(self):
        # Bag struttura
        self.page.vertical(datapath="cliente")
            self.page.input(value="^.nome")
            self.page.input(value="^.cognome")

        # Bag dati
        self.data["cliente.nome"] = "Mario"
        self.data["cliente.cognome"] = "Rossi"
```

---

## Sintassi dei Path

### Prefissi

| Prefisso | Nome | Comportamento | Subscription |
|----------|------|---------------|--------------|
| `^path` | **Trigger** | Bidirezionale: legge e scrive | ✅ Sì |
| `=path` | **Value** | One-way: solo lettura al render | ❌ No |
| `==expr` | **Formula** | Espressione JavaScript/Python | Dipende |

### Esempi

```python
# ^path - Bidirezionale con subscription
page.input(value="^.nome")
# → Legge da data, scrive su data, si aggiorna quando data cambia

# =path - Lettura one-way
page.static(text="=.titolo")
# → Legge da data al momento del render, non si aggiorna

# ==formula - Espressione calcolata
page.static(text="==f'{nome} {cognome}'", nome="^.nome", cognome="^.cognome")
# → Ricalcola quando nome o cognome cambiano
```

---

## L'Attributo `datapath` - Contesto Dati

### Concetto Base

`datapath` definisce il "prefisso" per tutti i path relativi nei nodi discendenti.

```python
page.vertical(datapath="cliente")
    page.input(value="^.nome")      # Risolve a → "cliente.nome"
    page.input(value="^.cognome")   # Risolve a → "cliente.cognome"

    page.vertical(datapath=".indirizzo")  # Relativo al parent
        page.input(value="^.via")   # Risolve a → "cliente.indirizzo.via"
        page.input(value="^.citta") # Risolve a → "cliente.indirizzo.citta"
```

### Risoluzione: `abs_datapath()`

L'algoritmo risale la gerarchia dei nodi concatenando i `datapath`:

```
Nodo corrente: input(value="^.via")
    ↑
Parent: vertical(datapath=".indirizzo")
    ↑
Grandparent: vertical(datapath="cliente")
    ↑
Root: (nessun datapath)

Risoluzione:
".via"
→ ".indirizzo" + ".via" = ".indirizzo.via"
→ "cliente" + ".indirizzo.via" = "cliente.indirizzo.via"
```

### Regole di Risoluzione

| Path | Tipo | Comportamento |
|------|------|---------------|
| `.nome` | Relativo | Concatena con datapath del parent |
| `cliente.nome` | Assoluto | Usa direttamente, non cerca datapath |
| `.` | Corrente | Restituisce il datapath del nodo |
| `.?` | Attributi | Accede agli attributi del nodo dati |

---

## Path Simbolici (`#`)

I path simbolici permettono riferimenti dinamici e isolamento:

### `#nodeId` - Riferimento a Nodo

```python
page.input(id="search_field", value="^.search_term")
page.button(label="Cerca", action="^#search_field.value")
# → Legge il valore dall'input con id="search_field"
```

### `#DATA` - Path Assoluto

```python
page.vertical(datapath="form")
    page.static(text="^#DATA.app.title")
    # → Ignora datapath, va direttamente a "app.title"
```

### `#WORKSPACE` - Isolamento Componente

Permette a un componente di avere dati "privati" senza inquinare lo scope globale:

```python
page.vertical(_workspace="myFilter")
    page.input(value="^#WORKSPACE.temp_value")
    # → Risolve a "gnr.workspace.myFilter.temp_value"
    # Isolato dal resto dell'applicazione
```

### `#ROW` - Riga Corrente (in Griglie)

```python
grid.column(field="nome", edit="^#ROW.nome")
# → In ogni riga, punta ai dati di quella specifica riga
```

---

## `datapath` Dinamico

Il `datapath` stesso può essere un binding, permettendo contesti dati dinamici:

```python
# datapath statico
page.vertical(datapath="cliente")

# datapath come binding - cambia quando data["current_entity"] cambia
page.vertical(datapath="^.current_entity")

# datapath come funzione (Python)
page.vertical(datapath=lambda node: f"records.{node.attr.get('record_id')}")

# datapath simbolico
page.vertical(datapath="#selected_record")
```

---

## Riusabilità dei Componenti

### Il Pattern

Un componente usa **solo path relativi**, rendendolo completamente rilocabile:

```python
def address_form(parent):
    """Componente riusabile per indirizzo."""
    parent.input(value="^.via", placeholder="Via")
    parent.input(value="^.citta", placeholder="Città")
    parent.input(value="^.cap", placeholder="CAP")
```

### Uso in Contesti Diversi

```python
# Contesto 1: indirizzo cliente
page.vertical(datapath="cliente.indirizzo")
    address_form(page)
# → Legge/scrive: cliente.indirizzo.via, .citta, .cap

# Contesto 2: indirizzo fornitore
page.vertical(datapath="fornitore.sede")
    address_form(page)
# → Legge/scrive: fornitore.sede.via, .citta, .cap

# Contesto 3: indirizzo destinazione ordine
page.vertical(datapath="ordine.spedizione.destinazione")
    address_form(page)
# → Legge/scrive: ordine.spedizione.destinazione.via, .citta, .cap
```

Il componente `address_form` **non sa e non deve sapere** dove saranno i dati.

### Componenti con Workspace

Per componenti che necessitano stato interno:

```python
def filter_component(parent, filter_id):
    """Componente filtro con stato interno isolato."""
    parent.vertical(_workspace=f"filter_{filter_id}")
        # Stato interno (temporaneo, non persiste)
        parent.input(value="^#WORKSPACE.search_text")
        parent.checkbox(value="^#WORKSPACE.case_sensitive")

        # Output verso dati "reali"
        parent.button(label="Applica", action="apply_filter")

def apply_filter(node):
    search = node.get_relative_data("#WORKSPACE.search_text")
    # Scrive nel datapath "reale" del componente
    node.set_relative_data(".active_filter", search)
```

---

## Formule (`==`)

### Sintassi

```python
page.static(
    text="==f'{nome} {cognome}'",  # Formula Python
    nome="^.nome",                  # Variabile da binding
    cognome="^.cognome"             # Variabile da binding
)
```

### Risoluzione

1. Raccogli tutti gli attributi del nodo che NON sono formule
2. Per ogni attributo con `^` o `=`, risolvi il valore
3. Esegui la formula con questi valori come variabili
4. Se una variabile ha `^`, sottoscrivi per ricalcolo

### Casi d'Uso

```python
# Concatenazione
page.static(text="==f'Totale: {prezzo * quantita:.2f}€'",
            prezzo="^.prezzo", quantita="^.quantita")

# Condizionale
page.static(text="==('Attivo' if stato else 'Inattivo')",
            stato="^.is_active")

# Formattazione
page.static(text="==data.strftime('%d/%m/%Y')",
            data="^.data_nascita")
```

---

## Trigger sui Dati

### Flusso

```
data["cliente.nome"] = "Luigi"
        │
        ▼
Subscription trigger (path="cliente.nome")
        │
        ▼
Per ogni nodo con binding su quel path:
        │
        ├─► get_trigger_reason(node_path, event_path)
        │       │
        │       ├─► "node"      → path esatto modificato
        │       ├─► "child"     → modificato un discendente del mio path
        │       └─► "container" → modificato un antenato del mio path
        │
        ▼
update_widget_attr(attr, new_value)
```

### Trigger Reason - Algoritmo

La funzione `get_trigger_reason` confronta due path:
- **`node_path`**: il path a cui il nodo è sottoscritto (da `^path` risolto)
- **`event_path`**: il path dove è avvenuta la modifica nei dati

```python
def get_trigger_reason(node_path: str, event_path: str) -> str | None:
    """Determina la relazione tra path del nodo e path dell'evento."""

    # CASO 1: path identici
    if node_path == event_path:
        return 'node'

    # CASO 2: node_path INIZIA CON event_path + '.'
    # Il mio path è dentro il path modificato → il mio container è cambiato
    elif node_path.startswith(event_path + '.'):
        return 'container'

    # CASO 3: event_path INIZIA CON node_path + '.'
    # La modifica è dentro il mio path → un mio figlio è cambiato
    elif event_path.startswith(node_path + '.'):
        return 'child'

    # Nessuna relazione
    return None
```

### I Tre Casi Spiegati

| Reason | Condizione | Binding | Modifica | Significato |
|--------|------------|---------|----------|-------------|
| `node` | `node_path == event_path` | `^cliente.nome` | `cliente.nome` | Il dato esatto è cambiato |
| `child` | `event_path.startswith(node_path + '.')` | `^cliente` | `cliente.nome` | Un discendente è cambiato |
| `container` | `node_path.startswith(event_path + '.')` | `^cliente.nome` | `cliente` | Un antenato è stato sostituito |

### Esempi Dettagliati

```
Scenario 1: Modifica esatta
─────────────────────────────
Binding:  ^cliente.nome
Modifica: data["cliente.nome"] = "Luigi"
Risultato: 'node'
Azione: Aggiorna il valore del widget a "Luigi"


Scenario 2: Modifica di un discendente
──────────────────────────────────────
Binding:  ^cliente
Modifica: data["cliente.nome"] = "Luigi"
Risultato: 'child'
Azione: Potrei dover reagire se monitoro l'intera struttura
        (es. un componente che mostra "cliente" come oggetto)


Scenario 3: Sostituzione del container
──────────────────────────────────────
Binding:  ^cliente.nome
Modifica: data["cliente"] = new_cliente_bag  # Replace totale
Risultato: 'container'
Azione: Devo rileggere il mio valore perché il container è nuovo
        Il vecchio "cliente.nome" non esiste più, devo prendere
        il nuovo valore da new_cliente_bag["nome"]


Scenario 4: Nessuna relazione
─────────────────────────────
Binding:  ^cliente.nome
Modifica: data["fornitore.nome"] = "Acme"
Risultato: None
Azione: Nessuna (non mi riguarda)
```

### Comportamenti Speciali

```python
# In trigger_data():

if trigger_reason == 'child' and evt == 'fired':
    # Ignora eventi 'fired' su child
    # Serve per datapath dinamici che devono reagire
    # solo a cambiamenti del parent, non dei figli
    return

if trigger_reason and kw.reason == self:
    # Il nodo stesso ha causato la modifica
    # Ignora per evitare loop infiniti
    return
```

### Tabella Riassuntiva

| Il mio binding | Modifica a | Trigger Reason | Devo reagire? |
|----------------|------------|----------------|---------------|
| `^a.b.c` | `a.b.c` | `node` | ✅ Sì, dato esatto |
| `^a.b.c` | `a.b.c.d` | `child` | ⚠️ Dipende dal widget |
| `^a.b.c` | `a.b` | `container` | ✅ Sì, container sostituito |
| `^a.b.c` | `a` | `container` | ✅ Sì, container sostituito |
| `^a.b.c` | `x.y.z` | `None` | ❌ No, path diverso |

---

## Scrittura Widget → Bag (con Validazione)

Quando l'utente modifica un input, il valore deve passare attraverso validazioni prima di essere scritto sulla Bag dati.

### Flusso Completo

```
Input Widget (utente modifica)
        │
        ▼
    on_change(new_value)
        │
        ▼
 _do_change_in_data()
        │
        ├─► Controlla _modifying (anti-ricorsione)
        │
        ├─► abs_datapath('value') → risolve path
        │
        ├─► Confronta col valore corrente (ottimizzazione)
        │
        ├─► has_validations() ?
        │       │
        │       ▼
        │   validations_on_change()
        │       │
        │       ├─► validate_notnull
        │       ├─► validate_len
        │       ├─► validate_regex
        │       ├─► validate_call (custom)
        │       ├─► validate_remote (server)
        │       └─► ...
        │       │
        │       ▼
        │   result = {value, error, warnings}
        │       │
        │       ├─► Se error → return (NON SCRIVE)
        │       └─► Se ok → continua
        │
        ▼
 set_value_in_data(value, reason=self)
        │
        ▼
 data[path] = value  (con reason per evitare loop)
        │
        ▼
 Trigger pubblicato a tutti i subscriber
        │
        ▼
 Altri widget con binding su path
        │
        ├─► trigger_data() controlla reason != self
        │
        └─► update_widget_attr() → aggiorna widget
```

### Punto Centrale: `_do_change_in_data`

```python
def _do_change_in_data(self, source_node, value, value_attr=None):
    """Gestisce la modifica di un valore da widget verso la Bag dati."""

    # 1. Evita ricorsione durante validazioni
    if source_node._modifying:
        return

    # 2. Risolvi il path dall'attributo value (es. "^.nome" → "cliente.nome")
    path = source_node.attr_datapath('value')

    # 3. Ottieni il nodo dati corrispondente
    data_node = self.app.data.get_node(path)

    # 4. Normalizza: blank → null (configurabile)
    if source_node.get_inherited_attr('blank_is_null', True):
        value = None if value == '' else value

    # 5. Ottimizzazione: se il valore è lo stesso, esci
    if data_node.value == value:
        return

    # 6. VALIDAZIONE: se il nodo ha validazioni, eseguile
    if source_node.has_validations():
        result = source_node.validations_on_change(value)
        value = result['value']  # Il valore può essere modificato!

        # Gestione errori
        if result.get('error'):
            value_attr['_validation_error'] = result['error']
            # Pubblica messaggio di errore
            self.publish_error(f"{field_name}: {result['error']}")
            return  # NON scrive sulla bag se c'è errore!

        # Gestione warnings (scrive comunque)
        if result.get('warnings'):
            value_attr['_validation_warnings'] = result['warnings']

    # 7. Solo se passa validazione: scrivi sulla bag
    self.set_value_in_data(source_node, value, value_attr)
```

### Sistema di Validazione

```python
class Validator:
    """Validatore per valori dei widget."""

    # Tipi di validazione disponibili
    validation_tags = [
        'select',      # Valore deve essere nella lista
        'notnull',     # Campo obbligatorio
        'empty',       # Deve essere vuoto
        'case',        # Conversione maiuscolo/minuscolo
        'len',         # Lunghezza massima
        'min', 'max',  # Valori min/max per numeri
        'email',       # Formato email
        'regex',       # Pattern regex
        'call',        # Funzione custom
        'nodup',       # No duplicati
        'remote',      # Validazione server-side
    ]

    def validate(self, source_node, value) -> dict:
        """Esegue tutte le validazioni configurate.

        Returns:
            {
                'value': ...,           # Valore (possibilmente modificato)
                'modified': bool,       # Se la validazione ha modificato il valore
                'error': str | None,    # Errore (blocca scrittura)
                'warnings': list,       # Warnings (non bloccano)
                'required': bool,       # Se campo obbligatorio
            }
        """
        # Estrai validazioni da attributi validate_*
        validations = self._get_validations(source_node)

        result = {'value': value, 'warnings': []}

        for tag in self.validation_tags:
            if tag in validations:
                check_result = self._call_validation(tag, value, validations)

                if check_result.get('modified'):
                    result['value'] = check_result['value']
                    result['modified'] = True

                if check_result.get('error'):
                    result['error'] = check_result['message']
                    break  # Primo errore ferma la validazione

                if check_result.get('warning'):
                    result['warnings'].append(check_result['message'])

        return result
```

### Configurazione Validazioni (Attributi)

Le validazioni si configurano tramite attributi `validate_*` sul nodo:

```python
# Nella struttura (Bag page)
page.input(
    value="^.email",
    validate_notnull=True,
    validate_notnull_error="Email obbligatoria",
    validate_email=True,
    validate_email_error="Formato email non valido",
    validate_len=100,
    validate_len_error="Max 100 caratteri",
)

page.input(
    value="^.codice",
    validate_regex=r"^[A-Z]{3}\d{4}$",
    validate_regex_error="Formato: 3 lettere + 4 cifre",
    validate_call="return value.toUpperCase()",  # Trasforma in maiuscolo
)

page.input(
    value="^.quantita",
    validate_min=1,
    validate_max=1000,
    validate_notnull=True,
)
```

### Evitare Loop Infiniti

```python
def set_value_in_data(self, source_node, value, value_attr):
    """Scrive il valore sulla Bag dati evitando loop."""

    path = source_node.attr_datapath('value')

    # IMPORTANTE: passa source_node come 'reason'
    # Così quando il trigger arriva, il widget sa di ignorarlo
    self.app.data.set_item(
        path,
        value,
        value_attr,
        reason=source_node  # ← Chi ha causato la modifica
    )

# Nel trigger_data del widget:
def on_data_trigger(self, event):
    # Se sono io che ho causato la modifica, ignoro
    if event.reason == self:
        return

    # Altrimenti aggiorno il widget
    self.update_display(event.new_value)
```

### Flag `_modifying` (Anti-Ricorsione)

Alcune validazioni possono modificare il valore nel widget stesso:

```python
def validations_on_change(self, value):
    result = self.validator.validate(self, value)

    if result.get('modified'):
        # La validazione ha modificato il valore
        # Devo aggiornare il widget, ma senza ri-triggerare
        self._modifying = True
        self.widget.set_value(result['value'])
        self._modifying = False

    return result
```

### Validazione Remote (Server-Side)

```python
# validate_remote chiama il server
page.input(
    value="^.codice_fiscale",
    validate_remote="check_codice_fiscale",  # Nome metodo server
    validate_remote_error="Codice fiscale non valido",
)

# Sul server
def check_codice_fiscale(self, value):
    """Validazione server-side."""
    if not self.is_valid_cf(value):
        return {'error': 'invalid'}
    return True
```

---

## `get_relative_data` / `set_relative_data`

### API

```python
class BagNode:
    def get_relative_data(self, path, autocreate=False, default=None):
        """Legge dati usando path relativo al datapath del nodo."""
        abs_path = self.abs_datapath(path)
        return self.app.data[abs_path]

    def set_relative_data(self, path, value, **kw):
        """Scrive dati usando path relativo al datapath del nodo."""
        abs_path = self.abs_datapath(path)
        self.app.data[abs_path] = value
```

### Uso nei Widget

```python
# Nel widget
def on_change(self, new_value):
    # Scrive usando path relativo
    self.node.set_relative_data(self.node.attr["value"], new_value)

# Equivalente a (se value="^.nome" e datapath="cliente"):
self.app.data["cliente.nome"] = new_value
```

---

## Implementazione: Fasi

### Fase 1: Path Resolution
- [ ] `abs_datapath()` - risoluzione path relativi
- [ ] Supporto `datapath` statico
- [ ] Supporto path assoluti vs relativi

### Fase 2: Binding Base
- [ ] `^path` bidirezionale
- [ ] `=path` one-way
- [ ] Subscription setup durante compile

### Fase 3: Path Simbolici
- [ ] `#DATA` - path assoluto
- [ ] `#nodeId` - riferimento a nodo
- [ ] `#WORKSPACE` - isolamento

### Fase 4: Avanzato
- [ ] `datapath` dinamico (binding)
- [ ] Formule `==`
- [ ] `#ROW` per griglie

---

## Confronto Legacy JS vs Nuovo Python

| Aspetto | Legacy JS | Nuovo Python |
|---------|-----------|--------------|
| Bag dati | `genro._data` (globale) | `self.data` (istanza) |
| Risoluzione | `absDatapath()` | `abs_datapath()` |
| Lettura | `getRelativeData()` | `get_relative_data()` |
| Scrittura | `setRelativeData()` | `set_relative_data()` |
| Trigger | `dojo.subscribe('_trigger_data')` | `self.data.subscribe()` |
| Formula | `funcCreate()` | `eval()` o AST |

---

## Vantaggi dell'Architettura

1. **Componenti Riusabili**: Scrivi una volta, usa ovunque
2. **Separazione Concerns**: UI non conosce struttura dati
3. **Testabilità**: Testa componenti con dati mock
4. **Manutenibilità**: Cambia struttura dati senza toccare UI
5. **Composabilità**: Combina componenti liberamente

---

## Riferimenti

- Legacy: `gnrdomsource.js` → `absDatapath()`, `getRelativeData()`, `setRelativeData()`
- Legacy: `genro_src.js` → `trigger_data`, `stripData()`
- Doc: `evolutive_design/2026-01-21/triggers-dati.md`
