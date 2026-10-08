-- Product-grain aggregates cannot safely provide additive distinct-order counts.
CREATE MATERIALIZED VIEW IF NOT EXISTS mart.mv_sales_daily AS
SELECT date_key, store_key, product_key, SUM(quantity)::bigint AS units_sold,
       SUM(sales_amount)::numeric(18,2) AS net_revenue,
       SUM(cost_amount)::numeric(18,2) AS cost,
       COUNT(*)::bigint AS sales_line_count
FROM mart.fact_sales
GROUP BY date_key, store_key, product_key
WITH NO DATA;
CREATE UNIQUE INDEX IF NOT EXISTS ux_mv_sales_daily
ON mart.mv_sales_daily(date_key, store_key, product_key);
