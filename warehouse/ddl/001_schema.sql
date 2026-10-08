CREATE SCHEMA IF NOT EXISTS mart;
CREATE TABLE IF NOT EXISTS mart.dim_date (
 date_key integer PRIMARY KEY, calendar_date date NOT NULL UNIQUE,
 calendar_year integer NOT NULL, calendar_month integer NOT NULL,
 calendar_quarter integer NOT NULL
);
CREATE TABLE IF NOT EXISTS mart.dim_store (
 store_key integer PRIMARY KEY, store_code text NOT NULL UNIQUE,
 region text NOT NULL, city text NOT NULL
);
CREATE TABLE IF NOT EXISTS mart.dim_product (
 product_key integer PRIMARY KEY, sku text NOT NULL UNIQUE,
 category text NOT NULL, brand text NOT NULL, unit_cost numeric(12,2) NOT NULL CHECK (unit_cost >= 0)
);
-- Grain: one row per sale line. Order IDs may repeat across lines.
CREATE TABLE IF NOT EXISTS mart.fact_sales (
 sale_id bigint PRIMARY KEY,
 order_id bigint NOT NULL CHECK (order_id > 0),
 date_key integer NOT NULL REFERENCES mart.dim_date(date_key),
 store_key integer NOT NULL REFERENCES mart.dim_store(store_key),
 product_key integer NOT NULL REFERENCES mart.dim_product(product_key),
 quantity integer NOT NULL CHECK (quantity > 0),
 unit_price numeric(12,2) NOT NULL CHECK (unit_price >= 0),
 discount_amount numeric(12,2) NOT NULL CHECK (discount_amount >= 0),
 sales_amount numeric(14,2) GENERATED ALWAYS AS (quantity * unit_price - discount_amount) STORED,
 cost_amount numeric(14,2) NOT NULL CHECK (cost_amount >= 0),
 CONSTRAINT valid_discount CHECK (discount_amount <= quantity * unit_price)
);
-- Grain: date-store-product snapshot. Units must NOT be summed over dates.
CREATE TABLE IF NOT EXISTS mart.fact_inventory_daily (
 date_key integer NOT NULL REFERENCES mart.dim_date(date_key),
 store_key integer NOT NULL REFERENCES mart.dim_store(store_key),
 product_key integer NOT NULL REFERENCES mart.dim_product(product_key),
 on_hand_units integer NOT NULL CHECK (on_hand_units >= 0),
 PRIMARY KEY (date_key, store_key, product_key)
);
