"""Result-validated PostgreSQL benchmark; not evidence of Cognos runtime gains."""
from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from time import perf_counter

from .db import connect

BASE = """SELECT date_key, store_key, SUM(sales_amount) AS revenue
FROM mart.fact_sales GROUP BY date_key, store_key"""
OPTIMIZED = """SELECT date_key, store_key, SUM(net_revenue) AS revenue
FROM mart.mv_sales_daily GROUP BY date_key, store_key"""
ORDER = " ORDER BY revenue DESC, date_key, store_key LIMIT 25"
QUERIES = {"baseline": BASE + ORDER, "optimized": OPTIMIZED + ORDER}


def benchmark(output: Path, repeats: int = 5):
    if repeats < 1:
        raise ValueError("repeats must be positive")
    with connect() as conn:
        with conn.cursor() as cur:
            # Check the full result set in both directions, not only the top 25.
            for lhs, rhs in ((BASE, OPTIMIZED), (OPTIMIZED, BASE)):
                cur.execute("SELECT EXISTS(SELECT * FROM (" + lhs + ") a EXCEPT ALL SELECT * FROM (" + rhs + ") b)")
                if cur.fetchone()[0]:
                    raise AssertionError("Benchmark rejected: baseline and optimized SQL returned different data")
            results = {name: {"runs_ms": []} for name in QUERIES}
            for sql in QUERIES.values():
                cur.execute(sql)
                cur.fetchall()
            # Alternate execution order to reduce time-order bias.
            for iteration in range(repeats):
                ordered = tuple(QUERIES) if iteration % 2 == 0 else tuple(reversed(QUERIES))
                for name in ordered:
                    started = perf_counter()
                    cur.execute(QUERIES[name])
                    rows = cur.fetchall()
                    results[name]["runs_ms"].append(round((perf_counter() - started) * 1000, 3))
                    results[name]["output_rows"] = len(rows)
            for name, sql in QUERIES.items():
                results[name]["median_ms"] = median(results[name]["runs_ms"])
                cur.execute("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql)
                results[name]["plan"] = cur.fetchone()[0]
    payload = {
        "engine": "PostgreSQL", "scope": "database only; Cognos server and rendering excluded",
        "equivalence": "full grouped result sets equal (bidirectional EXCEPT ALL)",
        "repeats": repeats, "results": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return {name: result["median_ms"] for name, result in results.items()}
