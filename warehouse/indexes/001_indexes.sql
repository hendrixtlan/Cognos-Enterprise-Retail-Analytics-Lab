CREATE INDEX IF NOT EXISTS ix_sales_date_store ON mart.fact_sales (date_key, store_key);
CREATE INDEX IF NOT EXISTS ix_sales_product_date ON mart.fact_sales (product_key, date_key);
CREATE INDEX IF NOT EXISTS ix_sales_store_product ON mart.fact_sales (store_key, product_key);
CREATE INDEX IF NOT EXISTS ix_sales_order ON mart.fact_sales (order_id);
CREATE INDEX IF NOT EXISTS ix_inventory_date_store ON mart.fact_inventory_daily (date_key, store_key);
