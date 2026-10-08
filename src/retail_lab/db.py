"""Warehouse bootstrap, COPY ingestion, materialized views, and integrity checks."""
from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TABLES = ("dim_date", "dim_store", "dim_product", "fact_sales", "fact_inventory_daily")


def connect():
    import psycopg
    return psycopg.connect(os.environ.get("DATABASE_URL", "postgresql://retail:retail_dev_only@localhost:5432/retail"))


def run_sql(conn, path: Path):
    conn.execute(path.read_text(encoding="utf-8"))


def init():
    with connect() as conn:
        run_sql(conn, ROOT / "warehouse/ddl/001_schema.sql")


def load(directory: Path):
    with connect() as conn:
        with conn.cursor() as cur:
            for table in TABLES:
                with (directory / f"{table}.csv").open("rb") as source:
                    with cur.copy(f"COPY mart.{table} FROM STDIN WITH (FORMAT CSV, HEADER TRUE)") as copy:
                        while chunk := source.read(1024 * 1024):
                            copy.write(chunk)
    return {"tables_loaded": list(TABLES)}


def optimize():
    with connect() as conn:
        run_sql(conn, ROOT / "warehouse/indexes/001_indexes.sql")
        run_sql(conn, ROOT / "warehouse/aggregates/001_daily_sales.sql")
        conn.execute("REFRESH MATERIALIZED VIEW mart.mv_sales_daily")
        run_sql(conn, ROOT / "warehouse/transformations/001_reporting_views.sql")
        run_sql(conn, ROOT / "warehouse/ddl/002_reporting_role.sql")
        conn.execute("ANALYZE mart.fact_sales")
        conn.execute("ANALYZE mart.fact_inventory_daily")
    return {"status": "materialized views refreshed; reporting grants applied"}


def validate():
    with connect() as conn:
        base = conn.execute("""
          SELECT COUNT(*), COUNT(DISTINCT order_id),
                 COALESCE(SUM(sales_amount), 0), COALESCE(SUM(cost_amount), 0)
          FROM mart.fact_sales
        """).fetchone()
        agg = conn.execute("""
          SELECT COALESCE(SUM(sales_line_count), 0),
                 COALESCE(SUM(net_revenue), 0), COALESCE(SUM(cost), 0)
          FROM mart.mv_sales_daily
        """).fetchone()
        if base[0] == 0 or (base[0], base[2], base[3]) != agg:
            raise AssertionError(f"Sales aggregate mismatch: base={base}, aggregate={agg}")
        malformed_orders = conn.execute("""
          SELECT COUNT(*) FROM (
            SELECT order_id FROM mart.fact_sales
            GROUP BY order_id HAVING COUNT(DISTINCT (date_key, store_key)) > 1
          ) inconsistent
        """).fetchone()[0]
        if malformed_orders:
            raise AssertionError(f"Orders have multiple date-store assignments: {malformed_orders}")
        inventory = conn.execute("SELECT COUNT(*), COALESCE(SUM(on_hand_units), 0) FROM mart.fact_inventory_daily").fetchone()
        if inventory[0] == 0:
            raise AssertionError("No inventory snapshot rows loaded")
        return {
            "sales_lines": base[0], "distinct_orders": base[1],
            "net_revenue": str(base[2]), "cost": str(base[3]),
            "gross_profit": str(base[2] - base[3]),
            "inventory_snapshot_rows": inventory[0],
            "inventory_units_all_dates_for_integrity_only": inventory[1],
            "note": "Never use the across-date inventory unit total as a business measure.",
        }
