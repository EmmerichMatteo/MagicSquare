# MagicSquare

## Benchmark

Eseguire dalla sandbox di Codex, senza dipendenze aggiuntive:

```powershell
python benchmark.py
```

Avvia realmente `main.py` in un processo separato: 3 tentativi su quadrati
4x4, seed 42 e limite totale di 60 secondi. Il processo separato non crea
una sandbox: il comando va eseguito nella sandbox gia disponibile.

Per misurare i 100 tentativi previsti normalmente da main:

```powershell
python benchmark.py --rounds 100 --timeout 3600
```

Per una verifica rapida su quadrati 3x3:

```powershell
python benchmark.py --size 3 --rounds 1 --timeout 30
```

Il riepilogo mostra tempo totale del processo, tentativi completati, quadrati
risolti, percentuale di successo, fitness e matrice di ogni tentativo.
Un quadrato e risolto quando la fitness e zero e contiene tutti i numeri
da 1 a N^2 una sola volta. Il numero di soluzioni conta i tentativi riusciti,
non necessariamente quadrati distinti.

Ogni esecuzione salva `summary.json`, `rounds.jsonl` e l'output originale
`main.log` in una sottocartella di `benchmark-results/`, esclusa da Git.
Al timeout conserva i tentativi completati ed esce con codice 124; un errore
di main mantiene il relativo codice di uscita. Il tempo totale include avvio,
import e output; la media riguarda solo i tentativi completati. Un tentativo
ancora in corso al timeout non entra nella percentuale di successo.

Usare gli stessi parametri, seed, versione Python e macchina per confronti
tra modifiche; ripetere con seed diversi per valutare l'affidabilita della ricerca.
`python main.py` mantiene i valori originali: 100 tentativi, N=4, seed casuale.
