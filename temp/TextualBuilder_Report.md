# Report di Revisione -- TextualBuilder (Bag → Textual)

## Contesto

Il `TextualBuilder` compila una `Bag` in widget Textual usando: - schema
dichiarativo (`@element`) - mapping `tag → compile_class` - `mount()`
ricorsivo - override per casi speciali (`TabbedContent`, `TabPane`,
`Static`)

L'architettura è **coerente**, **estendibile** e allineata al modello
Bag-driven.\
Ci sono però alcuni **punti critici** da correggere per robustezza e
correttezza semantica.

------------------------------------------------------------------------

## Punti di Forza

-   Separazione chiara: **Bag (modello)** → **Builder (renderer)** →
    **Textual (vista)**
-   Uso corretto di `@element` con `compile_module` / `compile_class`
-   Override mirati per widget non banali (`TabbedContent`)
-   Salvataggio proxy `node.compiled["widget"]`
-   Auto-generazione `id` (utile per debug/devtools)

------------------------------------------------------------------------

## Problemi Critici

### 1) Uso improprio del parametro posizionale `content`

Attualmente molti widget vengono istanziati come:

``` python
widget = textual_class(content, **kwargs)
```

Questo **non è valido** per molti widget Textual (`Input`, `DataTable`,
`Tree`, ecc.) e può causare: - `TypeError` - interpretazione errata
degli argomenti - bug silenziosi

**Correzione consigliata**\
Istanziare sempre con keyword, mappando `content` solo se supportato
dalla signature.

------------------------------------------------------------------------

### 2) `DataTable` trattata come container

`DataTable` non è un container di widget: - le righe **non** si
montano - vanno aggiunte con `add_row()`

Serve un `_compile_datatable` dedicato che: - monti la tabella - legga i
dati dalla Bag - chiami `add_columns()` e `add_row()`

------------------------------------------------------------------------

### 3) `TabPane` fuori contesto `TabbedContent`

`TabPane` deve essere aggiunto con `add_pane()` e non montato
genericamente.

È consigliato: - vietare `TabPane` fuori da `TabbedContent` - o gestirlo
esplicitamente con controllo del parent

------------------------------------------------------------------------

## Raccomandazioni Architetturali

-   Tenere `content` come concetto **di ricetta**, non come argomento
    universale
-   Usare compile dedicati per widget "non-container"
-   Mantenere la Bag come **single source of truth**
-   Considerare il builder come renderer pluggabile (Textual / DOM /
    PyQt)

------------------------------------------------------------------------

## Conclusione

Il `TextualBuilder` è **molto ben allineato** con la filosofia di
Textual e con il modello Bag. Con pochi aggiustamenti mirati diventa un
renderer: - robusto - deterministico - multi-backend ready

È una base solida per un DSL UI realmente cross-renderer.
