from retail_lab.benchmark import QUERIES, BASE, OPTIMIZED


def test_benchmark_paths_have_equivalent_grain():
    for sql in QUERIES.values():
        assert "date_key, store_key" in sql
        assert "ORDER BY revenue DESC, date_key, store_key LIMIT 25" in sql
    assert "fact_sales" in BASE
    assert "mv_sales_daily" in OPTIMIZED
