# Cognos Analytics 12 Data Module track (Cognos required)

IBM recommends Data Modules as the primary metadata-modeling environment. Build a second model from the same PostgreSQL curated views and dimensions to compare with the Framework Manager package.

1. Create a secured PostgreSQL data-server connection through the Cognos administration interface. Verify JDBC support for the exact Cognos 12 build.
2. Add `mart.v_sales_detail`, `mart.v_sales_daily`, `mart.v_inventory_snapshot` and the relevant dimensions to a new Data Module. Prefer one clearly documented join path per fact grain.
3. Define relationships using `semantic/relationship_matrix.csv` as the contract; confirm actual join paths in the module, rather than assuming they can be inferred correctly.
4. Implement KPI calculations from `semantic/kpi_catalog.json` using supported Cognos expressions. Reconcile all results with SQL reference calculations.
5. Ensure that inventory units are evaluated for exactly one date or an explicitly selected latest snapshot. Never sum balances across dates.
6. Create a report/dashboard from this module with the same dimensions, measures, filters, and output as the Framework Manager package report.
7. Capture version/build, connection mode, prompts, returned rows, generated SQL where supported, execution times and cache settings.

## Comparative tests

- Revenue, gross profit, margin and distinct orders must match SQL reference values.
- Distinct orders should not be summed from product-group subtotals; do not use product-grain line counts as distinct orders.
- Inventory balances should not be summed across multiple snapshot dates.
- Compare identical query paths, not just superficially similar visuals.
- Preserve exported module and report metadata only after creating it in a real Cognos environment; no native file is fabricated in this repository.

References:
- https://www.ibm.com/docs/en/cognos-analytics/12.0.x?topic=modules-data-framework-manager
- https://www.ibm.com/docs/en/cognos-analytics/12.0.x?topic=data-packages
