"""CLI entry point for the standalone retail warehouse lab."""
import argparse
import json
from pathlib import Path

from .benchmark import benchmark
from .db import init, load, optimize, validate
from .generate import generate
from .semantic import check_catalog


def main():
    parser = argparse.ArgumentParser(description="Retail Cognos analytics lab")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--sales", type=int, default=100_000)
    gen.add_argument("--stores", type=int, default=25)
    gen.add_argument("--products", type=int, default=200)
    gen.add_argument("--days", type=int, default=365)
    gen.add_argument("--seed", type=int, default=42)
    gen.add_argument("--inventory-step-days", type=int, default=7)
    gen.add_argument("--out", type=Path, default=Path("data/generated"))
    loader = sub.add_parser("load")
    loader.add_argument("--from-dir", type=Path, default=Path("data/generated"))
    bench = sub.add_parser("benchmark")
    bench.add_argument("--output", type=Path, default=Path("benchmarks/results/latest.json"))
    bench.add_argument("--repeats", type=int, default=5)
    for name in ("init", "optimize", "validate", "contract"):
        sub.add_parser(name)
    args = parser.parse_args()
    operations = {
        "generate": lambda: generate(args.out, args.sales, args.stores, args.products, args.days,
                                     args.seed, args.inventory_step_days),
        "init": init, "load": lambda: load(args.from_dir), "optimize": optimize,
        "validate": validate, "benchmark": lambda: benchmark(args.output, args.repeats),
        "contract": check_catalog,
    }
    print(json.dumps(operations[args.command](), indent=2))


if __name__ == "__main__":
    main()
