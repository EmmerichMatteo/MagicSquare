"""Lancia main.py in un processo separato e misura tempo e risultati."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--size", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--timeout", type=float, default=60,
                        help="Limite in secondi (default: 60)")
    args = parser.parse_args()
    if args.rounds <= 0 or args.size < 3 or not 0 < args.timeout < float("inf"):
        parser.error("Servono rounds > 0, size >= 3 e un timeout positivo finito")

    root = Path(__file__).resolve().parent
    output = root / "benchmark-results" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    output.mkdir(parents=True)
    records_path = output / "rounds.jsonl"
    command = [sys.executable, "-u", str(root / "main.py"),
               "--rounds", str(args.rounds), "--size", str(args.size),
               "--seed", str(args.seed), "--report", str(records_path)]
    print(f"Avvio main: {args.rounds} tentativi, {args.size}x{args.size}, "
          f"seed {args.seed}, limite {args.timeout:g}s", flush=True)
    start = time.perf_counter()
    with (output / "main.log").open("w", encoding="utf-8") as log:
        try:
            process = subprocess.run(command, cwd=root, stdout=log,
                                     stderr=subprocess.STDOUT, timeout=args.timeout)
            status = "completed" if process.returncode == 0 else "error"
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            status, returncode = "timeout", None
    elapsed = time.perf_counter() - start
    records = []
    if records_path.exists():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # Un timeout puo interrompere la scrittura dell'ultima riga.
                continue
    solved = sum(record["solved"] for record in records)
    summary = {
        "status": status, "returncode": returncode, "wall_seconds": elapsed,
        "settings": vars(args), "python": sys.version, "platform": platform.platform(),
        "completed_rounds": len(records), "solved": solved,
        "success_rate": solved / len(records) if records else None,
        "mean_round_seconds": statistics.mean(r["seconds"] for r in records) if records else None,
        "best_fitness": min((r["fitness"] for r in records), default=None),
        "rounds": records,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    labels = {"completed": "completato", "timeout": "limite di tempo raggiunto", "error": "errore"}
    print(f"Stato: {labels[status]} | Tempo totale: {elapsed:.3f}s")
    print(f"Tentativi completati: {len(records)}/{args.rounds} | Quadrati risolti: {solved}")
    if records:
        print(f"Successo sui tentativi completati: {summary['success_rate']:.1%} | "
              f"Tempo medio: {summary['mean_round_seconds']:.3f}s")
    for record in records:
        outcome = "RISOLTO" if record["solved"] else "non risolto"
        print(f"  Tentativo {record['round']}: {outcome}, "
              f"fitness {record['fitness']}, {record['seconds']:.3f}s")
        for row in range(args.size):
            print("    " + " ".join(f"{v:3d}" for v in record["matrix"][row * args.size:(row + 1) * args.size]))
    if status == "timeout":
        print("Il tentativo interrotto non e incluso nei risultati.")
    print(f"Report e log: {output}")
    return 124 if status == "timeout" else (returncode or 0)


if __name__ == "__main__":
    raise SystemExit(main())
