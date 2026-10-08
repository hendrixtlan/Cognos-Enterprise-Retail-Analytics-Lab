# Cognos Analytics 12: Framework Manager build guide (Cognos required)

**Dependency:** licensed Cognos Analytics 12 server + compatible Framework Manager desktop tooling. Local Docker only runs PostgreSQL.

1. Create a read-only PostgreSQL runtime login outside the repo; grant the `cognos_reporting` NOLOGIN role created by `retail-lab optimize`. Configure JDBC where required for dynamic query mode/dashboard compatibility; validate connectivity from the Cognos server, not just the desktop.
2. Import the warehouse dimensions and fact/query subjects. Name namespaces `Physical`, `Business`, `Presentation`. Keep separate business query paths for line-detail sales, daily-product sales aggregates and snapshot inventory to avoid fanout.
3. Use `semantic/relationship_matrix.csv` to define and verify one-to-many relationships from conformed date/store/product dimensions; use `semantic/determinants.csv` for determinant keys. Non-unique Year and Year-Month determinants group by the documented composite items.
4. Sales line grain: `sale_id` unique, `order_id` repeated. Daily sales materialized view grain: `(date_key,store_key,product_key)`. Inventory grain: `(date_key,store_key,product_key)` with snapshots on a configured interval.
5. Define metric expressions from `semantic/kpi_catalog.json`. Revenue/cost/units/line count are additive. Gross margin and distinct orders are non-additive. Inventory on-hand is semi-additive and should never sum across dates.
6. Do NOT model `sales_line_count` as transaction count. Do NOT sum product-grain distinct-order subtotals to derive unique store-level orders.
7. Validate model query subjects, generated SQL and aggregation behavior in test queries. Publish a `Retail Analytics` package to a controlled Cognos folder with query mode recorded.
8. Build reports R01–R06. Reconcile detail-level measures and snapshot balances to reference SQL. Capture identical parameter sets, generated SQL and run times; keep PostgreSQL plan timings separate from report rendering time.
9. Export sanitized model/package/report artifacts after actual Cognos authoring; never invent a `.cpf` file or publish credentials.

## Acceptance evidence

- Determinant/cardinality screenshots and successful test queries
- Published package verification and source-controlled export where tooling permits
- R01/R02/R03/R04 KPI comparison against PostgreSQL reference
- R05 identical-result verified end-to-end timing comparison

Official IBM references:
- https://www.ibm.com/docs/en/cognos-analytics/12.0.x?topic=subjects-determinants
- https://www.ibm.com/docs/en/cognos-analytics/12.0.x?topic=packages-publishing
- https://www.ibm.com/docs/en/cognos-analytics/12.0.x?topic=udqm-enabling-framework-manager-models-packages-use-dynamic-query-mode
