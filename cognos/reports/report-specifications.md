# Report catalog — implementation requires Cognos 12

## R01 Executive sales performance

Date range, region, category. Net revenue, gross profit, gross margin percentage, units sold, line count. Drill-through to store. Distinct orders is sourced from detailed sales, not from additive product daily line counts.

## R02 Product profitability

Category, brand, store. Revenue, cost, gross profit, margin%. Reconcile ratio-of-sums to SQL, never average individual product margin percentages.

## R03 Store performance

Date range, region. Revenue, units and distinct orders. IMPORTANT: distinct orders are not additive across product dimension rollups.

## R04 Inventory snapshot

Source: `mart.v_inventory_snapshot`. Store/category filters and one snapshot date. Units are additive across store/product within the same snapshot date, but not across dates. Latest snapshot is defined only inside explicit reporting scope; specify that scope in the report metadata.

## R05 Baseline versus optimized

One variant sources line-grain `v_sales_detail`, one uses `v_sales_daily`; same date/store revenue grain, filters, format, output and cache/concurrency settings. Compare generated SQL and Cognos end-to-end durations. Do not compare distinct-order counts because the aggregated source does not represent them.

## R06 Framework Manager vs Data Module

Same sales and inventory KPI contracts authored independently against the same warehouse. Verify display filters, SQL, joins, aggregation and rendering for equivalence. Save screenshots and sanitized exports; Cognos environment is required.
