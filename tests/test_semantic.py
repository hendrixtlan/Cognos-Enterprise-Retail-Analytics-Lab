import json

import pytest

from retail_lab.semantic import CATALOG, check_catalog


def test_catalog_is_valid():
    result = check_catalog()
    assert result["metrics"] >= 10


def test_sales_lines_and_distinct_orders_not_confused():
    metrics = {item["id"]: item for item in json.loads(CATALOG.read_text())["metrics"]}
    assert metrics["sales_line_count"]["aggregation"] == "additive"
    assert metrics["distinct_orders"]["aggregation"] == "non_additive"
    assert metrics["inventory_on_hand"]["non_additive_across"] == ["date"]


def test_invalid_catalog_detected(tmp_path):
    file = tmp_path / "catalog.json"
    file.write_text(json.dumps({"metrics": [
        {"id": "x", "aggregation": "additive", "grain": "line", "definition": "sum(x)"},
        {"id": "x", "aggregation": "additive", "grain": "line", "definition": "sum(x)"},
    ]}))
    with pytest.raises(ValueError, match="Duplicate"):
        check_catalog(file)
