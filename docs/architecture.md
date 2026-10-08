# Architecture and execution boundaries — v0.2

```text
Python deterministic retail simulator
    |-- dim_date, dim_store, dim_product
    |-- fact_sales.csv (one line per row, order_id shared across lines)
    `-- fact_inventory_daily.csv (store-product-date snapshot)
                        |
                        v
                 PostgreSQL 16
     mart.fact_sales / mart.fact_inventory_daily
              |                |
         indexed sales      inventory snapshot view
              |
      mart.mv_sales_daily (date x store x product)
              |
       reporting views + role grants
              |
       Shared KPI contracts + tests
              |
         +----+----+
         |         |
    Framework     Data Modules
    Manager       track
    package       (Cognos 12)
         |         |
         +----+----+
              |
      Cognos Reports/Dashboards
```

The Python generator, warehouse SQL, SQL benchmarks, catalog validator and CI database tests are executable without IBM tools. The Cognos modeling/reporting branches are **specifications** and require a real licensed Cognos 12 environment.

## Three different kinds of proof

1. **SQL correctness:** exact reconciliation of detail and preaggregated totals, order-grain integrity, inventory snapshot uniqueness and foreign keys.
2. **PostgreSQL performance:** full-result equivalence followed by controlled repeated queries and `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` plans. Report cache/format/layout not measured.
3. **Cognos semantic/report performance:** real Framework Manager model, report design, generated SQL and report runtime with consistent prompt values and workload. Requires Cognos installation.

## Modeling contracts

- Sales fact: `sale_id` unique, `order_id` nonunique. Distinct orders cannot be summed across product groups.
- Sales daily materialized view: unique `(date_key,store_key,product_key)` and additive monetary/units/line count; no distinct order KPI.
- Inventory fact: unique `(date_key,store_key,product_key)`; balances are semi-additive across time.
- KPI expression source of truth: `semantic/kpi_catalog.json`.
- Relationship and determinant specifications: `semantic/relationship_matrix.csv`, `semantic/determinants.csv`.

## Security and governance

`warehouse/ddl/002_reporting_role.sql` creates a NOLOGIN role with permission to curated reporting objects. Create/login and password rotation externally. No row-level or column-level security is implemented yet. Dev PostgreSQL is localhost-only with disposable example credentials. Protect report queries with managed credentials/TLS and configure content-store roles in Cognos.
