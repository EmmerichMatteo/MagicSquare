# MagicSquare

## University benchmark

`python main.py` apre il menu iniziale in inglese:
`1. Try algorithms` per la prova interattiva e `2. Run tests` per il benchmark.
Il menu dei test permette di scegliere 3x3?6x6, 7x7?10x10, una dimensione
singola n oppure un intervallo libero da a a b (inclusi, con 3 <= a <= b).
Poi chiede il numero di ripetizioni, la funzione di errore e, per ultima,
la configurazione iniziale opzionale.
Per dimensioni superiori a 10 chiede conferma, avvisando che la ricerca puo
richiedere molto tempo. Per ogni dimensione esegue
prima tutte le ripetizioni del backtracking, poi simulated annealing, poi genetico.
Ogni tentativo viene eseguito anche se il precedente ha trovato una soluzione.
Sia Try sia test chiedono la funzione di errore:
`1. Squared error` oppure `2. Absolute error`, con `b. Back` per tornare indietro.
La scelta vale per tutte le prove del benchmark e viene indicata nel report.

Il file `benchmark_unive/benchmark.py` salva un report di testo in inglese
in `benchmark_unive/benchmark-DATA-ORA.txt`, con impostazioni, tempi,
fitness, validita e matrici. I report sono esclusi da Git.
`Ctrl+C` interrompe il benchmark conservando i risultati completati.
Non viene imposto un timeout aggiuntivo ai singoli algoritmi.

Per configurare l'intervallo da axa a bxb e le ripetizioni dalla riga di comando:

```powershell
python benchmark_unive/benchmark.py --min-size 3 --max-size 6 --rounds 2
```

## Backtracking

`back_tracking(n)` riceve la dimensione e usa una copia di `Matrix.empty(n)`,
il modello condiviso di matrice con tutte le celle a zero.
Restituisce la matrice risolta oppure `None` se non esiste una soluzione.

```python
from Algorithms.backtracking.backtracking import back_tracking

solution = back_tracking(3)
if solution is not None:
    solution.print_matrix()
```

La ricerca usa MRV, LCV, forward checking per l'unicita e limiti Min/Max
sulle somme di righe, colonne e diagonali. Quando in una linea manca una
sola cella, ne assegna il valore obbligato; elimina inoltre dai domini i
candidati incompatibili con le somme. La propagazione continua fino a
stabilizzare i domini e scarta il ramo se un dominio diventa vuoto o una
somma e impossibile.

## Prova interattiva

La modalita `Try algorithms` chiede quale algoritmo avviare: `1` backtracking con
propagazione dei vincoli, `2` simulated annealing, `3` genetico.
Le scelte non valide vengono richieste nuovamente.
La schermata della dimensione non offre il back.
Le schermate successive mostrano la voce `b. Back` (dopo `3.` nel menu
algoritmi): dal menu algoritmi e dalla conferma si torna alla dimensione.
Dopo il risultato, `h. Home` torna al menu iniziale con prova e test.
La voce `e. Exit` chiude il programma.
Durante la ricerca, `Ctrl+C` interrompe il calcolo e
torna allo stesso menu.
Prima del menu viene chiesta la lunghezza del lato, un intero maggiore di 2.
Per lati superiori a 10 viene richiesta conferma, dato il possibile tempo di ricerca.
Anche `Matrix` e `Matrix.empty` richiedono un lato maggiore di 2.
Il genetico gestisce internamente fino a 100 tentativi (`MAX_ATTEMPTS`),
fermandosi alla prima soluzione. Try e benchmark chiamano la stessa funzione.
Per gli altri algoritmi, Try usa `ROUNDS` di `main.py` (default: 100).
La classe `Printer` in `Entities/printer.py` raccoglie i metodi statici
per stampare menu, soluzione, tempi e riepilogo.

## Funzioni di errore

In `Algorithms/functions.py`, `error_function_square` somma i quadrati degli
scarti dalla somma magica di righe, colonne e delle due diagonali.
`error_function_absolute` somma i valori assoluti degli stessi scarti.
Entrambe valgono zero quando tutte le somme coincidono con la somma magica.
Il backtracking usa i propri vincoli; la scelta determina la fitness riportata
anche per il suo risultato.

## Configurazione iniziale

Come ultima opzione, Try e test chiedono se fissare alcuni valori (`y`, `n`,
`b. Back`). La matrice si inserisce riga per riga, con valori separati da
spazi e `0` o `.` per le celle libere. La griglia si aggiorna dopo ogni riga,
pulendo lo schermo.
Nei test su intervallo si inserisce una configurazione separata per ogni
lato, condivisa da tutti gli algoritmi e tutte le ripetizioni di quel lato.
Una matrice di soli zeri lascia quella dimensione libera.

Le API `back_tracking(n, fixed_cells=None)`,
`genetic(f, n, fixed_cells=None)` e `simulated_annealing(f, n, fixed_cells=None)`
accettano un dizionario `{indice: valore}` con indice lineare da zero.
Il runner riceve `fixed_cells`; il benchmark riceve
`fixed_by_size={n: fixed_cells}`. I valori fissati vengono mantenuti durante
la ricerca e verificati nell'esito; le configurazioni possono anche non
ammettere una soluzione. Il report registra le celle fissate per ogni lato.

Ogni richiesta di input offre `h. Home` per tornare al menu iniziale e
`e. Exit` per uscire, anche durante l?inserimento delle righe.

Inserire n righe di n
valori separati da spazi, usando `0` o `.` nelle celle libere. Esempio 3x3:

```text
8 0 0
0 5 0
0 0 2
```

Questa configurazione viene passata a backtracking, genetico e simulated
annealing, che completano le celle libere mantenendo i valori fissati.
