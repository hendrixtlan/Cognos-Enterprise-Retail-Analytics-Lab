-- Optional least-privilege role; NOLOGIN so no credentials are stored in repo.
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cognos_reporting') THEN
  CREATE ROLE cognos_reporting NOLOGIN;
 END IF;
END $$;
GRANT USAGE ON SCHEMA mart TO cognos_reporting;
GRANT SELECT ON mart.dim_date, mart.dim_store, mart.dim_product,
 mart.mv_sales_daily, mart.v_sales_detail, mart.v_sales_daily,
 mart.v_inventory_snapshot TO cognos_reporting;
-- To create a login, use credential management outside this repo, then:
-- GRANT cognos_reporting TO cognos_runtime;
-- Current inventory permissions via curated view only; no direct fact_inventory access.
