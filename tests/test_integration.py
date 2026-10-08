"""Requires RUN_DB_TESTS=1 and DATABASE_URL pointing to a disposable PostgreSQL DB."""
import os
from pathlib import Path

import pytest

from retail_lab.benchmark import benchmark
from retail_lab.db import connect, validate

pytestmark = pytest.mark.skipif(os.getenv("RUN_DB_TESTS") != "1", reason="No disposable PostgreSQL test DB configured")


def test_sales_inventory_and_semantic_grains():
    result = validate()
    assert result["sales_lines"] > result["distinct_orders"]
    assert result["inventory_snapshot_rows"] > 0
    with connect() as conn:
        # Distinct order count is not additive across product groups.
        total_orders = conn.execute("SELECT COUNT(DISTINCT order_id) FROM mart.fact_sales").fetchone()[0]
        product_orders = conn.execute("""
          SELECT SUM(order_count) FROM (
            SELECT product_key, COUNT(DISTINCT order_id) AS order_count
            FROM mart.fact_sales GROUP BY product_key
          ) p
        """).fetchone()[0]
        assert product_orders >= total_orders
        assert conn.execute("SELECT COUNT(*) FROM mart.v_inventory_snapshot").fetchone()[0] > 0


def test_benchmark_validates_equivalence(tmp_path: Path):
    out = tmp_path / "benchmark.json"
    summary = benchmark(out, repeats=2)
    assert set(summary) == {"baseline", "optimized"}
    assert '"equivalence"' in out.read_text()
