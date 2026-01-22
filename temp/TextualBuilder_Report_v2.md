# Report di Revisione -- TextualBuilder & TextualApp

## Contesto

Questo report analizza l'attuale implementazione di **TextualBuilder** e
**TextualApp**, che trasformano una `Bag` in una UI Textual tramite un
approccio dichiarativo/imperativo controllato.

L'architettura è coerente con: - modello Bag-driven - renderer
esplicito - assenza di data-binding automatico

------------------------------------------------------------------------

## Punti di Forza

-   Separazione netta:
    -   **Bag** → modello / ricetta
    -   **Builder** → renderer Textual
    -   **Textual** → runtime UI
-   Uso corretto di `@element` con schema dichiarativo
-   Gestione esplicita dei casi speciali:
    -   `TabbedContent` / `TabPane`
    -   `DataTable` come widget non-container
-   Proxy `node.compiled["widget"]` ben definito
-   Base pronta per renderer alternativi (DOM, PyQt)

------------------------------------------------------------------------

## Problemi e Migliorie

### 1. Gestione del parametro `content`

Attualmente il contenuto del nodo Bag viene passato come primo argomento
posizionale **solo** se il parametro si chiama `content`.

Questo è troppo restrittivo: - `Button` usa tipicamente `label` - altri
widget usano `text`, `title`, ecc.

#### Raccomandazione

Mappare il valore leaf sul **primo parametro posizionale reale** della
signature:

-   individuare il primo parametro dopo `self`
-   se non già presente in kwargs, assegnare lì il contenuto

Questo rende il builder robusto senza hardcoding.

------------------------------------------------------------------------

### 2. `DataTable.add_row()` e parametri opzionali

`height` non è garantito come parametro valido in tutte le versioni di
Textual.

#### Raccomandazione

Filtrare i parametri di `add_row()` in base alla signature (come già
fatto per i costruttori) per evitare errori runtime.

------------------------------------------------------------------------

### 3. `DataTable` come widget non-container

La scelta di introdurre: - `datatable` - `column` - `row` con
`_compile_datatable()` dedicato è **corretta e ben progettata**.

È importante mantenere questa regola: - nessun `mount()` di figli dentro
`DataTable` - solo `add_column()` / `add_row()`

------------------------------------------------------------------------

### 4. `TabPane` e `TabbedContent`

L'uso di `add_pane()` è corretto.

Si raccomanda di: - vietare il montaggio diretto di `TabPane` fuori da
`TabbedContent` - mantenere `_compile_tabpane_for_tabbedcontent` come
unico entry point valido

------------------------------------------------------------------------

### 5. Lifecycle Textual (`compose` / `on_mount`)

`compile()` viene chiamato in `on_mount`.

#### Nota

In Textual moderno: - `mount()` può essere awaitable - l'ordine di mount
può influire su layout e focus

La soluzione attuale è accettabile, ma in futuro si può valutare: -
`compile()` async - `await mount(...)` per massima robustezza

------------------------------------------------------------------------

## Raccomandazioni Architetturali

-   Considerare il Builder come **renderer pluggabile**
-   Mantenere la Bag come **single source of truth**
-   Preferire rebuild deterministici a binding impliciti
-   Usare compile dedicati per widget "strutturali" o "non container"

------------------------------------------------------------------------

## Conclusione

L'implementazione attuale è **solida**, coerente e molto ben allineata
alla filosofia di Textual.

Con pochi aggiustamenti mirati: - gestione più intelligente di
`content` - filtraggio dei parametri di `add_row` - controllo più
stretto dei widget speciali

il sistema diventa un **renderer UI generale**, riutilizzabile e stabile
su più backend.

È una base eccellente per un DSL UI realmente cross-renderer.
