CREATE OR REPLACE VIEW mart.v_sales_detail AS
SELECT f.sale_id, f.order_id, d.calendar_date, d.calendar_year, d.calendar_month,
 s.store_code, s.region, s.city, p.sku, p.category, p.brand,
 f.quantity, f.sales_amount AS net_revenue, f.cost_amount AS cost,
 f.sales_amount - f.cost_amount AS gross_profit
FROM mart.fact_sales f
JOIN mart.dim_date d USING(date_key)
JOIN mart.dim_store s USING(store_key)
JOIN mart.dim_product p USING(product_key);
CREATE OR REPLACE VIEW mart.v_sales_daily AS
SELECT d.calendar_date, s.store_code, s.region, p.sku, p.category, p.brand,
 a.units_sold, a.net_revenue, a.cost, a.net_revenue-a.cost AS gross_profit,
 a.sales_line_count
FROM mart.mv_sales_daily a
JOIN mart.dim_date d USING(date_key)
JOIN mart.dim_store s USING(store_key)
JOIN mart.dim_product p USING(product_key);
CREATE OR REPLACE VIEW mart.v_inventory_snapshot AS
SELECT d.calendar_date, s.store_code, s.region, p.sku, p.category,
 i.on_hand_units
FROM mart.fact_inventory_daily i
JOIN mart.dim_date d USING(date_key)
JOIN mart.dim_store s USING(store_key)
JOIN mart.dim_product p USING(product_key);
