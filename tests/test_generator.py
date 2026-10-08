import csv
from collections import defaultdict

import pytest

from retail_lab.generate import generate


def test_deterministic_generation(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    first = generate(a, sales=31, stores=3, products=4, days=7, seed=9)
    second = generate(b, sales=31, stores=3, products=4, days=7, seed=9)
    assert first == second
    for name in ("dim_date", "dim_store", "dim_product", "fact_sales", "fact_inventory_daily"):
        assert (a / f"{name}.csv").read_bytes() == (b / f"{name}.csv").read_bytes()
    with (a / "fact_sales.csv").open() as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 31
    assert first["orders"] == 11
    assert all(int(row["quantity"]) > 0 for row in rows)
    assert all(float(row["discount_amount"]) <= int(row["quantity"]) * float(row["unit_price"]) for row in rows)
    order_keys = defaultdict(set)
    for row in rows:
        order_keys[row["order_id"]].add((row["date_key"], row["store_key"]))
    assert all(len(assignments) == 1 for assignments in order_keys.values())


def test_inventory_snapshot_grain(tmp_path):
    result = generate(tmp_path, sales=15, stores=2, products=3, days=9, inventory_step_days=4)
    assert result["inventory_snapshots"] == 18  # three dates * two stores * three products
    with (tmp_path / "fact_inventory_daily.csv").open() as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 18
    assert len({(r["date_key"], r["store_key"], r["product_key"]) for r in rows}) == 18
    assert all(int(r["on_hand_units"]) >= 0 for r in rows)


@pytest.mark.parametrize("kwargs", [{"sales": 0}, {"stores": 0}, {"products": -1},
                                    {"days": 0}, {"inventory_step_days": 0}])
def test_reject_invalid_sizes(tmp_path, kwargs):
    with pytest.raises(ValueError):
        generate(tmp_path, **kwargs)
