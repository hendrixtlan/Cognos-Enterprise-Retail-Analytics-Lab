# Verification and evidence strategy

## Contract checks (run without Cognos)

- `retail-lab contract`: validates structure of semantic KPI catalog.
- `pytest -q -k 'not integration'`: deterministic CSV generation, snapshot uniqueness, semantic types.
- PostgreSQL integration CI: actual DDL, COPY, materialized view, GRANT, totals reconciliation and benchmark.

## SQL performance evidence

`retail-lab benchmark` first compares the **complete** date/store revenue result in both directions using `EXCEPT ALL`. Any mismatch fails the benchmark. Then it warms both queries, alternates execution order, and saves client-observed duration samples and PostgreSQL `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` execution plans.

Do not claim a performance win without examining the resulting numbers. Treat runs as workload-specific. For rigorous comparisons, test multiple dataset sizes (100k / 1M / 5M), cold and warm cache, refresh costs, plan stability and concurrency; capture host characteristics.

## Cognos-dependent evidence

When Cognos 12 becomes available, collect for BOTH Framework Manager and Data Module implementations:

- Instance version/build, modeling client version, driver, query mode and connection type.
- Exported/sanitized package/model/report artifacts where supported.
- Screenshot evidence: dimensions, determinant settings, relationship/cardinality settings, aggregation behavior and published package.
- Generated/native SQL and report execution history with parameters, row counts, concurrency, cold/warm cache, format and report rendering.
- SQL reconciliation of revenue, margin, distinct orders and inventory balances.

Repository evidence never substitutes local PostgreSQL timings for Cognos server timings.
