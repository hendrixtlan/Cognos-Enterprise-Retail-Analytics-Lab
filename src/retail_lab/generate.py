"""Deterministic CSV generator with explicit order-line and inventory-snapshot grains."""
from __future__ import annotations

import csv
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import numpy as np


def _money(amount: Decimal) -> str:
    return str(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def generate(
    out: Path, sales: int = 100_000, stores: int = 25, products: int = 200,
    days: int = 365, seed: int = 42, inventory_step_days: int = 7,
) -> dict[str, int]:
    if min(sales, stores, products, days, inventory_step_days) <= 0:
        raise ValueError("All sizes and the inventory interval must be positive")
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    start = date(2025, 1, 1)

    def write(name, header, rows):
        with (out / f"{name}.csv").open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)

    write("dim_date", ["date_key", "calendar_date", "calendar_year", "calendar_month", "calendar_quarter"],
          ((int((start + timedelta(days=i)).strftime("%Y%m%d")), (start + timedelta(days=i)).isoformat(),
            (start + timedelta(days=i)).year, (start + timedelta(days=i)).month,
            ((start + timedelta(days=i)).month - 1) // 3 + 1) for i in range(days)))
    write("dim_store", ["store_key", "store_code", "region", "city"],
          ((i, f"STORE-{i:04d}", ["North", "South", "Central", "West"][i % 4],
            ["Monterrey", "Merida", "Mexico City", "Guadalajara"][i % 4])
           for i in range(1, stores + 1)))
    # Store prices and costs as cents to avoid floating-point rounding drift.
    cost_cents = rng.integers(500, 12001, size=products)
    write("dim_product", ["product_key", "sku", "category", "brand", "unit_cost"],
          ((i, f"SKU-{i:05d}", ["Electronics", "Grocery", "Home", "Apparel"][i % 4],
            f"Brand-{i % 12:02d}", _money(Decimal(int(cost_cents[i - 1])) / 100))
           for i in range(1, products + 1)))

    with (out / "fact_sales.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["sale_id", "order_id", "date_key", "store_key", "product_key",
                         "quantity", "unit_price", "discount_amount", "cost_amount"])
        for base in range(0, sales, 50_000):
            count = min(50_000, sales - base)
            product_ids = rng.integers(1, products + 1, count)
            quantities = rng.integers(1, 6, count)
            for j in range(count):
                sale_id = base + j + 1
                order_id = (sale_id - 1) // 3 + 1
                # One order owns one date/store; multiple sale lines can share an order.
                day = (order_id * 2654435761 + seed) % days
                store_id = (order_id * 97 + seed) % stores + 1
                product_id = int(product_ids[j])
                quantity = int(quantities[j])
                cents = int(cost_cents[product_id - 1])
                price = Decimal(cents) * Decimal("1.65") / 100
                unit_price = Decimal(_money(price))
                discount = (unit_price * quantity * Decimal("0.10")) if order_id % 10 == 0 else Decimal(0)
                writer.writerow((sale_id, order_id, int((start + timedelta(days=day)).strftime("%Y%m%d")),
                                 store_id, product_id, quantity, _money(unit_price), _money(discount),
                                 _money(Decimal(cents * quantity) / 100)))

    snapshots = 0
    with (out / "fact_inventory_daily.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["date_key", "store_key", "product_key", "on_hand_units"])
        for day in range(0, days, inventory_step_days):
            date_key = int((start + timedelta(days=day)).strftime("%Y%m%d"))
            for store_id in range(1, stores + 1):
                for product_id in range(1, products + 1):
                    # Deterministic per-snapshot balances, not additive over time.
                    units = (store_id * 19 + product_id * 31 + day * 7 + seed) % 251
                    writer.writerow((date_key, store_id, product_id, units))
                    snapshots += 1
    return {"sales_lines": sales, "orders": (sales + 2) // 3, "stores": stores,
            "products": products, "days": days, "inventory_snapshots": snapshots}
