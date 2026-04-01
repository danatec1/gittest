from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def compare_files(old_file: str, new_file: str, output_dir: str = "output") -> Path:
    old_df = load_csv(old_file)
    new_df = load_csv(new_file)

    join_cols = ["data_type", "title"]
    left = old_df[join_cols + ["view_count", "metric_name", "metric_value"]].copy()
    right = new_df[join_cols + ["view_count", "metric_name", "metric_value"]].copy()

    merged = right.merge(left, on=join_cols, how="outer", suffixes=("_new", "_old"))
    merged["view_diff"] = merged["view_count_new"].fillna(0) - merged["view_count_old"].fillna(0)
    merged["metric_diff"] = merged["metric_value_new"].fillna(0) - merged["metric_value_old"].fillna(0)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(output_dir) / "compare_result.csv"
    merged.to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-file", required=True)
    parser.add_argument("--new-file", required=True)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    out_path = compare_files(args.old_file, args.new_file, args.output_dir)
    print(f"saved compare file: {out_path}")


if __name__ == "__main__":
    main()
