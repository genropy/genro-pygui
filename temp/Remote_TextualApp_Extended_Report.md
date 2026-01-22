# Report Tecnico Estremamente Dettagliato

## Sistema di Remote Control, Registry e CLI per TextualApp / BagApp

------------------------------------------------------------------------

## 1. Obiettivo del sistema

Il sistema implementa un meccanismo di **controllo remoto interattivo**
per applicazioni basate su `TextualApp` e `Bag`, con i seguenti
obiettivi:

-   Avviare un'applicazione Textual come **processo separato**
-   Registrarla tramite un **nome logico**
-   Consentire a un altro processo (REPL) di:
    -   modificare la `page` (Bag UI)
    -   osservare effetti immediati sull'interfaccia
-   Supportare workflow:
    -   `textual run foo.py`
    -   `textual run foo.py -c`
    -   `textual connect foo`

Il sistema è composto da tre blocchi principali:

1.  **Remote layer** (socket + proxy)
2.  **Registry** (name → port)
3.  **CLI orchestration**

------------------------------------------------------------------------

## 2. Architettura complessiva

    ┌─────────────┐        socket        ┌────────────────────┐
    │  REPL       │  ─────────────────▶ │  RemoteServer      │
    │  (client)   │                     │  (in TextualApp)  │
    └─────┬───────┘                     └─────────┬──────────┘
          │                                       │
          │ PageProxy                             │ _safe_call
          ▼                                       ▼
    ┌─────────────┐                     ┌────────────────────┐
    │ RemoteProxy │                     │  TextualApp.page   │
    └─────────────┘                     │  (Bag + Builder)   │
                                        └────────────────────┘

------------------------------------------------------------------------

## 3. RemoteProxy / PageProxy (Client side)

### 3.1 Responsabilità

-   Serializzare chiamate Python locali
-   Trasmetterle via socket
-   Ricevere il risultato
-   Esporre un'API "trasparente" simile alla Bag reale

### 3.2 Meccanismo attuale

``` python
cmd = "__call__:method_name:<pickle_hex>"
```

Operazioni supportate: - `__call__` - `__getitem__` - `__setitem__` -
`__keys__`

### 3.3 Problemi critici

#### 3.3.1 Uso di `pickle` (CRITICO)

`pickle.loads()` consente esecuzione di codice arbitrario.

**Implicazioni:** - RCE locale - escalation tra utenti - rischio in
ambienti condivisi / container

**Mitigazioni minime consigliate:** - bind solo su `localhost` (già
presente) - token segreto obbligatorio per ogni comando - rifiuto
connessioni senza handshake valido

------------------------------------------------------------------------

#### 3.3.2 Framing TCP assente

Uso diretto di:

``` python
recv(65536)
```

**Problema:** - TCP non garantisce confini di messaggio - payload \> 64k
o spezzati causano corruzione

**Soluzione standard:** - prefisso di lunghezza (4 o 8 byte) - lettura
esatta di N byte

------------------------------------------------------------------------

#### 3.3.3 Uso di `send` invece di `sendall`

`send()` può inviare solo parte del buffer.

**Correzione:** - usare sempre `sendall()` lato client e server

------------------------------------------------------------------------

## 4. RemoteServer (Server side)

### 4.1 Threading model

-   Un thread dedicato
-   Loop `accept()`
-   Gestione sincrona delle connessioni

### 4.2 Problemi

#### 4.2.1 `listen(1)` troppo restrittivo

Coda di una sola connessione → rifiuti sporadici.

**Fix:**

``` python
server.listen(50)
```

------------------------------------------------------------------------

#### 4.2.2 Mancata restituzione dei valori

Il server ignora il valore di ritorno dei metodi remoti:

``` python
self._app._safe_call(do_call)
return "ok"
```

**Effetto:** - Il client non può usare risultati - API "monca" rispetto
alla Bag reale

**Fix concettuale:** - `_safe_call()` deve ritornare il valore - il
server deve serializzarlo come risposta

------------------------------------------------------------------------

#### 4.2.3 `_safe_call` non definito

Il corretto funzionamento **dipende interamente** da `_safe_call`.

### 4.3 Requisiti reali di `_safe_call`

-   esecuzione nel thread UI di Textual
-   serializzazione delle mutazioni UI
-   possibilità di:
    -   bloccare il thread server
    -   restituire valore o eccezione

**Modello corretto:**

    thread socket
       ↓
    post callback nel loop UI
       ↓
    attendere completamento
       ↓
    ritornare risultato

Senza questo, il sistema è **intrinsecamente instabile**.

------------------------------------------------------------------------

## 5. Registry

### 5.1 Funzione

Mappare:

    app_name → port

### 5.2 Problemi

#### 5.2.1 Race condition

Scritture concorrenti non protette.

#### 5.2.2 Permessi file

`/tmp/bagapp_registry.json`: - potenzialmente leggibile/scrivibile da
altri utenti

### 5.3 Fix minimi

-   lock file (fcntl o O_EXCL)
-   chmod 600
-   scrittura atomica (write → rename)

------------------------------------------------------------------------

## 6. CLI (`textual`)

### 6.1 Funzioni supportate

-   `run`
-   `run -c`
-   `run -r`
-   `list`
-   `connect`

### 6.2 `run -c`

Workflow: 1. spawn subprocess 2. polling registry 3. apertura REPL

**Problemi:** - timeout fisso (2s) - fragile su startup lenti

**Soluzioni:** - timeout configurabile - handshake esplicito via
stdout - retry adattivo

------------------------------------------------------------------------

## 7. Valutazione architetturale complessiva

### 7.1 Punti di forza

-   modello concettuale eccellente
-   Bag come single source of truth
-   REPL remoto estremamente potente
-   allineamento perfetto con filosofia Genropy

### 7.2 Rischi principali

  Area          Rischio
  ------------- --------------
  Sicurezza     pickle
  Stabilità     framing TCP
  UI safety     `_safe_call`
  Concorrenza   registry

------------------------------------------------------------------------

## 8. Roadmap consigliata (ordine)

1.  Framing + sendall
2.  Restituzione valori da remoto
3.  Implementazione robusta `_safe_call`
4.  Token di autenticazione
5.  Lock registry
6.  Estensione API PageProxy

------------------------------------------------------------------------

## 9. Conclusione

Il sistema è **concettualmente molto avanzato** e raro da vedere: - REPL
che modifica UI viva - separazione modello / renderer / runtime -
orchestrazione elegante via CLI

Tuttavia, allo stato attuale è: - **ottimo per sviluppo locale** - **non
ancora robusto per uso continuativo**

Con pochi interventi mirati diventa: \> un'infrastruttura di sviluppo di
altissimo livello, \> coerente con Genropy, \> e potenzialmente
riutilizzabile anche fuori da Textual.
