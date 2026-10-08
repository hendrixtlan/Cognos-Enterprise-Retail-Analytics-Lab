"""Static validation for semantic contracts independent of proprietary authoring tools."""
from __future__ import annotations

import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[2] / "semantic" / "kpi_catalog.json"
VALID_AGGREGATION = {"additive", "semi_additive", "non_additive"}


def check_catalog(path: Path = CATALOG) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    metrics = data["metrics"]
    seen = set()
    for metric in metrics:
        ident = metric["id"]
        if ident in seen:
            raise ValueError(f"Duplicate metric id: {ident}")
        seen.add(ident)
        if metric["aggregation"] not in VALID_AGGREGATION:
            raise ValueError(f"Invalid aggregation type: {ident}")
        if not metric.get("grain") or not metric.get("definition"):
            raise ValueError(f"Missing grain or definition: {ident}")
        if metric["aggregation"] == "semi_additive" and not metric.get("non_additive_across"):
            raise ValueError(f"Missing non-additive dimension: {ident}")
    return {"status": "valid", "metrics": len(metrics), "metric_ids": sorted(seen)}
